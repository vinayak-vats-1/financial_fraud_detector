# API Gateway for fraud detection system
resource "aws_api_gateway_rest_api" "fraud_api" {
  name        = "${var.project_name}-api"
  description = "API for fraud detection system"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway resource for fraud investigation
resource "aws_api_gateway_resource" "fraud_resource" {
  rest_api_id = aws_api_gateway_rest_api.fraud_api.id
  parent_id   = aws_api_gateway_rest_api.fraud_api.root_resource_id
  path_part   = "investigate"
}

# POST method for fraud queries
resource "aws_api_gateway_method" "fraud_method" {
  rest_api_id   = aws_api_gateway_rest_api.fraud_api.id
  resource_id   = aws_api_gateway_resource.fraud_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Lambda integration for POST method
resource "aws_api_gateway_integration" "fraud_integration" {
  rest_api_id = aws_api_gateway_rest_api.fraud_api.id
  resource_id = aws_api_gateway_resource.fraud_resource.id
  http_method = aws_api_gateway_method.fraud_method.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.fraud_investigator.invoke_arn
}

# OPTIONS method for CORS
resource "aws_api_gateway_method" "fraud_options" {
  rest_api_id   = aws_api_gateway_rest_api.fraud_api.id
  resource_id   = aws_api_gateway_resource.fraud_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# CORS integration for OPTIONS method
resource "aws_api_gateway_integration" "fraud_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.fraud_api.id
  resource_id = aws_api_gateway_resource.fraud_resource.id
  http_method = aws_api_gateway_method.fraud_options.http_method

  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# OPTIONS method response
resource "aws_api_gateway_method_response" "fraud_options_response" {
  rest_api_id = aws_api_gateway_rest_api.fraud_api.id
  resource_id = aws_api_gateway_resource.fraud_resource.id
  http_method = aws_api_gateway_method.fraud_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

# CORS integration response
resource "aws_api_gateway_integration_response" "fraud_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.fraud_api.id
  resource_id = aws_api_gateway_resource.fraud_resource.id
  http_method = aws_api_gateway_method.fraud_options.http_method
  status_code = aws_api_gateway_method_response.fraud_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "fraud_deployment" {
  depends_on = [
    aws_api_gateway_integration.fraud_integration,
    aws_api_gateway_integration.fraud_options_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.fraud_api.id
  stage_name  = var.environment
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fraud_investigator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.fraud_api.execution_arn}/*/*"
}