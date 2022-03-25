# Docker-Compose-Containers

IF YOU WANT TO GET THE PIPELINE SIMULATION WORKING ON YOUR MACHINE (Ubuntu 20.04): 

1. Pull the current git repo
2. Modify the start script.sh to start grafana the way the rest of the containers are started (docker-compose up -d)
3. Run ipconfig and find the "docker0" ip address associated with the docker bridge on your machine
4. Replace the IPs in the following files with the  ip found in step 3.
  4.1. kafka/docker-compose.yml
  4.2. producer/producer.py
  4.3. consumer/consumer.py
  4.4. grafana/provisions/datasource/databases.yml
5. Run the start script
6. Restart the consumer with 
docker-compose down && docker-compose up -d

You should now see data in grafana/populating in the sensordata table of your timescale instance (inside sensorsdb database)

You can then run docker ps in your terminal to determine the localhost ports each docker container is forwarding to
  - Grafana: 3000
  - Timescale: 5432
  - Kafka: 9092

The consumer and producer will also appear on this list but are not binded to a port. These are just python scripts executing in "empty" containers.
