import asyncio
from typing import Optional
from time import perf_counter
from datetime import datetime
from aiohttp import ClientSession, ClientTimeout

from pasc.util import compute_timedelta_seconds
from pasc.env import SCRAPESTACK_URL


async def _async_request(
    session: ClientSession,
    url: str,
    key: str,
):
    start = perf_counter()
    try:
        async with session.get(
            SCRAPESTACK_URL,
            params={
                "access_key": key,
                "url": url,
            },
        ) as resp:
            data = await resp.read()
            end = perf_counter()
            elapsed = end - start
            return data, url, resp.status, round(elapsed, 4)
    except asyncio.TimeoutError:
        end = perf_counter()
        elapsed = end - start
        return None, url, 408, round(elapsed, 4)


async def _async_batch_request(
    urls: list[str],
    key: str,
    headers: Optional[dict] = None,
    cookies: Optional[dict] = None,
    timeout: Optional[int] = 100,
) -> list:
    batch_start_time = datetime.now()
    async with ClientSession(
        headers=headers, cookies=cookies, timeout=ClientTimeout(total=timeout)
    ) as session:
        tasks = []
        for url in urls:
            tasks.append(
                asyncio.ensure_future(_async_request(session=session, url=url, key=key))
            )
        results = await asyncio.gather(*tasks)
    batch_end_time = datetime.now()
    return results, compute_timedelta_seconds(start=batch_start_time, end=batch_end_time)
