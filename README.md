# FlightPulse

FlightPulse is an end-to-end data science project that analyzes U.S. airline delays and predicts whether a departure will be delayed by at least 15 minutes. It combines a Python data pipeline, SQL analytics, a scikit-learn model, a Streamlit dashboard, and secure AWS infrastructure defined with Terraform.

## What it demonstrates

- Imports real Bureau of Transportation Statistics (BTS) on-time flight records
- Validates and cleans data with pandas, then loads an analytics database
- Answers carrier, route, and departure-time questions with SQL
- Trains a random-forest classification model and reports reproducible metrics
- Presents results and interactive predictions in a Streamlit dashboard
- Designs private, encrypted S3 and PostgreSQL infrastructure on AWS
- Runs tests, linting, dependency auditing, and static security checks in CI

## Local workflow

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
make demo
make load
make train
make dashboard
```

The generated demo data exists only to exercise the pipeline. Portfolio results should use the official BTS file and clearly identify its source and coverage.

The prediction model intentionally excludes actual departure delay, weather-delay attribution,
and air time because those values are not known when a pre-departure prediction is made. This
prevents target leakage and keeps the evaluation honest.

## Real BTS release

Convert a downloaded pipe-delimited BTS `.asc` release:

```bash
.venv/bin/python -m src.import_bts_asc /path/to/ontime.td.202605.asc \
  --output data/raw/flights.csv
make load
make train
```

## Reproduced May 2026 results

The current evaluation uses the official May 2026 BTS on-time release downloaded as
`ontime.td.202605.asc`.

- Source rows validated and loaded: **677,216**
- Cancelled flights excluded from model training: **6,361**
- Flights used for training/evaluation: **670,855**
- Flights delayed at least 15 minutes: **146,863 (21.69%)**
- Holdout ROC-AUC: **0.697**
- Holdout accuracy: **64.53%**
- Holdout precision: **33.49%**
- Holdout recall: **63.17%**

The model uses a seeded, stratified 80/20 train/test split. Metrics are baseline results for
one month and should not be interpreted as proof of future performance. See
[`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for definitions and limitations.

Run `make check` before every push. Never commit `.env`, credentials, databases, raw datasets, or trained model artifacts.
