"""Tests de src/tools/web_tools.py sin internet (urlopen parcheado con mocks)."""
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tools import web_tools

HTML = (
    "<!DOCTYPE html>"
    "<html><head><title>Titulo</title>"
    "<style>body { color: red; }</style>"
    "<script>alert('no');</script>"
    "</head>"
    "<body>  <h1>Hola   Mundo</h1>"
    "<p>Texto de ejemplo.</p>"
    "<script>var x = 1;</script>"
    "<p>Fin.</p></body></html>"
)
HTML_LIMPIO = "Titulo Hola Mundo Texto de ejemplo. Fin."
URL = "https://example.com/pagina"


def _fake_response(data: bytes, headers=None, status=200):
    """Response falso de urllib: cabeceras, status y .read() en un solo trozo."""
    final_headers = {"Content-Type": "text/html; charset=utf-8"}
    final_headers.update(headers or {})
    headers = final_headers
    response = mock.MagicMock()
    response.__enter__.return_value = response
    response.headers = headers
    response.status = status
    response.getcode.return_value = status
    response.getheader = lambda name, default=None: headers.get(name, default)
    response.read.return_value = data
    return response


class FetchUrlTest(unittest.TestCase):
    """Prueba fetch_url con un HTML de ejemplo, sin tocar la red."""

    def test_descarga_y_limpia_html(self):
        with mock.patch("pathlib.Path.write_text") as write:
            with mock.patch(
                "urllib.request.urlopen",
                return_value=_fake_response(HTML.encode("utf-8")),
            ) as m:
                text = web_tools.fetch_url(URL)

        self.assertEqual(text, HTML_LIMPIO)
        self.assertNotIn("alert", text)
        self.assertNotIn("color", text)
        self.assertNotIn("<", text)
        self.assertEqual(write.call_count, 0)  # nunca escribe: solo save_text

        request = m.call_args.args[0]
        self.assertEqual(request.full_url, URL)
        self.assertEqual(dict(request.header_items())["User-agent"], "Mini-JFC/0.1")
        self.assertEqual(m.call_args.kwargs.get("timeout"), 15)

    def test_recorta_a_max_chars(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(HTML.encode("utf-8"))):
            completo = web_tools.fetch_url(URL)
            corto = web_tools.fetch_url(URL, max_chars=10)

        self.assertEqual(corto, completo[:10] + "[...recortado]")
        self.assertTrue(corto.startswith("Titulo Hol"))

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(HTML.encode("utf-8"))):
            self.assertEqual(web_tools.fetch_url(URL, max_chars=10_000), completo)

    def test_rechaza_esquemas_no_web(self):
        with mock.patch("urllib.request.urlopen") as m:
            for url in (
                "file:///etc/passwd",
                "ftp://host/archivo.txt",
                "data:text/html,hola",
                "javascript:alert(1)",
                "mailto:a@b.es",
                "",
                None,
                "www.example.com",
            ):
                with self.subTest(url=url):
                    with self.assertRaises(ValueError):
                        web_tools.fetch_url(url)
            self.assertEqual(m.call_count, 0)

    def test_errores_de_red_y_http(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("sin red")):
            with self.assertRaises(ConnectionError) as ctx:
                web_tools.fetch_url(URL)
        self.assertIn("fallo de red", str(ctx.exception))

        with mock.patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.HTTPError("http://x", 404, "no existe", None, None),
        ):
            with self.assertRaises(ConnectionError) as ctx:
                web_tools.fetch_url(URL)
        self.assertIn("404", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"oops", status=500)):
            with self.assertRaises(ConnectionError) as ctx:
                web_tools.fetch_url(URL)
        self.assertIn("HTTP 500", str(ctx.exception))

    def test_contenido_no_texto_y_respuesta_vacia(self):
        with mock.patch(
            "urllib.request.urlopen",
            return_value=_fake_response(b"\x89PNG", {"Content-Type": "image/png"}),
        ):
            with self.assertRaises(ValueError) as ctx:
                web_tools.fetch_url(URL)
        self.assertIn("texto/HTML", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"")):
            with self.assertRaises(ValueError) as ctx:
                web_tools.fetch_url(URL)
        self.assertIn("vac", str(ctx.exception))

    def test_decodifica_charset_declarado(self):
        response = _fake_response(
            "café".encode("iso-8859-1"),
            {"Content-Type": "text/html; charset=iso-8859-1"},
        )
        with mock.patch("urllib.request.urlopen", return_value=response):
            self.assertEqual(web_tools.fetch_url(URL), "café")

    def test_max_chars_invalido(self):
        with mock.patch("urllib.request.urlopen") as m:
            for bad in (-1, "x", None):
                with self.subTest(max_chars=bad):
                    with self.assertRaises(ValueError):
                        web_tools.fetch_url(URL, max_chars=bad)
            self.assertEqual(m.call_count, 0)


class SaveTextTest(unittest.TestCase):
    """Prueba save_text en una carpeta temporal."""

    def test_crea_carpetas_y_escribe(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "informes" / "2026" / "salida.txt"
            ruta = web_tools.save_text("hola\nmundo", dest)

            self.assertEqual(ruta, str(dest))
            self.assertEqual(dest.read_text(encoding="utf-8"), "hola\nmundo")

    def test_texto_none_guarda_vacio(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "nota.txt"
            ruta = web_tools.save_text(None, dest)

            self.assertEqual(ruta, str(dest))
            self.assertEqual(dest.read_text(encoding="utf-8"), "")

    def test_dest_path_vacio(self):
        for bad in (None, "", "   "):
            with self.subTest(dest_path=bad):
                with self.assertRaises(ValueError):
                    web_tools.save_text("x", bad)


if __name__ == "__main__":
    unittest.main()
