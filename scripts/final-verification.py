import boto3
import json

def clear_dynamodb():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    response = table.scan()
    items = response['Items']
    
    if items:
        print(f"Clearing {len(items)} existing records...")
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={'transaction_id': item['transaction_id']})
        print("DynamoDB cleared")
    else:
        print("DynamoDB already empty")

def test_lambda_with_correct_filter():
    lambda_client = boto3.client('lambda')
    
    response = lambda_client.invoke(
        FunctionName='fraud-processor',
        InvocationType='RequestResponse'
    )
    
    result = json.loads(response['Payload'].read())
    print(f"Lambda result: {result}")

def verify_final_state():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    response = table.scan()
    items = response['Items']
    
    print(f"\nFINAL VERIFICATION:")
    print(f"Records in DynamoDB: {len(items)}")
    
    if len(items) == 0:
        print("✅ CORRECT: No records stored (no anomaly scores > 2.5)")
    else:
        print(f"❌ ERROR: {len(items)} records found, but should be 0")
        for item in items[:5]:
            print(f"  - {item['transaction_id']}: score {item['anomaly_score']}")

if __name__ == "__main__":
    clear_dynamodb()
    test_lambda_with_correct_filter()
    verify_final_state()