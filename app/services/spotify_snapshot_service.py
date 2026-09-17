from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.spotify_snapshot import SpotifySnapshot
from app.models.spotify_snapshot_artist import SpotifySnapshotArtist
from app.models.spotify_snapshot_track import SpotifySnapshotTrack


def save_artist_snapshot(
    db: Session,
    snapshot: SpotifySnapshot,
    top_artists_data: dict,
) -> None:
    
    for rank, artist in enumerate(top_artists_data["items"], start=1):
        snapshot_artist = SpotifySnapshotArtist(
            snapshot_id=snapshot.id,
            spotify_artist_id=artist["id"],
            name=artist["name"],
            rank=rank,
        )
        db.add(snapshot_artist)

  
def create_snapshot(
        db: Session, 
        time_range: str, 
        top_artists_data: dict,
        top_tracks_data: dict
) -> SpotifySnapshot:
    try:
        snapshot = SpotifySnapshot(
            captured_at=datetime.now(timezone.utc), 
            time_range=time_range
        )
        db.add(snapshot)
        db.flush()  # Flush to get the snapshot ID for the foreign key relationship

        save_artist_snapshot(db, snapshot, top_artists_data)
        save_track_snapshot(db, snapshot, top_tracks_data)

        db.commit()
        return snapshot
    
    except SQLAlchemyError:
        db.rollback()
        raise

def save_track_snapshot(
        db: Session, 
        snapshot: SpotifySnapshot, 
        top_tracks_data: dict
) -> None:
    
    for rank, track in enumerate(top_tracks_data["items"], start=1):
        snapshot_track = SpotifySnapshotTrack(
            snapshot_id=snapshot.id,
            spotify_track_id=track["id"],
            name=track["name"],
            artist_name=track["artists"][0]["name"] if track["artists"] else "Unknown",
            rank=rank,
        )
        db.add(snapshot_track)


def get_snapshots(db: Session) -> list[SpotifySnapshot]:
    return db.execute(
        select(SpotifySnapshot)
        .order_by(SpotifySnapshot.captured_at.desc())
    ).scalars().all()

def get_snapshot_by_id(
    db: Session,
    snapshot_id: int,
) -> SpotifySnapshot | None:
    return db.execute(
        select(SpotifySnapshot)
        .where(SpotifySnapshot.id == snapshot_id)
    ).scalar_one_or_none()

def compare_artist_snapshots(
    current_snapshot: SpotifySnapshot,
    previous_snapshot: SpotifySnapshot,
) -> list[dict]:

    current_artists = {artist.spotify_artist_id: artist for artist in current_snapshot.artists}
    previous_artists = {artist.spotify_artist_id: artist for artist in previous_snapshot.artists}
    
    comparison_results = []

    for artist_id, current_artist in current_artists.items():
        previous_artist = previous_artists.get(artist_id)
        if previous_artist:
            rank_change = previous_artist.rank - current_artist.rank

            if rank_change > 0:
                status = "up"
            elif rank_change < 0:
                status = "down"
            else:
                status = "same"

            comparison_results.append({
                "spotify_artist_id": artist_id,
                "name": current_artist.name,
                "current_rank": current_artist.rank,
                "previous_rank": previous_artist.rank,
                "rank_change": rank_change,
                "status": status,
            })
        else:
            comparison_results.append({
                "spotify_artist_id": artist_id,
                "name": current_artist.name,
                "current_rank": current_artist.rank,
                "previous_rank": None,
                "rank_change": None,  # New entry
                "status": "new",
            })

    for artist_id, previous_artist in previous_artists.items():
        if artist_id not in current_artists:
            comparison_results.append({
                "spotify_artist_id": artist_id,
                "name": previous_artist.name,
                "current_rank": None,
                "previous_rank": previous_artist.rank,
                "rank_change": None,  # Removed entry
                "status": "out",
            })

    return comparison_results

    