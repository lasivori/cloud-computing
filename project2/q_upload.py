import requests, csv, os, sys

BASE = "https://example.execute-api.us-east-1.amazonaws.com" #put your link here

if len(sys.argv) < 2:
	print("You need to give the path to a directory of CSV files containing the stock information we need")
	exit(0)
if len(sys.argv) > 2:
	print("Too many arguments")
	exit(0)

path = sys.argv[1]

for file in os.scandir(path):
	with open(file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter =',')
		line_count = 0
		for row in csv_reader:
			if line_count == 1:
				#add new tickers
				p = {'tickr':row[0][:-3], 'name':row[0]}
				r = requests.put(BASE + "/ticker", params=p)
				print(r)
				print(r.text)
				#add quotes to tickers
				p = {'tickr':row[0][:-3], 'date':row[2], 'time':row[3], 'open':row[4],
				'high':row[5], 'low':row[6], 'close':row[7], 'vol':row[8]}
				r = requests.put(BASE + "/quote", params=p)
				print(r)
				print(r.text)
				line_count += 1
			if line_count == 0:
				line_count += 1
			else:
				#add quotes to tickers
				p = {'tickr':row[0][:-3], 'date':row[2], 'time':row[3], 'open':row[4],
				'high':row[5], 'low':row[6], 'close':row[7], 'vol':row[8]}
				r = requests.put(BASE + "/quote", params=p)
				print(r)
				print(r.text)
				line_count+=1
