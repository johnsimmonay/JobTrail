# services/application_service.py
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.schemas import ApplicationCreate, ApplicationUpdate
from app.models import Application

def create_application(data: ApplicationCreate, user_id: int, db: Session) -> Application:
    new_app = Application(user_id=user_id, **data.model_dump(mode="json"))

    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return new_app


def get_application(application_id: int, user_id: int, db: Session) -> Application:
    data = db.scalars(select(Application).where(Application.id == application_id, Application.user_id == user_id)).first()
    if data is None :
        raise HTTPException(status_code=404, detail="Application not found!")

    return data


def list_applications(user_id: int, db: Session) -> list[Application]:
    return db.scalars(select(Application).where(Application.user_id == user_id).order_by(Application.id)).all()


def update_application(application_id: int, data: ApplicationUpdate, user_id: int, db: Session) -> Application:
    db_app = get_application(application_id, user_id, db)

    app_data = data.model_dump(mode="json", exclude_unset=True)

    for field, value in app_data.items():
        setattr(db_app, field, value)

    db.commit()
    db.refresh(db_app)

    return db_app

def delete_application(application_id: int, user_id: int, db: Session) -> None:
    row = get_application(application_id, user_id, db)

    db.delete(row)
    db.commit()