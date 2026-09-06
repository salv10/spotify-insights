import httpx
from fastapi import APIRouter, HTTPException

from app.services.spotify_service import SpotifyService
from app.services.spotify_token_service import get_valid_access_token

router = APIRouter(
    prefix="/spotify",
    tags=["spotify"],
)

spotify_service = SpotifyService()


@router.get("/me")
async def get_current_user_profile():
    access_token = await get_valid_access_token()

    try:
        profile = await spotify_service.get_current_user_profile(access_token)

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve Spotify profile.",
        ) from exc

    return profile


@router.get("/top-artists")
async def get_current_user_top_artists(limit: int = 20, time_range: str = "medium_term"):
    access_token = await get_valid_access_token()

    try:
        top_artists = await spotify_service.get_top_artists(access_token, limit, time_range)

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve Spotify top artists.",
        ) from exc

    return top_artists


@router.get("/top-tracks")
async def get_current_user_top_tracks(limit: int = 20, time_range: str = "medium_term"):
    access_token = await get_valid_access_token()

    try:
        top_tracks = await spotify_service.get_top_tracks(access_token, limit, time_range)

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve Spotify top tracks.",
        ) from exc

    return top_tracks
