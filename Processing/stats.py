from sqlalchemy import Column, Integer, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Stats(Base):
    """ Event Statistics """
    
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    number_of_thermostat_events = Column(Integer, default=0)
    number_of_lighting_events = Column(Integer, default=0)
    average_temperature = Column(Float, nullable=True)  # Allow NULL values
    average_light_intensity = Column(Float, nullable=True)  # Allow NULL values

    last_updated = Column(DateTime)

    def __init__(self, number_of_thermostat_events, number_of_lighting_events, average_temperature, average_light_intensity, last_updated=None):
        self.number_of_thermostat_events = number_of_thermostat_events
        self.number_of_lighting_events = number_of_lighting_events
        self.average_temperature = round(average_temperature, 2) if average_temperature is not None else None
        self.average_light_intensity = round(average_light_intensity, 2) if average_light_intensity is not None else None
        self.last_updated = last_updated if last_updated is not None else datetime.datetime.now()

    def to_dict(self):
        return {
            'number_of_thermostat_events': self.number_of_thermostat_events,
            'number_of_lighting_events': self.number_of_lighting_events,
            'average_temperature': self.average_temperature,
            'average_light_intensity': self.average_light_intensity,
            'last_updated': self.last_updated.strftime("%Y-%m-%d %H:%M:%S")
        }
