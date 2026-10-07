"""Tests de src/tools/literature_tools.py sin internet (urlopen parcheado con mocks)."""
import json
import re
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tools import literature_tools

ARXIV_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>ArXiv Query: search_query=all:transformer</title>
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <title>Attention Is All You Need</title>
    <summary>
      The dominant sequence transduction models are based on complex recurrent
      or convolutional neural networks.
    </summary>
    <author><name>Ashish Vaswani</name></author>
    <author><name>Noam Shazeer</name></author>
    <link href="http://arxiv.org/abs/1706.03762v7" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1706.03762v7" rel="related" type="application/pdf"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/1810.04805v2</id>
    <title>BERT: Pre-training of Deep Bidirectional Transformers</title>
    <summary>We introduce a new language representation model called BERT.</summary>
    <author><name>Jacob Devlin</name></author>
    <link href="http://arxiv.org/abs/1810.04805v2" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1810.04805v2" rel="related" type="application/pdf"/>
  </entry>
</feed>
"""

INSPIRE_JSON = json.dumps(
    {
        "hits": {
            "total": 2,
            "hits": [
                {
                    "id": "1457891",
                    "metadata": {
                        "control_number": 1457891,
                        "titles": [{"title": "Deep learning in particle physics"}],
                        "authors": [
                            {"full_name": "Example, Alice"},
                            {"full_name": "Muestra, Bob"},
                        ],
                        "earliest_date": "2021-05-12",
                        "arxiv_eprints": [{"value": "2105.04567"}],
                    },
                },
                {
                    "id": "1234567",
                    "metadata": {
                        "control_number": 1234567,
                        "titles": [{"title": "Record antiguo sin arXiv"}],
                        "authors": [],
                        "earliest_date": "1999",
                    },
                },
            ],
        }
    }
).encode("utf-8")


def _fake_response(data, headers=None):
    """Response falso: soporta 'with' y .read()/.headers() como el de urllib."""
    response = mock.MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = data
    response.headers = headers or {}
    response.getheader = lambda name, default=None: (headers or {}).get(name, default)
    return response


class SearchArxivTest(unittest.TestCase):
    """Prueba search_arxiv con un feed Atom de ejemplo y sin red."""

    def test_parsea_feed_atom(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(ARXIV_XML)) as m:
            rows = literature_tools.search_arxiv("transformer", max_results=2)

        self.assertEqual(len(rows), 2)
        first = rows[0]
        self.assertEqual(sorted(first), sorted(
            ["id", "title", "authors", "summary", "url", "pdf_url"]
        ))
        self.assertEqual(first["id"], "http://arxiv.org/abs/1706.03762v7")
        self.assertEqual(first["title"], "Attention Is All You Need")
        self.assertEqual(first["authors"], ["Ashish Vaswani", "Noam Shazeer"])
        self.assertIn("sequence transduction", first["summary"])
        self.assertEqual(first["url"], "http://arxiv.org/abs/1706.03762v7")
        self.assertEqual(first["pdf_url"], "http://arxiv.org/pdf/1706.03762v7")
        self.assertEqual(rows[1]["authors"], ["Jacob Devlin"])

        request = m.call_args.args[0]
        query = urllib.parse.parse_qs(urllib.parse.urlparse(request.full_url).query)
        self.assertIn("export.arxiv.org/api/query", request.full_url)
        self.assertEqual(query["search_query"], ["all:transformer"])
        self.assertEqual(query["max_results"], ["2"])
        self.assertEqual(m.call_args.kwargs.get("timeout"), 15)
        self.assertIn("Mini-JFC", dict(request.header_items())["User-agent"])

    def test_respuesta_vacia_y_error_de_red(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"")):
            with self.assertRaises(ValueError) as ctx:
                literature_tools.search_arxiv("transformer")
        self.assertIn("vac", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("sin red")):
            with self.assertRaises(ConnectionError) as ctx:
                literature_tools.search_arxiv("transformer")
        self.assertIn("fallo de red", str(ctx.exception))

        with mock.patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.HTTPError("http://x", 503, "caido", None, None),
        ):
            with self.assertRaises(ConnectionError) as ctx:
                literature_tools.search_arxiv("transformer")
        self.assertIn("503", str(ctx.exception))

    def test_xml_invalido_y_argumentos_invalidos(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"<feed")):
            with self.assertRaises(ValueError):
                literature_tools.search_arxiv("transformer")
        with self.assertRaises(ValueError):
            literature_tools.search_arxiv("   ")
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(ARXIV_XML)):
            with self.assertRaises(ValueError):
                literature_tools.search_arxiv("transformer", max_results=0)


class SearchInspireTest(unittest.TestCase):
    """Prueba search_inspire con un JSON de INSPIRE de ejemplo y sin red."""

    def test_parsea_json_de_inspire(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(INSPIRE_JSON)) as m:
            rows = literature_tools.search_inspire("hep-ph", max_results=2)

        self.assertEqual(len(rows), 2)
        first, second = rows
        self.assertEqual(first["recid"], "1457891")
        self.assertEqual(first["title"], "Deep learning in particle physics")
        self.assertEqual(first["authors"], ["Example, Alice", "Muestra, Bob"])
        self.assertEqual(first["year"], 2021)
        self.assertEqual(first["arxiv_id"], "2105.04567")
        self.assertEqual(first["url"], "https://inspirehep.net/literature/1457891")
        self.assertEqual(second["arxiv_id"], None)
        self.assertEqual(second["year"], 1999)
        self.assertEqual(second["authors"], [])

        request = m.call_args.args[0]
        query = urllib.parse.parse_qs(urllib.parse.urlparse(request.full_url).query)
        self.assertIn("inspirehep.net/api/literature", request.full_url)
        self.assertEqual(query["q"], ["hep-ph"])
        self.assertEqual(query["size"], ["2"])
        self.assertIn("titles", query["fields"][0])
        self.assertEqual(m.call_args.kwargs.get("timeout"), 15)
        self.assertIn("Mini-JFC", dict(request.header_items())["User-agent"])

    def test_errores_claros(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"")):
            with self.assertRaises(ValueError) as ctx:
                literature_tools.search_inspire("hep-ph")
        self.assertIn("vac", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"<html>")):
            with self.assertRaises(ValueError) as ctx:
                literature_tools.search_inspire("hep-ph")
        self.assertIn("JSON", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("sin red")):
            with self.assertRaises(ConnectionError):
                literature_tools.search_inspire("hep-ph")


class FetchArxivTextTest(unittest.TestCase):
    """Prueba fetch_arxiv_text descargando bytes falsos a un destino temporal."""

    def test_descarga_pdf_en_destino(self):
        pdf = b"%PDF-1.4\nfake pdf\n%%EOF"
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("urllib.request.urlopen", return_value=_fake_response(pdf)) as m:
                local = literature_tools.fetch_arxiv_text("1706.03762", tmp)

            path = Path(local)
            self.assertTrue(path.is_file())
            self.assertEqual(path.parent, Path(tmp))
            self.assertEqual(path.name, "1706.03762.pdf")
            self.assertEqual(path.read_bytes(), pdf)
            request = m.call_args.args[0]
            self.assertEqual(request.full_url, "https://arxiv.org/pdf/1706.03762")
            self.assertEqual(m.call_args.kwargs.get("timeout"), 15)

    def test_id_con_barra_no_crea_subcarpeta(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"%PDF")):
                local = literature_tools.fetch_arxiv_text(" hep-th/9901001 ", tmp)
            path = Path(local)
            self.assertEqual(path.parent, Path(tmp))
            self.assertEqual(path.name, "hep-th_9901001.pdf")
            self.assertTrue(path.is_file())

    def test_errores_claros_sin_guardar(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"")):
                with self.assertRaises(ValueError) as ctx:
                    literature_tools.fetch_arxiv_text("1706.03762", tmp)
            self.assertIn("vac", str(ctx.exception))

            with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("x")):
                with self.assertRaises(ConnectionError):
                    literature_tools.fetch_arxiv_text("1706.03762", tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])

            with self.assertRaises(ValueError):
                literature_tools.fetch_arxiv_text("  ", tmp)


class LogRetrievalTest(unittest.TestCase):
    """Prueba log_retrieval sobre un archivo temporal."""

    def test_crea_archivo_con_encabezado(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "retrieval_log.md"
            row = literature_tools.log_retrieval(
                log, "paper", "http://arxiv.org/abs/1706.03762", str(log.parent / "p.pdf"), "base"
            )
            lineas = log.read_text(encoding="utf-8").splitlines()

            self.assertEqual(lineas[0], "| fecha | tipo | fuente/URL | ruta local | motivo |")
            self.assertEqual(lineas[1], "| --- | --- | --- | --- | --- |")
            self.assertEqual(len(lineas), 3)
            self.assertEqual(len(re.split(r"(?<!\\)\|", lineas[2])), 7)  # 5 columnas
            self.assertTrue(lineas[2].startswith("| "))
            self.assertIn("paper", lineas[2])
            self.assertIn("http://arxiv.org/abs/1706.03762", lineas[2])
            self.assertIn("base", lineas[2])
            self.assertEqual(row, lineas[2])

    def test_anade_filas_sin_repetir_encabezado(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "sub" / "retrieval_log.md"
            literature_tools.log_retrieval(log, "dataset", "https://opendata.cern", "/a/b.root", "explorar")
            literature_tools.log_retrieval(log, "doc", "https://docs", "/c/d.md", "consulta | manual")

            lineas = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lineas), 4)
            self.assertEqual(sum(1 for l in lineas if l.startswith("| fecha")), 1)
            self.assertIn(r"consulta \| manual", lineas[3])
            for linea in lineas[2:]:
                # separa por '|' sin contar los '|' escapados dentro de una celda
                self.assertEqual(len(re.split(r"(?<!\\)\|", linea)), 7)


if __name__ == "__main__":
    unittest.main()
