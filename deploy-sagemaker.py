import boto3
import json
import time

sagemaker = boto3.client('sagemaker')
iam = boto3.client('iam')

# Create SageMaker IAM role
role_name = 'SageMakerFraudDetectionRole'
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "sagemaker.amazonaws.com"},
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
    PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
)

iam.put_role_policy(
    RoleName=role_name,
    PolicyName='SageMakerS3Policy',
    PolicyDocument=json.dumps(s3_policy)
)

role_arn = iam.get_role(RoleName=role_name)['Role']['Arn']
print(f"Role ARN: {role_arn}")

# Wait for role to propagate
time.sleep(10)

# Create training job
training_job_name = 'fraud-detection-rcf-training'
try:
    response = sagemaker.create_training_job(
        TrainingJobName=training_job_name,
        RoleArn=role_arn,
        AlgorithmSpecification={
            'TrainingImage': '382416733822.dkr.ecr.us-east-1.amazonaws.com/randomcutforest:1',
            'TrainingInputMode': 'File'
        },
        InputDataConfig=[
            {
                'ChannelName': 'training',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': 's3://my-secure-bucket-wxj077wp/cleaned/',
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                },
                'ContentType': 'text/csv'
            }
        ],
        OutputDataConfig={
            'S3OutputPath': 's3://my-secure-bucket-wxj077wp/models/'
        },
        ResourceConfig={
            'InstanceType': 'ml.m5.large',
            'InstanceCount': 1,
            'VolumeSizeInGB': 30
        },
        StoppingCondition={
            'MaxRuntimeInSeconds': 3600
        },
        HyperParameters={
            'feature_dim': '6',
            'num_trees': '100',
            'num_samples_per_tree': '256'
        }
    )
    print(f"Started training job: {training_job_name}")
    
    # Wait for training to complete
    print("Waiting for training to complete...")
    waiter = sagemaker.get_waiter('training_job_completed_or_stopped')
    waiter.wait(TrainingJobName=training_job_name)
    
    # Get training job details
    training_job = sagemaker.describe_training_job(TrainingJobName=training_job_name)
    model_artifacts = training_job['ModelArtifacts']['S3ModelArtifacts']
    print(f"Training completed. Model artifacts: {model_artifacts}")
    
    # Create model
    model_name = 'fraud-detection-rcf-model'
    sagemaker.create_model(
        ModelName=model_name,
        PrimaryContainer={
            'Image': '382416733822.dkr.ecr.us-east-1.amazonaws.com/randomcutforest:1',
            'ModelDataUrl': model_artifacts
        },
        ExecutionRoleArn=role_arn
    )
    print(f"Created model: {model_name}")
    
    # Create batch transform job
    transform_job_name = 'fraud-detection-batch-transform'
    sagemaker.create_transform_job(
        TransformJobName=transform_job_name,
        ModelName=model_name,
        MaxConcurrentTransforms=1,
        MaxPayloadInMB=6,
        TransformInput={
            'DataSource': {
                'S3DataSource': {
                    'S3DataType': 'S3Prefix',
                    'S3Uri': 's3://my-secure-bucket-wxj077wp/cleaned/'
                }
            },
            'ContentType': 'text/csv'
        },
        TransformOutput={
            'S3OutputPath': 's3://my-secure-bucket-wxj077wp/scored/'
        },
        TransformResources={
            'InstanceType': 'ml.m5.large',
            'InstanceCount': 1
        }
    )
    print(f"Started batch transform job: {transform_job_name}")
    
except Exception as e:
    print(f"Error: {e}")

print("SageMaker pipeline deployed successfully!")