# 🚨 Financial Fraud Detection System

A comprehensive, serverless fraud detection pipeline built on AWS with AI-powered investigation capabilities.

## 🎯 Overview

This system provides end-to-end fraud detection using machine learning, real-time processing, and natural language query interface for fraud investigators.

## 🏗️ Architecture

```
Raw Transactions → Glue ETL → ML Anomaly Detection → Lambda Processing → DynamoDB → AI Assistant
```

### Core Components

- **Data Pipeline**: AWS Glue for ETL processing
- **ML Detection**: Isolation Forest algorithm for anomaly detection
- **Storage**: S3 for data, DynamoDB for fraud alerts
- **Processing**: Lambda functions for serverless processing
- **AI Interface**: Natural language fraud investigation assistant
- **Web UI**: Modern chat interface for investigators

## 📁 Project Structure

```
financial_fraud_detection/
├── terraform/              # Infrastructure as Code
│   ├── main.tf             # Provider configuration
│   ├── s3.tf               # S3 buckets
│   ├── dynamodb.tf         # DynamoDB tables
│   ├── lambda.tf           # Lambda functions
│   ├── api_gateway.tf      # API Gateway
│   ├── glue.tf             # Glue jobs
│   └── iam.tf              # IAM roles & policies
├── lambda/                 # Lambda function code
│   ├── fraud_investigator_lambda.py  # AI assistant
│   └── lambda_function.py  # Fraud processor
├── glue_scripts/           # Glue ETL scripts
│   └── fraud_detection.py  # Data processing
├── scripts/                # Utility scripts
│   ├── upload-transactions.py      # Data generation
│   ├── simple-anomaly-detection.py # ML processing
│   └── insert-sample-fraud-alerts.py # Test data
├── web/                    # Web interfaces
│   └── fraud-investigator-chat.html # Chat UI
├── tests/                  # Test suite
└── docs/                   # Documentation
```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured
- Terraform installed
- Python 3.9+

### Deployment

1. **Clone Repository**
   ```bash
   git clone https://github.com/vinayak-vats-1/financial_fraud_detector.git
   cd financial_fraud_detection
   ```

2. **Configure Terraform**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

3. **Deploy Infrastructure**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🔄 Data Flow

### 1. Data Generation
```bash
python scripts/upload-transactions.py
```
- Generates 200 synthetic banking transactions
- Uploads to S3: `s3://bucket/input/transactions.csv`

### 2. ETL Processing (Glue)
- Reads raw transaction data
- Cleans and validates data
- Outputs to: `s3://bucket/cleaned/`

### 3. Anomaly Detection
```bash
python scripts/simple-anomaly-detection.py
```
- **Algorithm**: Isolation Forest
- **Features**: amount, transaction_hour, country, merchant_category
- **Output**: Anomaly scores to `s3://bucket/scored/`

### 4. Fraud Alert Processing (Lambda)
- Filters transactions with `anomaly_score > 2.5`
- Stores high-risk alerts in DynamoDB
- Enriches with transaction details

## 🤖 AI Assistant Usage

### Web Interface
Open `web/fraud-investigator-chat.html` in your browser for a modern chat interface.

### Natural Language Queries
- *"Show me the top 5 suspicious transactions"*
- *"Which customers have the highest fraud scores?"*
- *"Explain why transaction TXN999004 was flagged"*
- *"Give me a fraud summary for today"*

### API Endpoint
```bash
curl -X POST https://api-gateway-url/investigate \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me fraud summary"}'
```

## 📊 Key Features

### Fraud Detection Rules
- **Amount Threshold**: Transactions > $1,500
- **Geographic Risk**: Non-US transactions
- **ML Anomaly Score**: Isolation Forest algorithm
- **Alert Threshold**: Anomaly score > 2.5

### Risk Levels
- **🔴 Critical (>5.0)**: Immediate investigation required
- **🟠 High (4.0-5.0)**: High priority review
- **🟡 Moderate (2.5-4.0)**: Standard review process

### Security Features
- **S3**: Encryption, versioning, blocked public access
- **DynamoDB**: Pay-per-request, encrypted at rest
- **Lambda**: Least privilege IAM roles
- **API Gateway**: CORS configured, rate limiting ready

## 🧪 Testing

### Run Test Suite
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=lambda --cov=scripts --cov-report=html
```

### Test Categories
- **Unit Tests**: Lambda functions, data processing
- **Integration Tests**: AWS service interactions
- **ML Tests**: Anomaly detection algorithm

## 📈 Monitoring & Metrics

### CloudWatch Metrics
- Lambda execution duration and errors
- DynamoDB read/write capacity
- API Gateway request count and latency

### Fraud Metrics
- Total alerts generated
- Average anomaly scores
- Customer risk distribution
- Transaction volume analysis

## 🔧 Configuration

### Environment Variables
```bash
# Lambda Functions
DYNAMODB_TABLE=fraud-alerts
S3_BUCKET=your-fraud-detection-bucket

# ML Parameters
ANOMALY_THRESHOLD=2.5
CONTAMINATION_RATE=0.1
```

### Terraform Variables
```hcl
# terraform.tfvars
project_name = "fraud-detection"
environment  = "prod"
aws_region   = "us-east-1"
```

## 🚨 Sample Fraud Alerts

```json
{
  "transaction_id": "TXN999004",
  "customer_id": "CUST9004",
  "amount": 50000.00,
  "anomaly_score": 5.7,
  "timestamp": "2025-01-14T03:22:18Z",
  "status": "PENDING_REVIEW"
}
```

## 📚 API Reference

### FraudInvestigator Endpoints

#### POST /investigate
Query the fraud detection system using natural language.

**Request:**
```json
{
  "query": "Show me the top 3 anomalous transactions"
}
```

**Response:**
```json
{
  "query": "Show me the top 3 anomalous transactions",
  "response": "Top 3 most anomalous transactions:\n1. TXN999004 - Score: 5.7 - $50,000.00\n2. TXN999002 - Score: 4.1 - $25,000.50\n3. TXN999005 - Score: 3.9 - $12,500.75"
}
```

## 🛠️ Development

### Local Development
```bash
# Run fraud investigator locally
python lambda/fraud_investigator.py

# Generate test data
python scripts/upload-transactions.py

# Run anomaly detection
python scripts/simple-anomaly-detection.py
```

### Adding New Features
1. Update Terraform configurations
2. Modify Lambda functions
3. Add corresponding tests
4. Update documentation

## 📋 Troubleshooting

### Common Issues

**Lambda Timeout**
- Increase timeout in `terraform/lambda.tf`
- Optimize query performance

**DynamoDB Throttling**
- Switch to provisioned capacity
- Add GSI for query patterns

**S3 Access Denied**
- Check IAM policies in `terraform/iam.tf`
- Verify bucket permissions

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- **Repository**: https://github.com/vinayak-vats-1/financial_fraud_detector
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/

---

**Built with ❤️ using AWS serverless technologies**