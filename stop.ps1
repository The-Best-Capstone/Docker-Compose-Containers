cd producer 
docker-compose down

cd ../consumer
docker-compose down

cd ../kafka
docker-compose down

cd ../grafana 
docker-compose down

cd ../timescaledb 
docker-compose down

cd ..

# print 
docker ps -a