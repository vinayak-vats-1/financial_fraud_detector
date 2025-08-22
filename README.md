# AWS Fraud Detection Pipeline with AI Assistant

A comprehensive fraud detection system built on AWS using Glue, SageMaker, DynamoDB, and Lambda with an intelligent AI assistant for natural language queries.

## 🏗️ Architecture

```
Raw Data (S3) → Glue ETL → SageMaker RCF → Anomaly Scores → Lambda → DynamoDB → AI Assistant
```

## 🚀 Features

- **Data Processing**: AWS Glue for ETL operations
- **Anomaly Detection**: SageMaker Random Cut Forest algorithm
- **Real-time Alerts**: Lambda functions for fraud alert processing
- **Data Storage**: DynamoDB for fraud alerts, S3 for data lake
- **AI Assistant**: Natural language interface for fraud investigation
- **Web Interface**: Beautiful chat-style UI for investigators
- **Infrastructure as Code**: Complete Terraform configuration

## 📊 Components

### 1. Data Pipeline
- **S3 Buckets**: Raw transaction data and processed results
- **Glue Jobs**: Data cleaning and transformation
- **SageMaker**: Machine learning model training and inference

### 2. Fraud Detection
- **Random Cut Forest**: Unsupervised anomaly detection
- **Scoring Pipeline**: Batch processing of transactions
- **Alert System**: Automated fraud alert generation

### 3. AI Assistant (FraudInvestigator)
- **Natural Language Queries**: Ask questions in plain English
- **Real-time Analysis**: Connect to live fraud data
- **Web Interface**: Modern chat-style UI
- **API Gateway**: RESTful API for external integrations

## 🛠️ Setup Instructions

### Prerequisites
- AWS CLI configured
- Python 3.9+
- Terraform (optional)

### Quick Start
1. **Deploy Infrastructure**:
   ```bash
   python deploy-lambda-resources.py
   python deploy-fraud-investigator.py
   ```

2. **Upload Sample Data**:
   ```bash
   python upload-transactions.py
   python simple-anomaly-detection.py
   ```

3. **Open AI Assistant**:
   - Open `fraud-investigator-chat.html` in your browser
   - Or use AWS Lambda console to test queries

### Sample Queries
- "Show me the top 3 most suspicious transactions"
- "Which customers have the highest fraud scores?"
- "Explain why transaction TXN999004 was flagged"
- "Give me a comprehensive fraud summary"

## 📁 Project Structure

```
codethon/
├── terraform/                 # Infrastructure as Code
│   ├── main.tf               # Main Terraform configuration
│   ├── variables.tf          # Variable definitions
│   └── outputs.tf            # Output values
├── glue_scripts/             # ETL Scripts
│   └── clean-transactions.py # Data cleaning script
├── lambda/                   # Lambda Functions
│   ├── lambda_function.py    # Fraud processor
│   └── fraud_investigator_lambda.py # AI assistant
├── web/                      # Web Interfaces
│   ├── fraud-investigator-chat.html # Main UI
│   └── fraud-investigator-web.html  # Alternative UI
├── scripts/                  # Utility Scripts
│   ├── create-bucket.py      # S3 bucket creation
│   ├── upload-transactions.py # Sample data upload
│   └── simple-anomaly-detection.py # Anomaly detection
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables
- `DYNAMODB_TABLE`: fraud-alerts
- `S3_BUCKET`: my-secure-bucket-wxj077wp
- `AWS_REGION`: us-east-1

### API Endpoints
- **FraudInvestigator API**: `https://cn4yjqa6ni.execute-api.us-east-1.amazonaws.com/prod/query`

## 📈 Monitoring

- **CloudWatch Logs**: Lambda function logs
- **DynamoDB Metrics**: Table performance
- **S3 Metrics**: Storage and access patterns

## 🛡️ Security

- **IAM Roles**: Least privilege access
- **S3 Encryption**: AES-256 encryption at rest
- **VPC**: Network isolation (optional)
- **API Gateway**: CORS and authentication

## 🤖 AI Assistant Features

- **Natural Language Processing**: Understands fraud investigation queries
- **Real-time Data Access**: Connects to live DynamoDB data
- **Intelligent Responses**: Contextual fraud analysis
- **Web Interface**: Modern, responsive design
- **API Integration**: RESTful API for external tools

## 📊 Sample Data

The system includes 5 sample fraud alerts:
- TXN999004: $50,000 (Score: 5.7) - Critical Risk
- TXN999002: $25,000 (Score: 4.1) - High Risk
- TXN999005: $12,500 (Score: 3.9) - High Risk
- TXN999001: $15,000 (Score: 3.2) - Moderate Risk
- TXN999003: $8,750 (Score: 2.8) - Moderate Risk

## 🚀 Deployment

### Using Terraform
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Using Python Scripts
```bash
python deploy-lambda-resources.py
python deploy-fraud-investigator.py
python insert-sample-fraud-alerts.py
```

## 📞 Support

For questions or issues:
1. Check AWS CloudWatch logs
2. Verify IAM permissions
3. Test API endpoints
4. Review DynamoDB data

## 🎯 Future Enhancements

- Real-time streaming with Kinesis
- Advanced ML models with SageMaker
- Dashboard with QuickSight
- Mobile app integration
- Multi-region deployment

---

**Built with ❤️ using AWS services and modern web technologies**