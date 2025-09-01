import boto3

def display_fraud_alerts():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    response = table.scan()
    items = response['Items']
    
    # Sort by anomaly score (highest first)
    sorted_items = sorted(items, key=lambda x: float(x['anomaly_score']), reverse=True)
    
    print("FRAUD ALERTS - HIGH RISK TRANSACTIONS")
    print("=" * 70)
    
    for i, item in enumerate(sorted_items, 1):
        print(f"{i}. Transaction ID: {item['transaction_id']}")
        print(f"   Customer ID: {item['customer_id']}")
        print(f"   Amount: ${float(item['amount']):,.2f}")
        print(f"   Anomaly Score: {float(item['anomaly_score']):.1f}")
        print(f"   Transaction Time: {item['timestamp']}")
        print(f"   Status: {item['status']}")
        print("-" * 50)
    
    print(f"\nSUMMARY:")
    print(f"Total High-Risk Alerts: {len(items)}")
    
    if items:
        amounts = [float(item['amount']) for item in items]
        scores = [float(item['anomaly_score']) for item in items]
        
        print(f"Total Amount at Risk: ${sum(amounts):,.2f}")
        print(f"Average Transaction: ${sum(amounts)/len(amounts):,.2f}")
        print(f"Highest Risk Score: {max(scores):.1f}")
        print(f"Average Risk Score: {sum(scores)/len(scores):.1f}")

if __name__ == "__main__":
    display_fraud_alerts()