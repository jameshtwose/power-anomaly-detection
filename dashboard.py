import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from ast import literal_eval
import time
import plotly.express as px
from anomaly_detection import create_simple_anomaly, hard_cutoff_anomaly_detector
from data_creation import kafka_producer_power

st.title("Power Data Dashboard")
st.write("This is a dashboard for power data")

engine = create_engine("trino://admin@localhost:8080")

pl1 = st.empty()
pl2 = st.empty()
pl3 = st.empty()

with st.sidebar:
    st.write("Add a new anomaly")
    amount = st.number_input("Amount", value=210, max_value=245)
    button_clicked = st.button("Add anomaly")
    if button_clicked:
        _ = kafka_producer_power(request_dict=create_simple_anomaly(anomaly_number=amount))
        time.sleep(5)

while True:
    with engine.connect() as conn:
        pre_df = pd.read_sql(
            text("select * from kafka.power.power_data where _timestamp > current_timestamp - interval '70' minute"),
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
    pl1.plotly_chart(fig)
    
    with engine.connect() as conn:
        anom_df = pd.read_sql(
            text("select * from postgres.public.anomalies_table where timestamp > current_timestamp - interval '10' minute"),
            conn
        )
    pl2.write(anom_df)
    
    latest_row = df.iloc[-1, :]
    
    if hard_cutoff_anomaly_detector(latest_row):
        with engine.connect() as conn:
            conn.execute(
                text("insert into postgres.public.anomalies_table values (:l1, :l2, :l3, :timestamp, :hard_cutoff_prediction)"),
                {
                    "l1": latest_row["l1"],
                    "l2": latest_row["l2"],
                    "l3": latest_row["l3"],
                    "timestamp": pd.to_datetime(latest_row["timestamp"]),
                    "hard_cutoff_prediction": True
                }
            )
            conn.commit()
    
    time.sleep(5)