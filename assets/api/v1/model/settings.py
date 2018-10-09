from flask_restplus import fields, Model

settings_model = Model('Settings', {
    'as_db_name': fields.String(
        requred=True,
        readonly=True,
        description='Name of asset structure database'
    ),
    'deployment_name': fields.String(
        requred=True,
        readonly=True,
        description='Name of current deployment'
    ),
    'feed_group_size': fields.String(
        required=True,
        readonly=True,
        description='Number of feeds that will be sent in one batch to Connector Agent'
    ),
    'time_window_days': fields.String(
        required=True,
        readonly=True,
        description='Size of time window (in days) according to which backfill/interpolation requests will be split'
    )
})
