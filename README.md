# Cloud Analytics File Processing App

A Streamlit application that accepts user uploads, provides lightweight data exploration, and integrates with AWS S3 and SNS for cloud storage and upload notifications.

## What I implemented

- File uploads for CSV, Excel, documents, PDFs, and images
- Dataset preview, null-value analysis, filtering, column editing, and charting
- AWS S3 upload integration
- Amazon SNS notification after an upload
- Environment-based cloud configuration so account-specific values are not committed

## Architecture

```
Browser → Streamlit application → Amazon S3
                           └──→ Amazon SNS notification
```

## Tech stack

Python, Streamlit, Pandas, Plotly, Matplotlib, Boto3, Amazon S3, Amazon SNS.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Export values from .env securely; do not commit it.
streamlit run app.py
```

Required environment variables:

```bash
export AWS_REGION=ap-south-1
export S3_BUCKET_NAME=your-unique-bucket-name
export SNS_TOPIC_ARN=arn:aws:sns:ap-south-1:123456789012:upload-alert
```

Use an AWS IAM role, AWS CLI profile, or short-lived credentials for authentication. Never place access keys in code or commit them.

## Attribution

This project began as a learning implementation inspired by the open-source **Data Analysis Web App** by `everydaycodings`. I extended it with AWS S3/SNS integration and configuration/security improvements. See the original project for its license and upstream credit.

## Improvement backlog

- Add unit tests and GitHub Actions checks
- Use presigned S3 URLs rather than exposing object URLs
- Track real upload metrics in DynamoDB
- Add least-privilege IAM policy documentation
