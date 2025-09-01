# Terraform Equivalents for deploy-lambda-resources.py

## Script vs Terraform Comparison

### Python Script Functions → Terraform Resources

| Python Function | Terraform Resource | File Location |
|----------------|-------------------|---------------|
| `create_dynamodb_table()` | `aws_dynamodb_table.fraud_alerts` | `dynamodb.tf` |
| `create_lambda_role()` | `aws_iam_role.lambda_role` + policies | `iam.tf` |
| `create_lambda_function()` | `aws_lambda_function.fraud_processor` | `lambda.tf` |
| `invoke_lambda_function()` | `null_resource.invoke_fraud_processor` | `invoke_lambda.tf` |

## Detailed Mapping

### 1. DynamoDB Table Creation
**Python Script:**
```python
dynamodb.create_table(
    TableName='fraud-alerts',
    KeySchema=[{'AttributeName': 'transaction_id', 'KeyType': 'HASH'}],
    BillingMode='PAY_PER_REQUEST'
)
```

**Terraform Equivalent:**
```hcl
resource "aws_dynamodb_table" "fraud_alerts" {
  name         = "fraud-alerts"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "transaction_id"
  
  attribute {
    name = "transaction_id"
    type = "S"
  }
}
```

### 2. IAM Role Creation
**Python Script:**
```python
iam.create_role(
    RoleName='FraudProcessorLambdaRole',
    AssumeRolePolicyDocument=trust_policy
)
iam.put_role_policy(
    RoleName='FraudProcessorLambdaRole',
    PolicyName='FraudProcessorPolicy',
    PolicyDocument=lambda_policy
)
```

**Terraform Equivalent:**
```hcl
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "${var.project_name}-lambda-s3-policy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.fraud_detection_bucket.arn,
        "${aws_s3_bucket.fraud_detection_bucket.arn}/*"
      ]
    }]
  })
}
```

### 3. Lambda Function Creation
**Python Script:**
```python
lambda_client.create_function(
    FunctionName='fraud-processor',
    Runtime='python3.9',
    Role=role_arn,
    Handler='lambda_function.lambda_handler',
    Code={'ZipFile': zip_content},
    Timeout=60,
    Environment={
        'Variables': {
            'DYNAMODB_TABLE': 'fraud-alerts',
            'S3_BUCKET': 'my-secure-bucket-wxj077wp'
        }
    }
)
```

**Terraform Equivalent:**
```hcl
resource "aws_lambda_function" "fraud_processor" {
  filename      = "../lambda/fraud_processor.zip"
  function_name = "${var.project_name}-fraud-processor"
  role         = aws_iam_role.lambda_role.arn
  handler      = "lambda_function.lambda_handler"
  runtime      = "python3.9"
  timeout      = 60

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.fraud_alerts.name
      S3_BUCKET      = aws_s3_bucket.fraud_detection_bucket.bucket
    }
  }
}
```

### 4. Lambda Function Invocation
**Python Script:**
```python
lambda_client.invoke(
    FunctionName='fraud-processor',
    InvocationType='RequestResponse'
)
```

**Terraform Equivalent:**
```hcl
resource "null_resource" "invoke_fraud_processor" {
  provisioner "local-exec" {
    command = <<-EOT
      aws lambda invoke \
        --function-name ${aws_lambda_function.fraud_processor.function_name} \
        --invocation-type RequestResponse \
        response.json
    EOT
  }
}
```

## Key Differences

### Advantages of Terraform Approach:
1. **Declarative**: Describes desired state vs imperative steps
2. **Idempotent**: Can be run multiple times safely
3. **State Management**: Tracks resource state and dependencies
4. **Variables**: Parameterized configuration
5. **Dependency Management**: Automatic resource ordering
6. **Version Control**: Infrastructure as code in Git

### Advantages of Python Script:
1. **Error Handling**: Custom logic for specific error conditions
2. **Dynamic Logic**: Can make runtime decisions
3. **Immediate Feedback**: Direct API responses and logging
4. **Flexibility**: Can handle complex conditional logic

## Usage

### Deploy with Terraform:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Deploy with Python Script:
```bash
python scripts/deploy-lambda-resources.py
```

Both approaches achieve the same infrastructure deployment but with different methodologies and benefits.