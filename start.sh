cd kafka
docker-compose up -d &&\

cd ../timescaledb 
docker-compose up -d &&\

cd ../consumer
docker-compose up -d &&\

cd ../producer 
docker-compose up -d &&\

cd ../grafana
docker-compose -H ssh://pi@10.42.0.32 up -d
