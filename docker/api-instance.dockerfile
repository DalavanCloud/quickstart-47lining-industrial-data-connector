FROM python:3.6-stretch

RUN apt-get install -y gcc && mkdir /assets

COPY ["./assets/api/api-requirements.txt", "/assets"]
COPY ["./assets/setup.py", "/assets"]

RUN cd /assets && \
    pip install -r api-requirements.txt && \
    python setup.py develop

COPY ["./assets", "/assets"]

EXPOSE 4005

CMD [ "gunicorn", "-w", "2", "-b", "0.0.0.0:4005", "-k", "gevent", "--chdir", "/assets/api", "--log-level=info", "run_app:app" ]