"""
Firebase Admin SDK bootstrap.

Credentials are read ONLY from environment variables (never from a committed
JSON file), so the service account key never touches the frontend or the
git repo. Set these in Vercel → Project → Settings → Environment Variables:

    FIREBASE_PROJECT_ID
    FIREBASE_CLIENT_EMAIL
    FIREBASE_PRIVATE_KEY

This module is safe to import multiple times — Firebase Admin is only
initialized once per serverless instance (module-level singleton).
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth


def _build_credentials() -> credentials.Certificate:
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
    private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "")

    if not project_id or not client_email or not private_key:
        raise RuntimeError(
            "Missing Firebase Admin credentials. Set FIREBASE_PROJECT_ID, "
            "FIREBASE_CLIENT_EMAIL, and FIREBASE_PRIVATE_KEY as environment "
            "variables (see .env.example)."
        )

    # Env vars store literal \n sequences (can't hold real newlines in most
    # dashboards), so convert them back before handing to the SDK.
    private_key = private_key.replace("\\n", "\n")

    service_account_info = {
        "type": "service_account",
        "project_id": project_id,
        "client_email": client_email,
        "private_key": private_key,
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    return credentials.Certificate(service_account_info)


def get_firebase_app() -> firebase_admin.App:
    """Returns the singleton Firebase Admin app, initializing it if needed."""
    if not firebase_admin._apps:
        cred = _build_credentials()
        firebase_admin.initialize_app(cred)
    return firebase_admin.get_app()


def get_db():
    """Returns a Firestore client bound to the initialized Firebase app."""
    get_firebase_app()
    return firestore.client()


def get_auth():
    """Returns the firebase_admin.auth module, ensuring the app is initialized."""
    get_firebase_app()
    return firebase_auth
