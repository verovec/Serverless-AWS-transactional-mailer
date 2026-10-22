# Development

## Toolchain

- Python 3.9 to match `provider.runtime`, with `pip`.
- Node.js and `npm` for the Serverless Framework, or Docker to use the provided image instead.
- The AWS CLI configured on `eu-west-1`.

## Recipes

```sh
python3 -m venv .venv && . .venv/bin/activate   # .venv is ignored by git
pip install -r requirements.txt                # sib-api-v3-sdk, Sendinblue, boto3
sls deploy --verbose --conceal                 # deploy (see deployment.md for the SSM prerequisites)
QUEUE_URL=<url> python3 test/test_mailer.py    # push one message in the queue
sls invoke -f send_email -p event.json         # invoke with a hand-written SQS event (see below)
sls logs -f send_email --tail                  # follow the CloudWatch logs
sls remove                                     # delete the stack
```

A minimal `event.json` for `sls invoke` mirrors what SQS delivers:

```json
{
  "Records": [
    {
      "receiptHandle": "test",
      "body": "{\"template_id\": 1, \"user\": {\"email\": \"ada@example.com\", \"name\": \"Ada\"}, \"params\": {\"firstname\": \"Ada\"}}"
    }
  ]
}
```

The `receiptHandle` is fake, so `sqs.delete_message` fails before the API is called; use the
real queue for an end-to-end check.

## Swapping the mail provider

The provider is isolated in `src/send_email_sendinblue/send_email_sendinblue.py`:

1. Replace `sib_api_v3_sdk` with the SDK of your provider in `requirements.txt`.
2. Rewrite the body of `lambda_handler` after `sqs.delete_message`: read `template_id`, `user`
   and `params` from `body` and call your API.
3. Rename `SENDINBLUE_API_KEY` in `serverless.yml` (`functions.send_email.environment`) and in
   SSM.

The e-commerce project of the author did exactly that with SendGrid.

## Conventions

- Nothing account-specific in the repository: every such value is an SSM parameter.
- `package.json` and `.serverless/` stay ignored; the plugin is installed with `sls plugin install`.
- Pin the Python dependencies: Lambda packages are built once and never resolved again.
