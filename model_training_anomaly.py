# %%
import pandas as pd
from glob import glob
from river import anomaly
import pickle

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
# %%
detector = anomaly.GaussianScorer(grace_period=50)
# %%
for i in range(df.shape[0]-10):
    detector.learn_one(None, df.iloc[i, :].values[0])
# %%
detector.score_one(None, df.iloc[-1, 0])
# %%
detector.score_one(None, df.iloc[-1, 2])
# %%
with open('GaussianScorer_model.pkl', 'wb') as f:
    pickle.dump(detector, f)
# %%
with open('GaussianScorer_model.pkl', 'rb') as f:
    detector = pickle.load(f)