# external_apis.py
from typing import Any

import httpx
import asyncio


class ExternalAPIError(Exception):
    pass


async def fetch_api(name: str) -> Any:
    try:
        async with httpx.AsyncClient() as client:

            tasks = [client.get(f"https://api.{site}.io?name={name}") for site
                     in ["genderize", "agify", "nationalize"]]

            genderize, agify, nationalize = await asyncio.gather(*tasks)

        return (
               genderize.json(),
               agify.json(),
               nationalize.json(),
        ), None

    except httpx.RequestError as e:
        raise ExternalAPIError("External API request failed") from e
        # Handle failed request from API call

if "__main__" == __name__:
    print(asyncio.run(fetch_api("test")))
