from sqlalchemy import Column, Integer, String, DateTime, Float, func
from base import Base
import datetime

class ThermostatEvent(Base):
    """ Thermostat Event """
    
    __tablename__ = "thermostat_event"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(50), nullable=False)
    temperature = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False, default=func.now())

    def __init__(self, trace_id, temperature, status, timestamp):
        self.trace_id = trace_id
        self.temperature = temperature
        self.status = status
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'trace_id': self.trace_id,
            'temperature': self.temperature,
            'status': self.status,
            'timestamp': self.timestamp,
            'date_created': self.date_created.strftime("%Y-%m-%d %H:%M:%S")
        }


class LightingEvent(Base):
    """ Lighting Event """

    __tablename__ = "lighting_event"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(50), nullable=False)
    intensity = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False, default=func.now())

    def __init__(self, trace_id, intensity, status, timestamp):
        self.trace_id = trace_id
        self.intensity = intensity
        self.status = status
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'trace_id': self.trace_id,
            'intensity': self.intensity,
            'status': self.status,
            'timestamp': self.timestamp,
            'date_created': self.date_created.strftime("%Y-%m-%d %H:%M:%S")
        }