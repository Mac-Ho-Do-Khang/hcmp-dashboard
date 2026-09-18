"""Guards the upload endpoint with a single shared token.

Matches the single admin, no user accounts decision, so there is no
login system, sessions, or password hashing to maintain.
"""
import os
from fastapi import Header, HTTPException


def require_admin(x_admin_token: str = Header(...)):
    # Rejects the request unless it carries the token set in ADMIN_TOKEN.
    expected = os.environ.get("ADMIN_TOKEN")
    if not expected or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Invalid admin token")
