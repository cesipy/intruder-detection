# verteilte-systeme-projekt

This README is still in progress.

## Setup credentials

In order to use AWS Rekognition you need to provide credentials in two places. 

1) Credentials in `res/credentials/creds.yaml`. If the file is not present, create it and copy the content from `res/credentials/creds.yaml.sample`. Of course you'll need to update the AWS credentials. 

2) Credentials in `res/credentials/.aws/credentials`. Here you can directly copy the credentials form the AWS Learners Lab and copy them into credentials. Again, if the file is not present, go ahead and create it. 


Credentials from point 1) are needed when setting up the rekognition cloud. The credentials from point 2) are needed for the `boto3` python package. I guess those could be combined to one, but I had no time to research that. 

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





## TODOs
- [ ] add frame buffer and worker thread working on all frames. 
- [ ] problem with edge not receiving incoming connections when yolo is running
- [ ] edge is too big - 1.76 GB - due to torch i guess

- [ ] face detection model - train own  model for detecting faces

- [ ] person tracking with yolo
- [ ] handle errors in flask app (with decorators, i guess?)
- [ ] limit frame sending in iot. not every frame has to be sended, maybe just one frame every second. 
