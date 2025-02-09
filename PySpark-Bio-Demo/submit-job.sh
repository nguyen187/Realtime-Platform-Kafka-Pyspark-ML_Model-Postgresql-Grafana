#!/bin/bash

# Accept operation as a parameter
job=$1

# If no parameter is provided, use a default value (optional)
if [ -z "$job" ]; then
    job="operation"
fi
echo "Running job: $job"
make build

docker exec -it ktech_spark bash -c "cd /app/dist/ && spark-submit --verbose --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.postgresql:postgresql:42.5.6 \
--driver-java-options '-Dlog4j.configuration=file:log4j.properties' \
--conf spark.ui.enabled=true \
--deploy-mode client \
--conf spark.dynamicAllocation.enabled=false \
--executor-memory 1G \
--executor-cores 1 \
--num-executors 1 \
--conf spark.dynamicAllocation.minExecutors=1 \
--conf spark.dynamicAllocation.maxExecutors=1 \
--conf spark.cores.max=1 \
--conf spark.executor.memoryOverhead=256 \
--py-files jobs.zip,libs.zip main.py --job $job"

