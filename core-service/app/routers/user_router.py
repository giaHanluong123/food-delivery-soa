from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdateProfile

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        password_hash=payload.password_hash,
        role=payload.role,
        is_active=payload.is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.asc()).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/{user_id}/profile", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}/profile", response_model=UserResponse)
def update_user_profile(user_id: int, payload: UserUpdateProfile, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.full_name = payload.full_name
    user.phone = payload.phone
    user.is_active = payload.is_active

    db.commit()
    db.refresh(user)

    return user