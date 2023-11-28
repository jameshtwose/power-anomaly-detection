from data_creation import kafka_producer_power, kafka_consumer_power
from multiprocessing import Process
import time

def run_kafka_producer_power():
    while True:
        kafka_producer_power()
        time.sleep(5)

if __name__ == "__main__":
    p1 = Process(target=run_kafka_producer_power)
    p1.start()
    # p2 = Process(target=kafka_consumer_power)
    # p2.start()