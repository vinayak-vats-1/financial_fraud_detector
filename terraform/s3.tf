# S3 bucket for fraud detection data
resource "aws_s3_bucket" "fraud_detection_bucket" {
  bucket = "${var.project_name}-bucket-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_versioning" "fraud_detection_versioning" {
  bucket = aws_s3_bucket.fraud_detection_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "fraud_detection_encryption" {
  bucket = aws_s3_bucket.fraud_detection_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket objects for folder structure
resource "aws_s3_object" "data_folders" {
  for_each = toset(["raw/", "cleaned/", "scored/", "models/", "scripts/"])
  
  bucket = aws_s3_bucket.fraud_detection_bucket.id
  key    = each.value
  source = "/dev/null"
}