# %%
import pandas as pd
from glob import glob
from sklearn.ensemble import RandomForestRegressor
import seaborn as sns
import joblib

# %%
pre_df = pd.read_csv(
    glob("data/*")[2],
    # index_col=0,
    parse_dates=True,
).loc[:, ["MEASUREMENT_CD_OMSCHRIJVING", "MEETWAARDE", "DT_MEETWAARDE"]]
# %%
df = (
    pre_df.pivot_table(
        index="DT_MEETWAARDE",
        columns="MEASUREMENT_CD_OMSCHRIJVING",
        values="MEETWAARDE",
    )
    .reset_index()
    .rename(
        columns={
            "DT_MEETWAARDE": "timestamp",
            "Avg. voltage L1 (V)": "l1",
            "Avg. voltage L2 (V)": "l2",
            "Avg. voltage L3 (V)": "l3",
        }
    )
    .loc[:, ["timestamp", "l1", "l2", "l3"]]
    .assign(
        **{
            "timestamp": lambda x: pd.to_datetime(
                x["timestamp"], format="%d/%m/%Y %H:%M"
            ),
        }
    )
    .dropna(axis="index")
    .set_index("timestamp")
    # normalize data frame df with mean of 0 and variance of 1
    # .apply(lambda x: (x - x.mean()) / x.std())
    # min max normalize
    # .apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    .reset_index()
)
df.columns.name = None
# %%
model = RandomForestRegressor(random_state=42)

# %%
# lag the data
X_df = df.loc[:, ["l1", "l2", "l3"]]
y_df = df.set_index("timestamp").shift(1).reset_index().fillna(230).loc[:, ["l1", "l2", "l3"]]
# %%
_ = model.fit(X_df, y_df)
# %%
model.predict(pd.DataFrame([[230, 230, 230]], columns=["l1", "l2", "l3"]))
# %%
y_pred = model.predict(X_df)
# %%
y_pred_df = pd.DataFrame(y_pred, columns=["l1", "l2", "l3"])
# %%
_ = sns.lineplot(
    data=y_pred_df.reset_index().melt(
        id_vars=["index"], value_vars=["l1", "l2", "l3"], var_name="measurement"
    ),
    x="index",
    y="value",
    hue="measurement",
)
# %%
_ = sns.lineplot(
    data=X_df.reset_index().melt(
        id_vars=["index"], value_vars=["l1", "l2", "l3"], var_name="measurement"
    ),
    x="index",
    y="value",
    hue="measurement",
)
# %%
joblib.dump(model, "ar_random_forest.joblib")
# %%
model = joblib.load("ar_random_forest.joblib")
# %%
model.predict(pd.DataFrame([[230, 230, 230]], columns=["l1", "l2", "l3"]))
# %%
y_pred_df.to_csv("example_data/meter_3.csv", index=False)

# %%
