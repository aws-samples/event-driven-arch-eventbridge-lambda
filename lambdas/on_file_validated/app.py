from aws_lambda_powertools.logging.logger import Logger
import boto3
import os
from datetime import datetime

logger = Logger()
ddb = boto3.resource('dynamodb')
ddb_resource = boto3.resource('dynamodb')
_ddb_table_name = os.getenv("DDB_TABLE_NAME")


def handler(event, context):
    filename = event["detail"]["filename"]
    validationMessage = event["detail"]["validationMessage"]

    saveToDatabase(filename, validationMessage)

    logger.info({
        "message": "Received request to save event for file {} on database".format(filename)
    })


def saveToDatabase(filename, validationMessage):
    """
    Saves the record to the database
    """
    table = ddb_resource.Table(_ddb_table_name)
    status = "OK" if validationMessage is None else "NOT_OK"
    logger.info({
        "message": "Saving record on ddb for file {} with status {}".format(filename, status),
        "validationMessage": validationMessage
    })
    response= table.put_item(
        Item={
            'filename': filename,
            'status': status,
            'datetime': datetime.utcnow().isoformat(),
            'validation_error': validationMessage
            }
    )

    logger.debug({
        "message": "Return from DDB",
        "ddb_return": response
    })