"""
Admin authentication dependency.

The Admin Panel logs in with the Firebase client SDK (email/password) and
sends the resulting ID token on every request as:

    Authorization: Bearer <firebase-id-token>

This dependency verifies that token server-side with the Firebase Admin SDK
(so it can't be forged) and additionally checks that the user's uid exists
in the `admins` Firestore collection, so having ANY Firebase account isn't
enough — only accounts you've explicitly added as admins can write data.
"""

from fastapi import Header, HTTPException, status
from typing import Optional

from .firebase_init import get_auth, get_db


async def get_current_admin(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Expected: Bearer <token>",
        )

    id_token = authorization.split(" ", 1)[1].strip()

    try:
        decoded_token = get_auth().verify_id_token(id_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )

    uid = decoded_token.get("uid")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token did not contain a valid uid.",
        )

    db = get_db()
    admin_doc = db.collection("admins").document(uid).get()
    if not admin_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not authorized as an admin.",
        )

    return {
        "uid": uid,
        "email": decoded_token.get("email"),
        **admin_doc.to_dict(),
    }
