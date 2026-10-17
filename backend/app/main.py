from pathlib import Path
from typing import Any, Dict, List, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.db import FirestoreRepository, utc_now_iso
from app.probes import probe_all_nodes

app = FastAPI(title="Labagotchi API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CustomizeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=24)
    species: Literal["cyber-cat", "server-slime", "mecha-owl"] = "cyber-cat"


def compute_stage(level: int) -> str:
    if level <= 2:
        return "Bit Hatchling"
    if level <= 5:
        return "Packet Prowler"
    return "Rack Sovereign"


def compute_status(hp: int, mood: int, overclocked: bool) -> str:
    if hp <= 50:
        return "CRITICAL"
    if hp < 100:
        return "DEGRADED"
    if overclocked:
        return "OVERCLOCKED"
    if mood >= 75:
        return "THRIVING"
    return "CHILL"


def apply_probe_results(
    pet: Dict[str, Any], nodes: List[Dict[str, Any]], is_feed_action: bool = True
) -> Dict[str, Any]:
    core_nodes = [n for n in nodes if n["role"] == "core"]
    bonus_nodes = [n for n in nodes if n["role"] == "bonus"]

    core_total = max(len(core_nodes), 1)
    core_online_nodes = [n for n in core_nodes if n["online"]]
    core_online = len(core_online_nodes)

    hp = round((core_online / core_total) * 100)
    ken_online = any(n["online"] for n in bonus_nodes)

    latencies = [n["latency_ms"] for n in core_online_nodes if n["latency_ms"] is not None]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

    xp_gain = 0
    mood_delta = 0

    if is_feed_action:
        base_xp = core_online * 5
        xp_gain = base_xp * 2 if ken_online else base_xp

        if core_online == core_total:
            mood_delta += 4 if (avg_latency > 0 and avg_latency < 10.0) else 2
        else:
            mood_delta -= (core_total - core_online) * 8

        if ken_online:
            mood_delta += 10

    new_xp = int(pet.get("xp", 0)) + xp_gain
    new_level = 1 + (new_xp // 50)
    new_mood = max(0, min(100, int(pet.get("mood", 85)) + mood_delta))
    new_stage = compute_stage(new_level)
    new_status = compute_status(hp, new_mood, ken_online)

    now = utc_now_iso()
    if ken_online:
        event_msg = (
            f"OVERCLOCK ACTIVE! Ken (.35) is awake — +{xp_gain} XP (2x boost) | "
            f"Core {core_online}/{core_total} UP ({avg_latency} ms)"
        )
    elif is_feed_action:
        event_msg = (
            f"Fed packets from {core_online}/{core_total} core nodes "
            f"(avg {avg_latency} ms) — +{xp_gain} XP!"
        )
    else:
        event_msg = f"Telemetry synced: {core_online}/{core_total} core nodes online."

    updated_pet = {
        **pet,
        "hp": hp,
        "mood": new_mood,
        "xp": new_xp,
        "level": new_level,
        "stage": new_stage,
        "status": new_status,
        "overclocked": ken_online,
        "streak": int(pet.get("streak", 1)) + (1 if is_feed_action and core_online == core_total else 0),
        "last_fed_at": now if is_feed_action else pet.get("last_fed_at") or now,
        "last_event": event_msg,
        "last_nodes": nodes,
        "avg_core_latency_ms": avg_latency,
    }

    log_entry = {
        "timestamp": now,
        "avg_core_latency_ms": avg_latency,
        "core_online": core_online,
        "core_total": core_total,
        "ken_online": ken_online,
        "nodes": nodes,
    }
    return {"pet": updated_pet, "log_entry": log_entry}


@app.get("/api/health")
async def health() -> Dict[str, Any]:
    repo = FirestoreRepository()
    return {
        "status": "ok",
        "service": "labagotchi-api",
        "firebase_mode": repo.mode,
        "timestamp": utc_now_iso(),
    }


@app.get("/api/state")
async def get_state() -> Dict[str, Any]:
    repo = FirestoreRepository()
    pet = repo.get_pet()
    if not pet.get("last_nodes"):
        nodes = await probe_all_nodes()
        res = apply_probe_results(pet, nodes, is_feed_action=False)
        pet = repo.save_pet(res["pet"])
        repo.add_ping_log(res["log_entry"])

    history = repo.get_recent_logs(limit=20)
    return {
        "pet": pet,
        "history": history,
        "firebase_mode": repo.mode,
    }


@app.post("/api/pet/feed")
async def feed_pet() -> Dict[str, Any]:
    repo = FirestoreRepository()
    pet = repo.get_pet()
    nodes = await probe_all_nodes()
    res = apply_probe_results(pet, nodes, is_feed_action=True)
    saved_pet = repo.save_pet(res["pet"])
    repo.add_ping_log(res["log_entry"])
    return {
        "pet": saved_pet,
        "history": repo.get_recent_logs(limit=20),
        "firebase_mode": repo.mode,
    }


@app.post("/api/pet/heal")
async def heal_pet() -> Dict[str, Any]:
    repo = FirestoreRepository()
    pet = repo.get_pet()
    if not pet.get("last_nodes"):
        nodes = await probe_all_nodes()
        pet = apply_probe_results(pet, nodes, is_feed_action=False)["pet"]

    new_xp = int(pet.get("xp", 0)) + 5
    new_level = 1 + (new_xp // 50)
    new_mood = min(100, int(pet.get("mood", 85)) + 15)
    hp = int(pet.get("hp", 100))
    overclocked = bool(pet.get("overclocked", False))

    pet.update(
        {
            "mood": new_mood,
            "xp": new_xp,
            "level": new_level,
            "stage": compute_stage(new_level),
            "status": compute_status(hp, new_mood, overclocked),
            "last_event": f"You petted {pet['name']}! +15 Mood, +5 XP 💚",
        }
    )
    saved_pet = repo.save_pet(pet)
    return {
        "pet": saved_pet,
        "history": repo.get_recent_logs(limit=20),
        "firebase_mode": repo.mode,
    }


@app.patch("/api/pet/customize")
async def customize_pet(payload: CustomizeRequest) -> Dict[str, Any]:
    repo = FirestoreRepository()
    pet = repo.get_pet()
    pet.update(
        {
            "name": payload.name.strip(),
            "species": payload.species,
            "last_event": f"Identity updated: {payload.name.strip()} ({payload.species}) ✨",
        }
    )
    saved_pet = repo.save_pet(pet)
    return {
        "pet": saved_pet,
        "history": repo.get_recent_logs(limit=20),
        "firebase_mode": repo.mode,
    }


# Serve production React frontend if built
FRONTEND_DIST = Path("/opt/labagotchi/frontend/dist")
if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(index_file))
    return {"message": "Labagotchi API running. Frontend bundle not built yet."}
