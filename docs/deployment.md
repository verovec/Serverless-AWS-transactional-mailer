# Deployment

Every command runs from the repository root. The AWS CLI must be configured
([aws configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)) on
`eu-west-1`, the region hard-coded in `serverless.yml`.

## 1. Create the cloud resources

- An SQS queue ([documentation](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_CreateQueue.html)).
  Note its URL and its ARN.
- An S3 bucket for the deployment packages ([documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html)).
- A Sendinblue (Brevo) account with a transactional email template
  ([documentation](https://help.brevo.com/hc/en-us/articles/360019787120)) and a v3 API key.

## 2. Store the secrets in SSM Parameter Store

```sh
aws ssm put-parameter --name API_KEY_SERVERLESS --value ${API_KEY_SERVERLESS} --type SecureString   # any value, unused API Gateway key
aws ssm put-parameter --name S3_BUCKET --value ${S3_BUCKET} --type SecureString                     # deployment bucket name
aws ssm put-parameter --name QUEUE_URL --value ${QUEUE_URL} --type SecureString                     # https://sqs.eu-west-1.amazonaws.com/<account>/<queue>
aws ssm put-parameter --name QUEUE_ARN --value ${QUEUE_ARN} --type SecureString                     # arn:aws:sqs:eu-west-1:<account>:<queue>
aws ssm put-parameter --name SENDINBLUE_API_KEY --value ${SENDINBLUE_API_KEY} --type SecureString   # Sendinblue v3 API key
```

## 3a. Deploy from your shell

```sh
npm install -g serverless                              # the Serverless Framework CLI (sls)
sls plugin install -n serverless-python-requirements   # writes package.json, ignored by git
sls deploy --verbose --conceal                         # --conceal hides the API key in the output
```

`serverless.yml` sets no `dockerizePip`, so `pip` runs on your machine: the pinned packages are
pure Python and work from any OS.

## 3b. Deploy from the Docker image

The image is a `node:17-alpine3.14` with Python 3, the framework and the plugin installed, and
`sls deploy --verbose --conceal` as its command. It needs AWS credentials at run time.

```sh
cp .env-example .env                                   # fill AWS_DEFAULT_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
docker build . -t serverless:node17-alpine3.14
docker run --env-file .env serverless:node17-alpine3.14
```

`.env` is not committed (`.gitignore`) and `.dockerignore` keeps `README.md`, `.env-example` and
`ressources/` out of the image.

## 4. Send a test message

```sh
python3 -m pip install boto3
QUEUE_URL=https://sqs.eu-west-1.amazonaws.com/<account>/<queue> python3 test/test_mailer.py
sls logs -f send_email --tail                          # the function logs the API response, or the ApiException
```

The test message has `template_id: 0` and an empty recipient, so Sendinblue rejects it; replace
the values in `test/test_mailer.py` with a real template id and `{"email": ..., "name": ...}` to
receive an email.

## 5. Clean up

```sh
sls remove                                             # deletes the stack: function, role, event source mapping, log group
aws ssm delete-parameter --name QUEUE_URL              # repeat for QUEUE_ARN, S3_BUCKET, SENDINBLUE_API_KEY, API_KEY_SERVERLESS
```

The queue and the bucket were created by hand and are not touched by `sls remove`.
