#!/bin/bash

PTON=python3
PIP=pip
VENV=v-env
IAM=123456789011 #your account number goes here
PREFIX=example #put your preferred prefix here
SUBNET=subnet-ab12345 #put your subnet here
SG=sg-12345678 #security group goes here

USAGE="Usage: $0 cache|create"

if [ "$#" -ne 1 ]; then
    echo $USAGE
    exit
fi
case $1 in
  cache)
    aws elasticache create-cache-cluster \
    --cache-cluster-id $PREFIX-stox-cluster \
    --cache-node-type cache.t2.small \
    --engine memcached \
    --engine-version 1.6.6 \
    --cache-parameter-group default.memcached1.6 \
    --num-cache-nodes 1
    ;;

  create)
    $PTON -m venv $VENV --without-pip
    source ${VENV}/bin/activate
    $PTON -m $PIP install elasticache-auto-discovery
    $PTON -m $PIP install pymemcache
    cd ${VENV}/lib/python3.8/site-packages
    zip -r9 ${OLDPWD}/main-lambda.zip .
    cd ${OLDPWD}
    zip -g main-lambda.zip functions.py
    deactivate

    getTickersARN=$(aws lambda create-function --function-name $PREFIX-get_tickers --timeout 30 --memory-size 1024 \
    --zip-file fileb://main-lambda.zip --handler functions.get_tickers_handler --runtime python3.8 \
    --role arn:aws:iam::$IAM:role/lambda-vpc-role \
    --vpc-config SubnetIds=$SUBNET,SecurityGroupIds=$SG | jq -r '.FunctionArn')

    getTickerARN=$(aws lambda create-function --function-name $PREFIX-get_ticker --timeout 30 --memory-size 1024 \
    --zip-file fileb://main-lambda.zip --handler functions.get_ticker_handler --runtime python3.8 \
    --role arn:aws:iam::$IAM:role/lambda-vpc-role \
    --vpc-config SubnetIds=$SUBNET,SecurityGroupIds=$SG | jq -r '.FunctionArn')

    createTickerARN=$(aws lambda create-function --function-name $PREFIX-create_ticker --timeout 30 --memory-size 1024 \
    --zip-file fileb://main-lambda.zip --handler functions.create_ticker_handler --runtime python3.8 \
    --role arn:aws:iam::$IAM:role/lambda-vpc-role \
    --vpc-config SubnetIds=$SUBNET,SecurityGroupIds=$SG | jq -r '.FunctionArn')

    delTickerARN=$(aws lambda create-function --function-name $PREFIX-del_ticker --timeout 30 --memory-size 1024 \
    --zip-file fileb://main-lambda.zip --handler functions.del_ticker_handler --runtime python3.8 \
    --role arn:aws:iam::$IAM:role/lambda-vpc-role \
    --vpc-config SubnetIds=$SUBNET,SecurityGroupIds=$SG | jq -r '.FunctionArn')

    getQuotesARN=$(aws lambda create-function --function-name $PREFIX-get_quotes --timeout 30 --memory-size 1024 \
    --zip-file fileb://main-lambda.zip --handler functions.get_quotes_handler --runtime python3.8 \
    --role arn:aws:iam::$IAM:role/lambda-vpc-role \
    --vpc-config SubnetIds=$SUBNET,SecurityGroupIds=$SG | jq -r '.FunctionArn')

    getQuoteARN=$(aws lambda create-function --function-name $PREFIX-get_quote --timeout 30 --memory-size 1024 \
    --zip-file fileb://main-lambda.zip --handler functions.get_quote_handler --runtime python3.8 \
    --role arn:aws:iam::$IAM:role/lambda-vpc-role \
    --vpc-config SubnetIds=$SUBNET,SecurityGroupIds=$SG | jq -r '.FunctionArn')

    addQuoteARN=$(aws lambda create-function --function-name $PREFIX-add_quote --timeout 30 --memory-size 1024 \
    --zip-file fileb://main-lambda.zip --handler functions.add_quote_handler --runtime python3.8 \
    --role arn:aws:iam::$IAM:role/lambda-vpc-role \
    --vpc-config SubnetIds=$SUBNET,SecurityGroupIds=$SG | jq -r '.FunctionArn')

    avgARN=$(aws lambda create-function --function-name $PREFIX-avg --timeout 30 --memory-size 1024 \
    --zip-file fileb://main-lambda.zip --handler functions.avg_handler --runtime python3.8 \
    --role arn:aws:iam::$IAM:role/lambda-vpc-role \
    --vpc-config SubnetIds=$SUBNET,SecurityGroupIds=$SG | jq -r '.FunctionArn')

    APIID=$(aws apigatewayv2 create-api --name $PREFIX-stox-api --protocol-type HTTP | jq -r '.ApiId')
    aws apigatewayv2 create-stage --api-id $APIID --auto-deploy --stage-name \$default

    getTickersID=$(aws apigatewayv2 create-integration --api-id $APIID --integration-type AWS_PROXY --integration-uri $getTickersARN --payload-format-version 2.0 | jq -r '.IntegrationId')
    getTickerID=$(aws apigatewayv2 create-integration --api-id $APIID --integration-type AWS_PROXY --integration-uri $getTickerARN --payload-format-version 2.0 | jq -r '.IntegrationId')
    createTickerID=$(aws apigatewayv2 create-integration --api-id $APIID --integration-type AWS_PROXY --integration-uri $createTickerARN --payload-format-version 2.0 | jq -r '.IntegrationId')
    delTickerID=$(aws apigatewayv2 create-integration --api-id $APIID --integration-type AWS_PROXY --integration-uri $delTickerARN --payload-format-version 2.0 | jq -r '.IntegrationId')
    getQuotesID=$(aws apigatewayv2 create-integration --api-id $APIID --integration-type AWS_PROXY --integration-uri $getQuotesARN --payload-format-version 2.0 | jq -r '.IntegrationId')
    getQuoteID=$(aws apigatewayv2 create-integration --api-id $APIID --integration-type AWS_PROXY --integration-uri $getQuoteARN --payload-format-version 2.0 | jq -r '.IntegrationId')
    addQuoteID=$(aws apigatewayv2 create-integration --api-id $APIID --integration-type AWS_PROXY --integration-uri $addQuoteARN --payload-format-version 2.0 | jq -r '.IntegrationId')
    avgID=$(aws apigatewayv2 create-integration --api-id $APIID --integration-type AWS_PROXY --integration-uri $avgARN --payload-format-version 2.0 | jq -r '.IntegrationId')

    aws apigatewayv2 create-route --api-id $APIID --route-key 'GET /tickers' --target 'integrations/'$getTickersID
    aws lambda add-permission --function-name $PREFIX-get_tickers --action lambda:InvokeFunction  --statement-id $PREFIX-1 --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:us-east-1:'$IAM':'$APIID'/*/*/tickers'
    aws apigatewayv2 create-route --api-id $APIID --route-key 'GET /ticker/{tickr}' --target 'integrations/'$getTickerID
    aws lambda add-permission --function-name $PREFIX-get_ticker --action lambda:InvokeFunction  --statement-id $PREFIX-2 --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:us-east-1:'$IAM':'$APIID'/*/*/ticker/{tickr}'
    aws apigatewayv2 create-route --api-id $APIID --route-key 'DELETE /ticker/{tickr}' --target 'integrations/'$delTickerID
    aws lambda add-permission --function-name $PREFIX-del_ticker --action lambda:InvokeFunction  --statement-id $PREFIX-3 --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:us-east-1:'$IAM':'$APIID'/*/*/ticker/{tickr}'
    aws apigatewayv2 create-route --api-id $APIID --route-key 'PUT /ticker' --target 'integrations/'$createTickerID
    aws lambda add-permission --function-name $PREFIX-create_ticker --action lambda:InvokeFunction  --statement-id $PREFIX-4 --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:us-east-1:'$IAM':'$APIID'/*/*/ticker'
    aws apigatewayv2 create-route --api-id $APIID --route-key 'GET /quotes/{tickr}' --target 'integrations/'$getQuotesID
    aws lambda add-permission --function-name $PREFIX-get_quotes --action lambda:InvokeFunction  --statement-id $PREFIX-5 --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:us-east-1:'$IAM':'$APIID'/*/*/quotes/{tickr}'
    aws apigatewayv2 create-route --api-id $APIID --route-key 'GET /quote/{tickr}/{datetime}' --target 'integrations/'$getQuoteID
    aws lambda add-permission --function-name $PREFIX-get_quote --action lambda:InvokeFunction  --statement-id $PREFIX-6 --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:us-east-1:'$IAM':'$APIID'/*/*/quote/{tickr}/{datetime}'
    aws apigatewayv2 create-route --api-id $APIID --route-key 'PUT /quote' --target 'integrations/'$addQuoteID
    aws lambda add-permission --function-name $PREFIX-add_quote --action lambda:InvokeFunction  --statement-id $PREFIX-7 --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:us-east-1:'$IAM':'$APIID'/*/*/quote'
    aws apigatewayv2 create-route --api-id $APIID --route-key 'GET /stat/avg/{tickr}/{datetime}/{period}' --target 'integrations/'$avgID
    aws lambda add-permission --function-name $PREFIX-avg --action lambda:InvokeFunction  --statement-id $PREFIX-2 --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:us-east-1:'$IAM':'$APIID'/*/*/stat/avg/{tickr}/{datetime}/{period}'
    ;;

  *)
      echo $USAGE
      ;;
  esac
