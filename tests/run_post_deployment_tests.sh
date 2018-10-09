#!/usr/bin/env bash

finish() {
    deactivate
}
trap finish EXIT

set -e

. $WORKSPACE/venv/bin/activate

AWS_DEFAULT_REGION=eu-west-1
python tests/run_post_deployment_tests.py --region $AWS_DEFAULT_REGION --stack-name 'jenkins-stack'
