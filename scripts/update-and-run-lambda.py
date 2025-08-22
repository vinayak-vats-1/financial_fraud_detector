import boto3
import json

def update_lambda_function():
    lambda_client = boto3.client('lambda')
    
    # Read the updated zip file
    with open('fraud_processor.zip', 'rb') as f:
        zip_content = f.read()
    
    # Update function code
    lambda_client.update_function_code(
        FunctionName='fraud-processor',
        ZipFile=zip_content
    )
    print("Updated Lambda function code")

def invoke_lambda_function():
    lambda_client = boto3.client('lambda')
    
    response = lambda_client.invoke(
        FunctionName='fraud-processor',
        InvocationType='RequestResponse'
    )
    
    result = json.loads(response['Payload'].read())
    print(f"Lambda execution result: {result}")
    return result

def check_dynamodb_items():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    response = table.scan()
    items = response['Items']
    
    print(f"Found {len(items)} fraud alerts in DynamoDB:")
    for item in items[:5]:  # Show first 5 items
        print(f"- Transaction: {item['transaction_id']}, Amount: ${item['amount']}, Score: {item['anomaly_score']}")
    
    if len(items) > 5:
        print(f"... and {len(items) - 5} more alerts")

if __name__ == "__main__":
    # Update Lambda function
    update_lambda_function()
    
    # Invoke Lambda function
    print("Invoking updated Lambda function...")
    result = invoke_lambda_function()
    
    # Check DynamoDB items
    print("\nChecking DynamoDB fraud-alerts table:")
    check_dynamodb_items()