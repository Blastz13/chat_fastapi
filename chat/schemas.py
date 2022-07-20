import datetime

from pydantic import BaseModel
from user.schemas import UserProfileRead


class ChatRoomCreate(BaseModel):
    title: str
    is_public: bool

    class Config:
        orm_mode = True


class ChatRoomRead(ChatRoomCreate):
    id: int
    create_date: datetime.datetime
    admins: list[UserProfileRead]
    users: list[UserProfileRead]
    is_public: bool

    class Config:
        orm_mode = True


class ChatRoomUpdate(ChatRoomCreate):
    pass


class ChatMessage(BaseModel):
    message: str
    user: UserProfileRead


class JoinTokenCreate(BaseModel):
    user_id: int
    chat_id: int


class JoinTokenRead(BaseModel):
    id: int
    token: str
    user_id: int
    chat_id: int
    is_used: bool
    create_date: datetime.datetime

    class Config:
        orm_mode = True
