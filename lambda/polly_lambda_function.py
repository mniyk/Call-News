import boto3
from datetime import datetime
import json
import os


# 定数の設定
JSON_BUCKET = os.environ["JSON_BUCKET"]
MP3_BUCKET = os.environ["MP3_BUCKET"]


def handler(event, context):
    result = {}

    polly_client = boto3.client("polly")
    s3_client = boto3.client("s3")

    try:
        timestamp = datetime.now().strftime("%Y%m%d")

        # S3から読込
        json_file_name = f"{timestamp}.json"
        obj_data = s3_client.get_object(Bucket=JSON_BUCKET, Key=json_file_name)

        # ファイルの内容を取得
        json_data = json.loads(obj_data["Body"].read().decode("utf-8"))

        # SSMLの組立
        ssml_text = f"""<speak>
            {datetime.now().strftime('%m月%d日')}のニュースです
            <break time="500ms"/>
        """
        for i, article in enumerate(json_data["articles"]):
            ssml_text += article["title"]

            if i + 1 < len(json_data["articles"]):
                ssml_text += '<break time="2s"/>'
            else:
                ssml_text += '<break time="500ms"/>以上です'
        
        ssml_text += "</speak>"

        # Pollyで音声を生成
        response = polly_client.synthesize_speech(
            Text=ssml_text,
            OutputFormat='mp3',
            VoiceId='Mizuki',
            TextType='ssml',
        )

        # S3に保存
        audio_stream = response["AudioStream"].read()
        mp3_file_name = f"{timestamp}.mp3"
        s3_client.put_object(
            Bucket=MP3_BUCKET,
            Key=mp3_file_name,
            Body=audio_stream,
            ContentType="audio/mpeg",
        )

        s3_url = f"https://{MP3_BUCKET}.s3.ap-northeast-1.amazonaws.com/{mp3_file_name}"

        result = {
            "statusCode": 200, 
            "body": json.dumps({
                "message": "Success",
                "data": {"url": s3_url},
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    except Exception as e:
        result = {
            "statusCode": 500, 
            "body": json.dumps({
                "message": str(e),
                "data": {"url": ""},
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    return result
