# PySpark-Bio-Realtime-Operator-Metric
<img src="https://github.com/nguyen187/Realtime-Platform-Kafka-Pyspark-ML_Model-Postgresql-Grafana/blob/main/Architecture.png" width="600">
## Overview
**PySpark-Bio-Realtime-Operator-Metric** is a real-time data processing system built using Apache Spark and PySpark, designed for handling large-scale bioinformatics streaming data. The system supports real-time metric computation and visualization for bio-related operations.

## Features
- Real-time data processing with PySpark.
- Docker-based deployment for seamless setup and execution.
- Modular job execution for different bioinformatics operations.
- Data generation scripts to simulate real-time processing scenarios.

## Prerequisites
Ensure you have the following installed before running the project:
- Docker & Docker Compose
- Python 3.x
- Apache Spark (for manual job execution if needed)

## Setup
### Set Working Directory
```sh
export PROJECT_BIO_REALTIME_DEMO=$(pwd)
```

### Start All Services
Use Docker Compose to start all necessary services:
```sh
docker compose -f ./docker/docker-compose.yaml up -d
```

## Running PySpark Jobs
### Operation Job
```sh
cd ./PySpark-Bio-Demo/
bash submit-job.sh operation
```

### Raman Job
```sh
cd ./PySpark-Bio-Demo/
bash submit-job.sh raman
```

## Generating Sample Data
Simulate real-time data streams for testing and validation.

### Generate Data for Operation
```sh
cd ./generate-data/operation/
python operation-realtime-generate.py
```

### Generate Data for Raman
```sh
cd ./generate-data/raman/
python raman-realtime-generate.py
```

## Project Structure
```
PySpark-Bio-Realtime-Operator-Metric/
│-- docker/
│   ├── docker-compose.yaml  # Configuration for Docker services
│-- PySpark-Bio-Demo/
│   ├── submit-job.sh        # Script to submit PySpark jobs
│-- generate-data/
│   ├── operation/
│   │   ├── operation-realtime-generate.py  # Data generator for Operation
│   ├── raman/
│   │   ├── raman-realtime-generate.py  # Data generator for Raman
```

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

## Contact
For any questions or support, please reach out via thanhnguyen187201@gmail.com.
