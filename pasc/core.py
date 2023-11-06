from pssm import secrets
from typing import Optional
from pydantic import BaseModel

# from pydantic.dataclasses import dataclass


class ResponseBatch(BaseModel):
    pass


class Retriever:
    def __init__(
        self,
        token: str = secrets.get("scrapestack"),
        timeout: int = 20,
        verbose: bool = False,
        parser: Optional[BaseModel] = None,
        cookies: Optional[dict] = None,
    ) -> None:
        self.token = token

    def get(self, urls: list[str]) -> ResponseBatch:
        pass
