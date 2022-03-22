cd producer 
docker-compose down

cd ../consumer
docker-compose down

cd ../kafka
docker-compose down

cd ../timescaledb 
docker-compose down

cd ../grafana 
docker-compose -H ssh://pi@10.42.0.32 down

# print 
docker ps -a
