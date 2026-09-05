from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
LOCATIONS_PATH = BASE_DIR / "data" / "locations.json"


SEEDED_PANCHAYATS = [
    {
        "id": "nimmanapalle",
        "state": "Andhra Pradesh",
        "district": "Chittoor",
        "mandal": "Madanapalle",
        "name": "Nimmanapalle",
        "latitude": 13.55,
        "longitude": 78.50,
        "soil_type": "Red loamy soil",
        "major_crops": ["Tomato", "Groundnut", "Paddy"],
    },
    {
        "id": "kurabalakota",
        "state": "Andhra Pradesh",
        "district": "Chittoor",
        "mandal": "Madanapalle",
        "name": "Kurabalakota",
        "latitude": 13.65,
        "longitude": 78.48,
        "soil_type": "Sandy loam",
        "major_crops": ["Groundnut", "Tomato", "Chilli"],
    },
    {
        "id": "basinikonda",
        "state": "Andhra Pradesh",
        "district": "Chittoor",
        "mandal": "Madanapalle",
        "name": "Basinikonda",
        "latitude": 13.566,
        "longitude": 78.51,
        "soil_type": "Black cotton soil",
        "major_crops": ["Paddy", "Tomato", "Cotton"],
    },
]


CROP_RULES = {
    "Tomato": {
        "disease": "High humidity can increase fungal disease risk in tomato.",
        "action": "Clear furrows and check standing water near tomato roots.",
    },
    "Groundnut": {
        "disease": "Waterlogging may damage groundnut pods and root health.",
        "action": "Avoid water stagnation and check drainage after rainfall.",
    },
    "Paddy": {
        "disease": "Watch for blast risk when humidity remains high.",
        "action": "Maintain controlled water level; avoid sudden excess flow.",
    },
    "Chilli": {
        "disease": "High humidity can increase fruit rot and leaf spot risk.",
        "action": "Delay spraying until leaves dry and wind speed reduces.",
    },
    "Cotton": {
        "disease": "Wet and windy conditions can stress young cotton plants.",
        "action": "Check field drainage and avoid foliar spray during wind.",
    },
}


def get_panchayats() -> list[dict]:
    if LOCATIONS_PATH.exists():
        with LOCATIONS_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    return SEEDED_PANCHAYATS
