from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from db import Base, SessionLocal
import datetime

db = SessionLocal()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    create_date = Column(DateTime, default=datetime.datetime.now())
    chat_rooms = relationship('ChatRoom', secondary='chat_room_user', back_populates='users')


class ChatRoom(Base):
    __tablename__ = 'chat_room'
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    create_date = Column(DateTime, default=datetime.datetime.now())
    is_public = Column(Boolean, default=True)
    admins = relationship('User', secondary='chat_room_admin', back_populates='chat_rooms', cascade="all, delete")
    users = relationship('User', secondary='chat_room_user', back_populates='chat_rooms', cascade="all, delete")


class ChatRoomUser(Base):
    __tablename__ = "chat_room_user"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    chat_room_id = Column(Integer, ForeignKey('chat_room.id', ondelete='CASCADE'))


class ChatRoomAdmin(Base):
    __tablename__ = "chat_room_admin"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    chat_room_id = Column(Integer, ForeignKey('chat_room.id', ondelete='CASCADE'))
