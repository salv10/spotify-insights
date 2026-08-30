from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.spotify import router as spotify_router
from app.core.config import settings

app = FastAPI(
    title="Spotify Insights API",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(spotify_router)


@app.get("/")
async def root():
    return {
        "message": "Spotify Insights API",
        "redirect_uri": settings.spotify_redirect_uri,
    }
