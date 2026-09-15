"""Export compact, read-only analytics for the Next.js dashboard."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from src.config import METRICS_PATH, ROOT

DATABASE_PATH = ROOT / "data/flights.db"
DEFAULT_OUTPUT = ROOT / "web/public/data/overview.json"


def query_rows(connection: sqlite3.Connection, sql: str) -> list[dict[str, object]]:
    cursor = connection.execute(sql)
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def export(database_path: Path, metrics_path: Path, output_path: Path) -> dict[str, object]:
    if not database_path.exists():
        raise FileNotFoundError(f"Analytics database not found: {database_path}")
    if not metrics_path.exists():
        raise FileNotFoundError(f"Model metrics not found: {metrics_path}")

    with sqlite3.connect(database_path) as connection:
        overview = query_rows(
            connection,
            """
            SELECT
                COUNT(*) AS flights,
                AVG(is_delayed) * 100.0 AS delay_rate,
                AVG(departure_delay_minutes) AS average_delay,
                MIN(flight_date) AS start_date,
                MAX(flight_date) AS end_date
            FROM flights
            WHERE cancelled = 0
            """,
        )[0]
        carriers = query_rows(
            connection,
            """
            SELECT carrier, COUNT(*) AS flights, AVG(is_delayed) * 100.0 AS delay_rate
            FROM flights
            WHERE cancelled = 0
            GROUP BY carrier
            ORDER BY delay_rate DESC
            """,
        )
        hourly = query_rows(
            connection,
            """
            SELECT scheduled_departure_hour AS hour,
                   COUNT(*) AS flights,
                   AVG(is_delayed) * 100.0 AS delay_rate
            FROM flights
            WHERE cancelled = 0
            GROUP BY scheduled_departure_hour
            ORDER BY scheduled_departure_hour
            """,
        )
        routes = query_rows(
            connection,
            """
            SELECT origin, destination, COUNT(*) AS flights,
                   AVG(is_delayed) * 100.0 AS delay_rate
            FROM flights
            WHERE cancelled = 0
            GROUP BY origin, destination
            HAVING COUNT(*) >= 10
            ORDER BY delay_rate DESC
            LIMIT 10
            """,
        )
        route_aggregates = query_rows(
            connection,
            """
            SELECT carrier, origin, destination,
                   COUNT(*) AS flights,
                   SUM(is_delayed) AS delayed_flights,
                   SUM(departure_delay_minutes) AS total_delay_minutes
            FROM flights
            WHERE cancelled = 0
            GROUP BY carrier, origin, destination
            ORDER BY carrier, origin, destination
            """,
        )
        options = {
            "carriers": [row["carrier"] for row in query_rows(
                connection,
                "SELECT DISTINCT carrier FROM flights ORDER BY carrier",
            )],
            "origins": [row["origin"] for row in query_rows(
                connection,
                "SELECT DISTINCT origin FROM flights ORDER BY origin",
            )],
            "destinations": [row["destination"] for row in query_rows(
                connection,
                "SELECT DISTINCT destination FROM flights ORDER BY destination",
            )],
        }

    payload = {
        "overview": overview,
        "carriers": carriers,
        "hourly": hourly,
        "routes": routes,
        "route_aggregates": route_aggregates,
        "options": options,
        "metrics": json.loads(metrics_path.read_text()),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DATABASE_PATH)
    parser.add_argument("--metrics", type=Path, default=METRICS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = export(args.database, args.metrics, args.output)
    print(
        f"Exported {payload['overview']['flights']:,} flights to {args.output} "
        f"({args.output.stat().st_size:,} bytes)"
    )


if __name__ == "__main__":
    main()
