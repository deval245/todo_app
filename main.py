from fastapi import FastAPI

from models import Users
from routers import auth, todos, admin,Users  # ✅ Import all routers
import models
from database import engine  # ✅ Import engine for DB connection

# ✅ Initialize the FastAPI app
app = FastAPI(
    title="Todo App with JWT Authentication",
    description="A FastAPI app with secure JWT authentication & protected routes",
    version="1.0.0"
)

# ✅ Create all tables in the database
models.Base.metadata.create_all(bind=engine)

# ✅ Register all routers
app.include_router(auth.router)   # Authentication and User creation
app.include_router(todos.router)  # Todo management with JWT
app.include_router(admin.router)  # Admin routes (protected)
app.include_router(Users.router)