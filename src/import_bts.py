"""Convert a standard BTS on-time-performance CSV to FlightPulse format."""

import argparse
from pathlib import Path

import pandas as pd

from src.config import RAW_DATA_PATH

MAX_INPUT_BYTES = 1_000_000_000
COLUMN_ALIASES = {
    "flight_date": ("FlightDate", "FL_DATE"),
    "carrier": ("Reporting_Airline", "OP_UNIQUE_CARRIER"),
    "flight_number": ("Flight_Number_Reporting_Airline", "OP_CARRIER_FL_NUM"),
    "origin": ("Origin", "ORIGIN"),
    "destination": ("Dest", "DEST"),
    "scheduled_departure": ("CRSDepTime", "CRS_DEP_TIME"),
    "departure_delay_minutes": ("DepDelay", "DEP_DELAY"),
    "distance_miles": ("Distance", "DISTANCE"),
    "cancelled": ("Cancelled", "CANCELLED"),
    "weather_delay_minutes": ("WeatherDelay", "WEATHER_DELAY"),
}


def _resolve_columns(columns: pd.Index) -> dict[str, str]:
    resolved = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        match = next((alias for alias in aliases if alias in columns), None)
        if match:
            resolved[canonical] = match
        elif canonical != "weather_delay_minutes":
            raise ValueError(f"Missing required BTS column for {canonical}: {aliases}")
    return resolved


def convert(source: Path, output: Path = RAW_DATA_PATH) -> pd.DataFrame:
    if source.suffix.lower() != ".csv":
        raise ValueError("BTS input must be a CSV file")
    if source.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("BTS input exceeds the 1 GB safety limit")
    source_data = pd.read_csv(source)
    columns = _resolve_columns(source_data.columns)
    result = pd.DataFrame()
    for canonical in (
        "flight_date",
        "carrier",
        "flight_number",
        "origin",
        "destination",
        "departure_delay_minutes",
        "distance_miles",
        "cancelled",
    ):
        result[canonical] = source_data[columns[canonical]]
    scheduled = pd.to_numeric(source_data[columns["scheduled_departure"]], errors="coerce").fillna(
        0
    )
    result["scheduled_departure_hour"] = (scheduled // 100).clip(0, 23).astype(int)
    result["departure_delay_minutes"] = pd.to_numeric(
        result["departure_delay_minutes"], errors="coerce"
    ).fillna(0)
    weather = (
        source_data[columns["weather_delay_minutes"]]
        if "weather_delay_minutes" in columns
        else pd.Series(0, index=source_data.index)
    )
    result["weather_severity"] = pd.to_numeric(weather, errors="coerce").fillna(0)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=RAW_DATA_PATH)
    args = parser.parse_args()
    convert(args.source, args.output)


if __name__ == "__main__":
    main()
