import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_firestore.json"
    monkeypatch.setenv("LABAGOTCHI_LOCAL_DB_PATH", str(db_file))
    monkeypatch.delenv("FIRESTORE_EMULATOR_HOST", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    yield


def test_health_and_initial_state(monkeypatch):
    from app.main import app
    import app.main as main_mod

    async def fake_probe_all():
        return [
            {"id": "proxmox", "name": "Proxmox VE", "ip": "192.168.1.34", "port": 8006, "role": "core", "online": True, "latency_ms": 0.9},
            {"id": "pihole", "name": "Pi-hole DNS", "ip": "192.168.1.36", "port": 53, "role": "core", "online": True, "latency_ms": 1.1},
            {"id": "docker", "name": "Docker Host", "ip": "192.168.1.38", "port": 22, "role": "core", "online": True, "latency_ms": 1.2},
            {"id": "ai-admin", "name": "AI-Admin", "ip": "192.168.1.50", "port": 22, "role": "core", "online": True, "latency_ms": 0.5},
            {"id": "ken", "name": "Ken (Gaming Rig)", "ip": "192.168.1.35", "port": 11434, "role": "bonus", "online": False, "latency_ms": None},
        ]

    monkeypatch.setattr(main_mod, "probe_all_nodes", fake_probe_all)
    client = TestClient(app)

    r_health = client.get("/api/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"

    r_state = client.get("/api/state")
    assert r_state.status_code == 200
    data = r_state.json()
    assert data["pet"]["hp"] == 100
    assert data["pet"]["overclocked"] is False
    assert data["pet"]["name"] == "Pvechi"
    assert len(data["pet"]["last_nodes"]) == 5


def test_feed_core_vs_bonus_overclock(monkeypatch):
    from app.main import app
    import app.main as main_mod

    # First feed: Ken is asleep (4/4 core up, bonus offline)
    async def probe_ken_asleep():
        return [
            {"id": "proxmox", "name": "Proxmox VE", "ip": "192.168.1.34", "port": 8006, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "pihole", "name": "Pi-hole DNS", "ip": "192.168.1.36", "port": 53, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "docker", "name": "Docker Host", "ip": "192.168.1.38", "port": 22, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "ai-admin", "name": "AI-Admin", "ip": "192.168.1.50", "port": 22, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "ken", "name": "Ken (Gaming Rig)", "ip": "192.168.1.35", "port": 11434, "role": "bonus", "online": False, "latency_ms": None},
        ]

    monkeypatch.setattr(main_mod, "probe_all_nodes", probe_ken_asleep)
    client = TestClient(app)

    r1 = client.post("/api/pet/feed")
    assert r1.status_code == 200
    pet1 = r1.json()["pet"]
    assert pet1["hp"] == 100
    assert pet1["overclocked"] is False
    xp_after_first = pet1["xp"]
    assert xp_after_first == 20  # 4 core nodes * 5 XP

    # Second feed: Ken wakes up! Overclocked 2x XP bonus
    async def probe_ken_awake():
        return [
            {"id": "proxmox", "name": "Proxmox VE", "ip": "192.168.1.34", "port": 8006, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "pihole", "name": "Pi-hole DNS", "ip": "192.168.1.36", "port": 53, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "docker", "name": "Docker Host", "ip": "192.168.1.38", "port": 22, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "ai-admin", "name": "AI-Admin", "ip": "192.168.1.50", "port": 22, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "ken", "name": "Ken (Gaming Rig)", "ip": "192.168.1.35", "port": 11434, "role": "bonus", "online": True, "latency_ms": 2.4},
        ]

    monkeypatch.setattr(main_mod, "probe_all_nodes", probe_ken_awake)
    r2 = client.post("/api/pet/feed")
    assert r2.status_code == 200
    pet2 = r2.json()["pet"]
    assert pet2["hp"] == 100
    assert pet2["overclocked"] is True
    assert pet2["xp"] > xp_after_first + 20  # Boosted XP when Ken is awake


def test_heal_and_customize(monkeypatch):
    from app.main import app
    import app.main as main_mod

    async def fake_probe():
        return [
            {"id": "proxmox", "name": "Proxmox VE", "ip": "192.168.1.34", "port": 8006, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "pihole", "name": "Pi-hole DNS", "ip": "192.168.1.36", "port": 53, "role": "core", "online": False, "latency_ms": None},
            {"id": "docker", "name": "Docker Host", "ip": "192.168.1.38", "port": 22, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "ai-admin", "name": "AI-Admin", "ip": "192.168.1.50", "port": 22, "role": "core", "online": True, "latency_ms": 1.0},
            {"id": "ken", "name": "Ken (Gaming Rig)", "ip": "192.168.1.35", "port": 11434, "role": "bonus", "online": False, "latency_ms": None},
        ]

    monkeypatch.setattr(main_mod, "probe_all_nodes", fake_probe)
    client = TestClient(app)

    r_heal = client.post("/api/pet/heal")
    assert r_heal.status_code == 200
    assert r_heal.json()["pet"]["mood"] >= 90

    r_cust = client.patch("/api/pet/customize", json={"name": "Zomboid Rex", "species": "mecha-owl"})
    assert r_cust.status_code == 200
    pet = r_cust.json()["pet"]
    assert pet["name"] == "Zomboid Rex"
    assert pet["species"] == "mecha-owl"
