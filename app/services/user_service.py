from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import User
from app.schemas import UserCreate, normalize_email
from app.security import hash_password, verify_password, DUMMY_HASH
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_user(data: UserCreate, db: Session) -> User:
    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User with this email already exists")
    
    return new_user


def get_user_by_email(email: str, db: Session) -> User | None:
    return db.scalars(select(User).where(User.email == normalize_email(email))).first()


def authenticate_user(email: str, password: str, db: Session) -> User | None:
    user = get_user_by_email(email, db)

    if not user:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user