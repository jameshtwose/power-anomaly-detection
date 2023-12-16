from data_creation import kafka_producer_power
from multiprocessing import Process
import time
import pandas as pd
import random
from glob import glob
import sys
from streamlit.web import cli as stcli


def run_dashboard():
    sys.argv = ["streamlit", "run", "dashboard.py"]
    sys.exit(stcli.main())


def run_kafka_producer_power():
    glob_choice = random.choice([0, 1, 2])
    df = pd.read_csv(glob("example_data/*.csv")[glob_choice])
    row_count = 0
    while True:
        new_request_dict = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "l1": df.iloc[row_count, 0],
            "l2": df.iloc[row_count, 1],
            "l3": df.iloc[row_count, 2],
        }
        _ = kafka_producer_power(request_dict=new_request_dict)
        row_count += 1
        if row_count == df.shape[0]:
            glob_choice = random.choice([0, 1, 2])
            df = pd.read_csv(glob("example_data/*.csv")[glob_choice])
            row_count = 0
        time.sleep(10)


if __name__ == "__main__":
    p1 = Process(target=run_kafka_producer_power)
    p1.start()
    p2 = Process(target=run_dashboard)
    p2.start()
