# Security

- Never commit AWS keys, database passwords, `.env`, raw datasets, or model artifacts.
- Use temporary AWS credentials or IAM Identity Center rather than long-lived access keys.
- Apply least-privilege IAM permissions and enable account MFA.
- Keep S3 public access blocked and encryption/versioning enabled.
- Keep RDS private; authorize only the application security group when an application tier is added.
- Store the RDS password in AWS Secrets Manager (configured through managed master credentials).
- Review Terraform plans before applying and destroy learning resources when finished to control cost.
- Run `make check` for tests, linting, Bandit analysis, and dependency vulnerability auditing.

FlightPulse does not use a generative-AI model or accept prompts. Its main risks are exposed credentials, untrusted data files, vulnerable dependencies, public cloud resources, and unsafe deployment settings; the controls above address those risks.
