from datetime import datetime, timezone
from fastapi import HTTPException
from app.schemas import ApplicationCreate
from app.dependencies import ApplicationStore


def create_application(data: ApplicationCreate, store: ApplicationStore) -> dict:

    application = {
         **data.model_dump(),
         "id": store.next_id,
         "created_at": datetime.now(timezone.utc)
    }

    store.applications.append(application)
    store.next_id += 1

    return application


def get_application(application_id: int, store: ApplicationStore) -> dict:
    for record in store.applications:
            if record["id"] == application_id:
                return record
    raise HTTPException(status_code=404, detail="Application not found!")


def list_applications(store: ApplicationStore) -> list[dict]:
    return store.applications