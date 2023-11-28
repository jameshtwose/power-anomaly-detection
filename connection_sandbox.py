# %%
from sqlalchemy import create_engine, text
# %%
engine = create_engine("postgresql://postgres:mysecretpassword@localhost:61661")
# %%
with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    print(result.all())
    conn.commit()
    
# %%
