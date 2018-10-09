from flask import request, current_app
from flask_restplus import Namespace
from injector import inject

from api.api_utils import raise_backend_exception
from api.v1.ApiResource import ApiResource
from api.v1.authentication.utils import login_required

from scheduling_manager.scheduling_manager import SchedulingManager, NoSuchRuleException
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager


def create_scheduler_namespace(api, **kwargs):
    scheduler_ns = Namespace('scheduler', description='Manage periodic operations')

    @scheduler_ns.route('/structure', methods=['POST'])
    class ScheduleStructureSync(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, scheduling_manager: SchedulingManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager
            self._scheduling_manager = scheduling_manager

        @raise_backend_exception('Cannot schedule structure sync')
        @api.response(200, 'Structure synchronization is scheduled')
        @api.expect(kwargs['schedule_request'])
        @login_required
        def post(self):
            """
            Schedule structure synchronization
            """
            arguments = {
                'cron_expr': _format_cron_expression(request.json['cron']),
                'as_struct_manager_payload': {
                    's3_bucket': current_app.config['CURATED_DATASETS_BUCKET_NAME'],
                    'database': self._feed_manager.get_settings().get('as_db_name', 'default')
                },
                'rule_name': current_app.config['SYNC_AS_STRUCTURE_EVENT_NAME']
            }
            self._scheduling_manager.create_as_sync_schedule(**arguments)
            return 'OK', 200

    @scheduler_ns.route('/feeds', methods=['POST'])
    class ScheduleFeedsSync(ApiResource):
        @inject
        def __init__(self, scheduling_manager: SchedulingManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._scheduling_manager = scheduling_manager

        @raise_backend_exception('Cannot schedule Feeds List sync')
        @api.response(200, 'Feeds synchronization is scheduled')
        @api.expect(kwargs['schedule_request'])
        @login_required
        def post(self):
            """
            Schedule feeds synchronization
            """
            arguments = {
                'cron_expr': _format_cron_expression(request.json['cron']),
                'feeds_manager_payload': {
                    's3_bucket': current_app.config['CURATED_DATASETS_BUCKET_NAME']
                },
                'rule_name': current_app.config['SYNC_FEEDS_EVENT_NAME']
            }
            self._scheduling_manager.create_feeds_sync_schedule(**arguments)
            return 'OK', 200

    @scheduler_ns.route('/rules', methods=['GET'])
    class SchedulerRule(ApiResource):
        @inject
        def __init__(self, scheduling_manager: SchedulingManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._scheduling_manager = scheduling_manager

        @api.marshal_with(kwargs['rules_response'], code=200, description='Scheduler rules are returned')
        @login_required
        def get(self):
            """
            Return scheduler rules - details about scheduled operations for structure and feeds
            """
            return {
                'structure': _make_scheduler_rule(self._scheduling_manager,
                                                  current_app.config['SYNC_AS_STRUCTURE_EVENT_NAME']),
                'feeds': _make_scheduler_rule(self._scheduling_manager, current_app.config['SYNC_FEEDS_EVENT_NAME'])
            }

    return scheduler_ns


def _make_scheduler_rule(scheduling_manager, rule_name):
    try:
        rule = scheduling_manager.get_rule_parameters_by_rule_name(
            rule_name, fetch_feed=False)
    except NoSuchRuleException:
        return {
            'name': rule_name,
            'cron': 'unknown'
        }

    rule = {
        'name': rule_name,
        'query': rule.get('query'),
        'db_name': rule.get('database'),
        'cron': rule['schedule_expression'].replace('cron(', '').replace(')', '')
    }

    return {k: v for k, v in rule.items() if v is not None}


def _format_cron_expression(cron_expr):
    return 'cron({})'.format(cron_expr)
