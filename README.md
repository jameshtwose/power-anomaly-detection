# power-anomaly-detection
This is a mock anomaly detection project. Mock data is streamed using Kafka to Trino, a trained model attempts to identify anomalies and the predicted anomalies are inserted into a mysql table. A streamlit frontend is there to see the continuous time series data and to insert anomalies to test the detection algorithm

## Setup
- `pip install -r requirements.txt`
- `docker-compose up -d`
- `docker exec -it power-anomaly-detection-kafka-1 bash` - enter the kafka container
- `cd /opt/bitnami/kafka/bin`
- `kafka-topics.sh --create --topic power.power_data --bootstrap-server localhost:9093`
- (Optional) `kafka-console-consumer.sh --topic power.power_data --from-beginning --bootstrap-server localhost:9093` - check if data is in the topic
- `exit` - exit the kafka container
- create the necessary tables in postgres
    - `python connection_sandbox_postgres.py`

## Run
- `streamlit run dashboard.py`

## Extras
- check what ports are in use: `sudo lsof -i -P -n | grep LISTEN`
- kill a process: `sudo kill -9 <PID>`