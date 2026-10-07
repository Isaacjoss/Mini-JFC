"""Acceso web genérico: descarga de páginas y guardado de texto (solo librería estándar)."""
import html.parser
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REQUEST_TIMEOUT = 15
USER_AGENT = "Mini-JFC/0.1"
DEFAULT_MAX_CHARS = 20_000
_TRUNCATED_MARKER = "[...recortado]"
_ALLOWED_SCHEMES = ("http", "https")
_SKIP_TAGS = {"script", "style"}


class _TextExtractor(html.parser.HTMLParser):
    """Extrae el texto visible de un HTML: ignora <script>/<style> y descarta las etiquetas."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self._skipping += 1
        elif not self._skipping:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS:
            if self._skipping:
                self._skipping -= 1
        elif not self._skipping:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self._skipping:
            self.parts.append(data)


def _header(response, name) -> str:
    """Valor de cabecera HTTP como texto, o '' si no está o no es texto."""
    for call in (
        lambda: response.getheader(name),
        lambda: (response.headers or {}).get(name),
    ):
        try:
            value = call()
        except Exception:
            continue
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _http_status(response) -> int | None:
    """Código HTTP de la respuesta (getcode/status/code) o None si no es un entero."""
    for call in (
        lambda: response.getcode(),
        lambda: getattr(response, "status", None),
        lambda: getattr(response, "code", None),
    ):
        try:
            value = call()
        except Exception:
            continue
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def _content_is_text(content_type: str) -> bool:
    """True si el Content-Type es texto/HTML/XML/JSON o no viene declarado."""
    if not content_type:
        return True
    essence = content_type.split(";")[0].strip().lower()
    if essence.startswith("text/"):
        return True
    return essence in {"application/xhtml+xml", "application/xml", "application/json"} or essence.endswith("+xml")


def _charset_of(content_type: str) -> str | None:
    """Codificación declarada en 'charset=...' del Content-Type, o None."""
    match = re.search(r"charset\s*=\s*([^\s;]+)", content_type or "", re.IGNORECASE)
    return match.group(1).strip("\"'") if match else None


def _extract_text(page: str) -> str:
    """Texto visible de la página (sin <script>/<style> ni etiquetas)."""
    extractor = _TextExtractor()
    extractor.feed(page)
    extractor.close()
    return "".join(extractor.parts)


def fetch_url(url, max_chars=DEFAULT_MAX_CHARS) -> str:
    """Descarga una página http/https y devuelve su texto plano, sin HTML y recortado a max_chars."""
    scheme = urllib.parse.urlparse(str(url or "").strip()).scheme.lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"solo se permiten URLs http/https, recibido: {url!r}")
    try:
        limit = int(max_chars)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"max_chars debe ser >= 0, recibido: {max_chars}") from exc
    if limit < 0:
        raise ValueError(f"max_chars debe ser >= 0, recibido: {max_chars}")

    target = str(url).strip()
    request = urllib.request.Request(target, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            status = _http_status(response)
            content_type = _header(response, "Content-Type")
            data = response.read()
    except urllib.error.HTTPError as exc:
        raise ConnectionError(f"HTTP {exc.code} al consultar {target}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise ConnectionError(f"fallo de red al consultar {target}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ConnectionError(f"timeout de {REQUEST_TIMEOUT} s al consultar {target}: {exc}") from exc
    except OSError as exc:
        raise ConnectionError(f"fallo de red al consultar {target}: {exc}") from exc

    if status is not None and status != 200:
        raise ConnectionError(f"HTTP {status} al consultar {target}")
    if not _content_is_text(content_type):
        raise ValueError(f"el contenido de {target} no es texto/HTML: {content_type}")
    if not data:
        raise ValueError(f"respuesta vacía de {target}")

    try:
        page = data.decode(_charset_of(content_type) or "utf-8", errors="replace")
    except LookupError:
        page = data.decode("utf-8", errors="replace")
    text = re.sub(r"\s+", " ", _extract_text(page)).strip()
    if len(text) > limit:
        text = text[:limit] + _TRUNCATED_MARKER
    return text


def save_text(text, dest_path) -> str:
    """Guarda text en dest_path (creando las carpetas necesarias) y devuelve la ruta escrita."""
    raw = "" if dest_path is None else str(dest_path).strip()
    if not raw:
        raise ValueError("dest_path no puede estar vacío")
    path = Path(raw).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("" if text is None else str(text), encoding="utf-8")
    return str(path)
