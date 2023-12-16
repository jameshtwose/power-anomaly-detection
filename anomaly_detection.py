import pandas as pd
import random
import pickle
from river import anomaly

with open("GaussianScorer_model.pkl", "rb") as f:
    gaussian_scorer_detector = pickle.load(f)


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


def hard_cutoff_anomaly_detector(row: pd.Series, cutoff: float = 210.5):
    if row["l1"] < cutoff:
        return True
    elif row["l2"] < cutoff:
        return True
    elif row["l3"] < cutoff:
        return True
    else:
        return False


def gaussian_scorer_anomaly_detector(
    row: pd.Series,
    detector=gaussian_scorer_detector,
    cutoff_percentile: float = 0.9,
):
    if detector.score_one(None, row["l1"]) >= cutoff_percentile:
        return True
    elif detector.score_one(None, row["l2"]) >= cutoff_percentile:
        return True
    elif detector.score_one(None, row["l3"]) >= cutoff_percentile:
        return True
    else:
        return False


def online_training(
    data, model: object = anomaly.GaussianScorer(grace_period=50)
):
    for i in range(data.shape[0] - 1):
        model.learn_one(None, data.iloc[i, :].values[0])
    return model
