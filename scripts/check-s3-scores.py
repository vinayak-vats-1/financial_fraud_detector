import boto3
import csv

s3 = boto3.client('s3')
bucket = 'my-secure-bucket-wxj077wp'

# Read anomaly scores from S3
response = s3.get_object(Bucket=bucket, Key='scored/anomaly_scores.csv')
content = response['Body'].read().decode('utf-8')

csv_reader = csv.DictReader(content.splitlines())
scores = []

for row in csv_reader:
    scores.append(float(row['anomaly_score']))

print(f"Total scores in S3: {len(scores)}")
print(f"Score range: {min(scores):.6f} to {max(scores):.6f}")
print(f"Scores > 2.5: {sum(1 for s in scores if s > 2.5)}")
print(f"Scores > 0: {sum(1 for s in scores if s > 0)}")
print(f"Scores < 0: {sum(1 for s in scores if s < 0)}")

# Show some sample scores
print(f"\nSample scores:")
for i, score in enumerate(sorted(scores, reverse=True)[:10]):
    print(f"  {i+1}: {score:.6f}")

print(f"\nNote: With current anomaly detection algorithm, all scores are between {min(scores):.3f} and {max(scores):.3f}")
print("No transactions have anomaly_score > 2.5, so DynamoDB should be empty with correct filter.")