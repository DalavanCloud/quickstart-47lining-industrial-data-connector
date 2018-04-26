#!/bin/bash

REPO_DIR=`pwd`
TMP_VENV_DIR=`mktemp -d`
LAMBDA_ZIP_NAME=lambda_deployment_package.zip
LAMBDA_ZIP_PATH=${REPO_DIR}/functions/packages/${LAMBDA_ZIP_NAME}
ASSETS_ZIP_NAME=assets.zip
ASSETS_ZIP_PATH=${REPO_DIR}/assets/assets.zip
PIP_PACKAGES_DIR_NAME=pip-packages
PIP_PACKAGES_DIR=${TMP_VENV_DIR}/${PIP_PACKAGES_DIR_NAME}

# Release resources
function finish {
    echo "Release resources"
    rm -fR ${TMP_VENV_DIR};
}
trap finish EXIT


echo "Prepare lambda deployment package"
mkdir ${PIP_PACKAGES_DIR}
cd ${TMP_VENV_DIR}

virtualenv -p python3.6 venv
(
    source venv/bin/activate
    pip install -t ${PIP_PACKAGES_DIR_NAME} -r ${REPO_DIR}/functions/source/requirements.txt
)
cd ${PIP_PACKAGES_DIR_NAME}
ls -l
zip ${LAMBDA_ZIP_NAME} -r . -x '*__pycache__/*' '*.pyc'
mv ${LAMBDA_ZIP_NAME} ${LAMBDA_ZIP_PATH}

# Add psycopg2 library with compiled source
cd ${TMP_VENV_DIR}
git clone https://github.com/jkehler/awslambda-psycopg2.git
cd awslambda-psycopg2
mv psycopg2 psycopg2-python2.7
mv psycopg2-3.6 psycopg2
zip -r ${LAMBDA_ZIP_PATH} -r psycopg2

echo "Update lambda deployment package"
cd ${REPO_DIR}/assets
zip ${LAMBDA_ZIP_PATH} -r service -x '*__pycache__/*' '*.pyc'
zip ${LAMBDA_ZIP_PATH} -r workers -x '*__pycache__/*' '*.pyc'
zip ${LAMBDA_ZIP_PATH} -r utils   -x '*__pycache__/*' '*.pyc' 'utils/piaf*'
zip ${LAMBDA_ZIP_PATH} -r model   -x '*__pycache__/*' '*.pyc'
zip ${LAMBDA_ZIP_PATH} -r scheduling_manager   -x '*__pycache__/*' '*.pyc'

cd ${REPO_DIR}/functions
zip ${LAMBDA_ZIP_PATH} -r source -x '*__pycache__/*' '*.pyc' 'source/requirements.txt'

echo "Create assets archive"
cd ${REPO_DIR}
zip ${ASSETS_ZIP_NAME} -r assets/webapp_management_console -x '*__pycache__/*' '*.pyc' 'assets/webapp_management_console/app/node_modules/*'
zip ${ASSETS_ZIP_NAME} -r assets/utils -x '*__pycache__/*' '*.pyc'
zip ${ASSETS_ZIP_NAME} -r assets/workers -x '*__pycache__/*' '*.pyc'
zip ${ASSETS_ZIP_NAME} -r assets/service -x '*__pycache__/*' '*.pyc'
zip ${ASSETS_ZIP_NAME} -r assets/scheduling_manager -x '*__pycache__/*' '*.pyc'
zip ${ASSETS_ZIP_NAME} -r assets/model -x '*__pycache__/*' '*.pyc'
zip ${ASSETS_ZIP_NAME} assets/osisoft_pi2aws_root.py
zip ${ASSETS_ZIP_NAME} assets/setup.py
mv assets.zip ${ASSETS_ZIP_PATH}
