"""Clean flight data and load it into the analytics database."""

from pathlib import Path

import boto3
import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DATABASE_URL, RAW_DATA_PATH, S3_BUCKET

REQUIRED_COLUMNS = {
    "flight_date",
    "carrier",
    "flight_number",
    "origin",
    "destination",
    "scheduled_departure_hour",
    "departure_delay_minutes",
    "distance_miles",
    "cancelled",
    "weather_severity",
}


def transform(flights: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(flights.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    cleaned = flights[list(sorted(REQUIRED_COLUMNS))].copy()
    cleaned["flight_date"] = pd.to_datetime(cleaned["flight_date"], errors="coerce")
    cleaned["carrier"] = cleaned["carrier"].astype(str).str.strip().str.upper()
    cleaned["origin"] = cleaned["origin"].astype(str).str.strip().str.upper()
    cleaned["destination"] = cleaned["destination"].astype(str).str.strip().str.upper()

    numeric = [
        "flight_number",
        "scheduled_departure_hour",
        "departure_delay_minutes",
        "distance_miles",
        "cancelled",
        "weather_severity",
    ]
    for column in numeric:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(
        subset=["flight_date", "carrier", "origin", "destination", *numeric]
    ).drop_duplicates()
    cleaned["cancelled"] = cleaned["cancelled"].astype(int).clip(0, 1)
    cleaned["month"] = cleaned["flight_date"].dt.month
    cleaned["day_of_week"] = cleaned["flight_date"].dt.dayofweek
    cleaned["is_delayed"] = (cleaned["departure_delay_minutes"] >= 15).astype(int)
    return cleaned.reset_index(drop=True)


def load(flights: pd.DataFrame, database_url: str = DATABASE_URL) -> None:
    engine = create_engine(database_url)
    flights.to_sql("flights", engine, if_exists="replace", index=False)
    with engine.begin() as connection:
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_flight_date ON flights(flight_date)")
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_route ON flights(origin, destination)")
        )
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_carrier ON flights(carrier)"))


def upload_raw_to_s3(path: Path, bucket: str = S3_BUCKET) -> None:
    if not bucket:
        return
    boto3.client("s3").upload_file(str(path), bucket, f"raw/{path.name}")


def main() -> None:
    raw_path = Path(RAW_DATA_PATH)
    if not raw_path.exists():
        raise FileNotFoundError(f"Input file not found: {raw_path}")
    upload_raw_to_s3(raw_path)
    load(transform(pd.read_csv(raw_path)))


if __name__ == "__main__":
    main()
