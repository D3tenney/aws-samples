import awswrangler as wr
from datetime import datetime, timedelta
from os import environ
import pandas as pd
import random

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

RAW_BUCKET = environ.get("RAW_BUCKET")
RAW_PREFIX = environ.get("RAW_PREFIX")


def event_handler(event, context):
    """Creates fake taxi data, writes to s3"""
    n = random.randint(100, 500)

    logger.info(f"{n} records")

    batch_timestamp = datetime.utcnow()

    data_list = []
    for _ in range(0, n):
        fare_start_odometer = random.randint(42000, 200000)
        fare_end_odometer = fare_start_odometer + random.randint(1, 42)
        fare_start_time = batch_timestamp - timedelta(minutes=random.randint(3, 42))
        fare_end_time = batch_timestamp - timedelta(seconds=random.randint(0, 60))
        driver_id = f"{random.randint(0, 10000):05}"
        fare = {
            "driver_id": driver_id,
            "fare_start_odometer": fare_start_odometer,
            "fare_end_odometer": fare_end_odometer,
            "fare_start_time": fare_start_time,
            "fare_end_time": fare_end_time,
            "processed_time": batch_timestamp
        }

        data_list.append(fare)

    df = pd.DataFrame(data_list)

    file_name = f"{str(batch_timestamp).replace(' ', '_').replace(':', '_').replace('-', '_').replace('.', '_')}.parquet"
    file_key = f"s3://{RAW_BUCKET}/{RAW_PREFIX}/{batch_timestamp.year}/{batch_timestamp.month}/{batch_timestamp.day}/{batch_timestamp.hour}/{file_name}"
    wr.s3.to_parquet(
        df=df,
        path=file_key,
        dataset=False
    )
    logger.info(f"{file_key} written successfully")