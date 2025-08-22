# Glue database for fraud detection
resource "aws_glue_catalog_database" "fraud_detection_db" {
  name = "${var.project_name}_db"
}

# Glue job for fraud detection
resource "aws_glue_job" "fraud_detection" {
  name     = "${var.project_name}-fraud-detection"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.fraud_detection_bucket.bucket}/scripts/fraud_detection.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"        = "python"
    "--job-bookmark-option" = "job-bookmark-enable"
    "--TempDir"            = "s3://${aws_s3_bucket.fraud_detection_bucket.bucket}/temp/"
  }

  max_retries = 1
  timeout     = 60
  
  glue_version = "4.0"
}