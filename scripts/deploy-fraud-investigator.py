import boto3
import json

def deploy_fraud_investigator():
    lambda_client = boto3.client('lambda')
    
    # Read the zip file
    with open('fraud_investigator.zip', 'rb') as f:
        zip_content = f.read()
    
    function_name = 'fraud-investigator'
    role_arn = 'arn:aws:iam::214617963177:role/FraudProcessorLambdaRole'
    
    try:
        # Create Lambda function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='fraud_investigator_lambda.lambda_handler',
            Code={'ZipFile': zip_content},
            Timeout=30,
            Environment={
                'Variables': {
                    'DYNAMODB_TABLE': 'fraud-alerts'
                }
            }
        )
        print(f"Created FraudInvestigator Lambda: {function_name}")
        
    except lambda_client.exceptions.ResourceConflictException:
        # Update existing function
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        print(f"Updated FraudInvestigator Lambda: {function_name}")

def test_fraud_investigator():
    lambda_client = boto3.client('lambda')
    
    # Test queries
    test_queries = [
        "Show me the top 2 anomalous transactions",
        "Give me a summary of fraud metrics",
        "Explain why transaction TXN999004 was flagged",
        "List customers with highest fraud scores"
    ]
    
    print("\nTesting FraudInvestigator with sample queries:")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        try:
            response = lambda_client.invoke(
                FunctionName='fraud-investigator',
                InvocationType='RequestResponse',
                Payload=json.dumps({'query': query})
            )
            
            result = json.loads(response['Payload'].read())
            if result['statusCode'] == 200:
                body = json.loads(result['body'])
                print(body['response'])
            else:
                print(f"Error: {result['body']}")
                
        except Exception as e:
            print(f"Error invoking function: {e}")

if __name__ == "__main__":
    deploy_fraud_investigator()
    test_fraud_investigator()