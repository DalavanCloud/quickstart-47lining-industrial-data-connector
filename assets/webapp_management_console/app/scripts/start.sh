rsync -av ../app-${connector_type}/src/. src &&
npm-run-all -p start-wml watch-css start-js