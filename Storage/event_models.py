# Import necessary modules from SQLAlchemy and dateutil
from sqlalchemy import Column, Integer, String, DateTime, Float, func
from sqlalchemy.ext.declarative import declarative_base
from dateutil import parser

# Base class for declarative class definitions
Base = declarative_base()

# Define the ThermostatEvent class
class ThermostatEvent(Base):
    """ Thermostat Event """
    __tablename__ = "thermostat_event"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(50), nullable=False)
    temperature = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    date_created = Column(DateTime, nullable=False, default=func.now())

    def __init__(self, trace_id, temperature, status, timestamp):
        self.trace_id = trace_id
        self.temperature = temperature
        self.status = status
        self.timestamp = parser.parse(timestamp)
        self.date_created = func.now()

    def to_dict(self):
        return {
            'id': self.id,
            'trace_id': self.trace_id,
            'temperature': self.temperature,
            'status': self.status,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'date_created': self.date_created.strftime("%Y-%m-%d %H:%M:%S.%f")
        }

# Define the LightingEvent class
class LightingEvent(Base):
    """ Lighting Event """
    __tablename__ = "lighting_event"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(50), nullable=False)
    intensity = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    date_created = Column(DateTime, nullable=False, default=func.now())

    def __init__(self, trace_id, intensity, status, timestamp):
        self.trace_id = trace_id
        self.intensity = intensity
        self.status = status
        self.timestamp = parser.parse(timestamp)
        self.date_created = func.now()

    def to_dict(self):
        return {
            'id': self.id,
            'trace_id': self.trace_id,
            'intensity': self.intensity,
            'status': self.status,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'date_created': self.date_created.strftime("%Y-%m-%d %H:%M:%S.%f")
        }
