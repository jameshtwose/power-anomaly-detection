from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class ExampleTable(Base):
    __tablename__ = 'example_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Float)
    
    def __repr__(self):
        return f"<ExampleTable(name={self.name}, value={self.value})>"