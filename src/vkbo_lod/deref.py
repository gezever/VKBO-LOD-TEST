from dataclasses import dataclass
from typing import Optional

import httpx
from rdflib import Graph, Namespace, URIRef

ORG = Namespace("http://www.w3.org/ns/org#")


@dataclass
class DerefResult:
    uri: str
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    is_valid_turtle: bool = False
    linked_onderneming: Optional[str] = None
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.status_code == 200 and self.is_valid_turtle


def deref_as_turtle(uri: str, client: httpx.Client) -> DerefResult:
    result = DerefResult(uri=uri)
    try:
        response = client.get(uri, headers={"Accept": "text/turtle"}, follow_redirects=True)
        result.status_code = response.status_code
        result.content_type = response.headers.get("content-type", "")

        if response.status_code != 200:
            result.error = f"HTTP {response.status_code}"
            return result

        graph = Graph()
        graph.parse(data=response.text, format="turtle")
        result.is_valid_turtle = True

        for obj in graph.objects(URIRef(uri), ORG.siteOf):
            result.linked_onderneming = str(obj)
            break

    except httpx.RequestError as exc:
        result.error = f"Request error: {exc}"
    except Exception as exc:
        result.error = f"Parse error: {exc}"

    return result


def check_vestiging(uri: str, client: httpx.Client) -> tuple[DerefResult, Optional[DerefResult]]:
    vestiging = deref_as_turtle(uri, client)
    onderneming = None
    if vestiging.linked_onderneming:
        onderneming = deref_as_turtle(vestiging.linked_onderneming, client)
    return vestiging, onderneming
