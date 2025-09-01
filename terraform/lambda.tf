# Lambda function for fraud processor
resource "aws_lambda_function" "fraud_processor" {
  filename         = "../lambda/fraud_processor.zip"
  function_name    = "${var.project_name}-fraud-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 60

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.fraud_alerts.name
      S3_BUCKET      = aws_s3_bucket.fraud_detection_bucket.bucket
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_dynamodb_policy,
    aws_iam_role_policy.lambda_s3_policy,
  ]
}

# Lambda function for fraud investigator
resource "aws_lambda_function" "fraud_investigator" {
  filename         = "../lambda/fraud_investigator.zip"
  function_name    = "${var.project_name}-fraud-investigator"
  role            = aws_iam_role.lambda_role.arn
  handler         = "fraud_investigator_lambda.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.fraud_alerts.name
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_dynamodb_policy,
  ]
}