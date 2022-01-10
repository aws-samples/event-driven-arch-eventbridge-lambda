from aws_lambda_powertools.logging.logger import Logger
import json
import boto3

logger = Logger()
eventBridge = boto3.client("events")

def handler(event, context):
    fileName = event["detail"]["filename"]
    fileContent = event["detail"]

    logger.info({
        "message": "Received event for file {}".format(fileName),
        "fileContent": fileContent
    })

    #TODO: validate on lambda(port simulator to here)
