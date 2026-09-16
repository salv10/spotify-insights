from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.spotify_snapshot import SpotifySnapshot
from app.models.spotify_snapshot_artist import SpotifySnapshotArtist


def save_artist_snapshot(
    db: Session,
    time_range: str,
    top_artists_data: dict,
) -> None:
    """
    Save a SpotifySnapshot to the database.

    Args:
        db (Session): The SQLAlchemy session.
        time_range (str): The time range for the snapshot.
        top_artists_data (dict): The top artists data from the Spotify API.

    Returns:
        None
    """
    try:
        snapshot = SpotifySnapshot(captured_at=datetime.now(timezone.utc), time_range=time_range)

        db.add(snapshot)
        db.flush()  # Flush to get the snapshot ID for the foreign key relationship

        for rank, artist in enumerate(top_artists_data["items"], start=1):
            snapshot_artist = SpotifySnapshotArtist(
                snapshot_id=snapshot.id,
                spotify_artist_id=artist["id"],
                name=artist["name"],
                rank=rank,
            )
            db.add(snapshot_artist)

        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise
