import boto3
import os

# Explicitly set credentials path
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = r'C:\Users\tripti.a.goel\.aws\credentials'
os.environ['AWS_CONFIG_FILE'] = r'C:\Users\tripti.a.goel\.aws\config'

s3 = boto3.client('s3')
response = s3.list_buckets()

print("Your S3 buckets:")
for bucket in response['Buckets']:
    print(f"- {bucket['Name']}")
    
print("\nYour secure buckets:")
for bucket in response['Buckets']:
    if 'my-secure-bucket' in bucket['Name'] or 'access-logs' in bucket['Name']:
        print(f"- {bucket['Name']}")
        
print("\nTotal buckets:", len(response['Buckets']))