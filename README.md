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

Pass several releases before `--output` to build a combined chronological dataset:

```bash
.venv/bin/python -m src.import_bts_asc \
  /path/to/ontime.td.202604.asc \
  /path/to/ontime.td.202605.asc \
  /path/to/ontime.td.202606.asc \
  --output data/raw/flights.csv
```

The combined importer sorts records by date and removes exact duplicate records.

## Reproduced April–May 2026 results

The current evaluation uses the official April and May 2026 releases from the
[BTS Airline Service Quality Performance 234 archive](https://www.bts.gov/browse-statistical-products-and-data/bts-publications/airline-service-quality-performance-234-time).

- Source rows validated and loaded: **1,337,905**
- Cancelled flights excluded from model training: **12,253**
- Non-cancelled flights available for training/evaluation: **1,325,652**
- Non-cancelled flights delayed at least 15 minutes: **276,089 (20.83%)**
- Out-of-month ROC-AUC: **0.688**
- Logistic-regression baseline ROC-AUC: **0.681**
- Out-of-month accuracy: **64.69%**
- Out-of-month precision: **33.24%**
- Out-of-month recall: **61.06%**

The model trains on all non-cancelled April flights and tests on every non-cancelled May flight, so
the test month never enters training. These two-month results remain a baseline and should not be
interpreted as proof of seasonal performance. Random forest is retained because it slightly
outperforms logistic regression on the identical May holdout. See
[`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for definitions and limitations.

Run `make check` before every push. Never commit `.env`, credentials, databases, raw datasets, or trained model artifacts.
