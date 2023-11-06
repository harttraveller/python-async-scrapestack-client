# from pydantic.dataclasses import dataclass
# from pasc import parallel

# external imports

import asyncio
from typing import Optional
from pydantic import BaseModel
from pssm import secrets
from time import perf_counter
from datetime import datetime
from aiohttp import ClientSession, ClientTimeout
from typing import Optional

# internal imports
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


class Retriever:
    def __init__(
        self,
        key: str = secrets.get("scrapestack"),
        timeout: int = 20,
        verbose: bool = False,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
        parser: Optional[BaseModel] = None,
        notebook: bool = False,
    ) -> None:
        self.key = key
        self.timeout = timeout
        self.verbose = verbose
        self.headers = headers
        self.cookies = cookies
        self.parser = parser
        self.notebook = notebook

    def __get_default(self, urls: list[str]):
        responses, batch_time = asyncio.run(
            _async_batch_request(
                urls=urls,
                key=self.key,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
            )
        )
        return responses, batch_time

    def __get_notebook(self, urls: list[str]):
        loop = asyncio.get_event_loop()
        responses, batch_time = loop.run_until_complete(
            asyncio.run(
                _async_batch_request(
                    urls=urls,
                    key=self.key,
                    headers=self.headers,
                    cookies=self.cookies,
                    timeout=self.timeout,
                )
            )
        )
        return responses, batch_time

    def get(self, urls: list[str]):
        if self.notebook:
            return self.__get_notebook(urls=urls)
        else:
            return self.__get_default(urls=urls)


if __name__ == "__main__":
    ret = Retriever()
    a, b = ret.get(["https://www.duckduckgo.com"] * 10)
    print(a)
    print(b)
    # * note: runs in terminal, not in notebook
    # ! RuntimeError: asyncio.run() cannot be called from a running event loop

# class ResponseResult:
#     pass


# class BatchResults:
#     pass


# class BatchStatistics:
#     pass


# class ResponseBatch(BaseModel):
#     pass

#     @property
#     def success(self) -> None:
#         pass

#     @property
#     def failure(self) -> None:
#         pass

#     @property
#     def results(self) -> None:
#         pass
