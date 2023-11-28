# power-anomaly-detection
This is a mock anomaly detection project. Mock data is streamed using Kafka to Trino, a trained model attempts to identify anomalies and the predicted anomalies are inserted into a mysql table. A streamlit frontend is there to see the continuous time series data and to insert anomalies to test the detection algorithm
