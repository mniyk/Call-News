import configparser
import json

from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_connect as connect,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_events as events,
    aws_iam as iam,
)
from constructs import Construct


config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")

config_default = config_ini["DEFAULT"]
config_gnews = config_ini["GNews"]


class CallNewsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # S3
        json_bucket = s3.Bucket(
            self, 
            "JsonBucket",
            removal_policy=RemovalPolicy.DESTROY,
        )

        mp3_bucket = s3.Bucket(
            self, 
            "Mp3Bucket",
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Lambda
        gnews_lambda = _lambda.Function(
            self, 
            "GNewsLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="gnews_lambda_function.handler",
            environment={
                "GNEWS_ENDPOINT": config_gnews["ENDPOINT"],
                "JSON_BUCKET": json_bucket.bucket_name,
            },
            timeout=Duration.seconds(30),
            code=_lambda.Code.from_asset("lambda"),
        )
        json_bucket.grant_put(gnews_lambda)

        polly_lambda = _lambda.Function(
            self, 
            "PollyLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="polly_lambda_function.handler",
            environment={
                "JSON_BUCKET": json_bucket.bucket_name,
                "MP3_BUCKET": mp3_bucket.bucket_name,
            },
            timeout=Duration.seconds(30),
            code=_lambda.Code.from_asset("lambda"),
        )
        polly_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["polly:SynthesizeSpeech"],
                resources=["*"],
            )
        )
        json_bucket.grant_read(polly_lambda)
        mp3_bucket.grant_put(polly_lambda)
