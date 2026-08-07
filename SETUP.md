# Setup

Requirements: Python 3.11+, Git, and optionally Docker, Terraform, and the AWS CLI.

1. Create the environment with `make setup`.
2. Copy `.env.example` to `.env` and keep it untracked.
3. Run `make demo`, `make load`, and `make train` for a local smoke test.
4. Run `make dashboard` and open the local Streamlit address.
5. Run `make check` before committing.

SQLite is intentionally used for local learning and inexpensive development. The Terraform configuration provides the later path to private Amazon RDS PostgreSQL and encrypted S3 storage.
