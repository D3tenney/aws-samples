from moto import mock_ec2, mock_sns
import boto3


@mock_ec2
def test_get_filtered_instances():
    # setup
    start_n_instances = 10
    stop_n_instances = 2
    active_n_instances = start_n_instances - stop_n_instances

    ec2_client = boto3.client('ec2')
    running_ec2_instances = ec2_client.run_instances(ImageId=ec2_client.describe_images()['Images'][0]['ImageId'],
                                                     MinCount=start_n_instances,
                                                     MaxCount=start_n_instances)

    for n in range(0, stop_n_instances):
        ec2_client.stop_instances(InstanceIds=[running_ec2_instances['Instances'][n]['InstanceId']])

    # test
    from aws_functions import get_filtered_instances

    ALARM_STATES = ['pending', 'running']

    FILTER_LIST = [{'Name': 'instance-state-name',
                    'Values': ALARM_STATES}]

    filtered_instance_list = get_filtered_instances(filter_list=FILTER_LIST,
                                                    max_results=active_n_instances - 1,
                                                    ec2_client=ec2_client)
    failures = list()
    if len(filtered_instance_list) != active_n_instances:
        failures.append("len(filtered_instance_list) != active_n_instances")

    failures_string = '\n'.join(failures)
    assert not failures, f"{len(failures)} Errors occurred: {failures_string}"
