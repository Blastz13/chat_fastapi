from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean

from db import Base
import datetime


class JoinToken(Base):
    __tablename__ = 'join_token'
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    chat_id = Column(Integer, ForeignKey('chat_room.id'), nullable=False)
    is_used = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.datetime.now())
