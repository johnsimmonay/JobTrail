from fastapi import FastAPI
from .routers import applications, user

app = FastAPI(title="JobTrail")

app.include_router(applications.router)
app.include_router(user.router)

@app.get("/health")
def health():
    return {"status": "ok", "version": 1}
