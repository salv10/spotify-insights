from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title="Spotify Insights API",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {
            "message": "Spotify Insights API",
            "redirect_uri": settings.spotify_redirect_uri,
    }