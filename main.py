from data_creation import kafka_producer_power
from multiprocessing import Process
import time
import pandas as pd
import random
import joblib
import pandas as pd
from glob import glob


def run_kafka_producer_power():
    # model = joblib.load("ar_random_forest.joblib")

    glob_choice = random.choice([0, 1, 2])

    df = pd.read_csv(glob("example_data/*.csv")[glob_choice])

    # y_pred = model.predict(df.loc[:, ["l1", "l2", "l3"]])
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
            # y_pred = model.predict(df.loc[:, ["l1", "l2", "l3"]])
            row_count = 0
        time.sleep(5)


if __name__ == "__main__":
    p1 = Process(target=run_kafka_producer_power)
    p1.start()
    # p2 = Process(target=kafka_consumer_power)
    # p2.start()
