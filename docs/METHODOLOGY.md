# Methodology and validation

## Dataset

FlightPulse currently analyzes the official BTS May 2026 on-time performance release. The
pipe-delimited source has 677,216 records and 71 fields. The importer validates the field count,
enforces a 1 GB input-size limit, selects an explicit field allowlist, normalizes dates and airport
codes, and writes a canonical CSV for the pipeline.

The database retains all 677,216 records for analytics. The model excludes 6,361 cancelled
flights because they do not have an observed departure-delay outcome, leaving 670,855 rows.

## Prediction target and features

A flight is labeled delayed when its observed departure delay is at least 15 minutes. The model
uses carrier, origin, destination, scheduled departure hour, month, and weekday. These variables
are available before departure.

Actual departure delay, cancellation status, weather-delay attribution, and air time are excluded
from the feature matrix. Including them would reveal information that is only known during or
after the flight and would create target leakage.

## Evaluation

The classifier is a class-balanced random forest with a fixed random seed. Evaluation uses a
stratified 80/20 holdout split so the delayed-flight rate is represented in both partitions.

| Metric | Result | Meaning |
| --- | ---: | --- |
| ROC-AUC | 0.697 | Ranking quality across classification thresholds |
| Accuracy | 64.53% | Share of holdout predictions classified correctly |
| Precision | 33.49% | Share of predicted delays that were delayed |
| Recall | 63.17% | Share of actual delays detected by the model |

Because only one month is represented, these results are a baseline rather than evidence of
performance across seasons. A stronger evaluation would train on several earlier months and test
on a later month, which is the next modeling milestone.

## Reproducibility

The raw source, generated database, and trained model are intentionally excluded from Git because
they are large generated artifacts. The importer, pipeline, pinned dependencies, SQL, and tests are
versioned. Running the documented commands against the same BTS release reproduces the results.
