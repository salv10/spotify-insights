from fastapi import FastAPI

app = FastAPI(
    title="Spotify Insights API",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Spotify Insights API"}