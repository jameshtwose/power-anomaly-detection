# %%
import pandas as pd
from glob import glob
from river import anomaly
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.covariance import EllipticEnvelope
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from anomaly_detection import create_simple_anomaly

# %%
df = (
    # pd.read_csv(glob("example_data/*.csv")[0])
    pd.concat([x for x in map(pd.read_csv, glob("example_data/*.csv"))])
    .assign(
        **{
            "timestamp": lambda x: pd.date_range(
                start=pd.Timestamp.now(), periods=x.shape[0], freq="5s"
            )
        }
    )
    .set_index("timestamp")
)
df.head()


# %%
def train_test_save_plot_model(
    data: pd.DataFrame = df.copy(deep=True),
    model: object = anomaly.GaussianScorer(grace_period=50),
):
    # plot initial data
    plot_df = data.reset_index().melt(
        id_vars=["timestamp"], value_vars=["l1", "l2", "l3"]
    )
    _ = sns.lineplot(data=plot_df, x="timestamp", y="value", hue="variable")
    _ = plt.title("Initial Data")
    _ = plt.show()

    # train
    if model.__class__.__name__ == "GaussianScorer":
        for i in range(df.shape[0] - 10):
            model.learn_one(None, df.iloc[i, :].values[0])
    elif "sklearn" in model.__module__:
        model.fit(data)
    else:
        for i in range(df.shape[0] - 10):
            model.learn_one(df.iloc[i, :].to_dict())
    # save
    with open(f"ml_models/{model.__class__.__name__}_model.pkl", "wb") as f:
        pickle.dump(model, f)

    # add some outliers at different times
    data.loc[
        data.sample(1, random_state=42).index.values[0] + pd.Timedelta(seconds=3),
        :,
    ] = [210, 240, 241]
    data.loc[
        data.sample(1, random_state=43).index.values[0] + pd.Timedelta(seconds=3),
        :,
    ] = [240, 209, 241]
    data.loc[
        data.sample(1, random_state=44).index.values[0] + pd.Timedelta(seconds=3),
        :,
    ] = [239, 240, 208]

    # plot new data
    plot_df = data.reset_index().melt(
        id_vars=["timestamp"], value_vars=["l1", "l2", "l3"]
    )
    _ = sns.lineplot(data=plot_df, x="timestamp", y="value", hue="variable")
    _ = plt.title("Data With Outliers")
    _ = plt.show()

    # plot scores
    print("Scores for l1, l2, l3 outliers:")
    if model.__class__.__name__ == "GaussianScorer":
        for line in ["l1", "l2", "l3"]:
            print(model.score_one(None, data.loc[lambda x: x[line] < 210.5, line]))
    elif "sklearn" in model.__module__:
        for line in ["l1", "l2", "l3"]:
            # sklearn models return -1 for outliers and 1 for inliers
            print(model.predict(data.loc[lambda x: x[line] < 210.5, :]))
    else:
        for line in ["l1", "l2", "l3"]:
            print(model.score_one(data.loc[lambda x: x[line] < 210.5, line]))
    return model


# %%
# GaussianScorer - river
_ = train_test_save_plot_model()

# %%
# HalfSpaceTrees - river
_ = train_test_save_plot_model(
    model=anomaly.HalfSpaceTrees(
        n_trees=10,
        height=15,
        window_size=100,
        seed=42,
        limits={"limits": (df.min().min(), df.max().max())}
    )
)

# %%
with open("ml_models/HalfSpaceTrees_model.pkl", "rb") as f:
    half_space_trees_detector = pickle.load(f)
# %%
half_space_trees_detector.score_one({"l1": 1000,
                                     "l2": 10000,
                                     "l3": 10000})
# %%
# EllipticEnvelope - sklearn
_ = train_test_save_plot_model(
    model=EllipticEnvelope(contamination=0.05, random_state=42)
)
# %%
# LocalOutlierFactor - sklearn
_ = train_test_save_plot_model(
    model=LocalOutlierFactor(n_neighbors=20, contamination=0.05,
                             novelty=True)
)
# %%
# OneClassSVM - sklearn
_ = train_test_save_plot_model(
    model=OneClassSVM(nu=0.05, kernel="rbf", gamma=0.1)
)
# %%
with open("ml_models/EllipticEnvelope_model.pkl", "rb") as f:
    elliptic_envelope_detector = pickle.load(f)
# %%
elliptic_envelope_detector.predict([[210, 230, 230]])[0]
# %%
