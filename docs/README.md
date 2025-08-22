# Financial Fraud Detection

Terraform project for AWS Glue-based fraud detection system.

## Project Structure

```
financial_fraud_detection/
├── terraform/          # Infrastructure as Code
├── glue_scripts/       # AWS Glue ETL scripts
├── lambda/            # Lambda functions
├── scripts/           # Utility and deployment scripts
├── web/              # Web interfaces
├── docs/             # Documentation
├── requirements.txt   # Python dependencies
└── .gitignore        # Git ignore rules
```

## Setup

1. Copy `terraform/terraform.tfvars.example` to `terraform/terraform.tfvars` and update values
2. Initialize Terraform: `cd terraform && terraform init`
3. Plan deployment: `terraform plan`
4. Apply infrastructure: `terraform apply`

## Dependencies

Install Python dependencies: `pip install -r requirements.txt`