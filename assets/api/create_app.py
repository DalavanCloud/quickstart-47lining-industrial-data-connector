import base64
import os
import sys
import logging

import boto3
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_injector import FlaskInjector
from injector import Injector, Module, singleton

from api.api_utils import BackendException
from api.json_encoder import CustomJSONEncoder
from api.v1 import create_app_blueprint_v1
from api.v1.ApiUserProvider import ApiUserProvider
from api.v1.authentication.cognito_authenticator import CognitoAuthenticator
from api.v1.user_management.cognito_user_manager import CognitoUserManager
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager
from scheduling_manager.scheduling_manager import SchedulingManager


class AppModule(Module):
    """Setup dependency injection"""

    def __init__(self, app):
        self.app = app

    def configure(self, binder):
        app = _create_app_config(self.app)

        app.json_encoder = CustomJSONEncoder

        engine = create_engine(self.app.config['POSTGRES_URI'], use_batch_mode=True)
        database = SQLAlchemy(self.app, session_options={'bind': engine})

        feed_manager = _create_managed_feeds_manager(self.app.config, database)
        scheduling_manager = _create_scheduling_manager(self.app.config)
        cognito_authenticator = _create_authenticator(self.app.config)
        cognito_user_manager = _create_user_manager(self.app.config)

        binder.bind(SQLAlchemy, to=database, scope=singleton)
        binder.bind(ManagedFeedsManager, to=feed_manager, scope=singleton)
        binder.bind(SchedulingManager, to=scheduling_manager, scope=singleton)
        binder.bind(CognitoAuthenticator, to=cognito_authenticator, scope=singleton)
        binder.bind(CognitoUserManager, to=cognito_user_manager, scope=singleton)


def create_app():
    app = Flask(__name__)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    app = _register_blueprints(app, os.environ['CONNECTOR_TYPE'])
    app = _add_healthcheck(app)

    @app.errorhandler(BackendException)
    def backend_exception_errorhandler(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    injector = Injector([AppModule(app)])
    FlaskInjector(app=app, injector=injector)

    return app


def _register_blueprints(app, connector_type):
    blueprint_v1 = create_app_blueprint_v1(connector_type=connector_type)
    app.register_blueprint(blueprint_v1)
    return app


def _add_healthcheck(app):
    @app.route("/healthcheck", methods=["GET"])
    def healthcheck():
        return 'OK', 200
    return app


def _create_app_config(app):
    config = dict(os.environ)
    config['S3_RULE_BUCKET_KEY_PREFIX'] = "rules"
    config['SQLALCHEMY_DATABASE_URI'] = config['POSTGRES_URI']
    config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    config['SYNC_FEEDS_EVENT_NAME'] = "{}-sync-feeds-{}".format(
        config['REGION'],
        config['ACCOUNT_ID']
    )
    config['SYNC_AS_STRUCTURE_EVENT_NAME'] = "{}-sync-as-structure-{}".format(
        config['REGION'],
        config['ACCOUNT_ID']
    )
    app.config.update(config)
    app.secret_key = base64.b64decode(config.get('APP_SECRET')) \
        if config.get('APP_SECRET') is not None \
        else os.urandom(47)
    return app


def _create_managed_feeds_manager(config, database):
    return ManagedFeedsManager.create_manager(
        aws_region=config['REGION'],
        postgres_session=database.session,
        incoming_queue_name=config['INCOMING_QUEUE_NAME'],
        subscription_queue_name=config['SUBSCRIPTION_QUEUE_NAME'],
        backfill_queue_name=config['BACKFILL_QUEUE_NAME'],
        interpolation_queue_name=config['INTERPOLATION_QUEUE_NAME'],
        connector_type=os.environ['CONNECTOR_TYPE'],
        user_provider=ApiUserProvider()
    )


def _create_scheduling_manager(config):
    lambda_arns = {
        'AS_SYNC_LAMBDA_ARN': config['AS_SYNC_LAMBDA_ARN'],
        'FEEDS_SYNC_LAMBDA_KEY': config['FEEDS_SYNC_LAMBDA_ARN']
    }

    boto_session = boto3.session.Session()
    return SchedulingManager(
        boto_session.client('events', region_name=config['REGION']),
        lambda_arns,
        s3_resource=boto_session.resource('s3'),
        s3_rule_bucket=config['CURATED_DATASETS_BUCKET_NAME'],
        s3_rule_bucket_key_prefix=config['S3_RULE_BUCKET_KEY_PREFIX']
    )


def _create_authenticator(config):
    return CognitoAuthenticator(
        cognito_user_pool_id=config['COGNITO_USER_POOL_ID'],
        cognito_client_id=config['COGNITO_APP_CLIENT_ID'],
        cognito_client_secret=config['COGNITO_CLIENT_SECRET']
    )


def _create_user_manager(config):
    return CognitoUserManager(
        cognito_user_pool_id=config['COGNITO_USER_POOL_ID'],
        cognito_client_id=config['COGNITO_APP_CLIENT_ID'],
        cognito_client_secret=config['COGNITO_CLIENT_SECRET']
    )
