from aws_lambda_powertools.logging.logger import Logger
import json
import boto3
import datetime

logger = Logger()
s3 = boto3.resource('s3')
eventBridge = boto3.client("events")

def handler(event, context):
    fileName = event["detail"]["filename"]
    fileContent = event["detail"]

    logger.info({
        "message": "Received event for file {}".format(fileName),
        "fileContent": fileContent
    })
