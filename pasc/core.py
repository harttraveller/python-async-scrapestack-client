# from pydantic.dataclasses import dataclass

# external imports

import asyncio
from typing import Optional
from pydantic import BaseModel
from pssm import secrets


# internal imports
from pasc.parallel import _async_batch_request


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
