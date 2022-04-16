from aws_functions import get_filtered_instances
import boto3
from message_functions import message_per_instance, single_message
from os import environ

REGION = environ.get("REGION")
TOPIC_ARN = environ.get("TOPIC_ARN")

ec2_client = boto3.client('ec2')
sns_client = boto3.client('sns')

# possible states: pending, running, shutting-down, terminated, stopping, stopped
ALARM_STATES = ['pending', 'running']

FILTER_LIST = [{'Name': 'instance-state-name',
                'Values': ALARM_STATES}]


def event_handler(event, context):
    ec2_instance_list = get_filtered_instances(filter_list=FILTER_LIST,
                                               max_results=20, # max results per `describe_instances` call, not max total
                                               ec2_client=ec2_client)

    if not ec2_instance_list:
        return None

    message_object_list = list()
    # create a message object for each instance
    per_instance_messages = message_per_instance('instance',
                                                 ec2_instance_list,
                                                 REGION)
    message_object_list.extend(per_instance_messages)

    # create a single message object listing all instances
    header = f'The following instances are still running in {REGION}:'
    footer = 'Please turn off instances when not in use.'

    all_instance_message = single_message('instance_list',
                                          ec2_instance_list,
                                          REGION, header, footer)
    message_object_list.append(all_instance_message)

    # send messages
    for message_object in message_object_list:
        response = sns_client.publish(TopicArn=TOPIC_ARN,
                                      Message=message_object['message'],
                                      MessageAttributes=message_object['attributes'])
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print(response)
