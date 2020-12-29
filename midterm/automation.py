import boto3

#automate stuff
s3_c = boto3.client('s3')
sns = boto3.client('sns')
iamRes = boto3.resource('iam')
role = iamRes.Role('lambda-s3-role')

prefix = 'lasivori'
iam = '188348546586'

#first create buckets:
s3_c.create_bucket(Bucket=prefix+'-upload')
s3_c.create_bucket(Bucket=prefix+'-results')

#add policies to lambda-s3-role (since it's used for all used lambda functions for this project)
role.attach_policy(PolicyArn='arn:aws:iam::aws:policy/AmazonSQSFullAccess')
role.attach_policy(PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess')
role.attach_policy(PolicyArn='arn:aws:iam::aws:policy/AWSLambdaExecute')
role.attach_policy(PolicyArn='arn:aws:iam::aws:policy/AmazonSNSFullAccess')

sns.subscribe(TopicArn='arn:aws:sns:us-east-1:'+iam+':'+prefix+'-sync', Protocol='lambda', Endpoint='arn:aws:lambda:us-east-1:'+iam+':function:lambda-avg')
