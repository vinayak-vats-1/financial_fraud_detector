import boto3
import json

def update_lambda_permissions():
    iam = boto3.client('iam')
    
    # Update the existing policy to include Scan and Query permissions
    policy_document = {
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
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem", 
                    "dynamodb:GetItem",
                    "dynamodb:Scan",
                    "dynamodb:Query"
                ],
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
        iam.put_role_policy(
            RoleName='FraudProcessorLambdaRole',
            PolicyName='FraudProcessorPolicy',
            PolicyDocument=json.dumps(policy_document)
        )
        print("Updated IAM policy with Scan and Query permissions")
        
        # Wait for policy to propagate
        import time
        time.sleep(5)
        
    except Exception as e:
        print(f"Error updating policy: {e}")

def test_after_update():
    lambda_client = boto3.client('lambda')
    
    print("\nTesting after permission update:")
    
    test_query = "Give me a summary of fraud metrics"
    
    try:
        response = lambda_client.invoke(
            FunctionName='fraud-investigator',
            InvocationType='RequestResponse',
            Payload=json.dumps({'query': test_query})
        )
        
        result = json.loads(response['Payload'].read())
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print("SUCCESS! Response:")
            print(body['response'])
        else:
            body = json.loads(result['body'])
            print(f"Error: {body.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_lambda_permissions()
    test_after_update()