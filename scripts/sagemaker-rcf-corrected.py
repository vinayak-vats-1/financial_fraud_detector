import boto3
import time

sagemaker = boto3.client('sagemaker')

# Create new training job with corrected data
training_job_name = 'fraud-detection-rcf-training-v2'
role_arn = 'arn:aws:iam::214617963177:role/SageMakerFraudDetectionRole'

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
            'feature_dim': '4',
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
    
    if training_job['TrainingJobStatus'] == 'Completed':
        model_artifacts = training_job['ModelArtifacts']['S3ModelArtifacts']
        print(f"Training completed. Model artifacts: {model_artifacts}")
        
        # Create model
        model_name = 'fraud-detection-rcf-model-v2'
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
        transform_job_name = 'fraud-detection-batch-transform-v2'
        sagemaker.create_transform_job(
            TransformJobName=transform_job_name,
            ModelName=model_name,
            MaxConcurrentTransforms=1,
            MaxPayloadInMB=6,
            TransformInput={
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': 's3://my-secure-bucket-wxj077wp/rcf-input/'
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
        print("SageMaker pipeline completed successfully!")
        
    else:
        print(f"Training failed: {training_job.get('FailureReason', 'Unknown error')}")
        
except Exception as e:
    print(f"Error: {e}")