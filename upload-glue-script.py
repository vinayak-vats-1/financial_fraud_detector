import boto3

s3 = boto3.client('s3')
bucket_name = 'my-secure-bucket-wxj077wp'

# Upload Glue script to S3
with open('glue_scripts/clean-transactions.py', 'rb') as f:
    s3.put_object(
        Bucket=bucket_name,
        Key='scripts/clean-transactions.py',
        Body=f.read(),
        ContentType='text/x-python'
    )

print(f"Uploaded Glue script to s3://{bucket_name}/scripts/clean-transactions.py")