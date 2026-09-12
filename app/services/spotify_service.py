import httpx

SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"


class SpotifyService:
    async def get_current_user_profile(self, access_token: str) -> dict:
        return await self._get_spotify_api("/me", access_token)

    async def get_top_artists(
        self, access_token: str, limit: int = 20, time_range: str = "medium_term"
    ) -> dict:
        return await self._get_spotify_api(
            "/me/top/artists",
            access_token,
            params={"limit": limit, "time_range": time_range},
        )

    async def get_top_tracks(
        self, access_token: str, limit: int = 20, time_range: str = "medium_term"
    ) -> dict:
        return await self._get_spotify_api(
            "/me/top/tracks",
            access_token,
            params={"limit": limit, "time_range": time_range},
        )

    async def _get_spotify_api(
        self, endpoint: str, access_token: str, params: dict | None = None
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient(base_url=SPOTIFY_API_BASE_URL) as client:
            response = await client.get(
                endpoint,
                headers=headers,
                params=params,
            )
        response.raise_for_status()

        return response.json()
