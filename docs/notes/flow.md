

Without parsers or cookies, pseudocode.

```py
from pasc import Retriever

retriever = Retriever(parser=None, cookies=None, timeout: int = 10, verbose: bool = False)

batch = retriever.get(urls=[url1, url2]) -> BatchResponse

batch.statistics

batch.results


batch.results -> {url: [Logs, Data]}

batch.results[url1] -> [Logs, Data]

batch.success -> {url: [Logs, Data]}

batch.failure -> {url: [Logs, Data]}


```