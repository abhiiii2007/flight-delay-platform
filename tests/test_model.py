from src.generate_demo import generate
from src.model import train
from src.pipeline import transform


def test_train_returns_valid_metrics(tmp_path):
    metrics = train(transform(generate(1000)), tmp_path / "model.joblib")
    assert metrics["rows"] == 1000
    assert 0 <= metrics["roc_auc"] <= 1
