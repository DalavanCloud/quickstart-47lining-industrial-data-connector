#!/usr/bin/env bash

set -e

python3 -m venv $WORKSPACE/venv
. $WORKSPACE/venv/bin/activate
pip install --requirement tests/requirements.txt
deactivate
