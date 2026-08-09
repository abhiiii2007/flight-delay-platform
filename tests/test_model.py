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
    assert metrics["split_strategy"] == "latest_month_holdout"
    assert metrics["train_end"] < metrics["test_start"]
    assert metrics["selected_model"] in {"random_forest", "logistic_regression"}
    assert 0 <= metrics["random_forest_roc_auc"] <= 1
    assert 0 <= metrics["logistic_regression_roc_auc"] <= 1


def test_chronological_split_keeps_future_dates_out_of_training():
    flights = transform(generate(1000))
    train_set, test_set = chronological_split(flights)
    assert train_set["flight_date"].max() < test_set["flight_date"].min()
    assert len(train_set) + len(test_set) == len(flights)


def test_chronological_split_holds_out_entire_latest_month():
    flights = transform(generate(1000))
    train_set, test_set = chronological_split(flights)
    assert test_set["flight_date"].dt.to_period("M").nunique() == 1
    assert test_set["flight_date"].dt.month.iloc[0] == 12
    assert train_set["flight_date"].max() < test_set["flight_date"].min()
