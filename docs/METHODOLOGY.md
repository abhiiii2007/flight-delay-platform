# Methodology and validation

## Dataset

FlightPulse currently analyzes the official BTS April and May 2026 on-time performance releases.
Together, the pipe-delimited sources have 1,337,905 records and 71 fields per record. The importer
validates the field count, enforces a 1 GB per-file input-size limit, selects an explicit field
allowlist, normalizes dates and airport codes, and writes a canonical CSV for the pipeline.

The database retains all 1,337,905 records for analytics. The model excludes 12,253 cancelled
flights because they do not have an observed departure-delay outcome, leaving 1,325,652 rows.

## Prediction target and features

A flight is labeled delayed when its observed departure delay is at least 15 minutes. The model
uses carrier, origin, destination, scheduled departure hour, month, and weekday. These variables
are available before departure.

Actual departure delay, cancellation status, weather-delay attribution, and air time are excluded
from the feature matrix. Including them would reveal information that is only known during or
after the flight and would create target leakage.

## Evaluation

The project compares a class-balanced random forest with a class-balanced logistic-regression
baseline. Both candidates receive identical preprocessing, train on April's 654,797 non-cancelled
flights, and are evaluated on May's 670,855 flights. No May record appears in training. The model
with the higher May ROC-AUC is saved for dashboard predictions.

| Metric | Result | Meaning |
| --- | ---: | --- |
| ROC-AUC | 0.688 | Ranking quality across classification thresholds |
| Logistic baseline ROC-AUC | 0.681 | Simpler linear-model comparison |
| Accuracy | 64.69% | Share of holdout predictions classified correctly |
| Precision | 33.24% | Share of predicted delays that were delayed |
| Recall | 61.06% | Share of actual delays detected by the model |

Because only two adjacent months are represented, these results are a baseline rather than
evidence of performance across seasons. A stronger evaluation would train on several earlier
months and test on a later month from another season.

## Reproducibility

The raw source, generated database, and trained model are intentionally excluded from Git because
they are large generated artifacts. The importer, pipeline, pinned dependencies, SQL, and tests are
versioned. Running the documented commands against the same BTS release reproduces the results.

The `.asc` importer accepts one or more monthly releases. When several files are provided, it
normalizes each release to the same schema, concatenates them, removes exact duplicate records, and
sorts the combined dataset chronologically before the regular pipeline runs.
