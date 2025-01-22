#!/bin/sh

IOT_IP=52.3.61.27
EDGE_IP=100.27.188.247
CLOUD_IP=34.203.14.74

# ssh -i ~/.ssh/mac.pem ec2-user@$IOT_IP "mkdir project && rm -rf project/*"
# ssh -i ~/.ssh/mac.pem ec2-user@$EDGE_IP "mkdir project && rm -rf project/*"
# ssh -i ~/.ssh/mac.pem ec2-user@$CLOUD_IP "mkdir project && rm -rf project/*"
# when everything should be transfered (also the videos)
# scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose* README.md res ec2-user@$IOT_IP:/home/ec2-user/project
# scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose* README.md res ec2-user@$EDGE_IP:/home/ec2-user/project
# scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose* README.md res ec2-user@$CLOUD_IP:/home/ec2-user/project


ssh -i ~/.ssh/mac.pem ec2-user@$IOT_IP "mkdir project && rm -rf project/src project/docker-compose*"
ssh -i ~/.ssh/mac.pem ec2-user@$EDGE_IP "mkdir project && rm -rf project/src project/docker-compose*"
ssh -i ~/.ssh/mac.pem ec2-user@$CLOUD_IP "mkdir project && rm -rf project/src project/docker-compose*"

scp -i ~/.ssh/mac.pem -r src docker-compose* docker res/credentials/.aws/credentials ec2-user@$IOT_IP:/home/ec2-user/project
scp -i ~/.ssh/mac.pem -r src docker-compose* docker res/credentials/.aws/credentials ec2-user@$EDGE_IP:/home/ec2-user/project
scp -i ~/.ssh/mac.pem -r src docker-compose* docker res/credentials/.aws/credentials ec2-user@$CLOUD_IP:/home/ec2-user/project
