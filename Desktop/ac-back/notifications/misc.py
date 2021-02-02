from itcs import settings

import boto3


client = boto3.client(
    service_name='sns',
    aws_access_key_id=settings.AWS_SNS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SNS_SECRET_KEY,
    region_name='eu-central-1',
)