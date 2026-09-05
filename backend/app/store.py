from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
STORE_PATH = DATA_DIR / "store.json"


SEED_DATA: dict[str, Any] = {
    "users": [
        {
            "id": "user_farmer_demo",
            "name": "Ramesh Kumar",
            "phone": "9876543210",
            "role": "farmer",
            "panchayat_id": "nimmanapalle",
            "assigned_area": "Nimmanapalle Panchayat",
        },
        {
            "id": "user_officer_demo",
            "name": "Anitha Reddy",
            "phone": "9000011111",
            "role": "officer",
            "panchayat_id": "kurabalakota",
            "assigned_area": "Madanapalle Mandal",
        },
    ],
    "otps": [],
}


def ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        write_store(deepcopy(SEED_DATA))


def read_store() -> dict[str, Any]:
    ensure_store()
    with STORE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_store(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with STORE_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def reset_store() -> dict[str, Any]:
    data = deepcopy(SEED_DATA)
    write_store(data)
    return data
