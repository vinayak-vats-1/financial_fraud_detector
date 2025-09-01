import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import io
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.simple_anomaly_detection import detect_anomalies

class TestAnomalyDetection:
    
    @pytest.fixture
    def sample_transaction_data(self):
        """Sample transaction data for testing"""
        return pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003', 'TXN004'],
            'customer_id': ['CUST001', 'CUST002', 'CUST003', 'CUST004'],
            'amount': [100.0, 5000.0, 200.0, 10000.0],
            'country': ['US', 'UK', 'US', 'FR'],
            'merchant_category': ['grocery', 'retail', 'gas', 'online'],
            'timestamp': [
                '2025-01-15 10:30:00',
                '2025-01-15 14:20:00',
                '2025-01-15 18:45:00',
                '2025-01-15 22:15:00'
            ]
        })
    
    @patch('scripts.simple_anomaly_detection.boto3')
    @patch('scripts.simple_anomaly_detection.pd.read_csv')
    def test_detect_anomalies_success(self, mock_read_csv, mock_boto3, sample_transaction_data):
        """Test successful anomaly detection"""
        # Mock S3 client
        mock_s3 = Mock()
        mock_boto3.client.return_value = mock_s3
        
        # Mock CSV reading
        mock_read_csv.return_value = sample_transaction_data
        
        # Mock S3 get_object
        mock_s3.get_object.return_value = {
            'Body': Mock(read=Mock(return_value=b'mock_csv_data'))
        }
        
        result = detect_anomalies()
        
        # Verify S3 operations
        assert mock_s3.get_object.called
        assert mock_s3.put_object.call_count == 2  # Two files uploaded
        
        # Verify put_object calls for results
        put_calls = mock_s3.put_object.call_args_list
        keys = [call[1]['Key'] for call in put_calls]
        assert 'scored/anomaly_results.csv' in keys
        assert 'scored/anomaly_scores.csv' in keys
    
    def test_feature_engineering(self, sample_transaction_data):
        """Test feature engineering for ML model"""
        df = sample_transaction_data.copy()
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['transaction_hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Encode categorical variables
        from sklearn.preprocessing import LabelEncoder
        le_country = LabelEncoder()
        le_category = LabelEncoder()
        
        df['country_encoded'] = le_country.fit_transform(df['country'])
        df['category_encoded'] = le_category.fit_transform(df['merchant_category'])
        
        # Verify features
        assert 'transaction_hour' in df.columns
        assert 'day_of_week' in df.columns
        assert 'country_encoded' in df.columns
        assert 'category_encoded' in df.columns
        
        # Verify hour extraction
        assert df.loc[0, 'transaction_hour'] == 10
        assert df.loc[1, 'transaction_hour'] == 14
    
    @patch('scripts.simple_anomaly_detection.boto3')
    def test_detect_anomalies_s3_error(self, mock_boto3):
        """Test S3 error handling"""
        # Mock S3 to raise exception
        mock_s3 = Mock()
        mock_s3.get_object.side_effect = Exception("S3 access denied")
        mock_boto3.client.return_value = mock_s3
        
        result = detect_anomalies()
        
        assert result is False
    
    def test_isolation_forest_parameters(self):
        """Test Isolation Forest configuration"""
        from sklearn.ensemble import IsolationForest
        
        # Test model initialization
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        
        assert iso_forest.contamination == 0.1
        assert iso_forest.random_state == 42
    
    def test_anomaly_score_calculation(self, sample_transaction_data):
        """Test anomaly score calculation"""
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import LabelEncoder
        
        df = sample_transaction_data.copy()
        
        # Prepare features
        le_country = LabelEncoder()
        le_category = LabelEncoder()
        
        df['country_encoded'] = le_country.fit_transform(df['country'])
        df['category_encoded'] = le_category.fit_transform(df['merchant_category'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['transaction_hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        features = ['amount', 'transaction_hour', 'country_encoded', 'category_encoded', 'day_of_week']
        X = df[features].values
        
        # Run anomaly detection
        iso_forest = IsolationForest(contamination=0.25, random_state=42)  # 25% for small dataset
        anomaly_scores = iso_forest.fit_predict(X)
        anomaly_scores_proba = iso_forest.decision_function(X)
        
        # Verify outputs
        assert len(anomaly_scores) == len(df)
        assert len(anomaly_scores_proba) == len(df)
        assert all(score in [-1, 1] for score in anomaly_scores)  # -1 = anomaly, 1 = normal