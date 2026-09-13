from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone

from ..firebase_init import get_db
from ..auth import get_current_admin
from ..models import (
    WebsiteSettings,
    Dashboard,
    ChallengeEntry,
    ChallengeEntryCreate,
    AboutTrading,
)

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
@router.get("/settings", response_model=WebsiteSettings)
def get_settings_admin():
    db = get_db()
    doc = db.collection("websiteSettings").document("main").get()
    return WebsiteSettings(**doc.to_dict()) if doc.exists else WebsiteSettings()


@router.put("/settings", response_model=WebsiteSettings)
def update_settings(payload: WebsiteSettings):
    db = get_db()
    db.collection("websiteSettings").document("main").set(payload.model_dump())
    return payload


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@router.get("/dashboard", response_model=Dashboard)
def get_dashboard_admin():
    db = get_db()
    doc = db.collection("dashboard").document("main").get()
    return Dashboard(**doc.to_dict()) if doc.exists else Dashboard()


@router.put("/dashboard", response_model=Dashboard)
def update_dashboard(payload: Dashboard):
    db = get_db()
    db.collection("dashboard").document("main").set(payload.model_dump())
    return payload


# ---------------------------------------------------------------------------
# Challenge entries
# ---------------------------------------------------------------------------
@router.get("/challenges", response_model=List[ChallengeEntry])
def list_challenges_admin():
    db = get_db()
    docs = db.collection("challengeEntries").order_by("date", direction="DESCENDING").stream()
    entries = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        entries.append(ChallengeEntry(**data))
    return entries


@router.post("/challenges", response_model=ChallengeEntry)
def create_challenge(payload: ChallengeEntryCreate):
    db = get_db()
    data = payload.model_dump()
    if data.get("totalPnl") is None:
        data["totalPnl"] = data["session1Result"] + data["session2Result"] + data["session3Result"]
    data["createdAt"] = datetime.now(timezone.utc).isoformat()

    doc_ref = db.collection("challengeEntries").document()
    doc_ref.set(data)

    data["id"] = doc_ref.id
    return ChallengeEntry(**data)


@router.put("/challenges/{challenge_id}", response_model=ChallengeEntry)
def update_challenge(challenge_id: str, payload: ChallengeEntryCreate):
    db = get_db()
    doc_ref = db.collection("challengeEntries").document(challenge_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Challenge entry not found")

    data = payload.model_dump()
    if data.get("totalPnl") is None:
        data["totalPnl"] = data["session1Result"] + data["session2Result"] + data["session3Result"]

    doc_ref.update(data)
    data["id"] = challenge_id
    return ChallengeEntry(**data)


@router.delete("/challenges/{challenge_id}")
def delete_challenge(challenge_id: str):
    db = get_db()
    doc_ref = db.collection("challengeEntries").document(challenge_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Challenge entry not found")
    doc_ref.delete()
    return {"deleted": True, "id": challenge_id}


# ---------------------------------------------------------------------------
# About Trading
# ---------------------------------------------------------------------------
@router.get("/about", response_model=AboutTrading)
def get_about_admin():
    db = get_db()
    doc = db.collection("aboutTrading").document("main").get()
    return AboutTrading(**doc.to_dict()) if doc.exists else AboutTrading()


@router.put("/about", response_model=AboutTrading)
def update_about(payload: AboutTrading):
    db = get_db()
    db.collection("aboutTrading").document("main").set(payload.model_dump())
    return payload
