# Management console

## Install dependencies

`npm install`

## (Optional) Build css from less

Only if less files in `./src/bootstrap/less` changed (it would be a pain to add this to current build pipeline).

`./node_modules/less/bin/lessc ./src/bootstrap/less/bootstrap.less ./src/bootstrap/css/bootstrap.css`

## Build for production

`npm run build`

## Usage

Run flask server

`python webapp_management_console/app.py --config webapp_management_console/development.ini`
