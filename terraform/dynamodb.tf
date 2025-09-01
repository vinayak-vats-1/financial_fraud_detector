# DynamoDB table for fraud alerts
resource "aws_dynamodb_table" "fraud_alerts" {
  name           = "fraud-alerts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "transaction_id"

  attribute {
    name = "transaction_id"
    type = "S"
  }

  attribute {
    name = "customer_id"
    type = "S"
  }

  global_secondary_index {
    name     = "customer-index"
    hash_key = "customer_id"
  }

  tags = {
    Name        = "fraud-alerts"
    Environment = var.environment
  }
}