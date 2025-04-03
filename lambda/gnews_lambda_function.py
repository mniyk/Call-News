import boto3
from datetime import datetime
import json
import os
import urllib.request


# 定数の設定
GNEWS_ENDPOINT = os.environ["GNEWS_ENDPOINT"]
JSON_BUCKET = os.environ["JSON_BUCKET"]


def handler(event, context):
    result = {}

    s3_client = boto3.client("s3")

    try:
        # APIにリクエスト
        with urllib.request.urlopen(GNEWS_ENDPOINT) as response:
            if response.status == 200:
                data = response.read().decode("utf-8")

                try:
                    json.loads(data)
                except json.JSONDecodeError:
                    result = {"statusCode": 500, "body": "Failure"}
                else:
                    file_name = f"{datetime.now().strftime('%Y%m%d')}.json"

                    # S3に保存
                    s3_client.put_object(
                        Bucket=JSON_BUCKET,
                        Key=file_name,
                        Body=data,
                        ContentType="application/json",
                    )

                    result = {"statusCode": 200, "body": "Success"}
            else:
                result = {"statusCode": response.status, "body": "Failure"}
    except Exception as e:
        result = {"statusCode": 500, "body": str(e)}

    return result
