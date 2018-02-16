#!/bin/bash

REPO_DIR=`pwd`
TMP_VENV_DIR=`mktemp -d`
LAMBDA_ZIP_NAME=lambda_deployment_package.zip
LAMBDA_ZIP_PATH=${REPO_DIR}/assets/lambdas/${LAMBDA_ZIP_NAME}
ASSETS_ZIP_NAME=assets.zip
ASSETS_ZIP_PATH=${REPO_DIR}/assets/assets.zip

# Release resources
function finish {
    echo "Release resources"
    rm -fR ${TMP_VENV_DIR};
}
trap finish EXIT


echo "Prepare lambda deployment package"
cd ${TMP_VENV_DIR}
virtualenv -p python3 venv
(
    source venv/bin/activate
    pip install -r ${REPO_DIR}/assets/lambdas/requirements.txt
)
cd venv/lib/python3.5/site-packages
zip ${LAMBDA_ZIP_NAME} -r ./* -x '*__pycache__/*' '*.pyc'
mv ${LAMBDA_ZIP_NAME} ${LAMBDA_ZIP_PATH}

echo "Update lambda deployment package"
cd ${REPO_DIR}/assets
zip ${LAMBDA_ZIP_PATH} -r service -x '*__pycache__/*' '*.pyc'
zip ${LAMBDA_ZIP_PATH} -r workers -x '*__pycache__/*' '*.pyc'
zip ${LAMBDA_ZIP_PATH} -r lambdas -x '*__pycache__/*' '*.pyc' 'lambdas/requirements.txt'
zip ${LAMBDA_ZIP_PATH} -r utils   -x '*__pycache__/*' '*.pyc' 'utils/piaf*'

echo "Create assets archive"
cd ${REPO_DIR}
zip ${ASSETS_ZIP_NAME} -r assets/webapp_management_console -x '*__pycache__/*' '*.pyc' 'assets/webapp_management_console/app/build/*' 'assets/webapp_management_console/app/node_modules/*'
zip ${ASSETS_ZIP_NAME} -r assets/utils -x '*__pycache__/*' '*.pyc'
zip ${ASSETS_ZIP_NAME} -r assets/workers -x '*__pycache__/*' '*.pyc'
zip ${ASSETS_ZIP_NAME} -r assets/service -x '*__pycache__/*' '*.pyc'
zip ${ASSETS_ZIP_NAME} assets/osisoft_pi2aws_root.py
zip ${ASSETS_ZIP_NAME} assets/setup.py
mv assets.zip ${ASSETS_ZIP_PATH}
