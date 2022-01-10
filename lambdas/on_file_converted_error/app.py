from aws_lambda_powertools.logging.logger import Logger
import boto3

logger = Logger()
eventBridge = boto3.client("events")

def handler(event, context):
    fileName = event["detail"]

    logger.info({
        "message": "Received error event for file {}".format(fileName),
    })

    #TODO: post to SQS