# Security Policy

## Reporting a vulnerability
Please do not open a public issue containing credentials, account IDs, or sensitive upload data. Contact the repository owner privately with a minimal reproduction.

## Operational rules

- Use IAM roles, profiles, or short-lived credentials; never commit AWS access keys.
- Keep bucket names and SNS topic ARNs in environment variables.
- Apply least privilege to the application's IAM principal.
- Review uploaded-data handling before deploying to a public environment.
