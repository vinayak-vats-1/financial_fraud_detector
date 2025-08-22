import boto3
import json

def clear_dynamodb_table():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    # Scan and delete all items
    response = table.scan()
    items = response['Items']
    
    print(f"Deleting {len(items)} existing records...")
    
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={'transaction_id': item['transaction_id']})
    
    print("All records deleted from DynamoDB")

def update_and_run_lambda():
    lambda_client = boto3.client('lambda')
    
    # Update function code
    with open('fraud_processor.zip', 'rb') as f:
        zip_content = f.read()
    
    lambda_client.update_function_code(
        FunctionName='fraud-processor',
        ZipFile=zip_content
    )
    print("Updated Lambda function with corrected filter (anomaly_score > 2.5)")
    
    # Invoke function
    response = lambda_client.invoke(
        FunctionName='fraud-processor',
        InvocationType='RequestResponse'
    )
    
    result = json.loads(response['Payload'].read())
    print(f"Lambda execution result: {result}")
    return result

def verify_results():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    response = table.scan()
    items = response['Items']
    
    print(f"\nFinal verification:")
    print(f"Records in DynamoDB: {len(items)}")
    
    if len(items) > 0:
        scores = [float(item['anomaly_score']) for item in items]
        print(f"Score range: {min(scores):.6f} to {max(scores):.6f}")
        
        # Check if all scores > 2.5
        valid_count = sum(1 for score in scores if score > 2.5)
        print(f"Records with score > 2.5: {valid_count}/{len(items)}")
    else:
        print("No records found (expected if no scores > 2.5)")

if __name__ == "__main__":
    # Clear existing data
    clear_dynamodb_table()
    
    # Update and run corrected Lambda
    update_and_run_lambda()
    
    # Verify results
    verify_results()