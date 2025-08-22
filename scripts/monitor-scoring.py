import boto3
import time
from datetime import datetime

def check_scoring_status():
    sagemaker = boto3.client('sagemaker')
    s3 = boto3.client('s3')
    bucket = 'my-secure-bucket-wxj077wp'
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring SageMaker jobs and S3 scored files...")
    
    # Check training job status
    try:
        training_response = sagemaker.describe_training_job(TrainingJobName='fraud-detection-rcf-final')
        training_status = training_response['TrainingJobStatus']
        print(f"Training Job Status: {training_status}")
        
        if training_status == 'Completed':
            model_artifacts = training_response['ModelArtifacts']['S3ModelArtifacts']
            print(f"Model artifacts available: {model_artifacts}")
            
            # Check if batch transform job exists and its status
            try:
                transform_jobs = sagemaker.list_transform_jobs(
                    NameContains='fraud-detection',
                    StatusEquals='InProgress'
                )
                
                if transform_jobs['TransformJobSummaries']:
                    job_name = transform_jobs['TransformJobSummaries'][0]['TransformJobName']
                    transform_response = sagemaker.describe_transform_job(TransformJobName=job_name)
                    transform_status = transform_response['TransformJobStatus']
                    print(f"Batch Transform Status: {transform_status}")
                    
                    if transform_status == 'Completed':
                        print("✅ Batch transform completed! Checking for scored files...")
                        return check_scored_files(s3, bucket)
                else:
                    print("No active batch transform jobs found")
                    
            except Exception as e:
                print(f"Transform job check error: {e}")
                
        elif training_status == 'Failed':
            failure_reason = training_response.get('FailureReason', 'Unknown')
            print(f"❌ Training failed: {failure_reason}")
            return False
            
    except Exception as e:
        print(f"Training job check error: {e}")
    
    return False

def check_scored_files(s3, bucket):
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix='scored/')
        
        if 'Contents' in response:
            scored_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.out')]
            
            if scored_files:
                print("🎉 SCORED FILES READY!")
                print("📁 Files found in s3://my-secure-bucket-wxj077wp/scored/:")
                for file in scored_files:
                    file_info = s3.head_object(Bucket=bucket, Key=file)
                    size = file_info['ContentLength']
                    modified = file_info['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                    print(f"  - {file} ({size} bytes, modified: {modified})")
                
                # Download and preview first few lines
                if scored_files:
                    preview_file(s3, bucket, scored_files[0])
                
                return True
            else:
                print("Scored folder exists but no .out files found yet")
        else:
            print("No files in scored/ folder yet")
            
    except Exception as e:
        print(f"S3 check error: {e}")
    
    return False

def preview_file(s3, bucket, key):
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        content = obj['Body'].read().decode('utf-8')
        lines = content.strip().split('\n')
        
        print(f"\n📊 Preview of {key} (first 5 lines):")
        for i, line in enumerate(lines[:5]):
            print(f"  {i+1}: {line}")
        
        if len(lines) > 5:
            print(f"  ... and {len(lines)-5} more lines")
            
    except Exception as e:
        print(f"Preview error: {e}")

if __name__ == "__main__":
    max_checks = 60  # Check for 30 minutes
    check_interval = 30  # Check every 30 seconds
    
    for i in range(max_checks):
        if check_scoring_status():
            break
        
        if i < max_checks - 1:
            print(f"Waiting {check_interval} seconds before next check...\n")
            time.sleep(check_interval)
    else:
        print("⏰ Monitoring timeout reached. Check AWS console for status.")