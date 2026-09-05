from __future__ import annotations

import random
import json
import time
import urllib.parse
import urllib.request
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .data import CROP_RULES, get_panchayats
from .store import read_store, reset_store, write_store


Role = Literal["farmer", "officer"]

app = FastAPI(title="FarmSmart API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SignupRequest(BaseModel):
    name: str = Field(min_length=2)
    phone: str = Field(pattern=r"^[6-9]\d{9}$")
    role: Role
    panchayat_id: str


class OtpRequest(BaseModel):
    phone: str = Field(pattern=r"^[6-9]\d{9}$")
    role: Role


class VerifyOtpRequest(BaseModel):
    phone: str = Field(pattern=r"^[6-9]\d{9}$")
    role: Role
    otp: str = Field(pattern=r"^\d{6}$")


class RecommendationRequest(BaseModel):
    panchayat_id: str
    crop: str
    temperature: float
    rain_probability: float
    humidity: float
    soil_moisture: float
    wind_speed: float


def find_panchayat(panchayat_id: str) -> dict:
    for panchayat in get_panchayats():
        if panchayat["id"] == panchayat_id:
            return panchayat
    raise HTTPException(status_code=404, detail="Panchayat not found")


def find_user(role: Role, phone: str) -> dict | None:
    data = read_store()
    for user in data["users"]:
        if user["role"] == role and user["phone"] == phone:
            return user
    return None


def clean_expired_otps(data: dict) -> None:
    now = int(time.time())
    data["otps"] = [item for item in data["otps"] if item["expires_at"] > now]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "farmsmart-api"}


@app.post("/dev/reset")
def dev_reset() -> dict:
    reset_store()
    return {"message": "Local store reset"}


@app.post("/auth/signup")
def signup(payload: SignupRequest) -> dict:
    find_panchayat(payload.panchayat_id)
    data = read_store()

    for user in data["users"]:
        if user["role"] == payload.role and user["phone"] == payload.phone:
            raise HTTPException(status_code=409, detail="Mobile number already exists for this role")

    panchayat = find_panchayat(payload.panchayat_id)
    user = {
        "id": f"user_{uuid4().hex[:12]}",
        "name": payload.name,
        "phone": payload.phone,
        "role": payload.role,
        "panchayat_id": payload.panchayat_id,
        "assigned_area": "Madanapalle Mandal" if payload.role == "officer" else f"{panchayat['name']} Panchayat",
    }
    data["users"].append(user)
    write_store(data)
    return {"message": "Account created", "user": user}


@app.post("/auth/request-otp")
def request_otp(payload: OtpRequest) -> dict:
    user = find_user(payload.role, payload.phone)
    if not user:
        raise HTTPException(status_code=403, detail="Mobile number is not registered for selected role")

    data = read_store()
    clean_expired_otps(data)
    otp = f"{random.randint(100000, 999999)}"
    data["otps"] = [
        item for item in data["otps"]
        if not (item["phone"] == payload.phone and item["role"] == payload.role)
    ]
    data["otps"].append(
        {
            "phone": payload.phone,
            "role": payload.role,
            "otp": otp,
            "expires_at": int(time.time()) + 300,
        }
    )
    write_store(data)

    return {
        "message": "OTP generated",
        "otp_for_local_testing": otp,
        "expires_in_seconds": 300,
        "note": "For production, send OTP by SMS and do not return it in API response.",
    }


@app.post("/auth/verify-otp")
def verify_otp(payload: VerifyOtpRequest) -> dict:
    data = read_store()
    clean_expired_otps(data)
    user = find_user(payload.role, payload.phone)
    if not user:
        raise HTTPException(status_code=403, detail="Mobile number is not registered for selected role")

    match = next(
        (
            item for item in data["otps"]
            if item["phone"] == payload.phone and item["role"] == payload.role and item["otp"] == payload.otp
        ),
        None,
    )
    if not match:
        write_store(data)
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    data["otps"].remove(match)
    write_store(data)
    return {
        "message": "Login successful",
        "access_token": f"local_{uuid4().hex}",
        "token_type": "local",
        "user": user,
    }


@app.get("/locations/states")
def states() -> dict:
    return {"states": sorted({item["state"] for item in get_panchayats()})}


@app.get("/locations/districts")
def districts(state: str) -> dict:
    return {"districts": sorted({item["district"] for item in get_panchayats() if item["state"] == state})}


@app.get("/locations/mandals")
def mandals(state: str, district: str) -> dict:
    return {
        "mandals": sorted(
            {item["mandal"] for item in get_panchayats() if item["state"] == state and item["district"] == district}
        )
    }


@app.get("/locations/panchayats")
def panchayats(state: str | None = None, district: str | None = None, mandal: str | None = None) -> dict:
    result = get_panchayats()
    if state:
        result = [item for item in result if item["state"] == state]
    if district:
        result = [item for item in result if item["district"] == district]
    if mandal:
        result = [item for item in result if item["mandal"] == mandal]
    return {"panchayats": result}


@app.get("/crops")
def crops() -> dict:
    return {"crops": sorted(CROP_RULES.keys())}


@app.get("/weather/live/{panchayat_id}")
def live_weather(panchayat_id: str) -> dict:
    panchayat = find_panchayat(panchayat_id)
    query = urllib.parse.urlencode(
        {
            "latitude": panchayat["latitude"],
            "longitude": panchayat["longitude"],
            "current": "temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m",
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,wind_speed_10m,soil_moisture_0_1cm",
            "forecast_days": 1,
            "timezone": "auto",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
        }
    )
    url = f"https://api.open-meteo.com/v1/forecast?{query}"

    try:
      with urllib.request.urlopen(url, timeout=12) as response:
          data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Weather provider unavailable: {exc}") from exc

    return {"source": "Open-Meteo", "panchayat": panchayat, "weather": data}


@app.post("/recommendations")
def recommendation(payload: RecommendationRequest) -> dict:
    find_panchayat(payload.panchayat_id)
    if payload.crop not in CROP_RULES:
        raise HTTPException(status_code=404, detail="Crop not found")

    high_rain = payload.rain_probability >= 70
    low_soil = payload.soil_moisture <= 30
    high_wind = payload.wind_speed >= 28
    high_humidity = payload.humidity >= 82
    crop = CROP_RULES[payload.crop]

    irrigation = "Avoid irrigation" if high_rain else "Irrigate carefully" if low_soil else "Wait and observe"
    spraying = "Avoid spraying" if high_rain or high_wind else "Spraying is possible"
    disease_risk = "High" if high_humidity else "Low"
    risk = "HIGH" if high_rain or (high_humidity and payload.crop in {"Tomato", "Chilli", "Paddy"}) else "MEDIUM"

    reasons = []
    if high_rain:
        reasons.append(f"Rain probability is {payload.rain_probability}%, so irrigation and spraying are unsafe.")
    if low_soil:
        reasons.append(f"Soil moisture is {payload.soil_moisture}%, so controlled irrigation may be needed.")
    if high_wind:
        reasons.append(f"Wind speed is {payload.wind_speed} km/h, so spray drift risk is high.")
    if high_humidity:
        reasons.append(f"Humidity is {payload.humidity}%, increasing disease risk for {payload.crop}.")

    return {
        "risk": risk,
        "irrigation": irrigation,
        "spraying": spraying,
        "disease_risk": disease_risk,
        "recommended_action": crop["action"],
        "crop_warning": crop["disease"],
        "reasons": reasons or ["Weather signals are moderate; observe before taking field action."],
    }
