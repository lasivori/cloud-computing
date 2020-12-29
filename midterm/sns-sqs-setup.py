import boto3

s3 = boto3.resource('s3')
sns = boto3.client('sns')
sqs = boto3.client('sqs')
sqs_res = boto3.resource('sqs')

# List topics with ARNs
def get_topics():
    topics = sns.list_topics()
    arns = [t['TopicArn'] for t in topics['Topics']]
    names = [t.split(":")[-1] for t in arns]
    names2arns = dict(zip( names, arns ))
    return names2arns 

# Create a topic
def create_topic( name ):
    print("sns.create_topic(): ", name, end=' >> ')
    topic = sns.create_topic( Name=name )
    print( topic['TopicArn'] )
    return topic
    
# Return topic ARN
def delete_topics_like( prefix ):
    n2a = get_topics()
    for topic in n2a.keys():
        if topic.startswith( prefix ):
            print( "delete-topic(): ", topic )
            sns.delete_topic( TopicArn=n2a[topic] )

# Create a queue
def create_queue( name ):
    print("sns.create_queue(): ", name, end=' >> ')
    q = sqs.create_queue(QueueName=name)
    print( q['QueueUrl'] )
    return q

# Returns 
def get_queues( prefix ):
    qs = sqs.list_queues( QueueNamePrefix=prefix )
    if 'QueueUrls' in qs:
        urls = qs['QueueUrls']
        names = [q.split("/")[-1] for q in urls]
        names2urls = dict(zip( names, urls))
        return names2urls

# Deletes all queues with the given prefix
def delete_queues_like( prefix ):
    qs = sqs.list_queues( QueueNamePrefix=prefix )
    while True:
        if 'QueueUrls' in qs:
            for q in qs['QueueUrls']:
                print( "delete_queue():", q)
                sqs.delete_queue(QueueUrl=q)
        if 'NextToken' not in qs:
            break
        qs = sqs.list_queues( QueueNamePrefix=prefix, NextToken=qs['NextToken'] )

# Deletes all subscriptions with the given prefix
def delete_subs_like( topic_prefix ):
    subs = sns.list_subscriptions()
    while True:
        for s in subs['Subscriptions']:
            topic = s['TopicArn'].split( ":")[-1]
            if topic.startswith( topic_prefix ):
                print( "delete_subs_like(): ", s['TopicArn'] )
                sns.unsubscribe( SubscriptionArn=s['SubscriptionArn'] )
        if 'NextToken' not in subs:
            break
        subs = sns.list_subscriptions(NextToken=subs['NextToken'])

# Produces a policy that allows SNS to send message to an SQS queue
def policy_allow_sns_to_sqs(topic_arn, queue_arn):
    policy = """{{
        "Version":"2012-10-17",
        "Statement":[
            {{
            "Sid":"AllowSNStoSQS",
            "Effect":"Allow",
            "Principal" : {{"AWS" : "*"}},
            "Action":"SQS:SendMessage",
            "Resource": "{}",
            "Condition":{{
                "ArnEquals":{{
                "aws:SourceArn": "{}"
                }}
                }}
            }}
        ]
        }}""".format(queue_arn, topic_arn)

    return policy
    
# Create topic and queue by the same name and subscribe q to topic
def setup_sns_sqs( name ):
    topic = create_topic(name)
    create_queue(name)
    q = sqs_res.get_queue_by_name(QueueName=name)
    q_attr = q.attributes

    res = sqs.set_queue_attributes( 
        QueueUrl = sqs.get_queue_url( QueueName=name)['QueueUrl'],
        Attributes = {
            'Policy' : policy_allow_sns_to_sqs( topic['TopicArn'], q_attr['QueueArn'])
        }
    )
    print("subscribe(sns->sqs): ", name, end=' >> ')
    sub = sns.subscribe( TopicArn=topic['TopicArn'], Protocol='sqs', Endpoint=q_attr['QueueArn'], ReturnSubscriptionArn=True )
    print( sub['SubscriptionArn'] )
    return sub

# Application architectural setup (constructor)
def setup( prefix, topics ):
    print( "setup(): ", prefix, topics )
    for key in topics:
        print( "setup_sns_sqs(): ", prefix + '-' + key ) 
        setup_sns_sqs( prefix + '-' + key)
    create_topic( prefix + '-' + 'sync')

# Application teardown (note that reclaimed resources may not be immediately available)
def teardown( prefix ):
    print( "teardown(): ", prefix )
    delete_queues_like( prefix )
    delete_topics_like( prefix )
    delete_subs_like( prefix )

stox = ['AAPL', 'AMZN', 'GOOG', 'MSFT', 'TSLA']

setup( 'lasivori', stox )
#teardown( 'lasivori' )























