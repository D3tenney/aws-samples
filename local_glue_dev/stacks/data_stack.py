from codecs import Codec
from logging import captureWarnings
from os import remove
from aws_cdk import (
    Aws,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as events,
    aws_events_targets as event_targets,
    aws_iam as iam,
    aws_glue as glue,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
)
from constructs import Construct

class DataStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        raw_bucket = s3.Bucket(self, "RawBucket",
            removal_policy=RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.S3_MANAGED,
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        raw_data_prefix = "fares"

        wrangler_layer = lambda_.LayerVersion.from_layer_version_arn(self, "WranglerLayer",
            layer_version_arn=f"arn:aws:lambda:{Aws.REGION}:336392948345:layer:AWSDataWrangler-Python39-Arm64:1"
        )

        data_generator = lambda_.Function(self, "DataGenerator",
            runtime=lambda_.Runtime.PYTHON_3_9,
            architecture=lambda_.Architecture.ARM_64,
            timeout=Duration.seconds(10),
            memory_size=256,
            code=lambda_.AssetCode("lambdas/data_generator"),
            handler="lambda_function.event_handler",
            environment={
                "RAW_BUCKET": raw_bucket.bucket_name,
                "RAW_PREFIX": raw_data_prefix
            },
            layers=[
                wrangler_layer
            ]
        )
        data_generator.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                    "s3:PutLifecycleConfiguration"
                ],
                resources=[
                    raw_bucket.bucket_arn,
                    f"{raw_bucket.bucket_arn}/*"
                ]
            )
        )

        # data_generator_trigger = events.Rule(self, "DataGeneratorTrigger",
        #     enabled=True,
        #     rule_name="Cron Lambda Trigger",
        #     schedule=events.Schedule.expression("rate(2 minutes)")
        # )
        # data_generator_trigger.add_target(
        #     event_targets.LambdaFunction(data_generator)
        # )

        curated_bucket = s3.Bucket(self, "CuratedBucket",
            removal_policy=RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.S3_MANAGED,
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        script_bucket = s3.Bucket(self, "ScriptBucket",
            removal_policy=RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.S3_MANAGED,
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )
        script_deploy = s3_deployment.BucketDeployment(self, "ScriptDeployment",
            destination_bucket=script_bucket,
            sources=[s3_deployment.Source.asset("glue_jobs/")]
        )

        glue_role = iam.Role(self, "GlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            inline_policies={
                "ScriptDataRead": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:ListBucket",
                                "s3:GetBucketLocation",
                                "s3:GetObjectVersion",
                                "s3:GetLifecycleConfiguration"
                            ],
                            resources=[
                                script_bucket.bucket_arn,
                                f"{script_bucket.bucket_arn}/*",
                                raw_bucket.bucket_arn,
                                f"{raw_bucket.bucket_arn}/*"
                            ]
                        )
                    ]
                ),
                "DataWrite": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:PutObject",
                                "s3:PutObjectAcl",
                                "s3:PutLifecycleConfiguration"
                            ],
                            resources=[
                                curated_bucket.bucket_arn,
                                f"{curated_bucket.bucket_arn}/*"
                            ]
                        )
                    ]
                )
            }
        )

        # TODO: Scheduler
        glue_job = glue.CfnJob(self, "GlueJob",
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=f"s3://{script_bucket.bucket_name}/glue_jobs/job.py"
            ),
            role=glue_role.role_arn,
            default_arguments={
                "--RAW_BUCKET": raw_bucket.bucket_name,
                "--RAW_PREFIX": raw_data_prefix,
                "--CURATED_BUCKET": curated_bucket.bucket_name,
                "--CURATED_PREFIX": raw_data_prefix,
                "--job-bookmark-option": "job-bookmark-enable"
            },
            glue_version="3.0",
            worker_type="G.1X",
            number_of_workers=2, # min 2
            max_retries=0,
            timeout=2
        )

        CfnOutput(self, "RawBucketName", value=raw_bucket.bucket_name)
        CfnOutput(self, "CuratedBucketName", value=curated_bucket.bucket_name)
