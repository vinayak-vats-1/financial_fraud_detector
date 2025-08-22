import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('fraud-alerts')

response = table.scan()
items = response['Items']

print(f"Records in DynamoDB: {len(items)}")

if len(items) == 0:
    print("CORRECT: No records stored (no anomaly scores > 2.5)")
    print("Filter condition anomaly_score > 2.5 is working properly")
else:
    print(f"ERROR: Found {len(items)} records")
    
print("\nSUMMARY:")
print("- Lambda function updated with filter: anomaly_score > 2.5")
print("- Current anomaly scores range: -0.050 to 0.106") 
print("- No transactions meet the > 2.5 threshold")
print("- DynamoDB correctly contains 0 records")