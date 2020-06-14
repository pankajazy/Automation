Architecture.
![alt text](s3-to-sqs.png)
# AWS CLIs

#s3

// create s3 bucket : <br>
aws s3 mb s3://smsbucket --endpoint-url http://localhost:4566

// list s3 bucket : <br>
aws  --endpoint-url http://localhost:4566 s3 ls

// upload a file to s3 : <br>
aws s3 cp sms.csv s3://smsbucket/sms.csv --endpoint-url http://localhost:4566

// s3 put trigger notification : <br>
aws s3api put-bucket-notification-configuration --bucket smsbucket --notification-configuration file://notification.json --endpoint-url http://localhost:4566

--------------------------------------------------------------------------------------------------------------------------

#lambda

// create lambda : <br>
aws lambda --endpoint-url=http://localhost:4566 \
         create-function --function-name=hellolambda \
         --runtime=python2.7 \
         --role=whatever \
         --zip-file fileb:///Users/b0205391/PycharmProjects/LearnLocalStack/s3-to-sqs.py.zip \
         --handler=s3-to-sqs.lambda_handler

// delete lambda functions : <br>
aws lambda --endpoint-url=http://localhost:4566 delete-function --function-name=hellolambda

// invoke lambda : <br>
aws lambda --endpoint-url=http://localhost:4566 invoke --function-name hellolambda dd

// list lambda functions :<br>
aws lambda --endpoint-url=http://localhost:4566 list-functions

--------------------------------------------------------------------------------------------------------------------------

#SQS

// create sqs : <br>
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name sms_queue

// send msg to sqs : <br>
aws --endpoint-url=http://localhost:4566 sqs send-message --queue-url http://localhost:4566/queue/smsqueue --message-body 
'Test Message!'

// retrieve msg from sqs : <br>
aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url http://localhost:4566/queue/sms_queue
