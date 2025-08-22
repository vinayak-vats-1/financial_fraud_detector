import boto3

glue = boto3.client('glue')

response = glue.start_job_run(JobName='clean-transactions-job')
job_run_id = response['JobRunId']

print(f"Started Glue job run: {job_run_id}")
print("Check job status in AWS Glue console")