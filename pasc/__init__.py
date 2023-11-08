from __future__ import annotations

import asyncio
from pprint import pprint
from typing import Optional, Any, Union
from pydantic import BaseModel
from pssm import secrets
from time import perf_counter
from datetime import datetime
from aiohttp import ClientSession, ClientTimeout


# * variables

SCRAPESTACK_URL = "https://api.scrapestack.com/scrape"

# source: https://gist.github.com/bl4de/3086cf26081110383631
RESPONSES = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
}


def compute_timedelta_seconds(start: datetime, end: datetime) -> float:
    "computes the timedelta in seconds between end and start"
    elapsed_timedelta = end - start
    elapsed = elapsed_timedelta.seconds + (elapsed_timedelta.microseconds / 1e6)
    return elapsed


# * objects


class Response(BaseModel):
    url: str
    status: int
    detail: str
    success: bool
    time: float
    data: Optional[bytes] = None

    def __str__(self) -> str:
        return f"Response(url={self.url}, code={self.status}, time={self.time})"

    def __repr__(self) -> str:
        return f"Response(url={self.url}, code={self.status}, time={self.time})"

    @staticmethod
    def parse(
        url: str, status_code: int, time: float, data: Optional[bytes] = None
    ) -> Response:
        return Response(
            url=url,
            status=status_code,
            detail=RESPONSES[status_code],
            success=bool(status_code == 200),
            time=time,
            data=data,
        )


class Batch(BaseModel):
    item: list[Response]
    time: float

    @property
    def n(self) -> int:
        return len(self.item)

    @property
    def success_percent(self) -> float:
        return self.success_count / self.n

    @property
    def failure_percent(self) -> float:
        return self.failure_count / self.n

    @property
    def success_count(self) -> int:
        return sum([1 if resp.success else 0 for resp in self.item])

    @property
    def failure_count(self) -> int:
        return sum([1 if not resp.success else 0 for resp in self.item])

    @property
    def success(self) -> list[Response]:
        return [resp for resp in self.item if resp.success]

    @property
    def failure(self) -> list[Response]:
        return [resp for resp in self.item if not resp.success]

    @property
    def approx_speedup(self) -> float:
        return self.sequential_time / self.time

    @property
    def sequential_time(self) -> float:
        "returns what the sequential time would have been otherwise (does not account for scrapestack proxy lag)"
        return sum([r.time for r in self.item])


# * async functions


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


class Retriever:
    def __init__(
        self,
        key: str = secrets.get("scrapestack"),
        timeout: int = 20,
        verbose: bool = False,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
    ) -> None:
        self.key = key
        self.timeout = timeout
        self.verbose = verbose
        self.headers = headers
        self.cookies = cookies

    def __parse_responses(
        self,
        responses: list[tuple[Union[str, int, bytes, None]]],
        batch_time: float,
    ) -> Batch:
        pass
        response_list = [
            Response.parse(url=r[1], status_code=r[2], time=r[3], data=r[0])
            for r in responses
        ]
        return Batch(item=response_list, time=batch_time)

    def fetch(self, urls: list[str]):
        # responses, batch_time = asyncio.run(
        #     _async_batch_request(
        #         urls=urls,
        #         key=self.key,
        #         headers=self.headers,
        #         cookies=self.cookies,
        #         timeout=self.timeout,
        #     )
        # )
        loop = asyncio.get_event_loop()
        responses, batch_time = loop.run_until_complete(
            _async_batch_request(
                urls=urls,
                key=self.key,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
            )
        )
        return self.__parse_responses(responses=responses, batch_time=batch_time)


if __name__ == "__main__":
    retriever = Retriever()
    batch = retriever.fetch(["https://www.duckduckgo.com"] * 10)
    # pprint(batch)
    # pprint(batch.success_percent)
    # pprint(batch.approx_speedup)
    pprint(batch.item[0].data.decode("utf8"))
