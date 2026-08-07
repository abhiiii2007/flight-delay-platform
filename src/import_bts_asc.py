"""Convert the fixed-layout BTS .asc release into FlightPulse columns."""

import argparse
import csv
from pathlib import Path

import pandas as pd

from src.import_bts import MAX_INPUT_BYTES

FIELD_POSITIONS = {
    0: "marketing_carrier",
    1: "marketing_flight_number",
    4: "actual_operating_carrier",
    5: "actual_operating_flight_number",
    6: "origin",
    7: "destination",
    8: "flight_date",
    9: "day_of_week_bts",
    11: "scheduled_departure_crs",
    20: "departure_delay_minutes",
    28: "air_time_minutes",
    29: "cancellation_code",
    31: "weather_delay_minutes",
}
EXPECTED_FIELD_COUNT = 71


def validate_row_shape(path: Path) -> None:
    with path.open(newline="", errors="replace") as source:
        reader = csv.reader(source, delimiter="|")
        for line_number, row in enumerate(reader, start=1):
            if len(row) != EXPECTED_FIELD_COUNT:
                raise ValueError(
                    f"Line {line_number} has {len(row)} fields; expected {EXPECTED_FIELD_COUNT}"
                )
            if line_number >= 1000:
                break


def read_release(path: Path, limit: int | None = None) -> pd.DataFrame:
    if path.suffix.lower() != ".asc":
        raise ValueError("BTS release input must be an .asc file")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("BTS input exceeds the 1 GB safety limit")
    validate_row_shape(path)
    selected = pd.read_csv(
        path,
        sep="|",
        header=None,
        usecols=list(FIELD_POSITIONS.keys()),
        dtype=str,
        keep_default_na=False,
        nrows=limit,
    )
    return selected.rename(columns=FIELD_POSITIONS)


def normalize(source: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame()
    result["flight_date"] = pd.to_datetime(source["flight_date"], errors="coerce").dt.strftime(
        "%Y-%m-%d"
    )
    result["carrier"] = source["marketing_carrier"].str.strip().str.upper()
    result["flight_number"] = pd.to_numeric(source["marketing_flight_number"], errors="coerce")
    result["origin"] = source["origin"].str.strip().str.upper()
    result["destination"] = source["destination"].str.strip().str.upper()
    scheduled = pd.to_numeric(source["scheduled_departure_crs"], errors="coerce").fillna(0)
    result["scheduled_departure_hour"] = (scheduled // 100).clip(0, 23).astype(int)
    result["departure_delay_minutes"] = pd.to_numeric(
        source["departure_delay_minutes"], errors="coerce"
    ).fillna(0)
    result["air_time_minutes"] = pd.to_numeric(source["air_time_minutes"], errors="coerce")
    result["cancelled"] = source["cancellation_code"].str.strip().ne("").astype(int)
    result["weather_severity"] = pd.to_numeric(
        source["weather_delay_minutes"], errors="coerce"
    ).fillna(0)
    return result


def convert(path: Path, output: Path, limit: int | None = None) -> pd.DataFrame:
    result = normalize(read_release(path, limit))
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    convert(args.source, args.output, args.limit)


if __name__ == "__main__":
    main()
