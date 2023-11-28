# power-anomaly-detection
This is a mock anomaly detection project. Mock data is streamed using Kafka to Trino, a trained model attempts to identify anomalies and the predicted anomalies are inserted into a mysql table. A streamlit frontend is there to see the continuous time series data and to insert anomalies to test the detection algorithm

## Kafka Setup
- `docker-compose up -d`
- `docker exec -it power-anomaly-detection-kafka-1 bash` - enter the kafka container
- `cd /opt/bitnami/kafka/bin`
- `kafka-topics.sh --create --topic powerData --bootstrap-server localhost:9093`
- (Optional) `kafka-console-consumer.sh --topic powerData --from-beginning --bootstrap-server localhost:9093` - check if data is in the topic
- `exit` - exit the kafka container

## Postgres Setup
- `docker run -p 61661:5432 --name new-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres`
- `docker exec -it new-postgres psql -U postgres`
- `exit` - exit the postgres container

## Trino Server Setup
- `docker run -p 8080:8080 --name trino trinodb/trino`
- `docker exec -it trino bash`
- copy paste the files in `example_configuration` to the trino container
<!-- - `docker cp ./example_configuration/ trino:/etc/trino/` -->
- `docker cp ./example_configuration/catalog/kafka.properties trino:/etc/trino/catalog/kafka.properties`
- `docker cp ./example_configuration/catalog/mysql.properties trino:/etc/trino/catalog/mysql.properties`

## Trino CLI Setup
- `docker run -it --rm --network host trinodb/trino:latest trino --server localhost:8080`
- `show catalogs;`
- `show schemas in kafka;`