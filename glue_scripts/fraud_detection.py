import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'bucket-name'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

bucket_name = args['bucket_name']

# Read transactions data
df = spark.read.option("header", "true").csv(f"s3://{bucket_name}/input/transactions.csv")

# Basic fraud detection logic
fraud_df = df.withColumn("is_fraud", 
    when((col("amount") > 1500) | (col("country") != "US"), 1).otherwise(0)
)

# Write results
fraud_df.write.mode("overwrite").option("header", "true").csv(f"s3://{bucket_name}/output/fraud_results/")

job.commit()