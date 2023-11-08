from __future__ import annotations

# from pydantic.dataclasses import dataclass
import asyncio
from typing import Optional, Any, Union
from pydantic import BaseModel
from pssm import secrets

from pasc.parallel import _async_batch_request
from pasc.env import RESPONSES


class Response(BaseModel):
    url: str
    status_code: int
    status_info: str
    time: float
    data: Optional[bytes] = None

    @staticmethod
    def parse(
        url: str, status_code: int, time: float, data: Optional[bytes] = None
    ) -> Response:
        return Response(
            url=url,
            status_code=status_code,
            status_info=RESPONSES[status_code],
            time=time,
            data=data,
        )


class Batch(BaseModel):
    responses: list[Response]
    time: float

    @property
    def success_percent(self) -> float:
        pass

    @property
    def failure_percent(self) -> float:
        pass

    @property
    def success_count(self) -> int:
        pass

    @property
    def failure_count(self) -> int:
        pass

    @property
    def success(self) -> list[Response]:
        pass

    @property
    def failure(self) -> list[Response]:
        pass

    @property
    def synchronous_time(self) -> float:
        "returns what the synchronous time would have been otherwise (does not account for scrapestack proxy lag)"
        return sum([r.time for r in self.responses])


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

    async def __get_notebook(self, urls: list[str]):
        responses, batch_time = await _async_batch_request(
            urls=urls,
            key=self.key,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout,
        )
        return responses, batch_time

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
        return Batch(responses=response_list, time=batch_time)

    def fetch(self, urls: list[str]):
        if self.notebook:
            responses, batch_time = self.__get_notebook(urls=urls)
        else:
            responses, batch_time = self.__get_default(urls=urls)
        return self.__parse_responses(resposnes=responses, batch_time=batch_time)


if __name__ == "__main__":
    ret = Retriever()
    a, b = ret.fetch(["https://www.duckduckgo.com"] * 10)
    print(a)
    print(b)
    # * note: runs in terminal, not in notebook
    # ! RuntimeError: asyncio.run() cannot be called from a running event loop
