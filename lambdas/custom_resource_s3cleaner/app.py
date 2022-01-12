import boto3
import logging
from crhelper import CfnResource

logger = logging.getLogger(__name__)
# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

try:
    s3 = boto3.resource('s3')
    pass
except Exception as e:
    helper.init_failure(e)


@helper.delete
def delete(event, context):
    logger.info("Emptying buckets")
    fileReceiverBucketName = event["ResourceProperties"]["FileReceiverBucketName"]
    EBTrailBucketName = event["ResourceProperties"]["EBTrailBucketName"]
    emptyBucket(fileReceiverBucketName)
    emptyBucket(EBTrailBucketName)
    

def handler(event, context):
    helper(event, context)

def emptyBucket(bucketName):
    bucket = s3.Bucket(bucketName)
    bucket.objects.all().delete()
