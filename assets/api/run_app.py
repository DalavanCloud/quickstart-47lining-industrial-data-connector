import logging

from api.create_app import create_app

app = create_app()

if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=4005, debug=True, threaded=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.setLevel(logging.WARNING)
    app.logger.handlers.extend(gunicorn_logger.handlers)
