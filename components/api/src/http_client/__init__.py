from httpx import AsyncClient


async def get_http_client():
    async with AsyncClient() as client:
        yield client
