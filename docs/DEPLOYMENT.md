# Deploying FlightPulse

FlightPulse is hosted on Streamlit Community Cloud. The service clones the GitHub repository,
installs `requirements.txt`, and runs `app/dashboard.py` from the repository root.

Live app: [flight-delay-platform-9wvanzjxnud3fg3zubxvgh.streamlit.app](https://flight-delay-platform-9wvanzjxnud3fg3zubxvgh.streamlit.app/)

## Why a separate artifact bundle exists

The official BTS releases, generated SQLite database, and trained model are intentionally excluded
from Git. A fresh cloud container therefore downloads the versioned
`flightpulse-deployment-artifacts.tar.gz` asset from the GitHub Release named `deployment-v1`.
The 35 MB bundle contains only:

- the read-only analytics database;
- the trained model; and
- the model-evaluation metrics.

The app requires HTTPS, verifies the bundle's pinned SHA-256 checksum before extraction, and
accepts only those three expected files. No AWS credentials, BTS source releases, `.env` file, or
other secrets are included.

## Rebuilding the bundle

After loading the official data and training the model locally, run:

```bash
.venv/bin/python scripts/package_deployment.py
```

The command writes the ignored bundle to `dist/` and prints its SHA-256 checksum. A new bundle must
be uploaded under a new GitHub Release tag, and its URL and checksum must be updated in
`src/deployment.py` before redeployment.

## Streamlit Community Cloud settings

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) and connect GitHub.
2. Create an app from `abhiiii2007/flight-delay-platform`.
3. Select branch `main`.
4. Set the entrypoint to `app/dashboard.py`.
5. Select Python 3.13 in advanced settings.
6. Do not add secrets; this deployment does not require any.
7. Deploy and verify the date range, row count, model metrics, confusion matrix, and prediction form.

Community Cloud automatically rebuilds the app after future pushes to the selected branch.
