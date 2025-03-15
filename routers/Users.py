from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.openapi.models import Response
from pydantic import Field, BaseModel
from sqlalchemy.orm import Session

from models import Users
from .auth import get_current_user, bcrypt_context  # ✅ Correctly imported
from database import SessionLocal
import models

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserVerification(BaseModel):
    password:str
    new_password :str = Field(min_length=6)

@router.get("/",status_code=status.HTTP_200_OK)
async def get_user( user: dict = Depends(get_current_user),db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401,detail="authentication failed")
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put("/password",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user_verification: UserVerification,user: dict = Depends(get_current_user),db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401,detail='authentication fail')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(user_verification.password,user_model.hashed_password):
        raise HTTPException(status_code=401,detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()