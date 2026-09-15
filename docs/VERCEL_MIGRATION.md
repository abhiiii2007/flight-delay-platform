# Vercel migration

Verified production deployment: <https://flightpulse-delay.vercel.app/>

FlightPulse's original Streamlit application remains available in `app/dashboard.py`. The Vercel
replacement is being built alongside it in `web/`; the original application must not be removed
until the replacement has passed local and hosted verification.

## Existing feature inventory

### Historical exploration

- Carrier, origin, and destination filters
- Analyzed-flight count, 15-minute delay rate, and average departure delay
- Delay rate by carrier
- Delay rate by scheduled departure hour
- Ten routes with the highest delay rate, requiring at least ten matching flights

### Model evaluation

- ROC-AUC, accuracy, precision, and recall
- Random-forest and logistic-regression comparison
- Chronological training and holdout date ranges
- Confusion matrix
- F1 score, specificity, and balanced accuracy

### Prediction

- Carrier
- Origin
- Destination
- Scheduled departure hour
- Month
- Day of week
- Estimated probability of a delay of at least 15 minutes

## Current artifacts

- `data/flights.db`: local SQLite analytics database (about 160 MB)
- `data/processed/delay_model.joblib`: trained scikit-learn pipeline (about 13 MB)
- `data/processed/delay_model.metrics.json`: evaluation results
- GitHub Release `deployment-v1`: versioned hosted artifact bundle for Streamlit

## Target architecture

- Next.js and TypeScript frontend deployed on Vercel
- Compact, precomputed analytics generated from the existing SQLite database
- FastAPI prediction endpoint using the existing scikit-learn model
- Vercel Hobby deployment first, with no paid service or custom-domain purchase
- Original data ingestion, transformation, training, tests, and Streamlit application preserved

## Cost boundary

The first implementation targets Vercel Hobby for a personal portfolio project. A generated
`vercel.app` URL is included. Do not purchase a domain, upgrade Vercel, or provision another paid
backend without explicit approval.
