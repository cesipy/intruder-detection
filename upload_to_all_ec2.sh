#!/bin/sh

IOT_IP=3.84.0.49
EDGE_IP=54.227.104.130
CLOUD_IP=54.82.163.174

# ssh -i ~/.ssh/mac.pem ec2-user@$IOT_IP "mkdir project && rm -rf project/*"
# ssh -i ~/.ssh/mac.pem ec2-user@$EDGE_IP "mkdir project && rm -rf project/*"
# ssh -i ~/.ssh/mac.pem ec2-user@$CLOUD_IP "mkdir project && rm -rf project/*"

# scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose.yaml README.md res ec2-user@$IOT_IP:/home/ec2-user/project
# scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose.yaml README.md res ec2-user@$EDGE_IP:/home/ec2-user/project
# scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose.yaml README.md res ec2-user@$CLOUD_IP:/home/ec2-user/project


ssh -i ~/.ssh/mac.pem ec2-user@$IOT_IP "mkdir project && rm -rf project/src project/docker-compose*"
ssh -i ~/.ssh/mac.pem ec2-user@$EDGE_IP "mkdir project && rm -rf project/src project/docker-compose*"
ssh -i ~/.ssh/mac.pem ec2-user@$CLOUD_IP "mkdir project && rm -rf project/src project/docker-compose*"

scp -i ~/.ssh/mac.pem -r src docker-compose* res/credentials/.aws/credentials ec2-user@$IOT_IP:/home/ec2-user/project
scp -i ~/.ssh/mac.pem -r src docker-compose* res/credentials/.aws/credentials ec2-user@$EDGE_IP:/home/ec2-user/project
scp -i ~/.ssh/mac.pem -r src docker-compose* res/credentials/.aws/credentials ec2-user@$CLOUD_IP:/home/ec2-user/project
