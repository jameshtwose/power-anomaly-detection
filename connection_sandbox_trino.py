# %%
from sqlalchemy import create_engine, text
import pandas as pd
from ast import literal_eval

# %%
engine = create_engine("trino://admin@localhost:8080")
# %%
with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    print(result.all())
    conn.commit()

# %%
with engine.connect() as conn:
    result = conn.execute(
        text("show catalogs")
    )
    print(result.all())
    conn.commit()
# %%
with engine.connect() as conn:
    result = conn.execute(
        text("show schemas from postgres")
    )
    print(result.all())
    conn.commit()
# %%
with engine.connect() as conn:
    result = conn.execute(
        text("show tables from postgres.public")
    )
    print(result.all())
    conn.commit()
# %%
with engine.connect() as conn:
    result = conn.execute(
        text("select * from postgres.public.example_table")
    )
    print(result.all())
    conn.commit()
# %%
with engine.connect() as conn:
    result = conn.execute(
        text("show tables from kafka.power")
    )
    print(result.all())
    conn.commit()
# %%
with engine.connect() as conn:
    result = conn.execute(
        text("select * from kafka.power.power_data")
    )
    print(result.all())
    conn.commit()
# %%
with engine.connect() as conn:
    pre_df = pd.read_sql(
        text("select * from kafka.power.power_data where _timestamp > current_timestamp - interval '61' minute"),
        conn
    )
# %%
df = pre_df["_message"].apply(literal_eval).apply(pd.Series)
# %%
df
# %%
df_melt = df.melt(
        id_vars=["timestamp"],
        value_vars=["l1", "l2", "l3"],
        var_name="measurement"
    )
# %%
df_melt
# %%

# %%
