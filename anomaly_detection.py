import pandas as pd
import random

def create_simple_anomaly(anomaly_number: int = 210):
    new_request_dict = {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "l1": random.randint(230, 235),
        "l2": random.randint(230, 235),
        "l3": random.randint(230, 235),
    }
    l_choice = random.choice(["l1", "l2", "l3"])
    new_request_dict[l_choice] = anomaly_number
    return new_request_dict

def hard_cutoff_anomaly_detector(
    row: pd.Series,
    cutoff: float = 210.5
    ):
    if row["l1"] < cutoff:
        return True
    elif row["l2"] < cutoff:
        return True
    elif row["l3"] < cutoff:
        return True
    else:
        return False