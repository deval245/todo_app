from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.openapi.models import Response
from pydantic import Field, BaseModel
from sqlalchemy.orm import Session
from .auth import get_current_user  # ✅ Correctly imported
from database import SessionLocal
import models

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Pydantic Model for Todo
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


# ✅ Public Route: Get all Todos (can be restricted if needed)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(db: Session = Depends(get_db)):
    todos = db.query(models.Todos).limit(100).all()
    return todos


# ✅ Protected Route: Read specific Todo (only owner can access)
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(todo_id: int,
                    user: dict = Depends(get_current_user),  # ✅ Protected by OAuth2
                    db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(
        models.Todos.id == todo_id,
        models.Todos.owner_id == user.get('id')  # ✅ Check ownership properly
    ).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found or unauthorized")


# ✅ Protected Route: Create Todo (only logged-in user can create)
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
        todo_req: TodoRequest,
        user: dict = Depends(get_current_user),  # ✅ Correctly pass function
        db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = models.Todos(**todo_req.dict(), owner_id=user.get('id'))  # Assuming `owner_id` is correct
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return {"message": "Todo created successfully", "todo": todo_model}


# ✅ Protected Route: Update Todo (only owner can update)
@router.put("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(todo_id: int,
                      todo_req: TodoRequest,
                      user: dict = Depends(get_current_user),  # ✅ Protected
                      db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(
        models.Todos.id == todo_id,
        models.Todos.owner_id == user.get('id')  # ✅ Check ownership
    ).first()

    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found or unauthorized")

    # ✅ Updating fields
    todo_model.title = todo_req.title
    todo_model.description = todo_req.description
    todo_model.priority = todo_req.priority
    todo_model.complete = todo_req.complete

    db.commit()
    return {"message": "Todo updated successfully"}


# ✅ Protected Route: Delete Todo (only owner can delete)
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int,
                      user: dict = Depends(get_current_user),  # ✅ Protected
                      db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(
        models.Todos.id == todo_id,
        models.Todos.owner_id == user.get('id')  # ✅ Check ownership
    ).first()

    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found or unauthorized")

    db.delete(todo_model)
    db.commit()

    # ✅ Return empty 204 response
    return Response(status_code=status.HTTP_204_NO_CONTENT)
