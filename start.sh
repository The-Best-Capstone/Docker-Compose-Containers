cd kafka
docker-compose up -d

cd ../timescaledb 
docker-compose up -d

cd ../grafana 
docker-compose up -d 

cd ../consumer
docker-compose up -d 

cd ../producer 
docker-compose up -d