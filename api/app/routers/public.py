from fastapi import APIRouter, HTTPException
from typing import List

from ..firebase_init import get_db
from ..models import WebsiteSettings, Dashboard, ChallengeEntry, AboutTrading, CryptoPrice
from ..services.crypto_service import get_crypto_prices

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/settings", response_model=WebsiteSettings)
def get_settings():
    db = get_db()
    doc = db.collection("websiteSettings").document("main").get()
    if not doc.exists:
        # Return sane defaults instead of erroring, so the frontend never breaks
        # before the admin has saved settings for the first time.
        return WebsiteSettings()
    return WebsiteSettings(**doc.to_dict())


@router.get("/dashboard", response_model=Dashboard)
def get_dashboard():
    db = get_db()
    doc = db.collection("dashboard").document("main").get()
    if not doc.exists:
        return Dashboard()
    return Dashboard(**doc.to_dict())


@router.get("/challenges", response_model=List[ChallengeEntry])
def list_challenges():
    db = get_db()
    docs = (
        db.collection("challengeEntries")
        .order_by("date", direction="DESCENDING")
        .stream()
    )
    entries = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        entries.append(ChallengeEntry(**data))
    return entries


@router.get("/challenges/{challenge_id}", response_model=ChallengeEntry)
def get_challenge(challenge_id: str):
    db = get_db()
    doc = db.collection("challengeEntries").document(challenge_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Challenge entry not found")
    data = doc.to_dict()
    data["id"] = doc.id
    return ChallengeEntry(**data)


@router.get("/about", response_model=AboutTrading)
def get_about():
    db = get_db()
    doc = db.collection("aboutTrading").document("main").get()
    if not doc.exists:
        return AboutTrading()
    return AboutTrading(**doc.to_dict())


@router.get("/crypto/prices", response_model=List[CryptoPrice])
def get_prices():
    return get_crypto_prices()
