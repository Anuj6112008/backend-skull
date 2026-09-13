import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import public, admin

app = FastAPI(title="SKULL TRADER API", version="1.0.0")

allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else [],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(public.router)
app.include_router(admin.router)


@app.get("/api")
def root():
    return {"service": "SKULL TRADER API", "status": "running"}
