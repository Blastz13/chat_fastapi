from uuid import uuid4

from fastapi import Depends, WebSocket, WebSocketDisconnect, HTTPException, APIRouter
from sqlalchemy.orm import Session

from .schemas import *
from chat.consumers import ConnectionManager
from db import get_db
from user import models, schemas
from chat.models import *
from user.jwt_bearer import JwtBearer, get_current_user
from user.jwt_handler import decode_jwt

chat_router = APIRouter(prefix="/chat", tags=["Chat"])

manager = ConnectionManager()


@chat_router.websocket("/ws/{chat_id}/{client_token}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, client_token: str, db: Session = Depends(get_db)):
    await manager.connect(websocket, chat_id, client_token)
    try:
        while True:
            data = await websocket.receive_text()
            user = decode_jwt(client_token)
            db_user = db.query(models.User).get(user["user_id"])
            await manager.send_personal_message({"message": data, "user_id": user["user_id"],
                                                 "username": db_user.username, "is_own_message": True}, websocket)
            await manager.broadcast({"message": data, "user_id": user["user_id"],
                                     "username": db_user.username, "is_own_message": False},
                                    chat_id, client_token, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)


@chat_router.get("/chat_room/", response_model=list[ChatRoomRead], dependencies=[Depends(JwtBearer())])
async def get_all_chat_rooms(db: Session = Depends(get_db)):
    db_chat_rooms = db.query(models.ChatRoom).all()
    return db_chat_rooms


@chat_router.get("/chat_room/entered", response_model=list[ChatRoomRead], dependencies=[Depends(JwtBearer())])
async def get_entered_chat_rooms(db: Session = Depends(get_db), user: get_current_user = Depends()):
    db_chat_rooms = db.query(models.User).get(user["user_id"]).chat_rooms
    return db_chat_rooms


@chat_router.post("/chat_room", response_model=ChatRoomRead, dependencies=[Depends(JwtBearer())])
async def create_chat_room(chat_room: ChatRoomCreate, db: Session = Depends(get_db),
                           user: get_current_user = Depends()):
    db_chat_room = models.ChatRoom(title=chat_room.title, is_public=chat_room.is_public)
    db.add(db_chat_room)
    db.commit()
    db.refresh(db_chat_room)
    db_chat_room_user = models.ChatRoomUser(user_id=user["user_id"], chat_room_id=db_chat_room.id)
    db.add(db_chat_room_user)
    db.commit()
    db_chat_room_admin = models.ChatRoomAdmin(user_id=user["user_id"], chat_room_id=db_chat_room.id)
    db.add(db_chat_room_admin)
    db.commit()
    db.refresh(db_chat_room_user)
    return db_chat_room


@chat_router.get("/chat_room/{chat_id}", response_model=ChatRoomRead, dependencies=[Depends(JwtBearer())])
async def get_chat_room(chat_id: int, db: Session = Depends(get_db)):
    db_chat_room = db.query(models.ChatRoom).get(chat_id)
    return db_chat_room


@chat_router.post("/chat_room/{chat_id}", status_code=204, dependencies=[Depends(JwtBearer())])
async def add_user_in_chat_room(chat_id: int, db: Session = Depends(get_db), user: get_current_user = Depends()):
    db_chat_room = db.query(models.ChatRoom).get(chat_id)
    db_user = db.query(models.User).get(user["user_id"])
    if db_user not in db_chat_room.users:
        if db.query(models.ChatRoom).get(chat_id).is_public:
            db_chat_room_user = models.ChatRoomUser(user_id=user["user_id"], chat_room_id=chat_id)
            db.add(db_chat_room_user)
            db.commit()
            db.refresh(db_chat_room_user)
            return {}
        else:
            raise HTTPException(status_code=403, detail="Chat is not public")
    else:
        raise HTTPException(status_code=400, detail="You are already in the chat")


@chat_router.post("/generate_token}", response_model=JoinTokenRead, dependencies=[Depends(JwtBearer())])
async def generate_invitation_token_chat(join_token: JoinTokenCreate, db: Session = Depends(get_db), user: get_current_user = Depends()):
    db_user = db.query(models.User).get(user["user_id"])
    db_user_invite = db.query(models.User).get(join_token.user_id)
    db_chat_room = db.query(models.ChatRoom).get(join_token.chat_id)
    if db_user in db_chat_room.users:
        if db_user_invite not in db_chat_room.users:
            db_join_token = JoinToken(token=str(uuid4()), user_id=db_user_invite.id, chat_id=db_chat_room.id)
            db.add(db_join_token)
            db.commit()
            return db_join_token
        else:
            raise HTTPException(status_code=400, detail="This user is already in the chat")
    else:
        raise HTTPException(status_code=403, detail="You are not a member of this chat")


@chat_router.get("/join_chat/{token}", status_code=200, dependencies=[Depends(JwtBearer())])
async def join_in_chat_room(token: str, db: Session = Depends(get_db), user: get_current_user = Depends()):
    db_join_token = db.query(JoinToken).filter(JoinToken.token == token).first()
    if db_join_token.user_id == user["user_id"] and db_join_token.is_used != True:
        db_chat_room_user = models.ChatRoomUser(user_id=db_join_token.user_id, chat_room_id=db_join_token.chat_id)
        db.add(db_chat_room_user)
        db.commit()
        return {}
    else:
        raise HTTPException(status_code=403, detail="Invalid or Expired join token!")


@chat_router.put("/chat_room/{chat_id}", response_model=ChatRoomRead, dependencies=[Depends(JwtBearer())])
async def update_chat_room(chat_id: int, chat_room: ChatRoomUpdate, db: Session = Depends(get_db),
                           user: get_current_user = Depends()):
    db_chat_room = db.query(models.ChatRoom).get(chat_id)
    db_user = db.query(models.User).get(user["user_id"])
    if db_user in db_chat_room.admins:
        for var, value in vars(chat_room).items():
            setattr(db_chat_room, var, value)
        db.commit()
        db.refresh(db_chat_room)
        return db_chat_room
    else:
        raise HTTPException(status_code=403, detail="You are not the administrator of this chat")


@chat_router.delete("/chat_room/{chat_id}", status_code=204, dependencies=[Depends(JwtBearer())])
async def delete_chat_room(chat_id: int, db: Session = Depends(get_db), user: get_current_user = Depends()):
    db_chat_room = db.query(models.ChatRoom).get(chat_id)
    db_user = db.query(models.User).get(user["user_id"])
    if db_user in db_chat_room.admins:
        db.query(models.ChatRoomUser).filter(models.ChatRoomUser.chat_room_id == chat_id).delete()
        db.query(models.ChatRoom).filter(models.ChatRoom.id == chat_id).delete()
        db.commit()
        return {}
    else:
        raise HTTPException(status_code=403, detail="You are not the administrator of this chat")


@chat_router.delete("/chat_room/{chat_id}/leave", status_code=204, dependencies=[Depends(JwtBearer())])
async def leave_from_chat_room(chat_id: int, db: Session = Depends(get_db), user: get_current_user = Depends()):
    db.query(models.ChatRoomUser).filter(models.ChatRoomUser.chat_room_id == chat_id) \
        .filter(models.ChatRoomUser.user_id == user["user_id"]).delete()
    db.commit()
    return {}


@chat_router.delete("/chat_room/{chat_id}/kick", status_code=204, dependencies=[Depends(JwtBearer())])
async def kick_from_chat_room(chat_id: int, target_user: schemas.UserIdRead, db: Session = Depends(get_db),
                              user: get_current_user = Depends()):
    db_chat_room = db.query(models.ChatRoom).get(chat_id)
    db_user = db.query(models.User).get(user["user_id"])
    if db_user in db_chat_room.admins:
        db.query(models.ChatRoomUser).filter(models.ChatRoomUser.chat_room_id == chat_id) \
            .filter(models.ChatRoomUser.user_id == target_user.id).delete()
        db.commit()
        return {}
    else:
        raise HTTPException(status_code=403, detail="You are not the administrator of this chat")
