"""Fail fast when local configuration contains common security mistakes."""

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    forbidden = {".env", "data/flights.db", "data/raw/flights.csv"}
    exposed = forbidden.intersection(tracked)
    if exposed:
        raise SystemExit(f"Sensitive/generated files are tracked: {sorted(exposed)}")
    if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        print("AWS credentials are present in the environment (values hidden).")
    print("Preflight checks passed.")


if __name__ == "__main__":
    main()
