import boto3
import json
import time

def test_fraud_investigator():
    lambda_client = boto3.client('lambda')
    
    print("Testing FraudInvestigator AI Assistant")
    print("=" * 50)
    
    # Wait for function to be ready
    print("Waiting for Lambda function to be ready...")
    time.sleep(10)
    
    test_queries = [
        "Show me the top 2 anomalous transactions",
        "Give me a summary of fraud metrics", 
        "Explain why transaction TXN999004 was flagged",
        "List customers with highest fraud scores"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        
        try:
            response = lambda_client.invoke(
                FunctionName='fraud-investigator',
                InvocationType='RequestResponse',
                Payload=json.dumps({'query': query})
            )
            
            result = json.loads(response['Payload'].read())
            if result['statusCode'] == 200:
                body = json.loads(result['body'])
                print("Response:")
                print(body['response'])
            else:
                body = json.loads(result['body'])
                print(f"Error: {body.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    test_fraud_investigator()