import json
import sys
import socket
import elasticache_auto_discovery
from pymemcache.client.hash import HashClient

#elasticache settings
elasticache_config_endpoint = "test.yd1veb.cfg.use1.cache.amazonaws.com:11211"
nodes = elasticache_auto_discovery.discover(elasticache_config_endpoint)
nodes = map(lambda x: (x[1], int(x[2])), nodes)
memcache_client = HashClient(nodes)

#GET tickers
def get_tickers_handler(event, context):
	data = memcache_client.get('tickers').decode("utf-8")
	data = json.loads(data.replace('\'', '"'))
	return data

#GET specific ticker
def get_ticker_handler(event, context):
	try:
		tickr = event['pathParameters'].get("tickr")
	except:
		return {
			'statusCode':505,
			'body':'A \"tickr\" needs to be given\n'
		}

	data = memcache_client.get('tickers').decode("utf-8")
	data = json.loads(data.replace('\'', '"'))
	return data[tickr]

#PUT ticker
def create_ticker_handler(event, context):
	try:
		tickr = event['queryStringParameters']['tickr']
	except:
		return {
			'statusCode':505,
			'body':'A \"tickr\" needs to be given\n'
		}
	try:
		name = event['queryStringParameters']['name']
	except:
		return {
			'statusCode':505,
			'body':'A \"name\" needs to be given\n'
		}

	# data = json.loads(memcache_client.get('quotes'))
	data = memcache_client.get('tickers')
	if data == None:
		memcache_client.set('tickers', {})
		data = memcache_client.get('tickers')

	data = json.loads(data.decode('utf-8').replace('\'', '"'))
	data[tickr] = name
	memcache_client.set('tickers', data)
	quotes = tickr + "-quotes"
	memcache_client.set(quotes, {})
	return

#DELETE specified ticker
def del_ticker_handler(event, context):
	try:
		tickr = event['pathParameters'].get("tickr")
	except:
		return {
			'statusCode':505,
			'body':'A \"tickr\" needs to be given\n'
		}

	data = json.loads(memcache_client.get('tickers').decode('utf-8').replace('\'', '"'))
	if tickr not in data:
		return {
			'statusCode':505,
			'body':'Ticker not found...\n'
		}

	del data[tickr]
	memcache_client.set('tickers', data)

	quotes = tickr + "-quotes"
	memcache_client.delete(quotes)
	return

#GET all quotes of a specific ticker
def get_quotes_handler(event, context):
	try:
		tickr = event['pathParameters'].get("tickr")
	except:
		return {
			'statusCode':505,
			'body':'A \"tickr\" needs to be given\n'
		}

	quotes = tickr + "-quotes"
	data = memcache_client.get(quotes)
	if data == None:
		return {
			'statusCode':505,
			'body':'Ticker not found...\n'
		}

	data = json.loads(data.decode('utf-8').replace('\'', '"'))
	return data

#GET a single specified quote
def get_quote_handler(event, context):
	try:
		tickr = event['pathParameters'].get('tickr')
	except:
		return {
			'statusCode':505,
			'body':'A \"tickr\" needs to be given\n'
		}

	try:
		datetime = event['pathParameters'].get('datetime')
	except:
		return {
			'statusCode':505,
			'body':'The date and time need to be given\n'
		}

	quotes = tickr + "-quotes"
	data = memcache_client.get(quotes)
	if data == None:
		return {
			'statusCode':505,
			'body':'Ticker not found...\n'
		}

	data = json.loads(data.decode('utf-8').replace('\'', '"'))

	if datetime not in data:
		return {
			'statusCode':505,
			'body':'There is no quote for the given date and time...\n'
		}

	return data[datetime]

#PUT a new quote in for a specific ticker
def add_quote_handler(event, context):
	try:
		tickr = event['queryStringParameters']['tickr']
	except:
		return {
			'statusCode':505,
			'body':'A \"tickr\" needs to be given\n'
		}

	date = event['queryStringParameters']['date']
	time = event['queryStringParameters']['time']
	open = event['queryStringParameters']['open']
	high = event['queryStringParameters']['high']
	low  = event['queryStringParameters']['low']
	close= event['queryStringParameters']['close']
	vol  = event['queryStringParameters']['vol']

	quotes = tickr + "-quotes"
	data = memcache_client.get(quotes)
	if data == None:
		print("Ticker given can not be found")
		sys.exit(1)

	data = json.loads(data.decode('utf-8').replace('\'', '"'))
	datetime = date + "-" + time
	if datetime in data:
		return {
			'statusCode':505,
			'body':'There is already a quote for the given date and time...\n'
		}

	data[datetime] = [open, high, low, close, vol]
	memcache_client.set(quotes, data)
	return

#GET an average computation based on given information
def avg_handler(event, context):
	try:
		tickr = event['pathParameters'].get("tickr")
	except:
		return {
			'statusCode':505,
			'body':'A \"tickr\" needs to be given\n'
		}
	try:
		datetime = event['pathParameters'].get("datetime")
	except:
		return {
			'statusCode':505,
			'body':'The date and time need to be given\n'
		}

	period = int(event['pathParameters'].get('period'))
	quotes = tickr + "-quotes"
	data = memcache_client.get(quotes)
	if data == None:
		return {
			'statusCode':505,
			'body':'Ticker not found...\n'
		}

	data = json.loads(data.decode('utf-8').replace('\'', '"'))

	start = list(data.keys()).index(datetime)
	total = 0.0
	for i in range(period):
		quote = list(data)[(start)-i]
		print(list(data[quote])[3])
		total += float(list(data[quote])[3])/period
	return total
