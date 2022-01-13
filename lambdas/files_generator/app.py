from aws_lambda_powertools.logging.logger import Logger
from datetime import datetime
import time
import os
import boto3
import random
import json


logger = Logger()
s3 = boto3.resource('s3')
_incorrect_factor = 0.20

def handler(event, context):
    bucket = os.getenv("DESTINATION_BUCKET")
    numberOfFiles = int(event["queryStringParameters"]['numberOfFiles'])

    logger.info({
        "message": "Starting to generate {} files on bucket{}".format(numberOfFiles, bucket)
    })

    generateFiles(bucket, numberOfFiles)

    logger.info({
        "message": "Finished to generate files"
    })

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Generated {} files correctly AND {} with incorrect format".format(numberOfFiles, round(numberOfFiles*_incorrect_factor))}),
        "headers": {
            "Content-Type": "application/json"
        }
    }
    
def generateFiles(bucket, numberOfFiles):
    xmlTemplate = """<nf>
                <tpAmb>2</tpAmb>
                <tpTransm>N</tpTransm>
                <dhTransm>{}</dhTransm>
                <infLeitura>
                <cUF>11</cUF>
                <dhPass>2021-07-23T21:14:00-03:00</dhPass>
                <CNPJOper>76500680000174</CNPJOper>
                <cEQP>012345678901234</cEQP>
                <latitude>1.970942</latitude>
                <longitude>6.680008</longitude>
                <tpSentido>E</tpSentido>
                <placa>{}</placa>
                <tpVeiculo>3</tpVeiculo>
                <velocidade>120</velocidade>
                <foto>cXVhZXF1YWVxdWFlcXVhZQ==</foto>
                <indiceConfianca>95</indiceConfianca>
                <pesoBrutoTotal>120</pesoBrutoTotal>
                <nroEixos>3</nroEixos>
                </infLeitura>
            </nf>"""
    
    #Generating WELL-FORMED files
    for x in range(numberOfFiles):
        logger.debug({
            "message": "Generating file {} out of {}".format(x, numberOfFiles)
        })
        isValid = bool(random.getrandbits(1))
        placa = "AWS2022" if isValid else "AWS20222"
        timeNow = datetime.now()
        xmlBody = xmlTemplate.format(timeNow, placa).encode("utf-8")
        key = "nf-{}.xml".format(time.time())
        s3.Bucket(bucket).put_object(Key=key, Body=xmlBody)

    #Generating BAD-FORMED files(20%)
    for x in range(round(numberOfFiles * _incorrect_factor)):
        logger.debug({
            "message": "Generating bad-formated file {} out of {}".format(x, numberOfFiles)
        })
        placa = "AWS2022"
        timeNow = datetime.now()
        xmlBody = xmlTemplate.format(timeNow, placa).encode("utf-8").replace("</infLeitura>", "")
        key = "invalid-nf-{}.xml".format(time.time())
        s3.Bucket(bucket).put_object(Key=key, Body=xmlBody)