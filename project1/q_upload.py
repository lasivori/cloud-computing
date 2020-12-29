import requests
import csv, os, sys

BASE = "http://127.0.0.1:5000/"

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
				response = requests.put(BASE + "ticker", {'ticker':row[0][:-3], 'name':row[0]})
				print(response)
				response = requests.post(BASE + "quote", {'ticker':row[0][:-3],
					'date':row[2], 'time':row[3], 'open':row[4], 'high':row[5],
					'low':row[6], 'close':row[7], 'vol':row[8]})
				print(response)
				line_count += 1
			if line_count == 0:
				line_count += 1
			else:
				response = requests.post(BASE + "quote", {'ticker':row[0][:-3],
					'date':row[2], 'time':row[3], 'open':row[4], 'high':row[5],
					'low':row[6], 'close':row[7], 'vol':row[8]})
				print(response)
				line_count+=1
