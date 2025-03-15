from datetime import timedelta, timezone, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database import SessionLocal
from models import Users

# ✅ Router initialization
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# ✅ Constants
SECRET_KEY = 'f62c561a50c029b11ff5ff215838ed138dbb9c7549eedd2ab89cd548dd248d6e'
ALGORITHM = 'HS256'
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# ✅ OAuth2PasswordBearer to enable Swagger "Authorize" Button
oauth_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')  # Notice correct token URL


# ✅ Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Pydantic Model for Token Response
class Token(BaseModel):
    access_token: str
    token_type: str


# ✅ Pydantic Model for User Creation
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


# ✅ Function to authenticate user
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


# ✅ Function to create JWT token
def create_access_token(username: str, user_id: int, role: str, expired_delta: timedelta):
    encode = {
        'sub': username,
        'id': user_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + expired_delta
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# ✅ Function to get current user from JWT token
async def get_current_user(token: str = Depends(oauth_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')


# ✅ Route to register new user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_req: CreateUserRequest, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(Users.email == create_user_req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    create_user_model = Users(
        email=create_user_req.email,
        username=create_user_req.username,
        first_name=create_user_req.first_name,
        last_name=create_user_req.last_name,
        role=create_user_req.role,
        hashed_password=bcrypt_context.hash(create_user_req.password),
        is_active=True
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return {"message": "User created successfully", "user_id": create_user_model.id}


# ✅ Route to login and generate JWT token
@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expired_delta=timedelta(minutes=30)
    )
    return {"access_token": token, "token_type": "bearer"}
