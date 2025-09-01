output "s3_bucket_name" {
  description = "Name of the S3 bucket for fraud detection data"
  value       = aws_s3_bucket.fraud_detection_bucket.bucket
}

output "glue_job_name" {
  description = "Name of the Glue job"
  value       = aws_glue_job.fraud_detection.name
}

output "glue_database_name" {
  description = "Name of the Glue database"
  value       = aws_glue_catalog_database.fraud_detection_db.name
}

output "glue_crawler_name" {
  description = "Name of the Glue crawler"
  value       = aws_glue_crawler.transaction_crawler.name
}

output "glue_role_arn" {
  description = "ARN of the Glue IAM role"
  value       = aws_iam_role.glue_role.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for fraud alerts"
  value       = aws_dynamodb_table.fraud_alerts.name
}

output "fraud_processor_function_name" {
  description = "Name of the fraud processor Lambda function"
  value       = aws_lambda_function.fraud_processor.function_name
}

output "fraud_investigator_function_name" {
  description = "Name of the fraud investigator Lambda function"
  value       = aws_lambda_function.fraud_investigator.function_name
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = "${aws_api_gateway_deployment.fraud_deployment.invoke_url}/investigate"
}

output "sagemaker_role_arn" {
  description = "ARN of the SageMaker IAM role"
  value       = aws_iam_role.sagemaker_role.arn
}