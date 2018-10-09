#!/usr/bin/env bash
rsync -av ../app-${connector_type}/src/. src &&
rsync -av ../react_shared/. src/shared --exclude node_modules &&
npm-run-all build-css build-js