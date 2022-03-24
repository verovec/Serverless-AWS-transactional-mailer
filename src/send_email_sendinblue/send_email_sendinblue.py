
from __future__ import print_function
import time
import os
from pprint import pprint
import json
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import boto3


sqs = boto3.client('sqs')

SENDINBLUE_API_KEY = os.environ.get('SENDINBLUE_API_KEY', None)
QUEUE_URL = os.environ.get('QUEUE_URL', None)

def lambda_handler(event, context):
    record = event["Records"][0]
    receipt_handle = record['receiptHandle']
    body = json.loads(record["body"])

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[body["user"]],
        template_id=body["template_id"],
        params=body["params"],
        headers={
            "api-key": SENDINBLUE_API_KEY,
            "content-type": "application/json",
            "accept": "application/json",
            "charset": "iso-8859-1"
        }
    )

    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        raise e
