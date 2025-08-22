import boto3
import json
import zipfile
import time

def create_dynamodb_table():
    dynamodb = boto3.client('dynamodb')
    
    try:
        response = dynamodb.create_table(
            TableName='fraud-alerts',
            KeySchema=[
                {
                    'AttributeName': 'transaction_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'transaction_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Created DynamoDB table: fraud-alerts")
        
        # Wait for table to be active
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName='fraud-alerts')
        print("DynamoDB table is active")
        
    except dynamodb.exceptions.ResourceInUseException:
        print("DynamoDB table fraud-alerts already exists")

def create_lambda_role():
    iam = boto3.client('iam')
    
    role_name = 'FraudProcessorLambdaRole'
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
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
            },
            {
                "Effect": "Allow",
                "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }
    
    try:
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        print(f"Created IAM role: {role_name}")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"IAM role {role_name} already exists")
    
    # Attach policy
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName='FraudProcessorPolicy',
        PolicyDocument=json.dumps(lambda_policy)
    )
    
    role_arn = iam.get_role(RoleName=role_name)['Role']['Arn']
    return role_arn

def create_lambda_function(role_arn):
    lambda_client = boto3.client('lambda')
    
    # Read the zip file
    with open('fraud_processor.zip', 'rb') as f:
        zip_content = f.read()
    
    function_name = 'fraud-processor'
    
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
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
        print(f"Created Lambda function: {function_name}")
        return response['FunctionArn']
        
    except lambda_client.exceptions.ResourceConflictException:
        print(f"Lambda function {function_name} already exists, updating...")
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        response = lambda_client.get_function(FunctionName=function_name)
        return response['Configuration']['FunctionArn']

def invoke_lambda_function():
    lambda_client = boto3.client('lambda')
    
    response = lambda_client.invoke(
        FunctionName='fraud-processor',
        InvocationType='RequestResponse'
    )
    
    result = json.loads(response['Payload'].read())
    print(f"Lambda execution result: {result}")
    return result

if __name__ == "__main__":
    print("Deploying Lambda resources...")
    
    # Create DynamoDB table
    create_dynamodb_table()
    
    # Create IAM role
    role_arn = create_lambda_role()
    print(f"Role ARN: {role_arn}")
    
    # Wait for role to propagate
    time.sleep(10)
    
    # Create Lambda function
    function_arn = create_lambda_function(role_arn)
    print(f"Function ARN: {function_arn}")
    
    # Invoke Lambda function
    print("Invoking Lambda function to process fraud alerts...")
    result = invoke_lambda_function()
    
    print("Deployment complete!")