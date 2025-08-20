# Financial Fraud Detection project

Terraform project for AWS Glue-based fraud detection system.

## Setup

1. Copy `terraform.tfvars.example` to `terraform.tfvars` and update values
2. Initialize Terraform: `terraform init`
3. Plan deployment: `terraform plan`
4. Apply infrastructure: `terraform apply`

## Glue Scripts

Python scripts for AWS Glue jobs are located in the `glue_scripts/` directory.

## Dependencies

Install Python dependencies: `pip install -r requirements.txt`