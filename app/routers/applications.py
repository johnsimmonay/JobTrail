# routers/applications.py
from fastapi import APIRouter, status
from app.schemas import ApplicationCreate, ApplicationRead, ApplicationUpdate
from app.services import application_service as service
from app.database import DbDep

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: DbDep):
    return service.get_application(application_id, db)


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(data: ApplicationCreate, db: DbDep):
    return service.create_application(data, db)


@router.get("", response_model=list[ApplicationRead])
def get_all_applications(db: DbDep):
    return service.list_applications(db)


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(application_id: int, data: ApplicationUpdate, db: DbDep):
    return service.update_application(application_id, data, db)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: DbDep):
    return service.delete_application(application_id, db)