#!/bin/sh

IOT_IP=98.84.139.0
EDGE_IP=3.85.237.189
CLOUD_IP=52.73.61.175

# ssh -i ~/.ssh/mac.pem ec2-user@$IOT_IP "mkdir project && rm -rf project/*"
# ssh -i ~/.ssh/mac.pem ec2-user@$EDGE_IP "mkdir project && rm -rf project/*"
# ssh -i ~/.ssh/mac.pem ec2-user@$CLOUD_IP "mkdir project && rm -rf project/*"

# scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose.yaml README.md res ec2-user@$IOT_IP:/home/ec2-user/project
# scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose.yaml README.md res ec2-user@$EDGE_IP:/home/ec2-user/project
# scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose.yaml README.md res ec2-user@$CLOUD_IP:/home/ec2-user/project


ssh -i ~/.ssh/mac.pem ec2-user@$IOT_IP "mkdir project && rm -rf project/src project/docker-compose*"
ssh -i ~/.ssh/mac.pem ec2-user@$EDGE_IP "mkdir project && rm -rf project/src project/docker-compose*"
ssh -i ~/.ssh/mac.pem ec2-user@$CLOUD_IP "mkdir project && rm -rf project/src project/docker-compose*"

scp -i ~/.ssh/mac.pem -r src docker-compose* ec2-user@$IOT_IP:/home/ec2-user/project
scp -i ~/.ssh/mac.pem -r src docker-compose* ec2-user@$EDGE_IP:/home/ec2-user/project
scp -i ~/.ssh/mac.pem -r src docker-compose* ec2-user@$CLOUD_IP:/home/ec2-user/project
