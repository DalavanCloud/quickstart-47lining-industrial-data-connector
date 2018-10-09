from urllib.parse import urljoin

from flask import (
    current_app,
    Blueprint,
    render_template,
    request
)
from api.api_utils import raise_backend_exception
import requests


api = Blueprint('API', __name__)


@api.route('/api/v1/<path:path>', methods=['GET', 'POST'])
@raise_backend_exception('Unable to connect to API')
def redirect_to_api(path):
    url = urljoin(current_app.config['API_URL'], f'api/v1/{path}')
    if request.method == 'GET':
        response = requests.get(url, headers=request.headers)
    elif request.method == 'POST':
        response = requests.post(url, json=request.get_json(), headers=request.headers)
    return response.text, response.status_code, response.headers.items()


@api.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@api.route('/<path:path>', methods=['GET', 'POST'])
@raise_backend_exception('Unable to load page')
def root_path(path):
    return render_template('index.html')
