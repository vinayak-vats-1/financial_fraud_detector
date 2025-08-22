import boto3
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import io

def detect_anomalies():
    s3 = boto3.client('s3')
    bucket = 'my-secure-bucket-wxj077wp'
    
    # Read the original transaction data
    try:
        obj = s3.get_object(Bucket=bucket, Key='input/transactions.csv')
        df = pd.read_csv(io.BytesIO(obj['Body'].read()))
        print(f"Loaded {len(df)} transactions")
        
        # Prepare features for anomaly detection
        le_country = LabelEncoder()
        le_category = LabelEncoder()
        
        df['country_encoded'] = le_country.fit_transform(df['country'])
        df['category_encoded'] = le_category.fit_transform(df['merchant_category'])
        
        # Convert timestamp to hour
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['transaction_hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Select features for anomaly detection
        features = ['amount', 'transaction_hour', 'country_encoded', 'category_encoded', 'day_of_week']
        X = df[features].values
        
        # Use Isolation Forest for anomaly detection
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_scores = iso_forest.fit_predict(X)
        anomaly_scores_proba = iso_forest.decision_function(X)
        
        # Create results dataframe
        results = df.copy()
        results['anomaly_score'] = anomaly_scores_proba
        results['is_anomaly'] = anomaly_scores == -1
        results['anomaly_rank'] = results['anomaly_score'].rank(ascending=True)
        
        # Sort by most anomalous
        results_sorted = results.sort_values('anomaly_score')
        
        print(f"Detected {sum(results['is_anomaly'])} anomalies out of {len(results)} transactions")
        
        # Save results to S3
        csv_buffer = io.StringIO()
        results_sorted.to_csv(csv_buffer, index=False)
        
        s3.put_object(
            Bucket=bucket,
            Key='scored/anomaly_results.csv',
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        
        # Save just the anomaly scores
        scores_buffer = io.StringIO()
        results_sorted[['transaction_id', 'anomaly_score', 'is_anomaly']].to_csv(scores_buffer, index=False)
        
        s3.put_object(
            Bucket=bucket,
            Key='scored/anomaly_scores.csv',
            Body=scores_buffer.getvalue(),
            ContentType='text/csv'
        )
        
        print("SCORED FILES ARE READY!")
        print("Files saved to:")
        print("- s3://my-secure-bucket-wxj077wp/scored/anomaly_results.csv")
        print("- s3://my-secure-bucket-wxj077wp/scored/anomaly_scores.csv")
        
        # Show top 10 anomalies
        print("\nTop 10 Most Anomalous Transactions:")
        anomalies = results_sorted.head(10)
        for idx, row in anomalies.iterrows():
            print(f"ID: {row['transaction_id']}, Amount: ${row['amount']:.2f}, "
                  f"Country: {row['country']}, Score: {row['anomaly_score']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    detect_anomalies()