import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from ast import literal_eval
import time
import plotly.express as px
from anomaly_detection import (
    create_simple_anomaly,
    hard_cutoff_anomaly_detector,
    elliptic_envelope_anomaly_detector,
    gaussian_scorer_anomaly_detector,
    half_space_trees_anomaly_detector,
    local_outlier_factor_anomaly_detector,
    one_class_svm_anomaly_detector,
)
from data_creation import kafka_producer_power

st.set_page_config(layout="wide", page_title="Power Data Dashboard", page_icon="🔌")

st.title("Power Data Dashboard")
st.write("This is a dashboard for power data")

engine = create_engine("trino://admin@localhost:8080")

pl1 = st.empty()
pl2 = st.empty()
pl3 = st.empty()

with st.sidebar:
    st.write("Add a new anomaly")
    amount = st.number_input("Amount", value=210.0, max_value=300.0, step=0.1)
    button_clicked = st.button("Add anomaly")
    if button_clicked:
        _ = kafka_producer_power(
            request_dict=create_simple_anomaly(anomaly_number=amount)
        )
        time.sleep(5)

while True:
    with engine.connect() as conn:
        pre_df = pd.read_sql(
            text(
                "select * from kafka.power.power_data where _timestamp > current_timestamp - interval '70' minute"
            ),
            conn,
        )
    df = pre_df["_message"].apply(literal_eval).apply(pd.Series)

    df_melt = df.melt(
        id_vars=["timestamp"],
        value_vars=["l1", "l2", "l3"],
        var_name="measurement",
    )
    fig = px.line(df_melt, x="timestamp", y="value", color="measurement", markers=True)
    pl1.plotly_chart(fig, use_container_width=True)

    with engine.connect() as conn:
        anom_df = pd.read_sql(
            text(
                "select * from postgres.public.anomalies_table where timestamp > current_timestamp - interval '5' minute"
            ),
            conn,
        )
    pl2.dataframe(
        anom_df.sort_values("timestamp", ascending=False), use_container_width=True
    )

    latest_rows = df.tail(10)

    # per latest rows check if there is an anomaly and if so, add it to the database,
    # do not add if it is already in the database
    for _, latest_row in latest_rows.iterrows():
        hard_cutoff_prediction = hard_cutoff_anomaly_detector(row=latest_row)
        elliptic_envelope_prediction = elliptic_envelope_anomaly_detector(
            row=latest_row
        )
        gaussian_scorer_prediction = gaussian_scorer_anomaly_detector(
            row=latest_row, cutoff_percentile=0.95
        )
        half_space_trees_prediction = half_space_trees_anomaly_detector(
            row=latest_row, cutoff_percentile=0.95
        )
        local_outlier_factor_prediction = local_outlier_factor_anomaly_detector(
            row=latest_row
        )
        one_class_svm_prediction = one_class_svm_anomaly_detector(row=latest_row)

        if any([hard_cutoff_prediction, gaussian_scorer_prediction]):
            with engine.connect() as conn:
                check_df = pd.read_sql(
                    text(
                        "select * from postgres.public.anomalies_table where timestamp > current_timestamp - interval '1' minute"
                    ),
                    conn,
                )
            if latest_row["timestamp"] not in check_df["timestamp"].values:
                with engine.connect() as conn:
                    new_anomalies_df = pd.DataFrame(
                        {
                            "l1": latest_row["l1"],
                            "l2": latest_row["l2"],
                            "l3": latest_row["l3"],
                            "timestamp": pd.to_datetime(latest_row["timestamp"]),
                            "hard_cutoff_prediction": hard_cutoff_prediction,
                            "elliptic_envelope_prediction": elliptic_envelope_prediction,
                            "gaussian_scorer_prediction": gaussian_scorer_prediction,
                            "half_space_trees_prediction": half_space_trees_prediction,
                            "local_outlier_factor_prediction": local_outlier_factor_prediction,
                            "one_class_svm_prediction": one_class_svm_prediction,
                        },
                        index=[0],
                    )
                    # get the rows that are not in the database yet
                    new_anomalies_df = new_anomalies_df[
                        ~new_anomalies_df["timestamp"].isin(
                            check_df["timestamp"].values
                        )
                    ]
                    insert_statement = text(
                        "insert into postgres.public.anomalies_table (l1, l2, l3, timestamp, hard_cutoff_prediction, elliptic_envelope_prediction, gaussian_scorer_prediction, half_space_trees_prediction, local_outlier_factor_prediction, one_class_svm_prediction) values (:l1, :l2, :l3, :timestamp, :hard_cutoff_prediction, :elliptic_envelope_prediction, :gaussian_scorer_prediction, :half_space_trees_prediction, :local_outlier_factor_prediction, :one_class_svm_prediction)"
                    )
                    for _, row in new_anomalies_df.iterrows():
                        conn.execute(
                            insert_statement,
                            {
                                "l1": row["l1"],
                                "l2": row["l2"],
                                "l3": row["l3"],
                                "timestamp": row["timestamp"],
                                "hard_cutoff_prediction": row["hard_cutoff_prediction"],
                                "elliptic_envelope_prediction": row[
                                    "elliptic_envelope_prediction"
                                ],
                                "gaussian_scorer_prediction": row[
                                    "gaussian_scorer_prediction"
                                ],
                                "half_space_trees_prediction": row[
                                    "half_space_trees_prediction"
                                ],
                                "local_outlier_factor_prediction": row[
                                    "local_outlier_factor_prediction"
                                ],
                                "one_class_svm_prediction": row[
                                    "one_class_svm_prediction"
                                ],
                            },
                        )

    time.sleep(5)
