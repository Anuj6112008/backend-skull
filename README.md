# SKULL TRADER — Backend (FastAPI + Firebase, deployed on Vercel)

## Structure
```
api/
├── index.py              # Vercel entry point (exposes the FastAPI `app`)
└── app/
    ├── main.py            # FastAPI instance, CORS
    ├── firebase_init.py   # Firebase Admin SDK init from env vars
    ├── auth.py            # Verifies Firebase ID tokens for /api/admin/*
    ├── models.py          # Pydantic schemas
    ├── routers/
    │   ├── public.py      # GET /api/settings, /dashboard, /challenges, /about, /crypto/prices
    │   └── admin.py        # Protected CRUD under /api/admin/*
    └── services/
        └── crypto_service.py
requirements.txt
vercel.json
.env.example
```

## Local dev
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in real values
cd api
uvicorn app.main:app --reload --port 8000
```
Then hit `http://localhost:8000/api/health`.

## Deploying
Full step-by-step Firebase + Vercel setup guide comes in the next message —
this zip is just the code. In short: push this folder to a GitHub repo,
import it into Vercel, set the env vars from `.env.example` in the Vercel
dashboard, deploy.

## Notes
- No Firebase credentials are ever hardcoded — everything comes from env vars.
- `/api/admin/*` requires `Authorization: Bearer <Firebase ID token>` AND the
  signed-in user's uid must exist in the `admins` Firestore collection.
- The crypto ticker uses CoinGecko's free public endpoint with no key, and
  silently falls back to mock data if that request ever fails.
