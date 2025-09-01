import boto3
from decimal import Decimal
from datetime import datetime

def insert_sample_fraud_alerts():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    # Sample fraud alerts with anomaly_score > 2.5
    sample_alerts = [
        {
            'transaction_id': 'TXN999001',
            'customer_id': 'CUST9001',
            'amount': Decimal('15000.00'),
            'anomaly_score': Decimal('3.2'),
            'timestamp': '2025-01-15 23:45:12',
            'alert_created': datetime.now().isoformat(),
            'status': 'PENDING_REVIEW'
        },
        {
            'transaction_id': 'TXN999002',
            'customer_id': 'CUST9002',
            'amount': Decimal('25000.50'),
            'anomaly_score': Decimal('4.1'),
            'timestamp': '2025-01-15 02:30:45',
            'alert_created': datetime.now().isoformat(),
            'status': 'PENDING_REVIEW'
        },
        {
            'transaction_id': 'TXN999003',
            'customer_id': 'CUST9003',
            'amount': Decimal('8750.25'),
            'anomaly_score': Decimal('2.8'),
            'timestamp': '2025-01-14 18:15:33',
            'alert_created': datetime.now().isoformat(),
            'status': 'PENDING_REVIEW'
        },
        {
            'transaction_id': 'TXN999004',
            'customer_id': 'CUST9004',
            'amount': Decimal('50000.00'),
            'anomaly_score': Decimal('5.7'),
            'timestamp': '2025-01-14 03:22:18',
            'alert_created': datetime.now().isoformat(),
            'status': 'PENDING_REVIEW'
        },
        {
            'transaction_id': 'TXN999005',
            'customer_id': 'CUST9005',
            'amount': Decimal('12500.75'),
            'anomaly_score': Decimal('3.9'),
            'timestamp': '2025-01-13 14:55:07',
            'alert_created': datetime.now().isoformat(),
            'status': 'PENDING_REVIEW'
        }
    ]
    
    print("Inserting 5 sample fraud alerts with anomaly_score > 2.5...")
    
    for alert in sample_alerts:
        table.put_item(Item=alert)
        print(f"Inserted: {alert['transaction_id']} - Score: {alert['anomaly_score']} - Amount: ${alert['amount']}")
    
    print(f"\nSuccessfully inserted {len(sample_alerts)} fraud alerts")

def verify_records():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    response = table.scan()
    items = response['Items']
    
    print(f"\nVerification - Records in DynamoDB: {len(items)}")
    
    for item in items:
        print(f"- {item['transaction_id']}: Score {item['anomaly_score']}, Amount ${item['amount']}")
    
    # Verify all scores > 2.5
    valid_scores = [item for item in items if float(item['anomaly_score']) > 2.5]
    print(f"\nRecords with score > 2.5: {len(valid_scores)}/{len(items)}")

if __name__ == "__main__":
    insert_sample_fraud_alerts()
    verify_records()