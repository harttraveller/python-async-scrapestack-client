import asyncio
from time import perf_counter
from pssm import secrets
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from aiohttp import ClientSession, ClientTimeout
from pasc.util import compute_timedelta_seconds
from pasc.env import SCRAPESTACK_URL

# from pydantic.dataclasses import dataclass


async def _async_request(session: ClientSession, url: str, key: str):
    start = perf_counter()
    try:
        async with session.get(
            SCRAPESTACK_URL,
            params={
                "access_key": key,
                "url": url,
            },
        ) as resp:
            html = await resp.text()
            end = perf_counter()
            elapsed = end - start
            return html, url, resp.status, round(elapsed, 4)
    except asyncio.TimeoutError:
        end = perf_counter()
        elapsed = end - start
        return None, url, 408, round(elapsed, 4)


async def _async_batch_request(
    urls: list[str],
    headers: dict = None,
    cookies: dict = None,
    timeout: int = 100,
) -> list:
    batch_start_time = datetime.now()
    async with ClientSession(
        headers=headers, cookies=cookies, timeout=ClientTimeout(total=timeout)
    ) as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(_async_request(session, url)))
        results = await asyncio.gather(*tasks)
    batch_end_time = datetime.now()
    return results, compute_timedelta_seconds(start=batch_start_time, end=batch_end_time)


class ResponseBatch(BaseModel):
    pass

    @property
    def success(self) -> None:
        pass

    @property
    def failure(self) -> None:
        pass

    @property
    def results(self) -> None:
        pass


class Retriever:
    def __init__(
        self,
        key: str = secrets.get("scrapestack"),
        timeout: int = 20,
        verbose: bool = False,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
        parser: Optional[BaseModel] = None,
    ) -> None:
        self.key = key

    def get(self, urls: list[str]) -> ResponseBatch:
        pass
