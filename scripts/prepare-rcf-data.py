import boto3
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import io

s3 = boto3.client('s3')
bucket = 'my-secure-bucket-wxj077wp'

# Read parquet files from cleaned folder
try:
    # List objects in cleaned folder
    response = s3.list_objects_v2(Bucket=bucket, Prefix='cleaned/')
    
    if 'Contents' not in response:
        print("No files found in cleaned folder")
        exit()
    
    # Read the first parquet file
    parquet_key = None
    for obj in response['Contents']:
        if obj['Key'].endswith('.parquet'):
            parquet_key = obj['Key']
            break
    
    if not parquet_key:
        print("No parquet files found")
        exit()
    
    # Download and read parquet file
    obj = s3.get_object(Bucket=bucket, Key=parquet_key)
    df = pd.read_parquet(io.BytesIO(obj['Body'].read()))
    
    print(f"Read {len(df)} records from {parquet_key}")
    print(f"Columns: {list(df.columns)}")
    
    # Prepare data for RCF
    # Encode categorical variables
    le_country = LabelEncoder()
    le_category = LabelEncoder()
    
    df['country_encoded'] = le_country.fit_transform(df['country'].astype(str))
    df['category_encoded'] = le_category.fit_transform(df['merchant_category'].astype(str))
    
    # Select numerical features only
    features = ['amount', 'transaction_hour', 'country_encoded', 'category_encoded']
    
    # Ensure all features are present
    for feature in features:
        if feature not in df.columns:
            print(f"Missing feature: {feature}")
            exit()
    
    # Create feature matrix (no headers, no index for RCF)
    feature_data = df[features].values
    
    # Convert to CSV format for RCF
    csv_buffer = io.StringIO()
    np.savetxt(csv_buffer, feature_data, delimiter=',', fmt='%.6f')
    
    # Upload processed data
    s3.put_object(
        Bucket=bucket,
        Key='rcf-input/training.csv',
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    
    print(f"Uploaded RCF training data: {feature_data.shape}")
    print(f"Features: {features}")
    
except Exception as e:
    print(f"Error: {e}")