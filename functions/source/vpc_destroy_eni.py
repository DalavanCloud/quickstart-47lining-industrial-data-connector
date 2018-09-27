import boto3
from source.utils import send_cfnresponse

ec2 = boto3.client('ec2')


def delete_groups_enis(group_id):
    params = {
        'Filters': [
            {
                'Name': 'group-id',
                'Values': [group_id]
            }
        ]
    }
    network_interfaces = ec2.describe_network_interfaces(**params)['NetworkInterfaces']
    assert len(network_interfaces) in [0, 1]
    if len(network_interfaces) == 1:
        network_interface = network_interfaces[0]
        print('Fetched network interface:', network_interface)
        network_interface_id = network_interface['NetworkInterfaceId']
        if 'Attachment' in network_interface:
            attachment_id = network_interface['Attachment']['AttachmentId']
            print('Detaching network interface with attachment id:', attachment_id)
            ec2.detach_network_interface(AttachmentId=attachment_id)
            print('Network interface detached.')
        print('Deleting related network interface:', network_interface_id)
        ec2.delete_network_interface(NetworkInterfaceId=network_interface_id)
        print('Network interface deleted.')
    print('Deleting security group:', group_id)
    ec2.delete_security_group(GroupId=group_id)
    print('Deleted security group.')


@send_cfnresponse
def handler(event, _):
    if event['RequestType'] == 'Delete':
        group_id = event['ResourceProperties']['SecurityGroups'][0]
        try:
            delete_groups_enis(group_id)
        except Exception as e:
            print(e)
            print('Sending success anyway to handle at least successfull custom resource delete action...')
