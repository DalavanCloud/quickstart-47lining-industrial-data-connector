HOW TO RUN TESTS
=========================
Tools that are required to run tests:
- Python 3.6
- pip
- Docker
- docker-compose

Before running any tests it is recommended to create venv:
`python3 -m venv venv`
`. venv/bin/activate`

How to run
----------

1. Install requirements:
`pip install -r tests/requirements.txt`

2. Run fake AWS services:
`docker-compose -f tests/docker-compose.yaml up -d`

3. Run tests:
`pytest tests/pre_deployment`

4. After all tests are finished, stop containers:
`docker-compose -f tests/docker-compose.yaml down`

Test results
------------
pytest returns exit **code 0** if tests succeeded. Otherwise it returns **code 1**
