from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sleep_records = relationship("SleepRecord", back_populates="user", cascade="all, delete-orphan")

class SleepRecord(Base):
    __tablename__ = 'sleep_records'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    sleep_time = Column(DateTime, nullable=False)
    wake_time = Column(DateTime, nullable=False)
    quality = Column(Integer, CheckConstraint('quality BETWEEN 1 AND 5'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="sleep_records")
    note = relationship("Note", back_populates="sleep_record", uselist=False, cascade="all, delete-orphan")

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    sleep_record_id = Column(Integer, ForeignKey('sleep_records.id', ondelete='CASCADE'), nullable=False)
    notes = Column(Text)
    sleep_record = relationship("SleepRecord", back_populates="note")