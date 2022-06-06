# https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-libraries.html

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
import pyspark.sql.functions as F
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
job_arguments = [
    "JOB_NAME",
    "RAW_BUCKET",
    "RAW_PREFIX",
    "CURATED_BUCKET",
    "CURATED_PREFIX"
]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# # test args
# args = {
#     "JOB_NAME": "data_job",
#     "RAW_BUCKET": "datastack-rawbucket0c3ee094-hxvl1j46clt",
#     "RAW_PREFIX": "fares",
#     "CURATED_BUCKET": "datastack-curatedbucket6a59c97e-1c5cyp5xhng19",
#     "CURATED_PREFIX": "fares"
# }

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


raw_dyf = glueContext.create_data_frame_from_options(
    connection_type="s3",
    connection_options={
        "paths": [f"s3://{RAW_BUCKET}/{RAW_PREFIX}/"]
    },
    format="parquet",
    transformation_ctx="raw_dyf"
)


sink = glueContext.write_dynamic_frame_from_options(
    connection_type="s3",
    connection_options={
        "path": f"s3://{CURATED_BUCKET}/{CURATED_PREFIX}/"
    }
)
job.commit()