import pytest
import csv
import io
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.upload_transactions import generate_transactions, upload_to_s3

class TestUploadTransactions:
    
    def test_generate_transactions(self):
        """Test transaction generation"""
        transactions = generate_transactions()
        
        assert len(transactions) == 200
        assert all('transaction_id' in t for t in transactions)
        assert all('customer_id' in t for t in transactions)
        assert all('amount' in t for t in transactions)
        assert all('country' in t for t in transactions)
        assert all('merchant_category' in t for t in transactions)
        assert all('timestamp' in t for t in transactions)
    
    def test_transaction_data_types(self):
        """Test transaction data types and ranges"""
        transactions = generate_transactions()
        
        for transaction in transactions[:10]:  # Test first 10
            assert transaction['transaction_id'].startswith('TXN')
            assert transaction['customer_id'].startswith('CUST')
            assert 5.0 <= transaction['amount'] <= 5000.0
            assert transaction['country'] in ['US', 'UK', 'CA', 'DE', 'FR', 'JP', 'AU', 'BR', 'IN', 'CN']
            assert transaction['merchant_category'] in ['grocery', 'gas', 'restaurant', 'retail', 'online', 'atm', 'transfer', 'bill_pay']
    
    def test_transaction_id_uniqueness(self):
        """Test that transaction IDs are unique"""
        transactions = generate_transactions()
        transaction_ids = [t['transaction_id'] for t in transactions]
        
        assert len(transaction_ids) == len(set(transaction_ids))
    
    @patch('scripts.upload_transactions.boto3')
    def test_upload_to_s3(self, mock_boto3):
        """Test S3 upload functionality"""
        mock_s3 = Mock()
        mock_boto3.client.return_value = mock_s3
        
        transactions = [
            {
                'transaction_id': 'TXN000001',
                'customer_id': 'CUST1234',
                'amount': 100.50,
                'country': 'US',
                'merchant_category': 'grocery',
                'timestamp': '2025-01-15 10:30:00'
            }
        ]
        
        upload_to_s3('test-bucket', transactions)
        
        # Verify S3 put_object was called
        mock_s3.put_object.assert_called_once()
        call_args = mock_s3.put_object.call_args
        
        assert call_args[1]['Bucket'] == 'test-bucket'
        assert call_args[1]['Key'] == 'input/transactions.csv'
        assert call_args[1]['ContentType'] == 'text/csv'
        
        # Verify CSV content
        csv_content = call_args[1]['Body']
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)
        
        assert len(rows) == 1
        assert rows[0]['transaction_id'] == 'TXN000001'
        assert rows[0]['amount'] == '100.5'