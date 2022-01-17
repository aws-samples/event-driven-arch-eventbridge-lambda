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
        return None
    
    generateEvent(jsonPayload)

def convertFromXmlToJson(bucket, key):
    fileContent = s3.Object(bucket, key).get()['Body'].read().decode('utf-8')
    try:
        jsonContent = xmltodict.parse(fileContent)
        jsonContent.update({"filename": key})
        return json.dumps(jsonContent)
    except Exception as e: 
        logger.error({
            "message": "Error converting file {} on bucket{}".format(key, bucket),
            "file": key,
            }, 
            exc_info=True)
        # in case of errors, we send the content a little bit more strucuted 
        # in order to help on further steps
        payload = json.dumps({
            "filename": key,
            "exception": str(e),
            "fileContent": str(fileContent)
        })
        generateEvent(payload, status="file-converted-error")
        return None

def generateEvent(payload, status="file-converted"):
    logger.info({
        "message": "Sending event {}".format(status),
        "payload": payload
    })
    event = {
        "Time": datetime.datetime.now(),
        "Source": "NFProcessor.file_receiver",
        "DetailType": status,
        "Detail": payload
    }
    logger.debug({
        "message": "event final payload",
        "payload": payload
        })

    eventBridgePutReturn = eventBridge.put_events(Entries = [event])
    logger.debug({
        "message": "Event Bridge PUT return",
        "eventBridgePutReturn": eventBridgePutReturn
        })