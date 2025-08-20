import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from S3
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="fraud_detection_db",
    table_name="transactions"
)

# Basic fraud detection logic
df = datasource.toDF()
fraud_df = df.filter(df.amount > 10000)  # Simple threshold-based detection

# Write results back to S3
glueContext.write_dynamic_frame.from_options(
    frame=DynamicFrame.fromDF(fraud_df, glueContext, "fraud_results"),
    connection_type="s3",
    connection_options={"path": "s3://your-bucket/fraud-results/"},
    format="parquet"
)

job.commit()