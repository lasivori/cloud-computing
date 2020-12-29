import csv
import json
import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus

sns = boto3.client('sns')
s3 = boto3.client('s3')
prefix = 'lasivori'
quote = 'close'

#read uploaded file as CSV
def readFile(upload):
	with open(upload) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				line_count += 1
			else:
			#send message to related topics
				line_count += 1
				ticker = row[0]
				embed = f'"TICKER" : "{row[0]}", "PER" : "{row[1]}", "DATE" : "{row[2]}", "TIME" : "{row[3]}", "OPEN" : "{row[4]}", "HIGH" : "{row[5]}", "LOW" : "{row[6]}", "CLOSE" : "{row[7]}", "VOL" : "{row[8]}", "OPENINT" : "{row[9]}"'
				message = '{' + embed + '}'
				topicName = prefix + '-' + row[0]
				topicArn = sns.create_topic(Name=topicName).get('TopicArn')
				sns.publish(TopicArn=topicArn, Message=message, MessageStructure='string')
	#send info to SYNC once done
	syncArn = sns.create_topic(Name=prefix + '-sync').get('TopicArn')
	sns.publish(TopicArn=syncArn, Message='{"prefix" : "'+ prefix +'", "ticker": "'+ ticker +'", "count": "'+ str(line_count-1) +'", "quote": "'+ quote +'"}') 

def handler(event, context):
	for record in event['Records']:
		bucket = record['s3']['bucket']['name']
		key = unquote_plus(record['s3']['object']['key'])
		tmpkey = key.replace('/', '')
		download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
		s3.download_file(bucket, key, download_path)
		readFile(download_path)
