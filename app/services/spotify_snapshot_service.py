from datetime import datetime, timezone

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


