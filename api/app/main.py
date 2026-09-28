import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import public, admin

app = FastAPI(title="SKULL TRADER API", version="1.0.0")

allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    # No origins configured → allow any origin. This is safe because these are
    # public read endpoints; every admin (write) route still requires a valid
    # Firebase ID token + an `admins` Firestore entry (see auth.py).
    allow_origins=allowed_origins if allowed_origins else ["*"],
    # Auth is a Bearer header (Firebase ID token), never cookies — so browser
    # credentials are not needed, which also makes the "*" fallback valid.
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------------------------------------------------------------------------
# HTTP caching (first-load performance)
#
# Public GETs are cacheable at Vercel's edge CDN (s-maxage): after the very
# first hit, every visitor gets the response in ~0ms instead of waiting for a
# cold serverless function + Firestore read (that was the 2-5s first load).
# Data changes only when the admin syncs, so 60s of edge staleness is safe;
# stale-while-revalidate keeps serving the stale copy while refreshing it.
#
# Admin routes are authenticated → never cached anywhere.
# ---------------------------------------------------------------------------
PUBLIC_CACHE_CONTROL = "public, max-age=30, s-maxage=60, stale-while-revalidate=600"
NO_STORE_CACHE_CONTROL = "no-store"


@app.middleware("http")
async def cache_control_middleware(request, call_next):
    response = await call_next(request)
    if request.method == "GET" and not request.url.path.startswith("/api/admin"):
        response.headers["Cache-Control"] = PUBLIC_CACHE_CONTROL
    else:
        response.headers["Cache-Control"] = NO_STORE_CACHE_CONTROL
    return response


app.include_router(public.router)
app.include_router(admin.router)


@app.get("/api")
def root():
    return {"service": "SKULL TRADER API", "status": "running"}
