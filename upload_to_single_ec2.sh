#!/bin/sh

EC2_IP=3.90.218.68

ssh -i ~/.ssh/mac.pem "mkdir project && rm -rf project/*"
scp -i ~/.ssh/mac.pem -r src docker collect_logs.sh docker-compose.yaml README.md res ec2-user@$EC2_IP:/home/ec2-user/project
