from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SpotifyAccount(Base):
    __tablename__ = "spotify_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    spotify_user_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    access_token: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    refresh_token: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    access_token_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
