import pytest

from src.import_bts_asc import EXPECTED_FIELD_COUNT, convert


def _row() -> list[str]:
    row = [""] * EXPECTED_FIELD_COUNT
    values = {
        0: "DL",
        1: "4631",
        4: "9E",
        5: "4631",
        6: "DTW",
        7: "CMH",
        8: "20260501",
        9: "5",
        11: "2205",
        20: "-4",
        28: "34",
        29: "",
        31: "0",
    }
    for position, value in values.items():
        row[position] = value
    return row


def test_converts_asc_release(tmp_path):
    source = tmp_path / "release.asc"
    source.write_text("|".join(_row()) + "\n")
    result = convert(source, tmp_path / "preview.csv")
    assert result.loc[0, "flight_date"] == "2026-05-01"
    assert result.loc[0, "carrier"] == "DL"
    assert result.loc[0, "scheduled_departure_hour"] == 22
    assert result.loc[0, "air_time_minutes"] == 34
    assert result.loc[0, "cancelled"] == 0


def test_rejects_malformed_row(tmp_path):
    source = tmp_path / "release.asc"
    source.write_text("too|short\n")
    with pytest.raises(ValueError, match="expected 71"):
        convert(source, tmp_path / "preview.csv")
