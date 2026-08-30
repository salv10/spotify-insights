import httpx
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.spotify_account import SpotifyAccount
from app.services.spotify_service import SpotifyService

router = APIRouter(
    prefix="/spotify",
    tags=["spotify"],
)

spotify_service = SpotifyService()


@router.get("/me")
async def get_current_user_profile():
    with SessionLocal() as db:
        account = db.scalar(select(SpotifyAccount).limit(1))

    if account is None:
        raise HTTPException(
            status_code=401,
            detail="Spotify account not authenticated.",
        )

    try:
        profile = await spotify_service.get_current_user_profile(account.access_token)

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve Spotify profile.",
        ) from exc

    return profile
