import datetime

from pydantic import BaseModel


class UserSignUp(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True


class UserRead(BaseModel):
    id: int
    username: str
    password: str
    create_date: datetime.datetime

    class Config:
        orm_mode = True


class UserLogin(UserSignUp):
    pass


class UserProfileRead(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class UserIdRead(BaseModel):
    id: int

    class Config:
        orm_mode = True
