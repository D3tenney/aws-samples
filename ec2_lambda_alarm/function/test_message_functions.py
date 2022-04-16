def test_make_message():
    from message_functions import make_message
    INSTANCE = {'InstanceId': '1',
                'Tags': [{'Key': 'Name', 'Value': 'test_1'},
                         {'Key': 'foo', 'Value': 'bar'}]}
    message = make_message(INSTANCE)

    assert message == f"Name: {INSTANCE['Tags'][0]['Value']}, InstanceId: {INSTANCE['InstanceId']}"


def test_make_attributes():
    from message_functions import make_attributes
    REGION = 'us-east-1'
    INSTANCE = {'InstanceId': '1',
                'Tags': [{'Key': 'Name', 'Value': 'test_1'},
                         {'Key': 'foo', 'Value': 'bar'}]}
    attributes = make_attributes('test',
                                 'us-east-1',
                                 INSTANCE['Tags'])

    EXPECTED_ATTRIBUTES = {'message_type': {'StringValue':'test',
                                            'DataType': 'String'},
                           'region': {'StringValue': REGION,
                                      'DataType': 'String'},
                           'Name': {'StringValue': 'test_1',
                                    'DataType': 'String'},
                           'foo': {'StringValue': 'bar',
                                   'DataType': 'String'}}

    assert attributes == EXPECTED_ATTRIBUTES


def test_message_per_instance():
    from message_functions import message_per_instance
    REGION = 'us-east-1'
    MESSAGE_TYPE = 'instance'
    INSTANCE_LIST = [{'InstanceId': '1',
                      'Tags': [{'Key': 'Name', 'Value': 'test_1'},
                               {'Key': 'foo', 'Value': 'bar'}]},
                     {'InstanceId': '2',
                      'Tags': [{'Key': 'Name', 'Value': 'test_2'},
                               {'Key': 'foo', 'Value': 'bar'}]},
                     {'InstanceId': '3',
                      'Tags': [{'Key': 'Name', 'Value': 'test_3'},
                               {'Key': 'foo', 'Value': 'bar'}]}]

    INSTANCE_0 = INSTANCE_LIST[0]
    EXPECTED_MESSAGE_0 = {'message': f"Name: {INSTANCE_0['Tags'][0]['Value']}, InstanceId: {INSTANCE_0['InstanceId']}",
                          'attributes': {'message_type': {'StringValue': MESSAGE_TYPE,
                                                          'DataType': 'String'},
                                         'region': {'StringValue': REGION,
                                                    'DataType': 'String'},
                                         'Name': {'StringValue': 'test_1',
                                                  'DataType': 'String'},
                                         'foo': {'StringValue': 'bar',
                                                 'DataType': 'String'}}}

    message_list = message_per_instance(MESSAGE_TYPE, INSTANCE_LIST, REGION)

    failures = list()
    if len(message_list) != len(INSTANCE_LIST):
        failures.append("Length of message list does not match instance list")
    if message_list[0] != EXPECTED_MESSAGE_0:
        failures.append("First Message Body does not match expected")

    failures_string = '\n'.join(failures)
    assert not failures, f"{len(failures)} Errors: {failures_string}"


def test_single_message():
    from message_functions import single_message
    REGION = 'us-east-1'
    MESSAGE_TYPE = 'instance_list'
    INSTANCE_LIST = [{'InstanceId': '1',
                      'Tags': [{'Key': 'Name', 'Value': 'test_1'},
                               {'Key': 'foo', 'Value': 'bar'}]},
                     {'InstanceId': '2',
                      'Tags': [{'Key': 'Name', 'Value': 'test_2'},
                               {'Key': 'foo', 'Value': 'bar'}]}]

    HEADER = 'header'
    FOOTER = 'footer'

    EXPECTED_MESSAGE = {'message': 'header\nName: test_1, InstanceId: 1\nName: test_2, InstanceId: 2\nfooter',
                        'attributes': {'message_type': {'StringValue': MESSAGE_TYPE,
                                                        'DataType': 'String'},
                                       'region': {'StringValue': REGION,
                                                  'DataType': 'String'}}}

    message = single_message(MESSAGE_TYPE, INSTANCE_LIST,
                             REGION, HEADER, FOOTER)

    assert message == EXPECTED_MESSAGE
