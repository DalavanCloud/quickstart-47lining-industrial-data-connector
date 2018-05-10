There are two configurations here. One for deployment with Amazon Kinesis as a data transport service and another with AWS IoT:
config-kinesis.yml - configuration for taskcat to test deployment with Amazon Kinesis as a data transport service
connector-test-kinesis.json - input parameters for deployment with Amazon Kinesis
config-iot.yml - configuration for taskcat to test deployment with AWS IoT as a data transport service
connector-test-iot.json - input parameters for deployment with AWS IoT

These two configurations are separated because of three main reasons:
- json configuration is different
- it is impossible to set up two deployments simultaneously in the same account and region because of AWS Limits
- deployment with Amazon Kinesis uses Kinesis Analytics which is available only in three regions (us-east-1, us-west-2, eu-west-1), whereas AWS IoT is available in more regions