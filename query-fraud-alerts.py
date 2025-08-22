import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

def query_top_fraud_alerts():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    # Scan all items and sort by anomaly score
    response = table.scan()
    items = response['Items']
    
    # Sort by anomaly score (most anomalous first - lowest scores)
    sorted_items = sorted(items, key=lambda x: float(x['anomaly_score']))
    
    print("TOP 10 MOST CRITICAL FRAUD ALERTS:")
    print("=" * 80)
    
    for i, item in enumerate(sorted_items[:10], 1):
        print(f"{i:2d}. Transaction ID: {item['transaction_id']}")
        print(f"    Customer ID: {item['customer_id']}")
        print(f"    Amount: ${float(item['amount']):,.2f}")
        print(f"    Anomaly Score: {float(item['anomaly_score']):.6f}")
        print(f"    Timestamp: {item['timestamp']}")
        print(f"    Status: {item['status']}")
        print("-" * 60)
    
    print(f"\nTotal fraud alerts in database: {len(items)}")
    
    # Statistics
    amounts = [float(item['amount']) for item in items]
    scores = [float(item['anomaly_score']) for item in items]
    
    print(f"\nFRAUD ALERT STATISTICS:")
    print(f"Average transaction amount: ${sum(amounts)/len(amounts):,.2f}")
    print(f"Highest amount: ${max(amounts):,.2f}")
    print(f"Most anomalous score: {min(scores):.6f}")
    print(f"Least anomalous score: {max(scores):.6f}")

if __name__ == "__main__":
    query_top_fraud_alerts()