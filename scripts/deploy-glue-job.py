import boto3
import json

# Create IAM role
iam = boto3.client('iam')
glue = boto3.client('glue')

role_name = 'GlueJobRole'
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "glue.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    ]
}

s3_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
            "Resource": [
                "arn:aws:s3:::my-secure-bucket-wxj077wp",
                "arn:aws:s3:::my-secure-bucket-wxj077wp/*"
            ]
        }
    ]
}

try:
    # Create IAM role
    iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy)
    )
    print(f"Created IAM role: {role_name}")
except iam.exceptions.EntityAlreadyExistsException:
    print(f"IAM role {role_name} already exists")

# Attach policies
iam.attach_role_policy(
    RoleName=role_name,
    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole'
)

iam.put_role_policy(
    RoleName=role_name,
    PolicyName='GlueS3Policy',
    PolicyDocument=json.dumps(s3_policy)
)

# Get role ARN
role_arn = iam.get_role(RoleName=role_name)['Role']['Arn']

# Create Glue job
try:
    glue.create_job(
        Name='clean-transactions-job',
        Role=role_arn,
        Command={
            'Name': 'glueetl',
            'ScriptLocation': 's3://my-secure-bucket-wxj077wp/scripts/clean-transactions.py',
            'PythonVersion': '3'
        },
        DefaultArguments={
            '--job-language': 'python',
            '--job-bookmark-option': 'job-bookmark-disable',
            '--INPUT_PATH': 's3://my-secure-bucket-wxj077wp/input/transactions.csv',
            '--OUTPUT_PATH': 's3://my-secure-bucket-wxj077wp/cleaned/'
        },
        GlueVersion='4.0',
        MaxRetries=0,
        Timeout=60,
        WorkerType='G.1X',
        NumberOfWorkers=2
    )
    print("Created Glue job: clean-transactions-job")
except glue.exceptions.AlreadyExistsException:
    print("Glue job already exists")

print("Glue job deployed successfully!")