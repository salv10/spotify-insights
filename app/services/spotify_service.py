import httpx

SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"


class SpotifyService:
    async def get_current_user_profile(self, access_token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient(base_url=SPOTIFY_API_BASE_URL) as client:
            response = await client.get(
                "/me",
                headers=headers,
            )

        response.raise_for_status()

        return response.json()
