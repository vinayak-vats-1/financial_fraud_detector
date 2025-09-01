import pytest
import json
from unittest.mock import Mock, patch
from decimal import Decimal
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lambda.fraud_investigator_lambda import FraudInvestigator, lambda_handler

class TestFraudInvestigator:
    
    @pytest.fixture
    def mock_table(self):
        """Mock DynamoDB table with sample data"""
        table = Mock()
        table.scan.return_value = {
            'Items': [
                {
                    'transaction_id': 'TXN001',
                    'customer_id': 'CUST001',
                    'amount': Decimal('5000.00'),
                    'anomaly_score': Decimal('4.5')
                },
                {
                    'transaction_id': 'TXN002',
                    'customer_id': 'CUST002',
                    'amount': Decimal('15000.00'),
                    'anomaly_score': Decimal('5.7')
                }
            ]
        }
        table.get_item.return_value = {
            'Item': {
                'transaction_id': 'TXN001',
                'customer_id': 'CUST001',
                'amount': Decimal('5000.00'),
                'anomaly_score': Decimal('4.5')
            }
        }
        return table
    
    @pytest.fixture
    def investigator(self, mock_table):
        return FraudInvestigator(mock_table)
    
    def test_query_top_anomalous_transactions(self, investigator):
        """Test top anomalous transactions query"""
        result = investigator.query_fraud_data("Show me top 2 anomalous transactions")
        assert "Top 2 most anomalous transactions" in result
        assert "TXN002" in result
        assert "5.7" in result
    
    def test_query_highest_fraud_scores(self, investigator):
        """Test highest fraud scores query"""
        result = investigator.query_fraud_data("List customers with highest fraud scores")
        assert "Customers with highest fraud scores" in result
        assert "CUST002: 5.7" in result
    
    def test_explain_transaction_flag(self, investigator):
        """Test transaction explanation query"""
        result = investigator.query_fraud_data("Explain why transaction TXN001 was flagged")
        assert "Transaction TXN001 flagged because" in result
        assert "Anomaly Score: 4.5" in result
        assert "Amount: $5,000.00" in result
    
    def test_summary_metrics(self, investigator):
        """Test summary metrics query"""
        result = investigator.query_fraud_data("Give me fraud summary")
        assert "FRAUD SUMMARY" in result
        assert "Total Alerts: 2" in result
        assert "Highest Score: 5.7" in result
    
    def test_anomaly_count(self, investigator):
        """Test anomaly count query"""
        result = investigator.query_fraud_data("How many fraud alerts")
        assert "Current fraud alerts: 2" in result
    
    def test_general_overview(self, investigator):
        """Test general overview for unknown queries"""
        result = investigator.query_fraud_data("Random query")
        assert "Monitoring 2 fraud alerts" in result
        assert "TXN002" in result

class TestLambdaHandler:
    
    @patch.dict(os.environ, {'DYNAMODB_TABLE': 'test-table'})
    @patch('lambda.fraud_investigator_lambda.boto3')
    def test_lambda_handler_success(self, mock_boto3):
        """Test successful lambda handler execution"""
        # Mock DynamoDB
        mock_table = Mock()
        mock_table.scan.return_value = {'Items': []}
        mock_boto3.resource.return_value.Table.return_value = mock_table
        
        event = {'query': 'Show me fraud summary'}
        context = {}
        
        result = lambda_handler(event, context)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['query'] == 'Show me fraud summary'
        assert 'response' in body
    
    @patch.dict(os.environ, {'DYNAMODB_TABLE': 'test-table'})
    @patch('lambda.fraud_investigator_lambda.boto3')
    def test_lambda_handler_error(self, mock_boto3):
        """Test lambda handler error handling"""
        # Mock DynamoDB to raise exception
        mock_boto3.resource.side_effect = Exception("DynamoDB error")
        
        event = {'query': 'test query'}
        context = {}
        
        result = lambda_handler(event, context)
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'error' in body