from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class ThermostatEvent(Base):
    __tablename__ = "thermostat_event"
    
    id = Column(Integer, primary_key=True)
    trace_id = Column(String(50), nullable=False)
    temperature = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    date_created = Column(DateTime, nullable=False, default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'trace_id': self.trace_id,
            'temperature': self.temperature,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'date_created': self.date_created.isoformat()
        }

class LightingEvent(Base):
    __tablename__ = "lighting_event"
    
    id = Column(Integer, primary_key=True)
    trace_id = Column(String(50), nullable=False)
    intensity = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    date_created = Column(DateTime, nullable=False, default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'trace_id': self.trace_id,
            'intensity': self.intensity,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'date_created': self.date_created.isoformat()
        }
