import boto3

sagemaker = boto3.client('sagemaker')

try:
    response = sagemaker.describe_training_job(TrainingJobName='fraud-detection-rcf-training-v2')
    print(f"Training Job Status: {response['TrainingJobStatus']}")
    if 'FailureReason' in response:
        print(f"Failure Reason: {response['FailureReason']}")
    print(f"Training Image: {response['AlgorithmSpecification']['TrainingImage']}")
except Exception as e:
    print(f"Error: {e}")