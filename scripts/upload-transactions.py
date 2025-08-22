import boto3
import csv
import random
from datetime import datetime, timedelta
import io

def generate_transactions():
    transactions = []
    countries = ['US', 'UK', 'CA', 'DE', 'FR', 'JP', 'AU', 'BR', 'IN', 'CN']
    categories = ['grocery', 'gas', 'restaurant', 'retail', 'online', 'atm', 'transfer', 'bill_pay']
    
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(200):
        transaction = {
            'transaction_id': f'TXN{i+1:06d}',
            'customer_id': f'CUST{random.randint(1000, 9999)}',
            'amount': round(random.uniform(5.0, 5000.0), 2),
            'country': random.choice(countries),
            'merchant_category': random.choice(categories),
            'timestamp': (start_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )).strftime('%Y-%m-%d %H:%M:%S')
        }
        transactions.append(transaction)
    
    return transactions

def upload_to_s3(bucket_name, transactions):
    s3 = boto3.client('s3')
    
    # Create CSV in memory
    csv_buffer = io.StringIO()
    fieldnames = ['transaction_id', 'customer_id', 'amount', 'country', 'merchant_category', 'timestamp']
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(transactions)
    
    # Upload to S3
    s3.put_object(
        Bucket=bucket_name,
        Key='input/transactions.csv',
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    
    print(f"Uploaded transactions.csv to s3://{bucket_name}/input/transactions.csv")

if __name__ == "__main__":
    bucket_name = 'my-secure-bucket-wxj077wp'
    transactions = generate_transactions()
    upload_to_s3(bucket_name, transactions)
    print(f"Generated {len(transactions)} synthetic transactions")