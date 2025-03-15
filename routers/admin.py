from fastapi import Depends, HTTPException, APIRouter
from fastapi.openapi.models import Response
from pydantic import Field, BaseModel
from sqlalchemy.orm import Session
from starlette import status
from .auth import get_current_user  # Import JWT auth dependency
import models
from database import SessionLocal

router = APIRouter(
    prefix='/Admin',
    tags=['Admin']
)

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):  # ✅ dict not Session
    if user is None or user.get('role') != 'admin':  # ✅ Fix here
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(models.Todos).all()