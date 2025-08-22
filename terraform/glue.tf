# Glue database for fraud detection
resource "aws_glue_catalog_database" "fraud_detection_db" {
  name = "${var.project_name}_db"
}

# Glue crawler for transaction data
resource "aws_glue_crawler" "transaction_crawler" {
  database_name = aws_glue_catalog_database.fraud_detection_db.name
  name          = "${var.project_name}-transaction-crawler"
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.fraud_detection_bucket.bucket}/raw/"
  }

  configuration = jsonencode({
    Grouping = {
      TableGroupingPolicy = "CombineCompatibleSchemas"
    }
    CrawlerOutput = {
      Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
    }
    Version = 1
  })
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
    "--S3_BUCKET"          = aws_s3_bucket.fraud_detection_bucket.bucket
  }

  max_retries = 1
  timeout     = 60
  glue_version = "4.0"
  
  worker_type       = "G.1X"
  number_of_workers = 2
}

# Glue trigger to run job on schedule
resource "aws_glue_trigger" "fraud_detection_trigger" {
  name = "${var.project_name}-fraud-detection-trigger"
  type = "SCHEDULED"
  
  schedule = "cron(0 2 * * ? *)"  # Run daily at 2 AM
  
  actions {
    job_name = aws_glue_job.fraud_detection.name
  }
}

# Upload Glue script to S3
resource "aws_s3_object" "glue_script" {
  bucket = aws_s3_bucket.fraud_detection_bucket.id
  key    = "scripts/fraud_detection.py"
  source = "../glue_scripts/fraud_detection.py"
  etag   = filemd5("../glue_scripts/fraud_detection.py")
}