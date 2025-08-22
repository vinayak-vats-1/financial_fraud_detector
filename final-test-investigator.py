import boto3
import json
import time

def final_test():
    lambda_client = boto3.client('lambda')
    
    print("Final test of FraudInvestigator (waiting for permissions to propagate)")
    time.sleep(15)  # Wait longer for permissions
    
    queries = [
        "Show me the top 2 anomalous transactions",
        "Give me a summary of fraud metrics"
    ]
    
    for query in queries:
        print(f"\nTesting: {query}")
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
                print("SUCCESS!")
                print(body['response'].replace('\\n', '\n'))
            else:
                body = json.loads(result['body'])
                print(f"Error: {body.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    final_test()