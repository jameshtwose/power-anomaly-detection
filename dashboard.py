import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from ast import literal_eval
import time
import plotly.express as px

st.title("Power Data Dashboard")
st.write("This is a dashboard for power data")

engine = create_engine("trino://admin@localhost:8080")

pl = st.empty()

while True:
    with engine.connect() as conn:
        pre_df = pd.read_sql(
            text("select * from kafka.power.power_data where _timestamp > current_timestamp - interval '65' minute"),
            conn
        )
    df = pre_df["_message"].apply(literal_eval).apply(pd.Series)
    
    df_melt = df.melt(
        id_vars=["timestamp"],
        value_vars=["l1", "l2", "l3"],
        var_name="measurement"
    )
    fig = px.line(
        df_melt,
        x="timestamp",
        y="value",
        color="measurement",
        markers=True
    )
    pl.plotly_chart(fig)
    
    time.sleep(5)