import boto3

def verify_anomaly_filter():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fraud-alerts')
    
    # Scan all items
    response = table.scan()
    items = response['Items']
    
    print(f"Total records in DynamoDB: {len(items)}")
    
    # Check filter condition: anomaly_score > -2.5
    valid_records = 0
    invalid_records = 0
    invalid_items = []
    
    for item in items:
        score = float(item['anomaly_score'])
        if score > -2.5:
            valid_records += 1
        else:
            invalid_records += 1
            invalid_items.append({
                'transaction_id': item['transaction_id'],
                'score': score
            })
    
    print(f"\nFILTER VERIFICATION RESULTS:")
    print(f"Records with anomaly_score > -2.5: {valid_records}")
    print(f"Records with anomaly_score <= -2.5: {invalid_records}")
    
    if invalid_records > 0:
        print(f"\nERROR: Found {invalid_records} records that should NOT be in DynamoDB:")
        for item in invalid_items[:10]:  # Show first 10
            print(f"  - {item['transaction_id']}: {item['score']}")
        if len(invalid_items) > 10:
            print(f"  ... and {len(invalid_items) - 10} more")
    else:
        print("\nSUCCESS: All records correctly have anomaly_score > -2.5")
    
    # Show score distribution
    scores = [float(item['anomaly_score']) for item in items]
    print(f"\nSCORE STATISTICS:")
    print(f"Minimum score: {min(scores):.6f}")
    print(f"Maximum score: {max(scores):.6f}")
    print(f"Average score: {sum(scores)/len(scores):.6f}")
    
    return invalid_records == 0

if __name__ == "__main__":
    verify_anomaly_filter()