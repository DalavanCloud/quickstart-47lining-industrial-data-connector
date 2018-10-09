import json
import logging
from io import BytesIO

from botocore.exceptions import ClientError

from utils.feeds_s3 import iter_feeds_from_s3

logger = logging.getLogger()


class CreateScheduleException(Exception):
    pass


class NoSuchRuleException(Exception):
    pass


class SchedulingManager(object):
    """
    Scheduling manager for generic periodic actions
    """
    TARGET_ID = 'SCHEDULE_MANAGER'

    AS_SYNC_LAMBDA_KEY = 'AS_SYNC_LAMBDA_ARN'
    FEEDS_SYNC_LAMBDA_KEY = 'FEEDS_SYNC_LAMBDA_KEY'
    INTERPOLATION = 'INTERPOLATION_LAMBDA_ARN'

    def __init__(self, event_client=None, lambda_arns=None, s3_resource=None, s3_rule_bucket=None,
                 s3_rule_bucket_key_prefix=''):
        self.event_client = event_client
        self.lambda_arns = lambda_arns
        self.s3_resource = s3_resource
        self.s3_rule_bucket = s3_rule_bucket
        self.s3_rule_bucket_key_prefix = s3_rule_bucket_key_prefix

    def create_as_sync_schedule(self, cron_expr, as_struct_manager_payload, rule_name):
        """
        Schedule asset structure update

        Determine lambda function by the name, prepare arguments for AS sync lambda and create a schedule
        """
        as_sync_lambda_arn = self.lambda_arns[self.AS_SYNC_LAMBDA_KEY]
        lambda_input = self._create_as_sync_lambda_input(as_struct_manager_payload)

        return self._create_schedule(rule_name, as_sync_lambda_arn, cron_expr, lambda_input)

    def create_feeds_sync_schedule(self, cron_expr, feeds_manager_payload, rule_name):
        """
        Schedule feeds sync

        :param cron_expr:
        :param feeds_manager_payload:
        :param rule_name:
        :return:
        """
        feeds_sync_lambda_arn = self.lambda_arns[self.FEEDS_SYNC_LAMBDA_KEY]
        lambda_input = self._create_feeds_sync_lambda_input(feeds_manager_payload)

        return self._create_schedule(rule_name, feeds_sync_lambda_arn, cron_expr, lambda_input)

    def get_as_sync_rule_names(self):
        target = self.lambda_arns[self.AS_SYNC_LAMBDA_KEY]
        return self._get_rule_names_by_target(target)

    def get_feeds_sync_rule_names(self):
        target = self.lambda_arns[self.FEEDS_SYNC_LAMBDA_KEY]
        return self._get_rule_names_by_target(target)

    def get_rule_parameters_by_rule_name(self, rule_name, fetch_feed=False):
        rule = self._get_rule_by_name(rule_name)
        return self._get_rule_parameters(rule, fetch_feed)

    def _create_schedule(self, rule_name, lambda_arn, time_expr, lambda_input):
        """
        Create aws schedule from given parameters
        """
        self._create_schedule_rule(rule_name, time_expr)
        self._create_target(rule_name, lambda_arn, lambda_input)

    def _create_schedule_rule(self, rule_name, time_expr):
        try:
            self.event_client.put_rule(
                Name=rule_name,
                ScheduleExpression=time_expr,
            )
        except ClientError as e:
            except_msg = 'Cannot create schedule rule "{}" with time expression "{}". The reason: "{}"'.format(
                rule_name, time_expr, e.response['Error']['Message']
            )
            cse_exception = CreateScheduleException(except_msg)
            logger.exception(cse_exception)
            raise cse_exception from e

    def _create_target(self, rule_name, lambda_arn, lambda_input):
        try:
            self.event_client.put_targets(
                Rule=rule_name,
                Targets=[
                    {
                        'Id': self.TARGET_ID,
                        'Arn': lambda_arn,
                        'Input': lambda_input
                    }
                ]
            )
        except ClientError as e:
            except_msg = 'Cannot create target "{}" with lambda arn "{}" for rule "{}". The reason: "{}"'.format(
                self.TARGET_ID, lambda_arn, rule_name, e.response['Error']['Message']
            )
            cse_exception = CreateScheduleException(except_msg)
            logger.exception(cse_exception)
            raise cse_exception from e

    @staticmethod
    def _create_as_sync_lambda_input(as_lambda_payload):
        lambda_input = {
            's3_bucket': as_lambda_payload['s3_bucket'],
            'database': as_lambda_payload['database']
        }
        return json.dumps(lambda_input)

    @staticmethod
    def _create_feeds_sync_lambda_input(feeds_lambda_payload):
        lambda_input = {
            's3_bucket': feeds_lambda_payload['s3_bucket']
        }
        return json.dumps(lambda_input)

    def _create_backfill_lambda_input(self, backfill_payload, feeds_s3_key):
        lambda_input = {
            'query_syntax': backfill_payload['query_syntax'],
            'query': backfill_payload.get('query'),
            'request_from': backfill_payload.get('request_from'),
            'request_to': backfill_payload.get('request_to'),
            'feeds_s3_bucket': self.s3_rule_bucket,
            'feeds_s3_key': feeds_s3_key,
        }
        return json.dumps(lambda_input)

    @staticmethod
    def _create_publish_feed_lambda_input(publish_feed_payload):
        # TODO
        pass

    def _create_interpolation_input(self, interpolation_payload, feeds_s3_key):
        lambda_input = {
            'query_syntax': interpolation_payload['query_syntax'],
            'interval': interpolation_payload['interval'],
            'interval_unit': interpolation_payload['interval_unit'],
            'query': interpolation_payload.get('query'),
            'request_from': interpolation_payload.get('request_from'),
            'request_to': interpolation_payload.get('request_to'),
            'feeds_s3_bucket': self.s3_rule_bucket,
            'feeds_s3_key': feeds_s3_key,
        }
        return json.dumps(lambda_input)

    def _get_rule_names_by_target(self, target):
        rule_names = self.event_client.list_rule_names_by_target(TargetArn=target)['RuleNames']
        return rule_names

    def _get_rule_by_name(self, rule_name):
        # Note: There is no boto3 method to get rule with exact name, so instead we get all rules
        #       that are prefixed with rule_name and then filter the desired one
        aws_prefixed_rules = self.event_client.list_rules(NamePrefix=rule_name)['Rules']
        aws_rule = next(filter(lambda r: r['Name'] == rule_name, aws_prefixed_rules), None)

        if aws_rule is None:
            exp_msg = 'There is no rule named {}'.format(rule_name)
            raise NoSuchRuleException(exp_msg)

        return aws_rule

    def _get_rule_parameters(self, rule, fetch_feed):
        aws_targets = self.event_client.list_targets_by_rule(Rule=rule['Name'])['Targets']

        # We are only interested in rules created by schedule manager
        target = next(filter(lambda x: x['Id'] == self.TARGET_ID, aws_targets), None)

        target_parameters = json.loads(target.get('Input', '{}')) if target else {}
        target_parameters['schedule_expression'] = rule['ScheduleExpression']
        if fetch_feed:
            target_parameters['feeds'] = self._get_target_feeds_from_s3(target_parameters)

        return target_parameters

    def _dump_backfill_feeds_to_s3(self, backfill_payload, rule_name):
        feeds = backfill_payload['feeds']
        return self._dump_feeds_to_s3(feeds, 'backfill', rule_name)

    def _dump_interpolation_feeds_to_s3(self, interpolation_payload, rule_name):
        feeds = interpolation_payload['feeds']
        return self._dump_feeds_to_s3(feeds, 'interpolation', rule_name)

    def _dump_feeds_to_s3(self, feeds, dir_suffix, rule_name):
        try:
            s3_obj = self._create_feed_s3_object(dir_suffix, rule_name)
            self._save_feed_to_s3(feeds, s3_obj)
            return s3_obj.key
        except ClientError as e:
            except_msg = 'Cannot dump feeds to s3 bucket {} for rule name {}. The reason: {}"'.format(
                self.s3_rule_bucket, rule_name, e.response['Error']['Message']
            )
            cse_exception = CreateScheduleException(except_msg)
            logger.exception(cse_exception)
            raise cse_exception from e

    def _create_feed_s3_object(self, dir_suffix, rule_name):
        s3_key = '/'.join([self.s3_rule_bucket_key_prefix, dir_suffix, rule_name]).lstrip('/')
        return self.s3_resource.Object(self.s3_rule_bucket, s3_key)

    def _save_feed_to_s3(self, feeds, s3_object):
        feeds_file_obj = self._get_feeds_fileobj(feeds)

        s3_object.upload_fileobj(
            Fileobj=feeds_file_obj
        )

    @staticmethod
    def _get_feeds_fileobj(feeds):
        feeds_bytes = b'\n'.join(map(str.encode, feeds))
        feeds_file_obj = BytesIO(feeds_bytes)
        feeds_file_obj.seek(0)
        return feeds_file_obj

    @staticmethod
    def _get_target_feeds_from_s3(target_parameters):
        s3_bucket, s3_key = target_parameters['feeds_s3_bucket'], target_parameters['feeds_s3_key']
        return list(iter_feeds_from_s3(s3_bucket, s3_key))
