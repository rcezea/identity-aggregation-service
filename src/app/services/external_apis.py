# external_apis.py
from typing import Any

import httpx
import asyncio


class ExternalAPIError(Exception):
    def __init__(self, api_name: str) -> None:
        self.api_name = api_name.capitalize()
        super().__init__(api_name)


async def fetch_api(name: str) -> Any:
    async with httpx.AsyncClient(timeout=5) as client:

        api_sites = ["genderize", "agify", "nationalize"]

        tasks = [
            asyncio.create_task(call_api(client, site, name))
            for site in api_sites
        ]

        try:
            responses = await asyncio.gather(*tasks)
        except ExternalAPIError as e:
            for task in tasks:
                if not task.done():
                    task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)
            raise

    return tuple(responses)


async def call_api(client: httpx.AsyncClient, site: str, name: str):
    try:
        response = await client.get(
            url=f"https://api.{site}.io", params={"name": name})
        response.raise_for_status()
        return response.json()

    except (httpx.RequestError, httpx.HTTPStatusError):
        raise ExternalAPIError(site)
