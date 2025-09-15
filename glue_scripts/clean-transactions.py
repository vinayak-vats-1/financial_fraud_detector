import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, hour, to_timestamp
from pyspark.sql.types import DoubleType

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'INPUT_PATH', 'OUTPUT_PATH'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read CSV file
df = spark.read.option("header", "true").csv(args['INPUT_PATH'])

# Drop rows with null or malformed values
df_clean = df.dropna()

# Cast amount column to Double
df_clean = df_clean.withColumn("amount", col("amount").cast(DoubleType()))

# Extract transaction_hour from timestamp
df_clean = df_clean.withColumn("timestamp", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss"))
df_clean = df_clean.withColumn("transaction_hour", hour(col("timestamp")))

# Write cleaned dataset in parquet format
df_clean.write.mode("overwrite").parquet(args['OUTPUT_PATH'])

job.commit()