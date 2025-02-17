from typing import List
from sqlalchemy.orm import Session
from camerenerve.dependencies import get_db
from camerenerve.schemas.messages import Message as MessageSchema, MessageCreate
from camerenerve.models import Category as CategoryModel, Message as MessageModel
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    response_model=List[MessageSchema],
    responses={403: {"description": "Operation forbidden"}},
)
def read_messages(db: Session = Depends(get_db)):
    messages = db.query(MessageModel).all()
    return list(map(lambda mess: mess.to_dict(), messages))


@router.get(
    "/{message_id}",
    response_model=MessageSchema,
    responses={403: {"description": "Operation forbidden"}},
)
def get_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(MessageModel).filter_by(id=message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message Not Found!")
    else:
        return message.to_dict()
    

@router.get(
    "/category/{category_id}",
    response_model=List[MessageSchema],
    responses={403: {"description": "Operation forbidden"}},
)
def get_message_by_category(category_id: int, db: Session = Depends(get_db)):
    messages = db.query(MessageModel).filter_by(category_id=category_id).all()
    return list(map(lambda mess: mess.to_dict(), messages))


@router.post(
    "/",
    response_model=MessageSchema,
    responses={403: {"description": "Operation forbidden"}},
)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    category: CategoryModel = db.query(CategoryModel).get(message.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category Not Found!")

    try:
        db_message = MessageModel(**message.dict())
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message.to_dict()
    except:
        raise HTTPException(status_code=500, detail="Server Error!")
