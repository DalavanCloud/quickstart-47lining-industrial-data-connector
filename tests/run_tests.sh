#!/usr/bin/env bash

finish() {
    docker-compose -f tests/docker-compose.yaml down
    deactivate
}
trap finish EXIT

set -e

. $WORKSPACE/venv/bin/activate
docker-compose -f tests/docker-compose.yaml up -d

sleep 10  # local stack and postgres have to have been woken up

pytest tests/pre_deployment
