import logging
import os
import sys

from flask import Flask, jsonify

from api.api_utils import BackendException
from osisoft_pi2aws_root import PROJECT_DIR

REACT_FOLDER = os.path.join(PROJECT_DIR, 'webapp_management_console/app/build')


def create_app():
    app = Flask(
        __name__,
        template_folder=REACT_FOLDER,
        static_folder=os.path.join(REACT_FOLDER, 'static')
    )
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    @app.errorhandler(BackendException)
    def backend_exception_errorhandler(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    app = _create_app_config(app)
    app = _register_blueprints(app)

    return app


def _register_blueprints(app):
    from webapp_management_console.web_api.api import api

    app.register_blueprint(api)

    return app


def _create_app_config(app):
    config = dict(os.environ)
    app.config.update(config)
    return app
