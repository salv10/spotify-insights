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

    async def get_top_artists(
        self, access_token: str, limit: int = 20, time_range: str = "medium_term"
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient(base_url=SPOTIFY_API_BASE_URL) as client:
            response = await client.get(
                "/me/top/artists",
                headers=headers,
                params={"limit": limit, "time_range": time_range},
            )
        response.raise_for_status()

        return response.json()
