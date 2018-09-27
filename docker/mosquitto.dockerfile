FROM eclipse-mosquitto:1.4.12

RUN apk update && apk add jq python py-pip groff less mailcap ca-certificates wget && pip install awscli --upgrade && update-ca-certificates

COPY ["./docker-scripts/mosquitto/bridge.conf", "/etc/mosquitto/conf.d/"]

COPY ["./docker-scripts/mosquitto/run-mosquitto.sh", "/"]

EXPOSE 8883

CMD [ "ash", "/run-mosquitto.sh" ]