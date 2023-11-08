# from pydantic.dataclasses import dataclass
import asyncio
from typing import Optional, Any
from pydantic import BaseModel
from pssm import secrets

from pasc.parallel import _async_batch_request


class ResponseResult(BaseModel):
    url: str
    status_code: int
    status_info: str
    data: Optional[bytes] = None


class BatchStatistics:
    pass


class ResponseBatch(BaseModel):
    items: list[ResponseResult]
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
    def success(self) -> list[ResponseResult]:
        pass

    @property
    def failure(self) -> list[ResponseResult]:
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

    def fetch(self, urls: list[str]):
        if self.notebook:
            responses, batch_time = self.__get_notebook(urls=urls)
        else:
            responses, batch_time = self.__get_default(urls=urls)
        return responses, batch_time


if __name__ == "__main__":
    ret = Retriever()
    a, b = ret.fetch(["https://www.duckduckgo.com"] * 10)
    print(a)
    print(b)
    # * note: runs in terminal, not in notebook
    # ! RuntimeError: asyncio.run() cannot be called from a running event loop
