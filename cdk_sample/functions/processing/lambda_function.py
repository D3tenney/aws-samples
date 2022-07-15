import boto3
import json
from os import environ

DYNAMO_TABLE = environ.get("DYNAMO_TABLE")

dynamo_client = boto3.client("dynamodb")
s3_client = boto3.client("s3")


def event_handler(event, context):
    record = event["Records"][0]

    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    data = json.loads(s3_client.get_object(Bucket=bucket, Key=key)["Body"].read())

    response = dynamo_client.update_item(
        TableName=DYNAMO_TABLE,
        Key={
            "id": {
                "S": data["id"],
            }
        },
        AttributeUpdates={
            "name": {
                "Value": {
                    "S": data["name"],
                },
            }
        },
    )
