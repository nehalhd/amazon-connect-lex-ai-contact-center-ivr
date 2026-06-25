
import os
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo
 
polly = boto3.client("polly")
s3 = boto3.client("s3")
 
BUCKET_NAME = os.environ.get("AUDIO_BUCKET", "techmart-ivr-prompts")
LOCAL_TZ = os.environ.get("GREETING_TIMEZONE", "Africa/Cairo")
 
 
def lambda_handler(event, context):
    hour = datetime.now(ZoneInfo(LOCAL_TZ)).hour
 
    if 5 <= hour < 12:
        time_of_day = "Good morning"
    elif 12 <= hour < 18:
        time_of_day = "Good afternoon"
    else:
        time_of_day = "Good evening"
 
    text = f"{time_of_day}, and thank you for calling TechMart customer service."
 
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId="Joanna",
        Engine="neural",
    )
 
    key = f"prompts/greeting-{hour}.mp3"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=response["AudioStream"].read(),
        ContentType="audio/mpeg",
    )
 
    return {
        "AudioS3Uri": f"s3://{BUCKET_NAME}/{key}",
        "GreetingText": text,
    }
 