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
# in the src directory
docker compose -f docker-compose.yaml up --build   # --build forces rebuild

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

For each layer (IoT, Edge, Cloud), I created a separate EC2 instance to run the distributed system. The Edge and Cloud instances need at least t2.medium instance type due to YOLO and AWS Rekognition requirements.

To set up a new instance:

1. Connect via SSH using the .pem file (contact me for access):
```bash
ssh -i ~/location/to/file.pem ec2-user@PUBLIC-IP
```

2. Install Docker and required tools:
```bash
sudo yum install docker -y
sudo service docker start 
sudo usermod -a -G docker ec2-user 
sudo chmod 666 /var/run/docker.sock

# install Docker Compose
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. Upload code to instances using the provided script:
```bash
# adapt IPs in script first
./upload_to_all_ec2.sh
```

4. Configure server addresses in `config.py`:
- Update `CLOUD_URL` with Cloud instance's public IP
- Update `EDGE_URL` with Edge instance's public IP

5. Start the services on each instance:
```bash
# run on respective instances (cloud, edge, or iot)
docker-compose -f docker/docker-compose-[layer].yaml up --build
```
Replace [layer] with cloud, edge, or iot depending on which instance you're deploying to.

Make sure the EC2 security groups allow traffic on the required ports (5000 for Cloud, 5001 for Edge).



## Evaluation
Adversaria for evaluation, before it is incorporated into the report.

The dataset consists of 14 images.
- 10 images include persons, 4 no persons
- 6 images include intruder, 8 no intruder

### yolo
2025-01-20 10:53:46 - INFO  - edge.py:process_frame_buffer:146 - yolo_person_detected: 10, yolo_request: 14
yolo accuracy very good!

### rekognition
total intruder detected: 3, total requests: 10
- does not recognize all intruders, one is missing!

### overal system accu. and latency


### table
| img name | yolo person detected | rekognition intruder detected |
| img1     |         True         |                    True       |
| img2     |         False        |                    /          |
| img3     |         False        |                    /          |    sollten beide personen detecten
| img4     |         False        |                    /          |    sollten beide personen detecten
| img5     |         False        |                    /          |
| img6     |         True         |                    True       |
| img7     |         False        |                    /          |
| img8     |         True         |                    True       |
| img9     |         False        |                    /          |
| img10    |         False        |                    /          |    sollte eigentlich true, schwer zu erkennen
| img11    |         False        |                    False      |
| img12    |         True         |                    True       |
| img13    |         False        |                    /          |
| img14    |         False        |                    /          |



### genAI analysis
#### iot
Result

Latency Analysis (in milliseconds):
Average: 1.45
Median: 0.57
Min: 0.09
Max: 7.06
Standard Deviation: 2.52
95th Percentile: 7.06

Distribution:
> 1ms: 1 frames (16.7%)
> 5ms: 1 frames (16.7%)



## TODOs
- [ ] edge is too big - 1.76 GB - due to torch i guess
- [ ] exception handling for no person found°
- [ ] how to use yolo to extract multiple persons
- [ ] face detection model - train own  model for detecting faces

- [ ] person tracking with yolo
- [ ] handle errors in flask app (with decorators, i guess?)
- [ ] limit frame sending in iot. not every frame has to be sended, maybe just one frame every second. 


- [ ] evaluation: 
    - [ ] YOLO precision, maybe comparision for different yolo models
    - [ ] Rekognition precision
    - [ ] overal precision/accuracy
    - [ ] latency of the network
    - [ ] some kind of cpu, memory, network usage would be nice!
    - [ ] connect one container to it, where you can send life photos - for presentation
    - [ ] test images for evaluation setup. 


- [ ] report:       
    - what to change/adapt in report?
    - [ ] security and fault tolerance in report
    - [ ] inconsistencies from prior versions: IOT-EDGE commication: HTTP vs message queue



###### TODO heute
- [ ] evaluation for: 
    - [x] edge
    - [x] iot
    - [x] comparision simulated latency vs real latency
    - [x] again accuracy on test set, with improved cloud

- [ ] fix exception handling
- [x] deploy everything and evaluate
- [ ] update README for new IP handling scheme
- [x] disable photo saving on edge
- [x] turn off metric collection on real deployment

