import pandas as pd
import pytest

from src.import_bts import convert


def test_converts_current_bts_headers(tmp_path):
    source = tmp_path / "bts.csv"
    pd.DataFrame(
        {
            "FlightDate": ["2026-05-01"],
            "Reporting_Airline": ["DL"],
            "Flight_Number_Reporting_Airline": [4631],
            "Origin": ["DTW"],
            "Dest": ["CMH"],
            "CRSDepTime": [2205],
            "DepDelay": [-4],
            "Distance": [155],
            "Cancelled": [0],
            "WeatherDelay": [0],
        }
    ).to_csv(source, index=False)
    result = convert(source, tmp_path / "output.csv")
    assert result.loc[0, "scheduled_departure_hour"] == 22
    assert result.loc[0, "carrier"] == "DL"


def test_converts_legacy_headers_without_weather(tmp_path):
    source = tmp_path / "legacy.csv"
    pd.DataFrame(
        {
            "FL_DATE": ["2026-05-01"],
            "OP_UNIQUE_CARRIER": ["DL"],
            "OP_CARRIER_FL_NUM": [1],
            "ORIGIN": ["DTW"],
            "DEST": ["CMH"],
            "CRS_DEP_TIME": [900],
            "DEP_DELAY": [3],
            "DISTANCE": [155],
            "CANCELLED": [0],
        }
    ).to_csv(source, index=False)
    assert convert(source, tmp_path / "output.csv").loc[0, "weather_severity"] == 0


def test_rejects_missing_columns(tmp_path):
    source = tmp_path / "bad.csv"
    pd.DataFrame({"FlightDate": ["2026-01-01"]}).to_csv(source, index=False)
    with pytest.raises(ValueError, match="Missing required BTS column"):
        convert(source, tmp_path / "output.csv")


def test_rejects_non_csv(tmp_path):
    source = tmp_path / "data.txt"
    source.write_text("test")
    with pytest.raises(ValueError, match="CSV"):
        convert(source)
