import boto3
import os

print("Checking AWS credentials...")
print(f"AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID', 'Not set')}")
print(f"AWS_SECRET_ACCESS_KEY: {'Set' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'Not set'}")
print(f"AWS_DEFAULT_REGION: {os.environ.get('AWS_DEFAULT_REGION', 'Not set')}")

try:
    session = boto3.Session()
    credentials = session.get_credentials()
    if credentials:
        print(f"Credentials found: {credentials.access_key[:10]}...")
        print(f"Region: {session.region_name}")
    else:
        print("No credentials found")
except Exception as e:
    print(f"Error: {e}")