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
                timeout=10.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def get_items(self) -> list[dict]:
        client = await self._get_client()
        response = await client.get("/items/")
        response.raise_for_status()
        return response.json()

    async def get_pass_rates(self, lab: str) -> list[dict]:
        client = await self._get_client()
        response = await client.get(f"/analytics/pass-rates?lab={lab}")
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> tuple[bool, str]:
        try:
            client = await self._get_client()
            response = await client.get("/items/")
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                return True, f"Health status: OK. {count} items available."
            return False, f"Backend returned HTTP {response.status_code}"
        except httpx.ConnectError as e:
            return False, f"Backend error: connection refused ({self.base_url}). Check that the services are running."
        except httpx.HTTPStatusError as e:
            return False, f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        except httpx.TimeoutException:
            return False, f"Backend error: request timed out ({self.base_url})"
        except Exception as e:
            return False, f"Backend error: {str(e)}"


lms_client = LMSClient()
