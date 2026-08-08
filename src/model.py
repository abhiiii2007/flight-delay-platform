"""Train and persist the FlightPulse delay classifier."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config import DATABASE_URL, METRICS_PATH, MODEL_PATH

CATEGORICAL = ["carrier", "origin", "destination"]
NUMERIC = ["scheduled_departure_hour", "month", "day_of_week"]


def chronological_split(
    flights: pd.DataFrame, train_fraction: float = 0.8
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dated = flights.copy()
    dated["flight_date"] = pd.to_datetime(dated["flight_date"])
    unique_dates = dated["flight_date"].sort_values().unique()
    if len(unique_dates) < 2:
        raise ValueError("Chronological evaluation requires at least two flight dates")

    split_index = min(max(int(len(unique_dates) * train_fraction), 1), len(unique_dates) - 1)
    test_start = unique_dates[split_index]
    train_set = dated[dated["flight_date"] < test_start].copy()
    test_set = dated[dated["flight_date"] >= test_start].copy()
    return train_set, test_set


def train(
    flights: pd.DataFrame,
    model_path: Path = MODEL_PATH,
    metrics_path: Path = METRICS_PATH,
) -> dict[str, float | int | str]:
    train_set, test_set = chronological_split(flights)
    x_train = train_set[CATEGORICAL + NUMERIC]
    y_train = train_set["is_delayed"]
    x_test = test_set[CATEGORICAL + NUMERIC]
    y_test = test_set["is_delayed"]
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
        "positive_rate": float(flights["is_delayed"].mean()),
        "majority_baseline_accuracy": float(max(y_test.mean(), 1 - y_test.mean())),
        "rows": int(len(flights)),
        "train_rows": int(len(train_set)),
        "test_rows": int(len(test_set)),
        "split_strategy": "chronological_by_flight_date",
        "train_start": train_set["flight_date"].min().strftime("%Y-%m-%d"),
        "train_end": train_set["flight_date"].max().strftime("%Y-%m-%d"),
        "test_start": test_set["flight_date"].min().strftime("%Y-%m-%d"),
        "test_end": test_set["flight_date"].max().strftime("%Y-%m-%d"),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2))
    return metrics


def main() -> None:
    from sqlalchemy import create_engine

    flights = pd.read_sql("SELECT * FROM flights WHERE cancelled = 0", create_engine(DATABASE_URL))
    print(json.dumps(train(flights), indent=2))


if __name__ == "__main__":
    main()
