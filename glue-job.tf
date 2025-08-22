resource "aws_iam_role" "glue_role" {
  name = "GlueJobRole"

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

resource "aws_iam_role_policy" "glue_s3_policy" {
  name = "GlueS3Policy"
  role = aws_iam_role.glue_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::my-secure-bucket-wxj077wp",
          "arn:aws:s3:::my-secure-bucket-wxj077wp/*"
        ]
      }
    ]
  })
}

resource "aws_glue_job" "clean_transactions_job" {
  name     = "clean-transactions-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://my-secure-bucket-wxj077wp/scripts/clean-transactions.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"        = "python"
    "--job-bookmark-option" = "job-bookmark-disable"
    "--INPUT_PATH"          = "s3://my-secure-bucket-wxj077wp/input/transactions.csv"
    "--OUTPUT_PATH"         = "s3://my-secure-bucket-wxj077wp/cleaned/"
  }

  glue_version      = "4.0"
  max_retries       = 0
  timeout           = 60
  worker_type       = "G.1X"
  number_of_workers = 2
}

resource "aws_glue_trigger" "clean_transactions_trigger" {
  name = "clean-transactions-trigger"
  type = "ON_DEMAND"

  actions {
    job_name = aws_glue_job.clean_transactions_job.name
  }
}