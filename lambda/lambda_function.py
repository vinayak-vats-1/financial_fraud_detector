import json
import boto3
import csv
import os
from datetime import datetime
from decimal import Decimal

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    
    bucket = os.environ['S3_BUCKET']
    table_name = os.environ['DYNAMODB_TABLE']
    table = dynamodb.Table(table_name)
    
    try:
        # Read anomaly scores from S3
        response = s3.get_object(Bucket=bucket, Key='scored/anomaly_scores.csv')
        content = response['Body'].read().decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(content.splitlines())
        fraud_alerts = []
        
        for row in csv_reader:
            anomaly_score = float(row['anomaly_score'])
            
            # Filter transactions with anomaly_score > 2.5
            if anomaly_score > 2.5:
                fraud_alerts.append({
                    'transaction_id': row['transaction_id'],
                    'anomaly_score': anomaly_score,
                    'is_anomaly': row['is_anomaly']
                })
        
        # Get additional transaction details from original results
        response = s3.get_object(Bucket=bucket, Key='scored/anomaly_results.csv')
        content = response['Body'].read().decode('utf-8')
        csv_reader = csv.DictReader(content.splitlines())
        
        transaction_details = {}
        for row in csv_reader:
            transaction_details[row['transaction_id']] = {
                'customer_id': row['customer_id'],
                'amount': float(row['amount']),
                'timestamp': row['timestamp']
            }
        
        # Write fraud alerts to DynamoDB
        alerts_written = 0
        for alert in fraud_alerts:
            transaction_id = alert['transaction_id']
            details = transaction_details.get(transaction_id, {})
            
            item = {
                'transaction_id': transaction_id,
                'customer_id': details.get('customer_id', 'UNKNOWN'),
                'amount': Decimal(str(details.get('amount', 0.0))),
                'anomaly_score': Decimal(str(alert['anomaly_score'])),
                'timestamp': details.get('timestamp', datetime.now().isoformat()),
                'alert_created': datetime.now().isoformat(),
                'status': 'PENDING_REVIEW'
            }
            
            table.put_item(Item=item)
            alerts_written += 1
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {alerts_written} fraud alerts',
                'alerts_written': alerts_written
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }