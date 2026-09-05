from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.spotify_account import SpotifyAccount

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# get_valid_access_token()
#        ↓
# token valido? → restituiscilo
#        ↓
# token scaduto?
#        ↓
# refresh
#        ↓
# salva nuovo token
#        ↓
# restituisci nuovo token


async def get_valid_access_token() -> str:

    with SessionLocal() as db:
        account = db.scalar(select(SpotifyAccount).limit(1))

        if account is None:
            raise HTTPException(
                status_code=401,
                detail="Spotify account not authenticated.",
            )

        if account.access_token_expires_at > datetime.now(timezone.utc):
            return account.access_token

        # Access token has expired, refresh it
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SPOTIFY_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": account.refresh_token,
                },
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

            access_token = token_response["access_token"]
            access_token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=token_response["expires_in"]
            )

            account.access_token = access_token
            account.access_token_expires_at = access_token_expires_at
            account.refresh_token = token_response.get("refresh_token", account.refresh_token)

            db.commit()

            return access_token
