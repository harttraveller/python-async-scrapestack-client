# pasc (python-async-scrapestack-client)

*If you need to use this but are confused by the docs, then submit an issue and I will create formal docs. Right now this functions as a dependency for personal projects.*

## links

- [PyPi](https://pypi.org/project/python-async-scrapestack-client/)

## description

Asynchronous requests for [scrapestack](https://scrapestack.com/).

## install

Install with pip:

```sh
pip install python-async-scrapestack-client
```

[python-simple-secrets-manager](https://github.com/harttraveller/pssm) is installed as a dependency.

once you get your scrapestack api key, you can add it to pssm with:

```sh
secrets keep -a -uid scrapestack -key [YOUR API TOKEN]
```

## usage

request urls

```py
from pasc import Retriever

retriever = Retriever()
batch = retriever.fetch(["https://www.duckduckgo.com"] * 10)
```

access results

```py
# from pasc import Response # * type import, note required

response: Response = batch.item[0]

print(response.url)
print(response.time)
print(response.code)
print(response.detail)
print(response.data)

# If response is rawtext like html, call:

html = response.data.decode("utf8")

```




## todo

- [ ] add back in progress bar
- [ ] resolve event loop issue for jupyter notebooks
- [ ] add better docs if requested
