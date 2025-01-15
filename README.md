# verteilte-systeme-projekt

This README is still in progress.

## Setup credentials

In order to use AWS Rekognition you need to provide credentials.

- Credentials in `res/credentials/.aws/credentials`. Here you can directly copy the credentials form the AWS Learners Lab and copy them into credentials. If the file is not present, create it!


Credentials are neede for boto3 initialisation and connecting to the rekognition client. 


## Simulation of topology with docker containers
To avoid deploying all the code to the cloud for testing, we can simulate the topology with docker containers.

In `/src` I created a `docker-compose.yml` file that defines the services and their configurations.
For each component in the network I created a Dockerfile and configured the container as a service in the `docker-compose file`. 

The dependency declaration for each container is stored in the `src/dependencies/` folder. There are all the python packages needed for the corresponding component.

in order to update the contents of this you can either run `pip freeze > dependencies/<component>.txt` or add them manually. 

Then the project can be executed using the following commands: 

```bash
docker compose up --build   # --build forces rebuild

# to stop all containers
docker compose down
``` 


## Collection of logs
After the docker containers run and the simulation produced sufficient logs, the logs in the corresponding directories in the containers `/app/logs` can be collected to the local host. Here the script `collect_logs.sh` comes into play. 

```bash
# if permissions are not right, change them (+x)
docker compose up --build 
# ...
# simulation runs for a few minutes
# ...

#after simulation stopped, run, saves logs to `res/collected_logs`
./collect_logs.sh
```


## Provisioning in cloud

For each layer, I created a EC2 instance to run the code of the distributed system. 
I have the .pem file locally available, so please ask me for it. 
If time allows, I will create a script that provisions the instances using Terraform.
In order to connect to the instance using ssh, you need the `.pem` file and the public IP. To connect: 

```bash
ssh -i ~/location/to/file.pem ec2-user@PUBLIC-IP
sudo yum install docker -y &&sudo service docker start && sudo usermod -a -G docker ec2-user && sudo chmod 666 /var/run/docker.sock

# also necessary to install docker-compose: 
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

# then run the corresponding docker containers with the compose command: 
docker-compose -f docker-compose-layer.yaml up --build
```

Then to start the docker container for the corresponding layer `layer`, run the `docker build` and `docker run` command. 
```bash

docker build -f docker/Dockerfile.layer . 
docker run -d <id or name> 
```
This has to be done for all three layers, namely `iot`, `edge` and `cloud`. 

As local changes have to be pushed there from time to time, use the script `./upload_to_all_ec2.sh`. There you have to adapt the public IPs of the instances. 

## TODOs
- [ ] path for camera set is not general - does not work on ec2
- [x] add frame buffer and worker thread working on all frames. 
- [x] problem with edge not receiving incoming connections when yolo is running
- [ ] edge is too big - 1.76 GB - due to torch i guess

- [ ] face detection model - train own  model for detecting faces

- [ ] person tracking with yolo
- [ ] handle errors in flask app (with decorators, i guess?)
- [ ] limit frame sending in iot. not every frame has to be sended, maybe just one frame every second. 
