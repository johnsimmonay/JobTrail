from fastapi import FastAPI, status, HTTPException
from app.schemas import ApplicationCreate, ApplicationRead
from datetime import datetime, timezone

app = FastAPI(title="JobTrail")

apps = []
id_counter = 1

@app.get("/health")
def health():
    return {"status": "ok", "version": 1}


@app.get("/applications/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int):
    for record in apps:
        if record["id"] == application_id:
            return record
    raise HTTPException(status_code=404, detail="Application not found!")


@app.post("/applications", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(application: ApplicationCreate):
    global id_counter

    application = {"id": id_counter, "created_at": datetime.now(timezone.utc), **application.model_dump()}
    apps.append(application)

    id_counter += 1

    return application


@app.get("/applications", response_model=list[ApplicationRead])
def get_all_applications():
    return apps