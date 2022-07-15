from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
)
from constructs import Construct


class CdkSampleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_bucket = s3.Bucket(
            self,
            "SourceBucket",
            removal_policy=RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.S3_MANAGED,
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )
        CfnOutput(self, "SourceBucketName", value=source_bucket.bucket_name)

        dynamo_table = dynamodb.Table(
            self,
            "CharacterTable",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
        )

        processing_function = lambda_.Function(
            self,
            "ProcessingLambda",
            architecture=lambda_.Architecture.ARM_64,
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(2),
            code=lambda_.AssetCode.from_asset("functions/processing/"),
            handler="lambda_function.event_handler",
            environment={"DYNAMO_TABLE": dynamo_table.table_name},
        )
        processing_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:ListBucket", "s3:GetObject"],
                resources=[
                    source_bucket.bucket_arn,
                    source_bucket.arn_for_objects("*"),
                ],
            )
        )
        processing_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["dynamodb:PutItem", "dynamodb:UpdateItem"],
                resources=[dynamo_table.table_arn],
            )
        )
        source_bucket.add_event_notification(
            event=s3.EventType.OBJECT_CREATED,
            dest=s3_notifications.LambdaDestination(processing_function),
        )
