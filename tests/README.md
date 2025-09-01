# Test Suite for Fraud Detection System

## Overview
This test suite provides comprehensive testing for the AWS fraud detection pipeline components.

## Test Structure
```
tests/
├── test_fraud_investigator.py    # AI Assistant Lambda tests
├── test_lambda_function.py       # Fraud processor Lambda tests  
├── test_upload_transactions.py   # Transaction upload tests
├── test_anomaly_detection.py     # ML anomaly detection tests
├── test_deploy_lambda.py         # Deployment script tests
├── conftest.py                   # Shared fixtures
└── README.md                     # This file
```

## Running Tests

### Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_fraud_investigator.py
```

### Run with Coverage
```bash
pytest --cov=lambda --cov=scripts --cov-report=html
```

### Run Only Unit Tests
```bash
pytest -m unit
```

## Test Categories

### Unit Tests
- **FraudInvestigator**: Natural language query processing
- **Lambda Functions**: Fraud alert processing logic
- **Data Generation**: Transaction creation and validation
- **Anomaly Detection**: ML model functionality

### Integration Tests
- **AWS Service Integration**: S3, DynamoDB, Lambda interactions
- **End-to-End Workflows**: Complete data pipeline testing

## Mock Strategy
- **AWS Services**: Mocked using unittest.mock and moto
- **External Dependencies**: Isolated using fixtures
- **Data Sources**: Sample data provided via fixtures

## Key Test Scenarios
1. **Query Processing**: Natural language to SQL conversion
2. **Data Filtering**: Anomaly score thresholds (>2.5)
3. **Error Handling**: AWS service failures and data issues
4. **Data Validation**: Transaction format and type checking
5. **Security**: IAM policy and permission validation