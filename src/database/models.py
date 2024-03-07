from sqlalchemy import Column, BigInteger, Boolean, Date, String, Integer, ForeignKey, REAL
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Passenger(Base):
    __tablename__ = 'passenger'
    
    id = Column(BigInteger, primary_key=True)
    is_active = Column(Boolean)
    balance = Column(REAL)
    card_id = Column(String(255), unique=True)
    category = Column(String(15))
    first_name = Column(String(255))
    last_name = Column(String(255))
    # relaciones si son necesarias
    histories = relationship('History', back_populates='passenger')

class History(Base):
    __tablename__ = 'history'
    
    id = Column(BigInteger, primary_key=True)
    challenge_completed = Column(Boolean)
    date = Column(Date)
    duration = Column(String(10))
    exercise = Column(String(25))
    repetitions_done = Column(Integer)
    target_reps = Column(Integer)
    passenger_id = Column(BigInteger, ForeignKey('passenger.id'))
    station_id = Column(BigInteger, ForeignKey('station.id'))
    # relaciones si son necesarias
    passenger = relationship('Passenger', back_populates='histories')
    station = relationship('Station', back_populates='histories')

class Station(Base):
    __tablename__ = 'station'
    
    id = Column(BigInteger, primary_key=True)
    enable = Column(Boolean)
    name = Column(String(255))
    line_id = Column(BigInteger, ForeignKey('line.id'))
    # relaciones si son necesarias
    histories = relationship('History', back_populates='station')
    line = relationship('Line', back_populates='stations')

class Line(Base):
    __tablename__ = 'line'
    
    id = Column(BigInteger, primary_key=True)
    enable = Column(Boolean)
    name = Column(String(255))
    transport_id = Column(BigInteger, ForeignKey('transport.id'))
    # relaciones si son necesarias
    stations = relationship('Station', back_populates='line')
    transport = relationship('Transport', back_populates='lines')

class Transport(Base):
    __tablename__ = 'transport'
    
    id = Column(BigInteger, primary_key=True)
    description = Column(String(255))
    name = Column(String(255), unique=True)
    # relaciones si son necesarias
    lines = relationship('Line', back_populates='transport')
