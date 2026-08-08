from src.generate_demo import generate
from src.model import chronological_split, train
from src.pipeline import transform


def test_train_returns_valid_metrics(tmp_path):
    model_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "metrics.json"
    metrics = train(transform(generate(1000)), model_path, metrics_path)
    assert metrics["rows"] == 1000
    assert 0 <= metrics["roc_auc"] <= 1
    assert model_path.exists()
    assert metrics_path.exists()
    assert metrics["split_strategy"] == "chronological_by_flight_date"
    assert metrics["train_end"] < metrics["test_start"]


def test_chronological_split_keeps_future_dates_out_of_training():
    flights = transform(generate(1000))
    train_set, test_set = chronological_split(flights)
    assert train_set["flight_date"].max() < test_set["flight_date"].min()
    assert len(train_set) + len(test_set) == len(flights)
