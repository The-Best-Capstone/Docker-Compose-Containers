cd kafka
docker-compose down

cd ../timescaledb 
docker-compose down

cd ../grafana 
docker-compose down

cd ../consumer
docker-compose down

cd ../producer 
docker-compose down

docker ps -a