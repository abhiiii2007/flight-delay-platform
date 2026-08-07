from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import RAW_DATA_PATH


def generate(rows: int = 12_000, seed: int = 42) -> pd.DataFrame:
    """Create realistic-looking data strictly for local pipeline demonstrations."""
    rng = np.random.default_rng(seed)
    carriers = np.array(["AA", "DL", "UA", "WN", "B6"])
    airports = np.array(["ATL", "JFK", "LAX", "ORD", "DFW", "DEN", "SFO"])
    dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    flight_date = rng.choice(dates, rows)
    origin = rng.choice(airports, rows)
    destination = rng.choice(airports, rows)
    same = origin == destination
    while same.any():
        destination[same] = rng.choice(airports, same.sum())
        same = origin == destination
    scheduled_hour = rng.integers(5, 23, rows)
    distance = rng.integers(200, 2801, rows)
    carrier = rng.choice(carriers, rows)
    weather_severity = rng.beta(1.5, 6, rows).round(3)
    weekend = pd.DatetimeIndex(flight_date).dayofweek >= 5
    peak = ((scheduled_hour >= 16) & (scheduled_hour <= 20)).astype(int)
    carrier_effect = (
        pd.Series(carrier).map({"AA": 1, "DL": -2, "UA": 2, "WN": 3, "B6": 4}).to_numpy()
    )
    delay = (
        (rng.normal(1, 13, rows) + weather_severity * 55 + peak * 7 + weekend * 2 + carrier_effect)
        .round()
        .astype(int)
    )
    cancelled = (rng.random(rows) < (0.008 + weather_severity * 0.035)).astype(int)
    return pd.DataFrame(
        {
            "flight_date": pd.to_datetime(flight_date).strftime("%Y-%m-%d"),
            "carrier": carrier,
            "flight_number": rng.integers(1, 9999, rows),
            "origin": origin,
            "destination": destination,
            "scheduled_departure_hour": scheduled_hour,
            "departure_delay_minutes": delay,
            "distance_miles": distance,
            "cancelled": cancelled,
            "weather_severity": weather_severity,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=12_000)
    parser.add_argument("--output", type=Path, default=RAW_DATA_PATH)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    generate(args.rows).to_csv(args.output, index=False)
    print(f"Generated {args.rows:,} demo rows at {args.output}")


if __name__ == "__main__":
    main()
