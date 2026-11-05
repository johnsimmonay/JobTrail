# auth.py
from fastapi import APIRouter, status
from app.schemas import UserCreate, UserRead
from app.services import user_service as service
from app.database import DbDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: DbDep):
    return service.create_user(data, db)