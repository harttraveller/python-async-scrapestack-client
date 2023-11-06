# external imports

import asyncio
from typing import Optional
from pydantic import BaseModel
from pssm import secrets

# internal imports
from pasc import parallel

# from pydantic.dataclasses import dataclass


class ResponseResult:
    pass


class BatchResults:
    pass


class BatchStatistics:
    pass


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
        self.timeout = timeout
        self.verbose = verbose
        self.headers = headers
        self.cookies = cookies
        self.parser = parser

    def get(self, urls: list[str]) -> ResponseBatch:
        responses, batch_time = asyncio.run(
            parallel._async_batch_request(
                urls=urls,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
            )
        )
