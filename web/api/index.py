"""Request-based FlightPulse prediction API for Vercel."""

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="FlightPulse prediction API", version="1.0.0")
model = joblib.load(Path(__file__).with_name("delay_model.joblib"))


class Flight(BaseModel):
    carrier: str = Field(min_length=2, max_length=2)
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    hour: int = Field(ge=0, le=23)
    month: int = Field(ge=1, le=12)
    day_of_week: int = Field(ge=0, le=6)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": "random_forest"}


@app.post("/api/predict")
def predict(flight: Flight) -> dict[str, float | str]:
    row = pd.DataFrame([{
        "carrier": flight.carrier.upper(),
        "origin": flight.origin.upper(),
        "destination": flight.destination.upper(),
        "scheduled_departure_hour": flight.hour,
        "month": flight.month,
        "day_of_week": flight.day_of_week,
    }])
    probability = float(model.predict_proba(row)[0, 1])
    return {"delay_probability": probability, "risk_label": "higher" if probability >= 0.5 else "lower"}
