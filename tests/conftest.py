import pytest
import os
import sys
from unittest.mock import Mock

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for testing"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def sample_fraud_alert():
    """Sample fraud alert data for testing"""
    from decimal import Decimal
    return {
        'transaction_id': 'TXN999001',
        'customer_id': 'CUST9001',
        'amount': Decimal('15000.00'),
        'anomaly_score': Decimal('3.2'),
        'timestamp': '2025-01-15 23:45:12',
        'status': 'PENDING_REVIEW'
    }

@pytest.fixture
def sample_transactions():
    """Sample transaction data for testing"""
    return [
        {
            'transaction_id': 'TXN001',
            'customer_id': 'CUST001',
            'amount': 1250.50,
            'country': 'US',
            'merchant_category': 'grocery',
            'timestamp': '2025-01-15 14:30:00'
        },
        {
            'transaction_id': 'TXN002',
            'customer_id': 'CUST002',
            'amount': 4500.00,
            'country': 'UK',
            'merchant_category': 'retail',
            'timestamp': '2025-01-15 02:15:00'
        }
    ]