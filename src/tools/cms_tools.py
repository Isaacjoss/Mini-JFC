"""Acceso y descubrimiento de datasets de CMS Open Data (opendata.cern.ch).

Solo se descarga un fichero en download_file; el resto de funciones solo leen
metadatos de la API. El registro de descargas reutiliza log_retrieval de
literature_tools.
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .literature_tools import log_retrieval  # reutilizada, no se duplica aquí

REQUEST_TIMEOUT = 15
USER_AGENT = "Mini-JFC/0.1 (herramienta de CMS Open Data; urllib)"
API_URL = "https://opendata.cern.ch/api/records"
PORTAL_URL = "https://opendata.cern.ch"
_CHUNK = 64 * 1024
_HTML_TAG_RE = re.compile(r"<[^>]+>")


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


def _get_json(url: str) -> dict:
    """GET que devuelve el JSON del portal y falla con error claro si no es JSON."""
    data = _get(url)
    try:
        payload = json.loads(data)
    except ValueError as exc:
        raise ValueError(f"la respuesta de {url} no es JSON válido: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"respuesta inesperada de {url}: se esperaba un objeto JSON")
    return payload


def _first(value):
    """Primer elemento de una lista/tupla, o el propio valor si no lo es."""
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def _clean(value):
    """Texto con espacios colapsados, o None si no hay valor."""
    if value is None:
        return None
    return " ".join(str(value).split())


def _field(meta, *keys):
    """Primer valor no vacío entre las claves indicadas de los metadatos, o None."""
    for key in keys:
        value = _first(meta.get(key)) if isinstance(meta, dict) else None
        if value is not None and str(value).strip():
            return value
    return None


def _unwrap(value):
    """Desempaqueta listas y dicts como {'description': '<p>...'} hasta dar con el valor textual."""
    for _ in range(6):
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None
        elif isinstance(value, dict):
            inner = _field(value, "description", "value", "text")
            value = inner if inner is not None else _first(list(value.values()))
        else:
            break
    return value


def _plain_text(value) -> str | None:
    """Texto plano: desempaqueta el valor y elimina las etiquetas HTML (re), o None si no hay texto."""
    text = _HTML_TAG_RE.sub(" ", str(_unwrap(value) or ""))
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)  # sin espacios antes de signos de puntuación
    return _clean(text) or None


def _year(meta) -> int | None:
    """Año del registro (clave 'year' o a partir de la fecha), o None si no se puede determinar."""
    value = _field(meta, "year", "publication_year")
    if value is None:
        value = _field(meta, "date", "publication_date", "date_created")
    if value is None:
        return None
    text = str(value).strip()
    return int(text[:4]) if text[:4].isdigit() else None


def _energy(meta):
    """Energía de centro de masa del registro ('collision_information.energy' en el portal), o None si falta."""
    value = _field(meta, "collision_energy", "center_of_mass_energy", "energy")
    if value is None and isinstance(meta, dict):
        info = _field(meta, "collision_information")
        value = _field(info, "energy", "center_of_mass_energy", "collision_energy")
    return value


def _metadata(record: dict) -> dict:
    """Metadatos del registro (en 'metadata' o directamente en la raíz)."""
    meta = record.get("metadata")
    return meta if isinstance(meta, dict) else record


def _recid(record: dict, meta: dict, fallback=None):
    """Identificador del registro ('id', 'recid' o el indicado), o None si falta."""
    value = record.get("id")
    if value is None:
        value = _field(meta, "recid", "control_number")
    return fallback if value is None else value


def _int_or_none(value) -> int | None:
    """Entero desde int/str/'12.3'/'{"value": 12}' o None si no es convertible."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        return int(text) if text.isdigit() else None
    if isinstance(value, dict):
        return _int_or_none(value.get("value"))
    return None


def _file_name(item: dict, uri) -> str | None:
    """Nombre del archivo: el declarado ('name', 'filename' o 'key') o, si falta, el último segmento del uri."""
    name = _first(item.get("name") or item.get("filename") or item.get("key"))
    if name is not None and str(name).strip():
        return str(name).strip()
    if uri:
        return Path(urllib.parse.urlparse(str(uri)).path).name or None
    return None


def _normalize_files(raw) -> list:
    """Convierte 'files' del portal en una lista de {name, size_bytes, uri} tolerando formatos."""
    if raw is None:
        return []
    if isinstance(raw, dict):
        for key in ("entries", "files", "objects"):
            inner = raw.get(key)
            if isinstance(inner, (list, dict)):
                raw = inner
                break
    if isinstance(raw, dict):
        items = []
        for name, spec in raw.items():
            item = dict(spec) if isinstance(spec, dict) else {"size": spec}
            item.setdefault("name", name)
            items.append(item)
    elif isinstance(raw, list):
        items = raw
    else:
        return []

    files = []
    for item in items:
        if isinstance(item, str):
            item = {"uri": item}
        if not isinstance(item, dict):
            continue
        uri = _field(item, "uri", "url", "href", "path")
        entry = {
            "name": _file_name(item, uri),
            "size_bytes": _int_or_none(_field(item, "size_bytes", "size")),
            "uri": uri,
        }
        if entry["name"] is None and entry["uri"] is None and entry["size_bytes"] is None:
            continue
        files.append(entry)
    return files


def _file_indices(meta: dict, payload: dict) -> list:
    """Índices de archivos del registro ('_file_indices'/'file_indices' en metadata o en la raíz)."""
    raw = None
    for source in (meta, payload):
        if not isinstance(source, dict):
            continue
        raw = source.get("_file_indices") or source.get("file_indices")
        if raw:
            break
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        return []
    return [index for index in raw if isinstance(index, dict)]


def _all_files(meta: dict, payload: dict) -> list:
    """Archivos {name, size_bytes, uri} del registro: 'files' (metadata o raíz) e índices _file_indices, sin duplicados."""
    chunks = [_normalize_files(meta.get("files")), _normalize_files(payload.get("files"))]
    for index in _file_indices(meta, payload):
        chunks.append(_normalize_files(index.get("files")))

    files, seen = [], set()
    for chunk in chunks:
        for entry in chunk:
            identity = (entry["name"], entry["size_bytes"], entry["uri"])
            if identity in seen:
                continue
            seen.add(identity)
            files.append(entry)
    return files


def _summary(hit: dict) -> dict:
    """Dict {recid, title, year, collision_energy, url} a partir de un hit del portal."""
    meta = _metadata(hit)
    recid = _recid(hit, meta)
    return {
        "recid": recid,
        "title": _clean(_field(meta, "title")),
        "year": _year(meta),
        "collision_energy": _energy(meta),
        "url": f"{PORTAL_URL}/record/{recid}" if recid is not None else None,
    }


def _to_https(uri) -> str:
    """Convierte root://eospublic.cern.ch//eos/... en https://opendata.cern.ch/eos/... (otras uris se quedan igual)."""
    text = str(uri or "").strip()
    if not text.startswith("root://"):
        return text
    rest = text[len("root://"):]
    slash = rest.find("/")
    path = rest[slash + 1:] if slash >= 0 else ""
    return f"{PORTAL_URL}/{path.lstrip('/')}"


def _content_length(response) -> int | None:
    """Tamaño declarado del recurso (Content-Length) o None si no está o no es numérico."""
    values = []
    for call in (
        lambda: response.getheader("Content-Length"),
        lambda: (response.headers or {}).get("Content-Length"),
        lambda: response.headers.get("content-length"),
        lambda: response.info().get("Content-Length"),
        lambda: response.length,
    ):
        try:
            values.append(call())
        except Exception:
            continue
    for value in values:
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None
        if value is None or isinstance(value, bool):
            continue
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            continue
    return None


def _too_big_message(name, size, limit) -> str:
    """Mensaje de error claro cuando un archivo supera max_bytes."""
    return (
        f"el archivo {name} pesa {size} bytes y supera max_bytes={limit}; "
        "vuelve a llamar con confirm=True para descargarlo"
    )


def _wrap_query(query: str) -> str:
    """Un término simple (sin '*', ':' ni espacios) se envuelve como *término*; con comodines o ':' se respeta tal cual.

    El portal hace búsqueda prefijo/sufijo exactos: 'HToTauTau*' no encuentra nada y '*HToTauTau*' sí.
    """
    if any(marker in query for marker in ("*", ":")):
        return query
    if any(character.isspace() for character in query):
        return query
    return f"*{query}*"


def _search_query(query: str, experiment, record_type) -> str:
    """q final: la consulta del usuario entre paréntesis y los filtros como términos de campo unidos con AND.

    El portal ignora el parámetro 'f' de la URL, así que experimento y tipo se aplican dentro de 'q'
    (p. ej. '(*tautau*) AND experiment:CMS AND type.primary:Dataset').
    """
    clauses = [f"({_wrap_query(query)})"]
    if experiment:
        clauses.append(f"experiment:{experiment}")
    if record_type:
        clauses.append(f"type.primary:{record_type}")
    return " AND ".join(clauses)


def _experiment_matches(meta, experiment) -> bool:
    """Red de seguridad en cliente: False solo si el registro trae 'experiment' y no coincide con el pedido.

    Si el campo no viene en la respuesta (o viene vacío) no se puede verificar y el registro se conserva.
    """
    if not isinstance(meta, dict):
        return True
    raw = meta.get("experiment")
    if raw is None:
        return True
    values = raw if isinstance(raw, (list, tuple)) else [raw]
    known = {str(value).strip().lower() for value in values if value is not None and str(value).strip()}
    if not known:
        return True
    return str(experiment).strip().lower() in known


def search_records(query, experiment="CMS", record_type="Dataset", max_results=10) -> list:
    """Busca registros en el portal y devuelve dicts {recid, title, year, collision_energy, url}."""
    query = str(query or "").strip()
    if not query:
        raise ValueError("query no puede estar vacía")
    try:
        size = int(max_results)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"max_results debe ser >= 1, recibido: {max_results}") from exc
    if size < 1:
        raise ValueError(f"max_results debe ser >= 1, recibido: {max_results}")

    params = [("q", _search_query(query, experiment, record_type)), ("size", str(size))]
    payload = _get_json(f"{API_URL}?{urllib.parse.urlencode(params)}")

    hits = payload.get("hits")
    if isinstance(hits, dict):
        hits = hits.get("hits")
    if not isinstance(hits, list):
        raise ValueError("respuesta inesperada del portal: falta 'hits.hits'")
    rows = []
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        if experiment and not _experiment_matches(_metadata(hit), experiment):
            continue
        rows.append(_summary(hit))
    return rows


def get_record(recid) -> dict:
    """Ficha de un registro: título, descripción, año, energía y lista de archivos."""
    text = str(recid).strip() if recid is not None else ""
    if not text:
        raise ValueError("recid no puede estar vacío")
    payload = _get_json(f"{API_URL}/{urllib.parse.quote(text, safe='')}")
    meta = _metadata(payload)
    record_id = _recid(payload, meta, fallback=text)
    return {
        "recid": record_id,
        "title": _clean(_field(meta, "title")),
        "description": _plain_text(_field(meta, "description", "abstract")),
        "year": _year(meta),
        "collision_energy": _energy(meta),
        "files": _all_files(meta, payload),
        "url": f"{PORTAL_URL}/record/{record_id}" if record_id is not None else None,
    }


def list_files(recid) -> list:
    """Lista los archivos {name, size_bytes, uri} de un registro (metadata.files o índices _file_indices)."""
    return get_record(recid)["files"]


def download_file(uri, dest_dir, max_bytes=500_000_000, confirm=False) -> str:
    """Descarga un archivo en streaming a dest_dir (convierte root:// a https://) y devuelve la ruta local."""
    url = _to_https(uri)
    if not url:
        raise ValueError("uri no puede estar vacía")
    try:
        limit = int(max_bytes)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"max_bytes debe ser un entero, recibido: {max_bytes}") from exc

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    name = Path(urllib.parse.urlparse(url).path).name or "descarga"
    path = dest / name

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        response = urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT)
    except urllib.error.HTTPError as exc:
        raise ConnectionError(f"HTTP {exc.code} al descargar {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise ConnectionError(f"fallo de red al descargar {url}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ConnectionError(f"timeout de {REQUEST_TIMEOUT} s al descargar {url}: {exc}") from exc
    except OSError as exc:
        raise ConnectionError(f"fallo de red al descargar {url}: {exc}") from exc

    total = 0
    too_big = False
    with response:
        size = _content_length(response)
        if not confirm and size is not None and size > limit:
            raise ValueError(_too_big_message(name, size, limit))
        previous = None
        try:
            with path.open("wb") as handle:
                while True:
                    chunk = response.read(_CHUNK)
                    if not chunk or chunk is previous:
                        break
                    previous = chunk
                    handle.write(chunk)
                    total += len(chunk)
                    if size is not None and total >= size:
                        break
                    if not confirm and total > limit:
                        too_big = True
                        break
        except OSError as exc:
            path.unlink(missing_ok=True)
            raise ConnectionError(f"fallo de red al descargar {url}: {exc}") from exc

    if too_big:
        path.unlink(missing_ok=True)
        raise ValueError(_too_big_message(name, total, limit))
    if total == 0:
        path.unlink(missing_ok=True)
        raise ValueError(f"respuesta vacía de {url}")
    return str(path)
