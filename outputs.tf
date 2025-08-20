output "s3_bucket_name" {
  description = "Name of the S3 bucket for Glue assets"
  value       = aws_s3_bucket.glue_assets.bucket
}

output "glue_job_name" {
  description = "Name of the Glue job"
  value       = aws_glue_job.fraud_detection.name
}

output "glue_role_arn" {
  description = "ARN of the Glue IAM role"
  value       = aws_iam_role.glue_role.arn
}