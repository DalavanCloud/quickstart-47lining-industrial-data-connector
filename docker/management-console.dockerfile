FROM python:3.6-slim-stretch

# install useful commands
RUN apt-get update && apt-get install -y gcc curl gnupg rsync
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash && \
    apt-get install -y nodejs && \
    mkdir /assets

COPY ["./assets/webapp_management_console/webapp-requirements.txt", "/assets"]
COPY ["./assets/setup.py", "/assets"]

RUN cd /assets && \
    pip install -r webapp-requirements.txt && \
    python setup.py develop

ARG connector_type

COPY ["./assets/webapp_management_console/app", "/assets/webapp_management_console/app"]
COPY "./assets/webapp_management_console/app-"$connector_type "/assets/webapp_management_console/app-"$connector_type
COPY ["./assets/webapp_management_console/react_shared", "/assets/webapp_management_console/react_shared"]
RUN cd /assets/webapp_management_console/app && \
    npm install && \
    npm run build

COPY ["./assets", "/assets"]

EXPOSE 4000

CMD [ "gunicorn", "-w", "2", "-b", "0.0.0.0:4000", "-k", "gevent", "--chdir", "/assets/webapp_management_console", "--log-level=info", "run_app:app"]