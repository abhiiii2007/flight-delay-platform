from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'data/flights.db'}")
RAW_DATA_PATH = Path(os.getenv("RAW_DATA_PATH", ROOT / "data/raw/flights.csv"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT / "data/processed/delay_model.joblib"))
METRICS_PATH = Path(os.getenv("METRICS_PATH", ROOT / "data/processed/delay_model.metrics.json"))
S3_BUCKET = os.getenv("S3_BUCKET", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
