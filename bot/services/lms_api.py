import httpx
from config import settings


class LMSClient:
    def __init__(self):
        self.base_url = settings.lms_api_base_url
        self.api_key = settings.lms_api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def get_labs(self) -> list[dict]:
        client = await self._get_client()
        response = await client.get("/labs")
        response.raise_for_status()
        return response.json()

    async def get_scores(self, lab_name: str) -> dict:
        client = await self._get_client()
        response = await client.get(f"/labs/{lab_name}/scores")
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> bool:
        try:
            client = await self._get_client()
            response = await client.get("/health")
            return response.status_code == 200
        except Exception:
            return False


lms_client = LMSClient()
