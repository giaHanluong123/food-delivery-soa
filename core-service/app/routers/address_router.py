from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Address, User
from app.schemas.address import AddressCreate, AddressResponse

router = APIRouter(tags=["Addresses"])


@router.post("/addresses", response_model=AddressResponse)
def create_address(payload: AddressCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.is_default:
        db.query(Address).filter(Address.user_id == payload.user_id).update({"is_default": False})

    address = Address(
        user_id=payload.user_id,
        contact_name=payload.contact_name,
        phone=payload.phone,
        address_line=payload.address_line,
        ward=payload.ward,
        district=payload.district,
        city=payload.city,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_default=payload.is_default,
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


@router.get("/addresses", response_model=List[AddressResponse])
def list_addresses(db: Session = Depends(get_db)):
    addresses = db.query(Address).order_by(Address.id.asc()).all()
    return addresses


@router.get("/addresses/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    return address


@router.get("/users/{user_id}/addresses", response_model=List[AddressResponse])
def list_addresses_by_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    addresses = (
        db.query(Address)
        .filter(Address.user_id == user_id)
        .order_by(Address.id.asc())
        .all()
    )
    return addresses