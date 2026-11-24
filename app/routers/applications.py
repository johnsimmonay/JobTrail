# routers/applications.py
from fastapi import APIRouter, Query, status
from app.schemas import ApplicationCreate, ApplicationPage, ApplicationRead, ApplicationStatus, ApplicationUpdate
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


@router.get("", response_model=ApplicationPage)
def get_all_applications(
        current_user: CurrentUser,
        db: DbDep,
        status_filter: ApplicationStatus | None = Query(default=None, alias="status"), 
        q: str | None = Query(default=None, min_length=1, max_length=100),
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0)):
    items, total = service.list_applications(current_user.id, db, status_filter, q, limit, offset)

    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(application_id: int, data: ApplicationUpdate, current_user: CurrentUser, db: DbDep):
    return service.update_application(application_id, data, current_user.id, db)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, current_user: CurrentUser, db: DbDep):
    return service.delete_application(application_id, current_user.id, db)