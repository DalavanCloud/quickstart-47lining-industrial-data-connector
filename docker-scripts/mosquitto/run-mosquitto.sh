#!/bin/ash
########################################################
# Script for configuring and running Eclipse Mosquitto
#
# Environment variables used:
# PRIVATE_KEY_FILE
# AWS_DEFAULT_REGION
# PISERVER
# DEPLOYMENT_SUFFIX
# IOT_CERTIFICATE_ID
#########################################################

private_key_file="/etc/mosquitto/certs/private.key"
if [ ! -f "$private_key_file" ]
then
    # download certificates and private keys
    mkdir -p /etc/mosquitto/certs/
    echo "-----BEGIN PRIVATE KEY-----" > /etc/mosquitto/certs/private.key
    echo $PRIVATE_KEY_FILE | tr " " "\n" | tail -n+4 | head -n-3 >> /etc/mosquitto/certs/private.key
    echo "-----END PRIVATE KEY-----" >> /etc/mosquitto/certs/private.key
    echo "" >> /etc/mosquitto/certs/private.key
    aws iot describe-certificate --certificate-id $IOT_CERTIFICATE_ID --region $AWS_DEFAULT_REGION | jq -r .certificateDescription.certificatePem > /etc/mosquitto/certs/cert.crt
    cd /etc/mosquitto/certs/
    chmod 644 private.key && chmod 644 cert.crt
    wget https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem -O rootCA.pem

    # make up config file
    echo address $(aws iot describe-endpoint --region $AWS_DEFAULT_REGION | jq -r .endpointAddress):8883 >> /etc/mosquitto/conf.d/bridge.conf
    echo topic $PISERVER/# out 0 >> /etc/mosquitto/conf.d/bridge.conf
    echo clientid $PISERVER-$DEPLOYMENT_SUFFIX >> /etc/mosquitto/conf.d/bridge.conf

fi
# run mosquitto
mosquitto -c /etc/mosquitto/conf.d/bridge.conf