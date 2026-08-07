"""Train and persist the FlightPulse delay classifier."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config import DATABASE_URL, METRICS_PATH, MODEL_PATH

CATEGORICAL = ["carrier", "origin", "destination"]
NUMERIC = ["scheduled_departure_hour", "month", "day_of_week"]


def train(flights: pd.DataFrame, model_path: Path = MODEL_PATH) -> dict[str, float]:
    features = flights[CATEGORICAL + NUMERIC]
    target = flights["is_delayed"]
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )
    preprocessing = ColumnTransformer(
        [("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL)],
        remainder="passthrough",
    )
    classifier = RandomForestClassifier(
        n_estimators=180,
        max_depth=12,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model = Pipeline([("preprocessing", preprocessing), ("classifier", classifier)])
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "positive_rate": float(target.mean()),
        "rows": int(len(flights)),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    return metrics


def main() -> None:
    from sqlalchemy import create_engine

    flights = pd.read_sql("SELECT * FROM flights WHERE cancelled = 0", create_engine(DATABASE_URL))
    print(json.dumps(train(flights), indent=2))


if __name__ == "__main__":
    main()
