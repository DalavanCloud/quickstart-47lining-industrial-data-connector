import logging
import sys

import pytest
from flask import Flask
from flask_injector import FlaskInjector
from injector import singleton
from mock import Mock

from api.create_app import _register_blueprints, _add_healthcheck
from api.json_encoder import CustomJSONEncoder
from api.v1.authentication.cognito_authenticator import CognitoAuthenticator
from scheduling_manager.scheduling_manager import SchedulingManager
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager


@pytest.fixture
def scheduling_manager():
    return SchedulingManager()


@pytest.fixture
def cognito_authenticator():
    cognito_authenticator = Mock()
    cognito_authenticator.get_user = Mock()
    return cognito_authenticator


@pytest.fixture
def api_test_client(api_test_pi_client):
    return api_test_pi_client


@pytest.fixture
def api_test_pi_client(managed_feeds_postgres_manager):
    app = Flask(__name__)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    app = _register_blueprints(app, 'PI')
    app = _add_healthcheck(app)
    app.testing = True
    _configure_dependencies(app, managed_feeds_postgres_manager, scheduling_manager, cognito_authenticator)
    with (app.app_context()):
        client = app.test_client()
        yield client


@pytest.fixture
def api_test_wonderware_client(managed_feeds_postgres_dao_wonderware):
    app = Flask(__name__)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    app = _register_blueprints(app, 'WONDERWARE')
    app = _add_healthcheck(app)
    app.testing = True
    _configure_dependencies(app, managed_feeds_postgres_dao_wonderware, scheduling_manager, cognito_authenticator)
    with (app.app_context()):
        client = app.test_client()
        yield client


@pytest.fixture
def api_test_kepware_client(managed_feeds_postgres_dao_kepware):
    app = Flask(__name__)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    app = _register_blueprints(app, 'KEPWARE')
    app = _add_healthcheck(app)
    app.testing = True
    _configure_dependencies(app, managed_feeds_postgres_dao_kepware, scheduling_manager, cognito_authenticator)
    with (app.app_context()):
        client = app.test_client()
        yield client


def _configure_dependencies(app, managed_feeds_postgres_manager, scheduling_manager, cognito_authenticator):
    def configure(binder):
        app.json_encoder = CustomJSONEncoder
        binder.bind(ManagedFeedsManager, to=managed_feeds_postgres_manager, scope=singleton)
        binder.bind(SchedulingManager, to=scheduling_manager, scope=singleton)
        binder.bind(CognitoAuthenticator, to=cognito_authenticator, scope=singleton)

    FlaskInjector(app=app, modules=[configure])
