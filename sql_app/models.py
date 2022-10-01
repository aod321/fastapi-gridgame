'''
Database tables Classes are defined here
'''
from tkinter.tix import Tree
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base



# database table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True, index=True)
    birthdate = Column(DateTime(), nullable=False, index=True)
    gender = Column(String(10), nullable=False, index=True)
    # email = Column(String(100), nullable=False, unique=True, index=True)
    # address = Column(String(100), nullable=False)
    # hashed_password = Column(String(100), nullable=False)
    # is_active = Column(Boolean, default=True)
    # items = relationship("Item", back_populates="owner")
    infos = relationship("PlayInfo", back_populates="owner")
    maps = relationship("MapInfo", back_populates="owner")
    # created = Column(DateTime, default=datetime.datetime.utcnow)
    created = Column(DateTime(), default=func.now(), nullable=True)
    last_time = Column(DateTime(), server_default=func.now(), onupdate=func.now(), nullable=True)


# database table
class MapInfo(Base):
    __tablename__ = "mapinfos"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    owner = relationship("User", back_populates="maps")
    level_id = Column(Integer, index=True)
    sum_count = Column(Integer, index=True)
    map = Column(String(1024), nullable=False, index=True)
    plays = relationship("PlayInfo", back_populates="map")
    map_type = Column(String(10), nullable=False, index=True)
    created = Column(DateTime(timezone=True), default=func.now(), nullable=True)
    last_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)


# database table
class PlayInfo(Base):
    __tablename__ = "playinfos"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    map_id = Column(Integer, ForeignKey("mapinfos.id", ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    block_index = Column(Integer, index=True)
    block_value = Column(Integer, index=True)
    block_clicked = Column(Integer, index=True)
    remain_count = Column(Integer, index=True)
    level_score = Column(Integer, index=True)
    sum_score = Column(Integer, index=True)
    reaction_time = Column(Float, index=True)
    is_finish = Column(Integer, index=True)
    owner = relationship("User", back_populates="infos")
    map = relationship("MapInfo", back_populates="plays")
    created = Column(DateTime(timezone=True), default=func.now(), nullable=True)
    last_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
