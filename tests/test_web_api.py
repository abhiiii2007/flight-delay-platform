from web.api.index import Flight, health, predict


def test_health_reports_loaded_model() -> None:
    assert health() == {"status": "ok", "model": "random_forest"}


def test_prediction_is_a_probability() -> None:
    result = predict(
        Flight(
            carrier="AA",
            origin="DTW",
            destination="JFK",
            hour=12,
            month=6,
            day_of_week=0,
        )
    )
    assert 0.0 <= result["delay_probability"] <= 1.0
    assert result["risk_label"] in {"lower", "higher"}
