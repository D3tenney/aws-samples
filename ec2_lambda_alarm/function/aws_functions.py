def get_filtered_instances(filter_list, max_results, ec2_client):
    '''
    Returns a filtered list of EC2 Instances.

    Describes instances and paginates over results to create instance list.
    '''
    reservation_list = list()
    reservations_all_retrieved = False
    next_token = ''

    while not reservations_all_retrieved:
        reservations = ec2_client.describe_instances(
                                  Filters=filter_list,
                                  MaxResults=max_results,
                                  NextToken=next_token
                                  )
        reservation_list.extend(reservations['Reservations'])
        if 'NextToken' in reservations.keys():
            next_token = reservations['NextToken']
        else:
            reservations_all_retrieved = True

    if not reservation_list:
        return None

    instance_list = list()
    for reservation in reservation_list:
        instance_list.extend(reservation['Instances'])

    return instance_list
