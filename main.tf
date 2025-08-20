terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for Glue scripts and data
resource "aws_s3_bucket" "glue_assets" {
  bucket = "${var.project_name}-glue-assets-${random_id.bucket_suffix.hex}"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# IAM role for Glue jobs
resource "aws_iam_role" "glue_role" {
  name = "${var.project_name}-glue-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service_role" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Glue job for fraud detection
resource "aws_glue_job" "fraud_detection" {
  name     = "${var.project_name}-fraud-detection"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.glue_assets.bucket}/scripts/fraud_detection.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language" = "python"
  }

  max_retries = 1
  timeout     = 60
}