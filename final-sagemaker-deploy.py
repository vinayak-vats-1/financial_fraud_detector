import boto3

sagemaker = boto3.client('sagemaker')
role_arn = 'arn:aws:iam::214617963177:role/SageMakerFraudDetectionRole'

# Final corrected training job
training_job_name = 'fraud-detection-rcf-final'

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
                'ChannelName': 'train',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': 's3://my-secure-bucket-wxj077wp/rcf-input/',
                        'S3DataDistributionType': 'ShardedByS3Key'
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
            'feature_dim': '4',
            'num_trees': '50',
            'num_samples_per_tree': '200'
        }
    )
    print(f"Started training job: {training_job_name}")
    print("Training in progress... Check AWS SageMaker console for status")
    print("Once training completes, run batch transform job manually")
    
except Exception as e:
    print(f"Error: {e}")

print("\nInfrastructure Summary:")
print("S3 bucket: my-secure-bucket-wxj077wp")
print("Glue job: clean-transactions-job")
print("SageMaker role: SageMakerFraudDetectionRole")
print("Training data: s3://my-secure-bucket-wxj077wp/rcf-input/")
print("Model output: s3://my-secure-bucket-wxj077wp/models/")
print("Scored output: s3://my-secure-bucket-wxj077wp/scored/")