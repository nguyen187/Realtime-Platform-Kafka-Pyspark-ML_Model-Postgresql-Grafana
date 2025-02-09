# PySpark-Bio-Realtime-Operator-Metric
# Set working dir PROJECT_BIO_REALTIME_DEMO
# run all service setup by docker compose
docker compose -f ./docker/docker-compose.yaml up -d
# run job
## Operation
cd ./PySpark-Bio-Demo/
bash submit-job.sh operation
## Raman
cd ./PySpark-Bio-Demo/
bash submit-job.sh raman

# run generate data
## Operation 
cd ./generate-data/operation/
python operation-realtime-generate.py
## Raman 
cd ./generate-data/raman/
python raman-realtime-generate.py