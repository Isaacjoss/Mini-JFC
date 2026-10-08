"""Búsqueda y recuperación de literatura científica (arXiv e INSPIRE)."""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

REQUEST_TIMEOUT = 15
PDF_TIMEOUT = 30
USER_AGENT = "Mini-JFC/0.1 (herramienta de literatura; urllib)"
ARXIV_API = "https://export.arxiv.org/api/query"
INSPIRE_API = "https://inspirehep.net/api/literature"

MAX_AUTHORS = 3  # autores que se devuelven en "authors" (el resto, en n_authors/et_al)
SUMMARY_MAX_CHARS = 600  # máximo de caracteres del summary de arXiv
# consultas con sintaxis propia de arXiv: prefijos de campo u operadores AND/OR
_FIELD_PREFIX_RE = re.compile(r"(?<!\w)(?:all|ti|abs|cat|au):", re.IGNORECASE)
_OPERATOR_RE = re.compile(r"\bAND\b|\bOR\b")  # operadores de arXiv (en mayúsculas)
# puntuación que se ignora en los sueltos de una consulta de texto libre
_LOOSE_EDGES = ".,;:!?()[]{}\"'"

RETRY_ATTEMPTS = 3
RETRY_DELAYS = (2, 5)  # espera en segundos antes del 2.º y del 3.º intento
RETRYABLE_HTTP_CODES = frozenset({429, 500, 502, 503, 504})

_ATOM = "{http://www.w3.org/2005/Atom}"
_LOG_HEADER = "| fecha | tipo | fuente/URL | ruta local | motivo |"
_LOG_SEP = "| --- | --- | --- | --- | --- |"


def _request_with_retry(req, timeout, attempts=RETRY_ATTEMPTS) -> bytes:
    """GET con reintentos ante timeout, fallos de red y HTTP 429/500/502/503/504.

    Espera 2 s y 5 s entre intentos (espera creciente). Los demás errores 4xx
    (por ejemplo un 404) no se reintentan: se lanzan a la primera. Si se agotan
    los intentos se lanza el mismo error claro de siempre, indicando cuántos
    intentos se hicieron.
    """
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            retryable = exc.code in RETRYABLE_HTTP_CODES
            error = ConnectionError(f"HTTP {exc.code} al consultar {req.full_url}: {exc.reason}")
        except urllib.error.URLError as exc:
            retryable = True
            error = ConnectionError(f"fallo de red al consultar {req.full_url}: {exc.reason}")
        except TimeoutError as exc:
            retryable = True
            error = ConnectionError(f"timeout de {timeout} s al consultar {req.full_url}: {exc}")
        except OSError as exc:
            retryable = True
            error = ConnectionError(f"fallo de red al consultar {req.full_url}: {exc}")
        if not retryable:
            raise error
        if attempt >= attempts:
            raise ConnectionError(f"{error} (tras {attempts} intentos)")
        time.sleep(RETRY_DELAYS[min(attempt - 1, len(RETRY_DELAYS) - 1)])


def _get(url: str, timeout: int = REQUEST_TIMEOUT) -> bytes:
    """GET con reintentos y User-Agent; errores claros si falla la red o la respuesta está vacía."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    data = _request_with_retry(request, timeout)
    if not data:
        raise ValueError(f"respuesta vacía de {url}")
    return data


def _clean(text) -> str:
    """Colapsa los espacios de un texto de XML/JSON."""
    return " ".join(str(text or "").split())


def _cell(value) -> str:
    """Prepara un valor para una celda de tabla Markdown (sin '|' ni saltos de línea)."""
    return _clean(str(value).replace("|", r"\|"))


def _safe_name(arxiv_id: str) -> str:
    """Convierte un id de arXiv en un nombre de archivo seguro (sin '/' ni espacios)."""
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in arxiv_id)


def _author_fields(authors: list) -> dict:
    """Autores recortados a MAX_AUTHORS con n_authors (total) y et_al (si hay más de 3).

    Las colaboraciones de INSPIRE/arXiv traen miles de nombres; se devuelven como
    mucho los 3 primeros y el total se indica con n_authors/et_al.
    """
    total = len(authors)
    return {
        "authors": authors[:MAX_AUTHORS],
        "n_authors": total,
        "et_al": total > MAX_AUTHORS,
    }


def _short_summary(text: str, limit: int = SUMMARY_MAX_CHARS) -> str:
    """Recorta el resumen a `limit` caracteres, terminando en '...' si se pasa de él."""
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _uses_arxiv_syntax(query: str) -> bool:
    """¿La consulta ya trae prefijos de campo (all:, ti:, ...) u operadores AND/OR?"""
    return bool(_FIELD_PREFIX_RE.search(query) or _OPERATOR_RE.search(query))


def _arxiv_search_query(query, cat=None) -> str:
    """Construye el parámetro search_query de arXiv.

    * Texto libre (sin prefijos ni operadores): cada palabra de 3+ letras se
      envuelve como `all:"palabra"` y se unen con AND (más relevante que
      `all:frase entera`, que arXiv interpreta como una sola cadena).
    * Consulta con sintaxis arXiv (prefijos o AND/OR): se respeta tal cual.
    * `cat` (por defecto None): añade `AND cat:hep-ex` al final.
    """
    text = _clean(query)
    if _uses_arxiv_syntax(text):
        search_query = text
    else:
        words = [w.strip(_LOOSE_EDGES) for w in text.split() if w.strip(_LOOSE_EDGES)]
        terms = [f'all:"{word}"' for word in words if len(word) >= 3]
        if not terms:  # sólo palabras cortas: no perder la consulta
            terms = [f'all:"{word}"' for word in words]
        search_query = " AND ".join(terms)
    if cat:
        search_query = f"{search_query} AND cat:{_clean(cat)}"
    return search_query


def search_arxiv(query, max_results=5, cat=None) -> list:
    """Busca en la API Atom de arXiv y devuelve dicts
    {id, title, authors, n_authors, et_al, summary, url, pdf_url}.

    `authors` contiene como máximo los 3 primeros nombres (n_authors es el total
    y et_al indica si había más); `summary` se recorta a 600 caracteres. `cat`
    (por ejemplo "hep-ex") añade `AND cat:hep-ex` a la consulta.
    """
    if not _clean(query):
        raise ValueError("query no puede estar vacía")
    if int(max_results) < 1:
        raise ValueError(f"max_results debe ser >= 1, recibido: {max_results}")
    params = urllib.parse.urlencode(
        {
            "search_query": _arxiv_search_query(query, cat),
            "start": 0,
            "max_results": int(max_results),
        }
    )
    data = _get(f"{ARXIV_API}?{params}")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(f"la respuesta de arXiv no es XML válido: {exc}") from exc

    results = []
    for entry in root.findall(f"{_ATOM}entry"):
        entry_id = _clean(entry.findtext(f"{_ATOM}id"))
        url = entry_id
        pdf_url = None
        for link in entry.findall(f"{_ATOM}link"):
            href = link.get("href")
            if link.get("rel") == "alternate":
                url = href or url
            if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                pdf_url = href or pdf_url
        authors = [
            _clean(a.findtext(f"{_ATOM}name"))
            for a in entry.findall(f"{_ATOM}author")
            if _clean(a.findtext(f"{_ATOM}name"))
        ]
        results.append(
            {
                "id": entry_id,
                "title": _clean(entry.findtext(f"{_ATOM}title")),
                **_author_fields(authors),
                "summary": _short_summary(_clean(entry.findtext(f"{_ATOM}summary"))),
                "url": url,
                "pdf_url": pdf_url or url.replace("/abs/", "/pdf/"),
            }
        )
    return results


def search_inspire(query, max_results=5) -> list:
    """Busca en la API de INSPIRE y devuelve dicts
    {recid, title, authors, n_authors, et_al, year, arxiv_id, url}.

    `authors` contiene como máximo los 3 primeros nombres (n_authors es el total
    y et_al indica si había más de 3, típico en colaboraciones).
    """
    if not _clean(query):
        raise ValueError("query no puede estar vacía")
    if int(max_results) < 1:
        raise ValueError(f"max_results debe ser >= 1, recibido: {max_results}")
    params = urllib.parse.urlencode(
        {
            "q": query,
            "size": int(max_results),
            "fields": "control_number,authors.full_name,earliest_date,arxiv_eprints,titles",
        }
    )
    data = _get(f"{INSPIRE_API}?{params}")
    try:
        payload = json.loads(data)
    except ValueError as exc:
        raise ValueError(f"la respuesta de INSPIRE no es JSON válido: {exc}") from exc

    hits = payload.get("hits", {}).get("hits") if isinstance(payload, dict) else None
    if not isinstance(hits, list):
        raise ValueError("respuesta inesperada de INSPIRE: falta 'hits.hits'")

    results = []
    for hit in hits:
        meta = hit.get("metadata") or {}
        titles = meta.get("titles") or []
        eprints = meta.get("arxiv_eprints") or []
        date = _clean(meta.get("earliest_date"))
        recid = hit.get("id") or meta.get("control_number")
        results.append(
            {
                "recid": recid,
                "title": _clean(titles[0].get("title")) if titles else "",
                **_author_fields(
                    [
                        _clean(a.get("full_name"))
                        for a in meta.get("authors", [])
                        if _clean(a.get("full_name"))
                    ]
                ),
                "year": int(date[:4]) if date[:4].isdigit() else None,
                "arxiv_id": eprints[0].get("value") if eprints else None,
                "url": f"https://inspirehep.net/literature/{recid}" if recid else None,
            }
        )
    return results


def fetch_arxiv_text(arxiv_id, dest_dir) -> str:
    """Descarga el PDF de arXiv en dest_dir y devuelve la ruta local guardada."""
    arxiv_id = str(arxiv_id).strip()
    if not arxiv_id:
        raise ValueError("arxiv_id no puede estar vacío")
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    data = _get(f"https://arxiv.org/pdf/{arxiv_id}", timeout=PDF_TIMEOUT)
    path = dest / f"{_safe_name(arxiv_id)}.pdf"
    path.write_bytes(data)
    return str(path)


def log_retrieval(log_path, kind, source, local_path, reason) -> str:
    """Añade una fila a retrieval_log.md (crea el archivo con su encabezado si no existe) y la devuelve."""
    values = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        str(kind),
        str(source),
        str(local_path),
        str(reason),
    ]
    row = "| " + " | ".join(_cell(v) for v in values) + " |"
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if not text:
        text = f"{_LOG_HEADER}\n{_LOG_SEP}\n"
    elif not text.endswith("\n"):
        text += "\n"
    path.write_text(text + row + "\n", encoding="utf-8")
    return row
