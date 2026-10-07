"""Búsqueda y recuperación de literatura científica (arXiv e INSPIRE)."""
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

REQUEST_TIMEOUT = 15
USER_AGENT = "Mini-JFC/0.1 (herramienta de literatura; urllib)"
ARXIV_API = "http://export.arxiv.org/api/query"
INSPIRE_API = "https://inspirehep.net/api/literature"

_ATOM = "{http://www.w3.org/2005/Atom}"
_LOG_HEADER = "| fecha | tipo | fuente/URL | ruta local | motivo |"
_LOG_SEP = "| --- | --- | --- | --- | --- |"


def _get(url: str) -> bytes:
    """GET con timeout de 15 s y User-Agent; errores claros si falla la red o la respuesta está vacía."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        raise ConnectionError(f"HTTP {exc.code} al consultar {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise ConnectionError(f"fallo de red al consultar {url}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ConnectionError(f"timeout de {REQUEST_TIMEOUT} s al consultar {url}: {exc}") from exc
    except OSError as exc:
        raise ConnectionError(f"fallo de red al consultar {url}: {exc}") from exc
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


def search_arxiv(query, max_results=5) -> list:
    """Busca en la API Atom de arXiv y devuelve dicts {id, title, authors, summary, url, pdf_url}."""
    if not _clean(query):
        raise ValueError("query no puede estar vacía")
    if int(max_results) < 1:
        raise ValueError(f"max_results debe ser >= 1, recibido: {max_results}")
    params = urllib.parse.urlencode(
        {"search_query": f"all:{query}", "start": 0, "max_results": int(max_results)}
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
                "authors": authors,
                "summary": _clean(entry.findtext(f"{_ATOM}summary")),
                "url": url,
                "pdf_url": pdf_url or url.replace("/abs/", "/pdf/"),
            }
        )
    return results


def search_inspire(query, max_results=5) -> list:
    """Busca en la API de INSPIRE y devuelve dicts {recid, title, authors, year, arxiv_id, url}."""
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
                "authors": [
                    _clean(a.get("full_name"))
                    for a in meta.get("authors", [])
                    if _clean(a.get("full_name"))
                ],
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
    data = _get(f"https://arxiv.org/pdf/{arxiv_id}")
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
