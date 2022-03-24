import boto3
import json
import os


QUEUE_URL = os.environ.get("QUEUE_URL", None)
if QUEUE_URL is None:
    raise TypeError("QUEUE_URL environment variable is None")

sqs = boto3.client('sqs')

message = {
    "template_id": 0,
    "user": {},
    "params": {}
}

sqs.send_message(
    QueueUrl=QUEUE_URL,
    DelaySeconds=0,
    MessageBody=(json.dumps(message))
)
