import pytest
import enum
import sys
import json
import boto3
import click

ConnectorType = enum.Enum('ConnectorType', 'pi kepware wonderware')


def no_arg_exit(arg):
    print(f'Missing {arg}. Exiting...')
    sys.exit(2)


def get_url(stack_outputs):
    maybe_elb_url = [o['OutputValue'] for o in stack_outputs if o['OutputKey'] == 'ManagementConsoleURL']
    return f'http://{maybe_elb_url[0]}' if maybe_elb_url else no_arg_exit('elb_url')


def get_curated_bucket_name(stack_outputs):
    maybe_curated_bucket_name = [o['OutputValue'] for o in stack_outputs if o['OutputKey'] == 'CuratedBucketName']
    return maybe_curated_bucket_name[0] if maybe_curated_bucket_name else no_arg_exit(
        'curated_bucket_name')


def get_connector_type(stack_name, region):
    client = boto3.client('cloudformation', region)
    stack_parameters = json.dumps(client.get_template(StackName=stack_name))
    if stack_parameters.find('PIPassword') != -1:
        return ConnectorType.pi
    elif stack_parameters.find('KepWarePassword') != -1:
        return ConnectorType.kepware
    elif stack_parameters.find('WonderwarePassword') != -1:
        return ConnectorType.wonderware
    else:
        print('Cannot find connector type')
        sys.exit(2)


@click.option('--region', help='AWS Region code', required=True)
@click.option('--stack-name', help='Stack name', required=True)
@click.command()
def main(region, stack_name):
    resource = boto3.resource('cloudformation', region_name=region)

    stack = resource.Stack(stack_name)
    stack_outputs = stack.outputs

    elb_url = get_url(stack_outputs)
    curated_bucket_name = get_curated_bucket_name(stack_outputs)
    connector_type = get_connector_type(stack_name, region)

    test_dir = f'tests/post_deployment/{connector_type.name}'
    pytest.main(
        ['-x', test_dir, '--elb', elb_url, '--user_name', 'ConsoleAdmin',
         '--password', 'Password1', '--curated_bucket', curated_bucket_name])


if __name__ == "__main__":
    main()
