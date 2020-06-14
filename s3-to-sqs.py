import csv
import json
import logging
import time
import os
import boto3

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_end_point = 'http://%s:4566' % os.environ['LOCALSTACK_HOSTNAME']
sqs_end_point = 'http://%s:4566' % os.environ['LOCALSTACK_HOSTNAME']
processing_queue_url = sqs_end_point + "/queue/sms_queue"


def push_records_to_sqs(messages):
    sqs = boto3.client('sqs', endpoint_url=sqs_end_point, region_name='us-east-1')
    try:
        response = sqs.send_message_batch(
            QueueUrl=processing_queue_url,
            Entries=messages
        )
        logger.info("response: {} ".format(response))
        if 'Failed' in response:
            logger.error('failed_count: {}'.format(len(response['Failed'])))
    except Exception as e:
        logger.error("error while pushing data to sqs : {}".format(e))


def csv_data_to_records(resp):
    if resp[-1] == '':
        # removing header metadata and extra newline
        total_records = len(resp) - 2
    else:
        # removing header metadata
        total_records = len(resp) - 1
    logger.info("total record count {} :".format(total_records))
    batch_size = 0
    record_count = 0
    # Write to SQS
    for row in csv.DictReader(resp):
        messages = []
        record_count += 1
        record = {}
        for k, v in row.items():
            record[k] = v
        logger.info(record)
        # mobile number column with values as unique
        unique_id = record['mobile_number']
        batch_size += 1
        messages.append(
            {
                'Id': unique_id,
                'MessageBody': json.dumps(record)
            })
        if batch_size == 10:
            batch_size = 0
            push_records_to_sqs(messages)
            messages = []

        # Handling last batch
        if record_count == total_records:
            push_records_to_sqs(messages)


def lambda_handler(event, context):
    logger.info('Start in.......')
    s3 = boto3.resource('s3', endpoint_url=s3_end_point, region_name='us-east-1')
    logger.info('event object : {}'.format(event))
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = str(event['Records'][0]['s3']['object']['key'])
    logger.info('key : {}'.format(key))
    logger.info('bucket_name : {}'.format(bucket_name))
    try:
        bucket_object = s3.Bucket(str(bucket_name))
        file_object = bucket_object.Object(key=key).get()
        file_content = file_object['Body'].read().decode('utf-8')
        logger.info(file_content)
        sms_data = file_content.split('\n')
        resp = list(sms_data)
        start_time = time.time()
        csv_data_to_records(resp)
        logger.info('That took {} seconds'.format(time.time() - start_time))
    except Exception as e:
        logger.error('error while reading data from s3 : {}'.format(e))
        raise e
