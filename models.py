from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean

Base = declarative_base()

class ExampleTable(Base):
    __tablename__ = 'example_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Float)
    
    def __repr__(self):
        return f"<ExampleTable(name={self.name}, value={self.value})>"
    
class AnomaliesTable(Base):
    __tablename__ = 'anomalies_table'
    # id = Column(Integer, primary_key=True, autoincrement=True)
    l1 = Column(Float)
    l2 = Column(Float)
    l3 = Column(Float)
    timestamp = Column(DateTime, primary_key=True)
    hard_cutoff_prediction = Column(Boolean)
    gaussian_scorer_prediction = Column(Boolean)
    
    def __repr__(self):
        return f"<AnomaliesTable(name={self.name}, value={self.value})>"
