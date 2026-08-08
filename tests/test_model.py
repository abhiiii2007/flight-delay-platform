from src.generate_demo import generate
from src.model import train
from src.pipeline import transform


def test_train_returns_valid_metrics(tmp_path):
    model_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "metrics.json"
    metrics = train(transform(generate(1000)), model_path, metrics_path)
    assert metrics["rows"] == 1000
    assert 0 <= metrics["roc_auc"] <= 1
    assert model_path.exists()
    assert metrics_path.exists()
