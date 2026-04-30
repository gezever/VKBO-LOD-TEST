# VKBO LOD TEST

Testproject voor de linked data publicatie van het VKBO (Vlaamse KruispuntBank van Ondernemingen).

## Doel

- Verifiëren dat vestiging-URI's gedereferenceerd kunnen worden
- Content negotiation testen voor `text/turtle`
- De `org:siteOf`-link naar de bijhorende onderneming volgen en ook dereferencen
- (Later) performantietesten uitvoeren op de linked data endpoints

## Vereisten

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Installatie

```bash
uv sync --extra dev
```

Voor performantietesten ook locust installeren:

```bash
uv sync --extra dev --extra perf
```

## Projectstructuur

```
├── src/vkbo_lod/
│   └── deref.py            # kernlogica: dereferencen + Turtle parsen
├── tests/
│   ├── functional/
│   │   └── test_deref.py   # pytest-tests voor dereference en content negotiation
│   └── performance/
│       └── locustfile.py   # Locust load tests (toekomstige fase)
├── scripts/
│   └── check_vestigingen.py  # bulk-check van alle URI's uit vestigingen.csv
└── sources/
    └── vestigingen.csv       # lijst van te testen vestiging-URI's
```

## Gebruik

### Functionele tests

Test dereference en content negotiation voor een voorbeeldvestiging en de gelinkte onderneming:

```bash
uv run pytest tests/functional/ -v
```

### Bulk-check van vestigingen.csv

Controleert alle URI's uit `vestigingen.csv` en schrijft het resultaat als CSV naar stdout:

```bash
uv run python scripts/check_vestigingen.py > resultaat.csv
```

Kolommen in de output:

| Kolom | Beschrijving |
|---|---|
| `vestiging_uri` | gecontroleerde vestiging-URI |
| `v_status` | HTTP-statuscode van de vestiging |
| `v_content_type` | Content-Type header van de response |
| `v_valid_turtle` | of de payload geldige Turtle is |
| `linked_onderneming` | gevonden `org:siteOf` onderneming-URI |
| `o_status` | HTTP-statuscode van de onderneming |
| `o_valid_turtle` | of de onderneming-payload geldige Turtle is |
| `error` | foutmelding indien van toepassing |

### Performantietesten (toekomstige fase)

```bash
uv run locust -f tests/performance/locustfile.py --host https://data.vlaanderen.be
```

Open daarna de Locust-webinterface op `http://localhost:8089`.

## Kernmodule

`src/vkbo_lod/deref.py` biedt twee publieke functies:

```python
from vkbo_lod.deref import deref_as_turtle, check_vestiging
import httpx

with httpx.Client(timeout=30) as client:
    # dereference één URI
    result = deref_as_turtle("https://data.vlaanderen.be/id/vestiging/2311823764", client)
    print(result.status_code, result.is_valid_turtle, result.linked_onderneming)

    # dereference vestiging + gelinkte onderneming in één aanroep
    vestiging, onderneming = check_vestiging("https://data.vlaanderen.be/id/vestiging/2311823764", client)
```

`DerefResult`-velden: `uri`, `status_code`, `content_type`, `is_valid_turtle`, `linked_onderneming`, `error`, `ok`.
