from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SensorData(Base):
    __tablename__ = 'sensor_data'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    voltage = Column(String(50), nullable=False)
    current = Column(String(50), nullable=False)
    power = Column(String(50), nullable=False)
    energy = Column(String(50), nullable=False)
    frequency = Column(String(50), nullable=False)
    pf = Column(String(50), nullable=False)
