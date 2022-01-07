from aws_lambda_powertools.logging.logger import Logger
import json
import xmltodict
import boto3
import datetime

logger = Logger()
s3 = boto3.resource('s3')
eventBridge = boto3.client("events")

def handler(event, context):
    bucket = event["detail"]["bucket"]["name"]
    key = event["detail"]["object"]["key"]

    logger.debug({
        "message": "Starting to process file {} on bucket{}".format(key, bucket),
        "file": key
    })

    jsonPayload = convertFromXmlToJson(bucket, key)
    if jsonPayload is None:
        logger.warning({
            "message": "Skipping file {}. Check exception bellow".format(key, bucket),
            "file": key
        })
        return None
    
    print(generateEvent(jsonPayload))

def convertFromXmlToJson(bucket, key):
    fileContent = s3.Object(bucket, key).get()['Body'].read()
    try:
        jsonContent = xmltodict.parse(fileContent)
        return json.dumps(jsonContent)
    except: 
        logger.error({
            "message": "Error converting file {} on bucket{}".format(key, bucket),
            "file": key,
            }, 
            exc_info=True)
        return None

def generateEvent(payload):
    event = {
        "Time": datetime.datetime.now(),
        "Source": "nfprocessor.file_receiver",
        "detail": payload
    }
    return event