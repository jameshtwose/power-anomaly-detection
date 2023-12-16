# %%
from sqlalchemy import create_engine, text
from models import ExampleTable, AnomaliesTable
import pandas as pd

# %%
# engine = create_engine("postgresql://postgres:mysecretpassword@localhost:5432")
# engine = create_engine("postgresql://admin:admin@localhost:5432/dev")
engine = create_engine("postgresql://trino:trino@localhost:5432/postgres")
# %%
with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    print(result.all())
    conn.commit()
    
# %%
# create the example table
try:
    ExampleTable.__table__.create(engine)
except Exception as e:
    print(e)
    
try:
    AnomaliesTable.__table__.create(engine)
except Exception as e:
    print(e)
# %%
# insert a row
with engine.connect() as conn:
    conn.execute(
        ExampleTable.__table__.insert(),
        {"name": "test", "value": 1.0}
    )
    conn.commit()
# %%
# query the table
# %%
with engine.connect() as conn:
    result = conn.execute(
        ExampleTable.__table__.select()
    )
    print(result.all())
# %%
with engine.connect() as conn:
    df = pd.read_sql(
        ExampleTable.__table__.select(),
        conn
    )
# %%
df
# %%
# drop anomaly table
# AnomaliesTable.__table__.drop(engine)
# %%
