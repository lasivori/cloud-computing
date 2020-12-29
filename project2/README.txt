Objective: "The purpose of this assignment is to deploy the code developed in part 1 of the assignment to AWS using the
Amazon API Gateway, lambda functions, and AWS-hosted memcached service"

The setup is quite simple this time:
First, the script assumes that you have a "lambda-vpc-role". If you do not, create one (https://docs.aws.amazon.com/lambda/latest/dg/services-elasticache-tutorial.html#vpc-ec-create-iam-role).
In the automation.sh file, you'll have to set up the variables in the beginning to your preferences.
You should be able to fill out all except for SUBNET and SG (these are to be filled after the cache creation)
After this, run it with the 'cache' option: 
	./automation.sh cache

Now go back and fill in the SUBNET and SG variables, then run the script with the 'create' option:
	./automation.sh create

This should set up the functions, the API, as well as it's integrations and routes.

After the setup, when using q_upload.py, you'll have to change the 'BASE' variable to your API's Invoke URL.