from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import JSON

from connect_database import engine

if not database_exists(engine.url): create_database(engine.url)

class Base(DeclarativeBase):
    ...

class Chats(Base):
    __tablename__ = "Chats_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_name = Column(String(25), nullable=False)
    chat_messages = Column(JSON, nullable=False)
    
session = Session(engine)