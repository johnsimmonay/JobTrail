# routers/applications.py
from fastapi import APIRouter, status
from app.schemas import ApplicationCreate, ApplicationRead, ApplicationUpdate
from app.services import application_service as service
from app.database import DbDep
from app.dependencies import CurrentUser

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, current_user: CurrentUser, db: DbDep):
    return service.get_application(application_id, current_user.id, db)


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(data: ApplicationCreate, current_user: CurrentUser, db: DbDep):
    return service.create_application(data, current_user.id, db)


@router.get("", response_model=list[ApplicationRead])
def get_all_applications(current_user: CurrentUser, db: DbDep):
    return service.list_applications(current_user.id, db)


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(application_id: int, data: ApplicationUpdate, current_user: CurrentUser, db: DbDep):
    return service.update_application(application_id, data, current_user.id, db)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, current_user: CurrentUser, db: DbDep):
    return service.delete_application(application_id, current_user.id, db)