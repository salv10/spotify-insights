import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Cookie, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.spotify_account import SpotifyAccount

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

SCOPES = [
    "user-top-read",
]


@router.get("/login")
async def login():
    state = secrets.token_urlsafe(16)

    query_params = {
        "client_id": settings.spotify_client_id,
        "response_type": "code",
        "redirect_uri": settings.spotify_redirect_uri,
        "scope": " ".join(SCOPES),
        "state": state,
    }

    authorization_url = f"{SPOTIFY_AUTHORIZE_URL}?{urlencode(query_params)}"

    response = RedirectResponse(url=authorization_url)

    response.set_cookie(
        key="spotify_auth_state",
        value=state,
        httponly=True,
        samesite="lax",
    )

    return response


@router.get("/callback")
async def callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    spotify_auth_state: str | None = Cookie(default=None),
):
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Spotify authorization failed: {error}",
        )

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Authorization code not provided.",
        )

    if not state or state != spotify_auth_state:
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state.",
        )

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.spotify_redirect_uri,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            SPOTIFY_TOKEN_URL,
            data=token_data,
            auth=(
                settings.spotify_client_id,
                settings.spotify_client_secret,
            ),
        )

    if response.is_error:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve Spotify access token.",
        )

    token_response = response.json()

    access_token_expires_at = datetime.now(timezone.utc)
    +timedelta(seconds=token_response["expires_in"])

    with SessionLocal() as db:
        statement = select(SpotifyAccount).limit(1)
        account = db.scalar(statement)
        refresh_token = token_response.get("refresh_token")
        if account is None:
            if not refresh_token:
                raise HTTPException(
                    status_code=502,
                    detail="Refresh token not provided.",
                )
            account = SpotifyAccount(
                access_token=token_response["access_token"],
                refresh_token=refresh_token,
                access_token_expires_at=access_token_expires_at,
            )
            db.add(account)
        else:
            account.access_token = token_response["access_token"]
            if refresh_token is not None:
                account.refresh_token = refresh_token
            account.access_token_expires_at = access_token_expires_at
        db.commit()

    result = JSONResponse(
        content={
            "message": "Spotify authentication completed.",
            "token_type": token_response["token_type"],
            "expires_in": token_response["expires_in"],
            "scope": token_response.get("scope"),
            "has_access_token": bool(token_response.get("access_token")),
            "has_refresh_token": bool(token_response.get("refresh_token")),
        }
    )

    result.delete_cookie("spotify_auth_state")

    return result
