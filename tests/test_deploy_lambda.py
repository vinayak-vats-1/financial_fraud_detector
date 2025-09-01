import pytest
import json
from unittest.mock import Mock, patch, mock_open
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.deploy_lambda_resources import (
    create_dynamodb_table,
    create_lambda_role,
    create_lambda_function,
    invoke_lambda_function
)

class TestDeployLambda:
    
    @patch('scripts.deploy_lambda_resources.boto3')
    def test_create_dynamodb_table_success(self, mock_boto3):
        """Test successful DynamoDB table creation"""
        mock_dynamodb = Mock()
        mock_boto3.client.return_value = mock_dynamodb
        
        # Mock successful table creation
        mock_dynamodb.create_table.return_value = {'TableDescription': {'TableName': 'fraud-alerts'}}
        
        # Mock waiter
        mock_waiter = Mock()
        mock_dynamodb.get_waiter.return_value = mock_waiter
        
        create_dynamodb_table()
        
        # Verify table creation call
        mock_dynamodb.create_table.assert_called_once()
        call_args = mock_dynamodb.create_table.call_args[1]
        
        assert call_args['TableName'] == 'fraud-alerts'
        assert call_args['BillingMode'] == 'PAY_PER_REQUEST'
        assert len(call_args['KeySchema']) == 1
        assert call_args['KeySchema'][0]['AttributeName'] == 'transaction_id'
    
    @patch('scripts.deploy_lambda_resources.boto3')
    def test_create_dynamodb_table_exists(self, mock_boto3):
        """Test DynamoDB table already exists scenario"""
        mock_dynamodb = Mock()
        mock_boto3.client.return_value = mock_dynamodb
        
        # Mock table already exists exception
        from botocore.exceptions import ClientError
        mock_dynamodb.create_table.side_effect = ClientError(
            {'Error': {'Code': 'ResourceInUseException'}}, 'CreateTable'
        )
        
        # Should not raise exception
        create_dynamodb_table()
    
    @patch('scripts.deploy_lambda_resources.boto3')
    def test_create_lambda_role(self, mock_boto3):
        """Test IAM role creation"""
        mock_iam = Mock()
        mock_boto3.client.return_value = mock_iam
        
        # Mock role creation and get_role
        mock_iam.get_role.return_value = {
            'Role': {'Arn': 'arn:aws:iam::123456789012:role/FraudProcessorLambdaRole'}
        }
        
        role_arn = create_lambda_role()
        
        # Verify role creation
        mock_iam.create_role.assert_called_once()
        mock_iam.put_role_policy.assert_called_once()
        
        assert role_arn == 'arn:aws:iam::123456789012:role/FraudProcessorLambdaRole'
    
    @patch('scripts.deploy_lambda_resources.boto3')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_zip_content')
    def test_create_lambda_function(self, mock_file, mock_boto3):
        """Test Lambda function creation"""
        mock_lambda = Mock()
        mock_boto3.client.return_value = mock_lambda
        
        # Mock successful function creation
        mock_lambda.create_function.return_value = {
            'FunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:fraud-processor'
        }
        
        role_arn = 'arn:aws:iam::123456789012:role/FraudProcessorLambdaRole'
        function_arn = create_lambda_function(role_arn)
        
        # Verify function creation
        mock_lambda.create_function.assert_called_once()
        call_args = mock_lambda.create_function.call_args[1]
        
        assert call_args['FunctionName'] == 'fraud-processor'
        assert call_args['Runtime'] == 'python3.9'
        assert call_args['Role'] == role_arn
        assert 'DYNAMODB_TABLE' in call_args['Environment']['Variables']
        assert 'S3_BUCKET' in call_args['Environment']['Variables']
        
        assert function_arn == 'arn:aws:lambda:us-east-1:123456789012:function:fraud-processor'
    
    @patch('scripts.deploy_lambda_resources.boto3')
    def test_invoke_lambda_function(self, mock_boto3):
        """Test Lambda function invocation"""
        mock_lambda = Mock()
        mock_boto3.client.return_value = mock_lambda
        
        # Mock successful invocation
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            'statusCode': 200,
            'body': json.dumps({'message': 'Success', 'alerts_written': 5})
        }).encode()
        
        mock_lambda.invoke.return_value = {'Payload': mock_response}
        
        result = invoke_lambda_function()
        
        # Verify invocation
        mock_lambda.invoke.assert_called_once()
        call_args = mock_lambda.invoke.call_args[1]
        
        assert call_args['FunctionName'] == 'fraud-processor'
        assert call_args['InvocationType'] == 'RequestResponse'
        
        assert result['statusCode'] == 200
    
    def test_iam_policy_structure(self):
        """Test IAM policy structure"""
        lambda_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject", "s3:ListBucket"],
                    "Resource": [
                        "arn:aws:s3:::my-secure-bucket-wxj077wp",
                        "arn:aws:s3:::my-secure-bucket-wxj077wp/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": ["dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:GetItem"],
                    "Resource": "arn:aws:dynamodb:us-east-1:*:table/fraud-alerts"
                }
            ]
        }
        
        # Verify policy structure
        assert lambda_policy["Version"] == "2012-10-17"
        assert len(lambda_policy["Statement"]) == 2
        
        # Verify S3 permissions
        s3_statement = lambda_policy["Statement"][0]
        assert "s3:GetObject" in s3_statement["Action"]
        assert "s3:ListBucket" in s3_statement["Action"]
        
        # Verify DynamoDB permissions
        dynamodb_statement = lambda_policy["Statement"][1]
        assert "dynamodb:PutItem" in dynamodb_statement["Action"]