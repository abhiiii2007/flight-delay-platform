import pytest

from src.import_bts_asc import EXPECTED_FIELD_COUNT, convert, convert_many


def _row(flight_date: str = "20260501", flight_number: str = "4631") -> list[str]:
    row = [""] * EXPECTED_FIELD_COUNT
    values = {
        0: "DL",
        1: flight_number,
        4: "9E",
        5: "4631",
        6: "DTW",
        7: "CMH",
        8: flight_date,
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


def test_combines_multiple_monthly_releases_in_date_order(tmp_path):
    may = tmp_path / "may.asc"
    june = tmp_path / "june.asc"
    may.write_text("|".join(_row("20260501", "4631")) + "\n")
    june.write_text("|".join(_row("20260601", "5000")) + "\n")

    result = convert_many([june, may], tmp_path / "combined.csv")

    assert result["flight_date"].tolist() == ["2026-05-01", "2026-06-01"]
    assert len(result) == 2


def test_combined_import_removes_exact_duplicates(tmp_path):
    first = tmp_path / "first.asc"
    duplicate = tmp_path / "duplicate.asc"
    record = "|".join(_row()) + "\n"
    first.write_text(record)
    duplicate.write_text(record)

    result = convert_many([first, duplicate], tmp_path / "combined.csv")

    assert len(result) == 1
