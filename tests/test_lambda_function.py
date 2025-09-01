import pytest
import json
import csv
import io
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lambda.lambda_function import lambda_handler

class TestLambdaFunction:
    
    @pytest.fixture
    def mock_s3_data(self):
        """Mock S3 CSV data"""
        anomaly_scores_csv = """transaction_id,anomaly_score,is_anomaly
TXN001,3.5,True
TXN002,1.2,False
TXN003,4.8,True"""
        
        anomaly_results_csv = """transaction_id,customer_id,amount,timestamp
TXN001,CUST001,5000.00,2025-01-15 10:30:00
TXN002,CUST002,1200.00,2025-01-15 14:20:00
TXN003,CUST003,8500.00,2025-01-15 18:45:00"""
        
        return {
            'scored/anomaly_scores.csv': anomaly_scores_csv,
            'scored/anomaly_results.csv': anomaly_results_csv
        }
    
    @patch.dict(os.environ, {
        'S3_BUCKET': 'test-bucket',
        'DYNAMODB_TABLE': 'test-table'
    })
    @patch('lambda.lambda_function.boto3')
    def test_lambda_handler_success(self, mock_boto3, mock_s3_data):
        """Test successful fraud alert processing"""
        # Mock S3 client
        mock_s3 = Mock()
        mock_s3.get_object.side_effect = [
            {'Body': Mock(read=Mock(return_value=mock_s3_data['scored/anomaly_scores.csv'].encode()))},
            {'Body': Mock(read=Mock(return_value=mock_s3_data['scored/anomaly_results.csv'].encode()))}
        ]
        
        # Mock DynamoDB table
        mock_table = Mock()
        
        # Mock boto3 clients
        mock_boto3.client.return_value = mock_s3
        mock_boto3.resource.return_value.Table.return_value = mock_table
        
        event = {}
        context = {}
        
        result = lambda_handler(event, context)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert 'Successfully processed' in body['message']
        assert body['alerts_written'] == 2  # Only TXN001 and TXN003 have score > 2.5
    
    @patch.dict(os.environ, {
        'S3_BUCKET': 'test-bucket',
        'DYNAMODB_TABLE': 'test-table'
    })
    @patch('lambda.lambda_function.boto3')
    def test_lambda_handler_s3_error(self, mock_boto3):
        """Test S3 error handling"""
        # Mock S3 to raise exception
        mock_s3 = Mock()
        mock_s3.get_object.side_effect = Exception("S3 access denied")
        mock_boto3.client.return_value = mock_s3
        
        event = {}
        context = {}
        
        result = lambda_handler(event, context)
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'error' in body
    
    def test_anomaly_score_filtering(self, mock_s3_data):
        """Test that only scores > 2.5 are processed"""
        csv_content = mock_s3_data['scored/anomaly_scores.csv']
        csv_reader = csv.DictReader(csv_content.splitlines())
        
        fraud_alerts = []
        for row in csv_reader:
            anomaly_score = float(row['anomaly_score'])
            if anomaly_score > 2.5:
                fraud_alerts.append(row['transaction_id'])
        
        assert len(fraud_alerts) == 2
        assert 'TXN001' in fraud_alerts
        assert 'TXN003' in fraud_alerts
        assert 'TXN002' not in fraud_alerts