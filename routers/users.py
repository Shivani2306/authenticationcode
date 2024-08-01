from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from datetime import timedelta  # Import timedelta
from schemas import CreateUserRequest, Token
# from auth import get_password_hash, create_access_token, get_current_user,get_user
from auth import get_password_hash, create_access_token, get_current_user,get_user, ACCESS_TOKEN_EXPIRE_MINUTES
router = APIRouter()

@router.post("/create_user", response_model=Token)
def create_user(create_user_request: CreateUserRequest, db: Session = Depends(get_db)):
    user = get_user(db, create_user_request.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(create_user_request.password)
    new_user = User(username=create_user_request.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
