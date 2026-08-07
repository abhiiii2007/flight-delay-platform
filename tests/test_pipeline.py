import pandas as pd
import pytest

from src.generate_demo import generate
from src.pipeline import transform


def test_demo_generation_is_deterministic():
    pd.testing.assert_frame_equal(generate(20, 7), generate(20, 7))


def test_transform_adds_target_and_removes_duplicates():
    source = generate(20, 7)
    source = pd.concat([source, source.iloc[[0]]], ignore_index=True)
    result = transform(source)
    assert len(result) == 20
    assert {"month", "day_of_week", "is_delayed"}.issubset(result.columns)
    assert result["is_delayed"].isin([0, 1]).all()


def test_transform_rejects_incomplete_input():
    with pytest.raises(ValueError, match="Missing required columns"):
        transform(pd.DataFrame({"flight_date": ["2026-01-01"]}))


def test_transform_accepts_release_without_distance():
    source = generate(20, 7).drop(columns="distance_miles")
    source["air_time_minutes"] = 60
    result = transform(source)
    assert "air_time_minutes" in result
    assert "distance_miles" not in result
