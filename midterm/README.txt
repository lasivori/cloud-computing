Objective: "The goal of this exam is to produce a working data processing pipeline that employs several AWS services – S3, SNS, SQS and Lambda"
We were tasked to take in simulated stock information (through CSV files), that would then return an average for the stock cost.

To set up the application:
	First, make sure that you set the prefix and IAM number in the scripts to your preferences. Currently, the prefixes are all lasivori, which can be left alone, but the IAM numbers should be changed. 
	These scripts have prefixes: sns-sqs-setup.py, automation.py, lambda-upload.py
	These scripts have IAM numbers: build-lambda.sh, automation.py
	
	Also, if you want to change which number gets averaged in the script, you can change that in lambda-upload.py
	
	The first step after the prefixes and IAMs is to make sure you have a 'lambda-s3-role' role created on your account. If not, please do so. A further used script will set up the policies, though.

	Next, use the python file 'sns-sqs-setup.py':
	
	python3 sns-sqs-setup.py
	
	Then build the two lambda functions:
	
	./build-lambda.sh new lambda-upload
	./build-lambda.sh new lambda-avg
	./build-lambda.sh create lambda-upload
	./build-lambda.sh create lambda-avg
	
	Then run the 'automation.py' script. This adds the necessary buckets, gives policies to the lambda-s3-role role, and subscribes the lambda-avg to the -sync topic:
	
	python3 automation.py

	Finally, we need to set up the triggers. Sadly I didn't figure out how to do this through code yet, so this will have to be manually done:
	set the trigger for lambda-upload to an S3 trigger of the (chosen prefix)-upload bucket, which the event type should be Object Created: Put. For lambda-avg, set the trigger to sns, with the subscription to (chosen prefix)-sync. 

	Now, everything should be working, and you can now upload a file to the -upload bucket, and the results should appear in the -results bucket. 
