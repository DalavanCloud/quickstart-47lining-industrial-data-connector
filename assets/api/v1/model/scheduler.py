from flask_restplus import fields, Model

schedule_request = Model('ScheduleRequest', {
    'cron': fields.String(
        required=True,
        description='Cron expression for scheduling'
    )
})

rule = Model('Rule', {
    'name': fields.String(
        required=False,
        description='Name of the rule'
    ),
    'query': fields.String(
        required=False
    ),
    'db_name': fields.String(
        required=False
    ),
    'cron': fields.String(
        required=False,
        description='Cron expression of scheduler rule'
    )
})

rules_response = Model('RulesResponse', {
    'structure': fields.Nested(
        rule,
        required=True,
        description='Structure sync scheduler rule'
    ),
    'feeds': fields.Nested(
        rule,
        required=True,
        description='Feeds sync scheduler rule'
    )
})
