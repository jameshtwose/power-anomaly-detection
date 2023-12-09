from data_creation import kafka_producer_power
from multiprocessing import Process
import time
import pandas as pd
import random

def run_kafka_producer_power():
    previous_request_dict = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "l1": 230,
            "l2": 230,
            "l3": 230,
        }
    while True:
        new_request_dict = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "l1": previous_request_dict["l1"] + random.normalvariate(0, 1),
            "l2": previous_request_dict["l2"] + random.normalvariate(0, 1),
            "l3": previous_request_dict["l3"] + random.normalvariate(0, 1),
        }
        previous_request_dict = kafka_producer_power(request_dict=new_request_dict)
        time.sleep(5)

if __name__ == "__main__":
    p1 = Process(target=run_kafka_producer_power)
    p1.start()
    # p2 = Process(target=kafka_consumer_power)
    # p2.start()