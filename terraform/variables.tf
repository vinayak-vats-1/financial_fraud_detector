variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "fraud-detection"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "lambda_zip_path" {
  description = "Path to Lambda deployment package"
  type        = string
  default     = "../lambda/fraud_investigator.zip"
}