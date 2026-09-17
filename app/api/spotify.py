from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.spotify_service import SpotifyService
from app.services.spotify_snapshot_service import (
    compare_artist_snapshots,
    create_snapshot,
    get_snapshot_by_id,
    get_snapshots,
)
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


@router.post("/snapshots")
async def save_top_artists_snapshot(
    db: Annotated[Session, Depends(get_db)],
    time_range: str = "medium_term",
):
    access_token = await get_valid_access_token()
    top_artists_data = await spotify_service.get_top_artists(
        access_token, limit=20, time_range=time_range
    )

    top_tracks_data = await spotify_service.get_top_tracks(
        access_token, limit=20, time_range=time_range
    )

    snapshot = create_snapshot(db, time_range, top_artists_data, top_tracks_data)

    return {

        "message": "Snapshot created successfully.",
        "snapshot_id": snapshot.id,
        "time_range": time_range,
    }

@router.get("/snapshots")
async def get_spotify_snapshots(
    db: Annotated[Session, Depends(get_db)],
):
    snapshots = get_snapshots(db)
    json_snapshots = []
    for snapshot in snapshots:
        json_snapshots.append({
            "id": snapshot.id,
            "captured_at": snapshot.captured_at.isoformat(),
            "time_range": snapshot.time_range,
        })

    return json_snapshots

@router.get("/snapshots/compare")
async def compare_spotify_snapshots(
    current_id: int,
    previous_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    current_snapshot = get_snapshot_by_id(db, current_id)
    previous_snapshot = get_snapshot_by_id(db, previous_id)

    if not current_snapshot or not previous_snapshot:
        raise HTTPException(status_code=404, detail="One or both snapshots not found.")

    comparison_artists_results = compare_artist_snapshots(current_snapshot, previous_snapshot)

    return {
        "current_snapshot_id": current_id,
        "previous_snapshot_id": previous_id,
        "artists": comparison_artists_results,
    }

@router.get("/snapshots/{snapshot_id}")
async def get_spotify_snapshot_by_id(
    db: Annotated[Session, Depends(get_db)], 
    snapshot_id: int
):
    snapshot = get_snapshot_by_id(db, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found.")

    artists = [
        {
            "spotify_artist_id": artist.spotify_artist_id,
            "name": artist.name,
            "rank": artist.rank,
        }
        for artist in sorted(snapshot.artists, key=lambda artist: artist.rank)
    ]

    tracks = [
        {
            "spotify_track_id": track.spotify_track_id,
            "name": track.name,
            "artist_name": track.artist_name,
            "rank": track.rank,
        }
        for track in sorted(snapshot.tracks, key=lambda track: track.rank)
    ]

    return {
        "id": snapshot.id,
        "captured_at": snapshot.captured_at.isoformat(),
        "time_range": snapshot.time_range,
        "artists": artists,
        "tracks": tracks,
    }

