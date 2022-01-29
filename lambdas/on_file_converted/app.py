from typing import Optional
from aws_lambda_powertools.logging.logger import Logger
import json
import boto3
import json
import datetime

logger = Logger()

def handler(event, context):
    filename = event["detail"]["filename"]
    fileContent = event["detail"]

    logger.info({
        "message": "Received event for file {}".format(filename),
        "fileContent": fileContent
    })

    validationMessage = validateContent(filename, fileContent)
    generateEvent(json.dumps({"filename": filename, "validationMessage": validationMessage}))  
    
def validateContent(filename, payload):
    """
        Validates the json payload
    """
    logger.debug({
        "message": "Performing file validation for file{}".format(filename)
    })

    if len(payload["nf"]["infLeitura"]["placa"]) != 7:
        logger.info({
            "message": "Field placa is invalid"
        })
        return "PLACA_INVALIDA"
    return None


def generateEvent(payload, status="file-validated"):
    eventBridge = boto3.client("events")
    logger.info({
        "message": "Sending event {}".format(status),
        "payload": payload
    })
    event = {
        "Time": datetime.datetime.now(),
        "Source": "NFProcessor.file_validator",
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