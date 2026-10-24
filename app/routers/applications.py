from fastapi import APIRouter, status, Depends
from app.schemas import ApplicationCreate, ApplicationRead
from app.services import application_service as service
from app.dependencies import ApplicationStore, get_store
from typing import Annotated


router = APIRouter(prefix="/applications", tags=["applications"])


StoreDep = Annotated[ApplicationStore, Depends(get_store)]


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, store: StoreDep):
    return service.get_application(application_id, store)


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(data: ApplicationCreate, store: StoreDep):
    return service.create_application(data, store)


@router.get("", response_model=list[ApplicationRead])
def get_all_applications(store: StoreDep):
    return service.list_applications(store)