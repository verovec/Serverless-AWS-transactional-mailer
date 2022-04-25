FROM node:17-alpine3.14

ENV AWS_DEFAULT_REGION=eu-west-1
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

WORKDIR '/serverless'

COPY . /serverless

RUN apk add --no-cache python3 py3-pip
RUN npm config set prefix /usr/local
RUN npm install -g serverless
RUN sls plugin install -n serverless-python-requirements

CMD ["sls", "deploy", "--verbose", "--conceal" ]
