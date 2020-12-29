#!/bin/bash

PTON=python3
PIP=pip
VENV=v-env
LAMBDA=quote_reader
IAM=123456789011

USAGE="Usage: $0 new|create|update|clean <lambda-func-name>"

if [ "$#" -ne 2 ]; then
    echo $USAGE
    exit
fi
LAMBDA=$2

case $1 in

# Prepares a new deployment package including boto3 library (add as needed)
new)
    $PTON -m venv $VENV                         # Setup Python virtual environment
    source ${VENV}/bin/activate
    $PIP install boto3                          # Add non-standard packages (boto3 is the AWS SDK)
    cd ${VENV}/lib/python3.8/site-packages
    zip -r9 ${OLDPWD}/${LAMBDA}.zip .           # Zip up the packages
    cd ${OLDPWD}
    zip -g ${LAMBDA}.zip ${LAMBDA}.py           # Add labda function code
    deactivate
    ;;
    
# Creates a new AWS Lambda function from a deployment package
create)
    time aws lambda create-function --function-name ${LAMBDA} --zip-file fileb://${LAMBDA}.zip --handler ${LAMBDA}.handler --runtime python3.8  --timeout 10 --memory-size 1024 --role arn:aws:iam::${IAM}:role/lambda-s3-role \
#    --cli-binary-format raw-in-base64-out #\
    --cli-read-timeout 0 --cli-connect-timeout 0    # These parameters are optional for slower connections to prevent timeouts
    ;;

# Updates an existing AWS Lambda function 
update)
    zip -g ${LAMBDA}.zip ${LAMBDA}.py
    time aws lambda update-function-code --function-name ${LAMBDA} --zip-file fileb://${LAMBDA}.zip \
#--cli-binary-format raw-in-base64-out \
    --cli-read-timeout 0 --cli-connect-timeout 0
    ;;
    
# Clean up temporary files
clean)
    rm -rf ~/.local/lib/python3.8/*
    rm -rf v-env
    rm $LAMBDA.zip
    ;;

*)
    echo $USAGE
    ;;
esac
