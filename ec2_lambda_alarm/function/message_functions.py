def make_message(instance):
    '''Creates message of running EC2 instances.'''

    name_tag = [tag['Value'] for tag in instance['Tags']
                if tag['Key'] == 'Name'][0]
    message_body = f'Name: {name_tag}, InstanceId: {instance["InstanceId"]}'

    return message_body


def make_attributes(message_type, region, instance_tag_list):
    '''Creates a set of attributes using message_type, region, and instance tags.'''
    instance_attributes = {'message_type': {'StringValue': message_type,
                                            'DataType': 'String'},
                           'region': {'StringValue': region,
                                      'DataType': 'String'}}

    if instance_tag_list:
        for tag in instance_tag_list:
            instance_attributes[tag['Key']] = {'StringValue': str(tag['Value']),
                                               'DataType': 'String'}

    return instance_attributes


def message_per_instance(message_type, instance_list, region):
    '''Returns a list of message objects, dictionaries specifying message text and attributes'''
    message_object_list = list()
    for instance in instance_list:
        message_object = {'message': make_message(instance),
                          'attributes': make_attributes(message_type,
                                                        region,
                                                        instance['Tags'])}
        message_object_list.append(message_object)

    return message_object_list


def single_message(message_type, instance_list, region, header, footer):
    '''
    Returns a single message object for a list of instances,
    specifying message text and attributes.
    '''
    instance_messages = [make_message(instance) for instance in instance_list]

    message_object = {'message': header + '\n' + '\n'.join(instance_messages) + '\n' + footer,
                      'attributes': make_attributes(message_type,
                                                    region,
                                                    None)}

    return message_object
