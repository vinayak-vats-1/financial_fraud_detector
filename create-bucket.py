import boto3
import random
import string

def generate_suffix():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def create_s3_bucket():
    s3 = boto3.client('s3')
    suffix = generate_suffix()
    bucket_name = f"my-secure-bucket-{suffix}"
    logs_bucket = f"access-logs-{suffix}"
    
    # Create main bucket
    s3.create_bucket(Bucket=bucket_name)
    
    # Block public access
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
    
    # Enable versioning
    s3.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={'Status': 'Enabled'}
    )
    
    # Enable encryption
    s3.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            'Rules': [{
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            }]
        }
    )
    
    # Create logs bucket
    s3.create_bucket(Bucket=logs_bucket)
    s3.put_public_access_block(
        Bucket=logs_bucket,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
    
    # Enable logging
    s3.put_bucket_logging(
        Bucket=bucket_name,
        BucketLoggingStatus={
            'LoggingEnabled': {
                'TargetBucket': logs_bucket,
                'TargetPrefix': 'access-logs/'
            }
        }
    )
    
    print(f"Bucket created: {bucket_name}")
    print(f"Logs bucket: {logs_bucket}")

if __name__ == "__main__":
    create_s3_bucket()