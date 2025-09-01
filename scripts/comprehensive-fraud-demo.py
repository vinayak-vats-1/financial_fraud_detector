import boto3
import json

def comprehensive_demo():
    lambda_client = boto3.client('lambda')
    
    print("FRAUDINVESTIGATOR AI ASSISTANT - COMPREHENSIVE DEMO")
    print("=" * 60)
    print("Natural Language Query Interface for Fraud Detection")
    print()
    
    # Comprehensive test queries
    demo_queries = [
        {
            "query": "Show me the top 3 anomalous transactions",
            "description": "Get highest risk transactions"
        },
        {
            "query": "List customers with highest fraud scores", 
            "description": "Identify risky customers"
        },
        {
            "query": "Explain why transaction TXN999004 was flagged as suspicious",
            "description": "Detailed transaction analysis"
        },
        {
            "query": "Give me a summary of fraud metrics",
            "description": "Overall fraud statistics"
        },
        {
            "query": "How many fraud alerts do we have?",
            "description": "Simple count query"
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"{i}. {demo['description'].upper()}")
        print(f"Query: \"{demo['query']}\"")
        print("-" * 50)
        
        try:
            response = lambda_client.invoke(
                FunctionName='fraud-investigator',
                InvocationType='RequestResponse',
                Payload=json.dumps({'query': demo['query']})
            )
            
            result = json.loads(response['Payload'].read())
            if result['statusCode'] == 200:
                body = json.loads(result['body'])
                print("AI Response:")
                print(body['response'].replace('\\n', '\n'))
            else:
                body = json.loads(result['body'])
                print(f"Error: {body.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*60 + "\n")
    
    print("FRAUDINVESTIGATOR CAPABILITIES SUMMARY:")
    print("✓ Natural language query processing")
    print("✓ Real-time DynamoDB fraud data access") 
    print("✓ Transaction risk analysis and explanations")
    print("✓ Customer fraud score rankings")
    print("✓ Comprehensive fraud metrics and statistics")
    print("✓ Deployed as serverless AWS Lambda function")
    print("✓ Integrated with existing fraud detection pipeline")

if __name__ == "__main__":
    comprehensive_demo()