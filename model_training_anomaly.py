# %%
import pandas as pd
from glob import glob
from river import anomaly
import pickle
import seaborn as sns

# %%
df = (
    pd.read_csv(glob("example_data/*.csv")[0])
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
plot_df = df.reset_index().melt(
    id_vars=["timestamp"], value_vars=["l1", "l2", "l3"]
)
_ = sns.lineplot(data=plot_df, x="timestamp", y="value", hue="variable")

# %%
detector = anomaly.GaussianScorer(grace_period=50)
# %%
for i in range(df.shape[0] - 10):
    detector.learn_one(None, df.iloc[i, :].values[0])
# %%
detector.score_one(None, df.iloc[-1, 0])
# %%
detector.score_one(None, df.iloc[-1, 2])
# %%
with open("GaussianScorer_model.pkl", "wb") as f:
    pickle.dump(detector, f)
# %%
with open("GaussianScorer_model.pkl", "rb") as f:
    detector = pickle.load(f)
# %%
# add some outliers at different times
df.loc[
    df.sample(1, random_state=42).index.values[0] + pd.Timedelta(seconds=3),
    "l1",
] = 210
df.loc[
    df.sample(1, random_state=43).index.values[0] + pd.Timedelta(seconds=3),
    "l2",
] = 209
df.loc[
    df.sample(1, random_state=44).index.values[0] + pd.Timedelta(seconds=3),
    "l3",
] = 208
# %%
plot_df = df.reset_index().melt(
    id_vars=["timestamp"], value_vars=["l1", "l2", "l3"]
)
_ = sns.lineplot(data=plot_df, x="timestamp", y="value", hue="variable")
# %%
for line in ["l1", "l2", "l3"]:
    print(detector.score_one(None, df.loc[lambda x: x[line] < 210.5, line]))
# %%

# %%
