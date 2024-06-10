from sqlalchemy import Column, Integer, String, Float, ForeignKey, BigInteger, TIMESTAMP, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
from sqlalchemy import Column, Integer, Float, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number_of_modules = Column(Integer, nullable=False)

    modules = relationship("Module", back_populates="device")

    def __str__(self):
        return f"Device(id={self.id}, number_of_modules={self.number_of_modules})"

class Module(Base):
    __tablename__ = 'modules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)
    module_number = Column(Integer, nullable=False)

    device = relationship("Device", back_populates="modules")
    measurements = relationship("Measurement", back_populates="module")

    def __str__(self):
        return f"Module(id={self.id}, device_id={self.device_id}, module_number={self.module_number})"

class Measurement(Base):
    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    voltage = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    power = Column(Float, nullable=False)
    energy = Column(Float, nullable=False)
    frequency = Column(Float, nullable=False)
    power_factor = Column(Float, nullable=False)

    module = relationship("Module", back_populates="measurements")

    def __str__(self):
        return (f"Measurement(id={self.id}, module_id={self.module_id}, timestamp={self.timestamp}, "
                f"voltage={self.voltage}, current={self.current}, power={self.power}, "
                f"energy={self.energy}, frequency={self.frequency}, power_factor={self.power_factor})")

