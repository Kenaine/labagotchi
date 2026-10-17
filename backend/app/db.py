import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import firebase_admin
from firebase_admin import credentials, firestore

_lock = threading.Lock()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


DEFAULT_PET: Dict[str, Any] = {
    "name": "Pvechi",
    "species": "cyber-cat",
    "hp": 100,
    "mood": 85,
    "xp": 0,
    "level": 1,
    "stage": "Bit Hatchling",
    "status": "THRIVING",
    "overclocked": False,
    "streak": 1,
    "last_fed_at": None,
    "last_event": "Booting up inside CT 102...",
    "last_nodes": [],
}


class FirestoreRepository:
    """
    Dual-mode Firebase/Firestore repository:
    - Uses official `firebase_admin.firestore` when FIRESTORE_EMULATOR_HOST
      or GOOGLE_APPLICATION_CREDENTIALS is configured.
    - Automatically falls back to a lightweight local Firestore-compatible
      JSON document store (/opt/labagotchi/data/firestore.json) for zero-JVM
      homelab operation inside CT 102.
    """

    def __init__(self) -> None:
        self.emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")
        self.cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.project_id = os.getenv("FIREBASE_PROJECT_ID", "labagotchi-homelab")
        self._firestore_client = None

        if self.emulator_host or (self.cred_path and os.path.exists(self.cred_path)):
            try:
                if not firebase_admin._apps:
                    if self.cred_path and os.path.exists(self.cred_path):
                        cred = credentials.Certificate(self.cred_path)
                        firebase_admin.initialize_app(cred, {"projectId": self.project_id})
                    else:
                        firebase_admin.initialize_app(options={"projectId": self.project_id})
                self._firestore_client = firestore.client()
            except Exception:
                self._firestore_client = None

    @property
    def mode(self) -> str:
        if self._firestore_client is not None:
            return "firebase-emulator" if self.emulator_host else "firebase-cloud"
        return "firebase-local-store"

    def _local_path(self) -> Path:
        custom = os.getenv("LABAGOTCHI_LOCAL_DB_PATH")
        if custom:
            return Path(custom)
        return Path("/opt/labagotchi/data/firestore.json")

    def _read_local(self) -> Dict[str, Any]:
        p = self._local_path()
        if not p.exists():
            return {"pets": {}, "ping_history": []}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {"pets": {}, "ping_history": []}

    def _write_local(self, data: Dict[str, Any]) -> None:
        p = self._local_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(p)

    def get_pet(self) -> Dict[str, Any]:
        if self._firestore_client is not None:
            doc = self._firestore_client.collection("pets").document("homelab_pet").get()
            if doc.exists:
                data = doc.to_dict()
                return {**DEFAULT_PET, **data}
            self.save_pet(DEFAULT_PET.copy())
            return DEFAULT_PET.copy()

        with _lock:
            store = self._read_local()
            pet = store.get("pets", {}).get("homelab_pet")
            if not pet:
                pet = DEFAULT_PET.copy()
                store.setdefault("pets", {})["homelab_pet"] = pet
                self._write_local(store)
            return {**DEFAULT_PET, **pet}

    def save_pet(self, pet: Dict[str, Any]) -> Dict[str, Any]:
        if self._firestore_client is not None:
            self._firestore_client.collection("pets").document("homelab_pet").set(pet)
            return pet

        with _lock:
            store = self._read_local()
            store.setdefault("pets", {})["homelab_pet"] = pet
            self._write_local(store)
            return pet

    def add_ping_log(self, entry: Dict[str, Any]) -> None:
        if self._firestore_client is not None:
            doc_id = entry.get("timestamp", utc_now_iso())
            self._firestore_client.collection("ping_history").document(doc_id).set(entry)
            return

        with _lock:
            store = self._read_local()
            history: List[Dict[str, Any]] = store.get("ping_history", [])
            history.append(entry)
            store["ping_history"] = history[-25:]
            self._write_local(store)

    def get_recent_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        if self._firestore_client is not None:
            docs = (
                self._firestore_client.collection("ping_history")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            items = [d.to_dict() for d in docs]
            items.reverse()
            return items

        with _lock:
            store = self._read_local()
            history = store.get("ping_history", [])
            return history[-limit:]
