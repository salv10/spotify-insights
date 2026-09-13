from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.spotify_account import Base

if TYPE_CHECKING:
    from app.models.spotify_snapshot import SpotifySnapshot


class SpotifySnapshotArtist(Base):
    __tablename__ = "spotify_snapshot_artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    snapshot_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("spotify_snapshots.id"),
        nullable=False,
    )

    spotify_artist_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    snapshot: Mapped["SpotifySnapshot"] = relationship(
        "SpotifySnapshot",
        back_populates="artists",
    )
