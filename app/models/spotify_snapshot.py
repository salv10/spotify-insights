from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.spotify_account import Base

if TYPE_CHECKING:
    from app.models.spotify_snapshot_artist import SpotifySnapshotArtist
    from app.models.spotify_snapshot_track import SpotifySnapshotTrack


class SpotifySnapshot(Base):
    __tablename__ = "spotify_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    time_range: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    artists: Mapped[list["SpotifySnapshotArtist"]] = relationship(
        "SpotifySnapshotArtist",
        back_populates="snapshot",
    )

    tracks: Mapped[list["SpotifySnapshotTrack"]] = relationship(
        "SpotifySnapshotTrack",
        back_populates="snapshot",
    )
 