import csv
import json
import boto3
import os
import sys
import time
import uuid
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

def getAvg(prefix, topic, count, quote):
	qName = prefix +'-'+ topic
	print(qName)
	qUrl = sqs.get_queue_url(QueueName=qName).get('QueueUrl')
	i=0
	total = 0
	vol = 0
	date = 'date'
	time = 'time'
	#receive messages, one at a time, and add to total to get avg
	while i < count:
		msgDetails = sqs.receive_message(QueueUrl=qUrl, VisibilityTimeout=10, WaitTimeSeconds=3)
		receipt = msgDetails.get('Messages')[0].get('ReceiptHandle')
		msg = json.loads(msgDetails.get('Messages')[0].get('Body')).get('Message')
		print(unquote_plus(msg))
		jmsg2 = json.loads(msg)
		#delete messages once we are done with them; comment out these 2 lines if you don't want to delete messages
		#sqs.delete_message(QueueUrl=qUrl, ReceiptHandle=receipt)
		#time.sleep(.5)

		total += float(jmsg2.get(quote.upper()))
		vol += float(jmsg2.get('VOL'))
		i+=1
		if i == count:
			date = jmsg2.get('DATE')
			time = jmsg2.get('TIME')
	avg = str(round((total/count),3))
	vol = vol/count
	result = [date, time, avg, vol]
	return result

def handler(event, context):
	message = event['Records'][0]['Sns']['Message']
	print(message)
	jmsg = json.loads(message)
	
	results = getAvg(jmsg.get('prefix'), jmsg.get('ticker'), int(jmsg.get('count')), jmsg.get('quote'))
	print(results)

	filename = jmsg.get('prefix') +'-'+ jmsg.get('ticker') +'-ma'+ jmsg.get('count')
	path = '/tmp/'+filename
	with open(path, 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['<TICKER>','<PER>','<AVG_TYPE>','<QUOTE>','<DATE>','<TIME>','<AVG>','<VOL>'])
		writer.writerow([jmsg.get('ticker'), '5', 'SMA'+jmsg.get('count'), jmsg.get('quote'), results[0], results[1], results[2], results[3]])
	s3.upload_file(path, 'lasivori-results', filename)
