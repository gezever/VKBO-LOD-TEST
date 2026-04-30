import pytest
import httpx
from pathlib import Path
from vkbo_lod.deref import deref_as_turtle, check_vestiging

SOURCES = Path(__file__).parent.parent.parent / "sources"


def load_uris() -> list[str]:
    lines = (SOURCES / "vestigingen.csv").read_text().splitlines()
    return [line.strip() for line in lines if line.strip()]


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=30) as c:
        yield c


@pytest.mark.parametrize("uri", load_uris())
def test_vestiging_dereferences(uri, client):
    result = deref_as_turtle(uri, client)
    assert result.status_code == 200, result.error


@pytest.mark.parametrize("uri", load_uris())
def test_vestiging_content_negotiation_turtle(uri, client):
    result = deref_as_turtle(uri, client)
    assert result.is_valid_turtle, result.error


@pytest.mark.parametrize("uri", load_uris())
def test_vestiging_links_to_onderneming(uri, client):
    vestiging, onderneming = check_vestiging(uri, client)
    assert vestiging.linked_onderneming is not None, f"geen org:siteOf link gevonden voor {uri}"
    assert onderneming is not None
    assert onderneming.status_code == 200, onderneming.error
    assert onderneming.is_valid_turtle, onderneming.error
