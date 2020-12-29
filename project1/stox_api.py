import flask
from flask import abort, jsonify, request

app = flask.Flask(__name__)

# Suggested internal data structure (example)
#
# {
#   "AAPL": {
#     "name": "Apple",
#     "quotes": {
#       "20201031-083000": [ "110.5", "111.17", "110.64", "110.64", "5684400"],
#       "20201031-083500": [ "111.5", "111.17", "111.64", "111.64", "1473400"],
#       "20201031-084000": [ "112.5", "112.17", "112.64", "112.64", "2987600"]
#     }
#   },
#   "AMZN": {
#     "name": "Amazon", "quotes": {}
#   }
# }

quotes = {
    'AAPL': {'name': 'Apple', 'quotes': {}},
    'GOOG': {'name': 'Alphabet', 'quotes':{}},
    'AMZN': {'name': 'Amazon', 'quotes': {}},
    'NFLX': {'name': 'Netflix', 'quotes': {}},
    'MSFT': {'name': 'Microsoft', 'quotes': {}}
}

# Return a list of all tickers and their name. E.g.:
# {
#     'AAPL': 'Apple',
#     'GOOG': 'Alphabet',
# }
@app.route('/tickers', methods=['GET'])
def get_tickers():
	d = {}
	for k, v in quotes.items():
		d[k] = v.get('name')

	print(d)
	return request.url

# Return a ticker and it name. E.g.:
# {
#     'AAPL': 'Apple',
# }
@app.route('/ticker/<tickr>', methods=['GET'])
def get_ticker(tickr):
	if tickr not in quotes:
		abort(404, "Ticker not found...")
	d = {}
	stock = quotes.get(tickr)
	d[tickr] = stock.get('name')
	print(d)
	return request.url

# Create a new ticker. E.g.:
# curl -i -X POST -d 'ticker=CSCO&name=Cisco' http://localhost:5000/ticker
# ---
@app.route('/ticker', methods=['PUT','POST'])
def create_ticker():
	if 'ticker' not in request.form:
		abort(400, "You need to give a ticker...")
	if 'name' not in request.form:
		abort(400, "You need to give a name...")
	if request.form['ticker'] in quotes:
		abort(409, "Ticker already added...")
	quotes[request.form['ticker']] = {'name':request.form['name'], 'quotes':{}}
	return request.url

# Delete a ticker, along with all quote information. E.g.:
# curl -i  -X DELETE http://localhost:5000/ticker/MSFT
# ---
@app.route('/ticker/<tickr>', methods=['DELETE'])
def delete_ticker(tickr):
	if tickr not in quotes:
		abort(404, 'Ticker not found...')
	del quotes[tickr]
	return request.url

# Get all quotes for a ticker. E.g.:
# {
#    "20201031-083000": [ "110.5", "111.17","110.64", "110.64", "5684400"],
#    "20201031-083500": [ "111.5", "112.17", "111.64", "111.64", "5684400"],
#    "20201031-084000": [ "112.5", "112.17", "112.64", "112.64", "5684400"]
# }
@app.route('/quotes/<tickr>',methods=['GET'])
def get_quotes(tickr):
	if tickr not in quotes:
		abort(404, 'Ticker not found...')
	print(quotes[tickr]['quotes'])
	return jsonify(quotes[tickr]['quotes'])

# Return a specific quote per ticker/datetime
# curl http://localhost:5000/quote/AAPL/20201031-083000
# ---
@app.route('/quote/<tickr>/<datetime>')
def get_quote(tickr,datetime):
	if tickr not in quotes:
		abort(404, 'Ticker not found...')
	if datetime not in quotes[tickr]['quotes']:
		abort(404, 'There is no quote for given date and time...')
	return jsonify(quotes[tickr]['quotes'])

# Create a new quote
# curl -i -X POST \
#      -d 'ticker=AAPL&date=20201031&time=084000&open=110.5&high=111.17&low=110.64&close=110.64&vol=5684400' \
#       http://localhost:5000/quote
# ---
@app.route('/quote',methods=['POST'])
def add_quote():
	r = request.form
	tickr = r['ticker']
	if tickr not in quotes:
		abort(404, 'Ticker not found...')
	if (r['date'] + '-' + r['time']) in quotes[tickr]['quotes']:
		abort(409, 'There is already a quote from that date and time')
	quotes[tickr]['quotes'][r['date'] + '-' + r['time']] = [r['open'], r['high'], r['low'], r['close'], r['vol']]
	return jsonify(quotes[tickr]['quotes'])

# --- average computation ---
# curl -i http://localhost:5000/stat/avg/AAPL/20201031-083000/20
# ---
@app.route('/stat/avg/<tickr>/<datetime>/<int:period>')
def avg(tickr, datetime, period):
	if tickr not in quotes:
		abort(404, 'Ticker not found...')
	if datetime not in quotes[tickr]['quotes']:
		abort(404, 'There is no quote for given date and time...')
	if period > len(quotes[tickr]['quotes']):
		abort(400, 'Not enough quotes for the period given...')
	start = list(quotes[tickr]['quotes'].keys()).index(datetime)
	total = 0.0
	for i in range(period):
		quote = list(quotes[tickr]['quotes'])[(start)-i]
		total += float(list(quotes[tickr]['quotes'][quote])[3])/period
	print(total)
	return request.url

# Debug interface: return internal data structures
# ---
@app.route('/debug/dump')
def dump():
	return jsonify(quotes)

if __name__ == "__main__":
	app.run(debug=True)
