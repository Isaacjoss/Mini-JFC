"""Tests de src/tools/cms_tools.py sin internet (urlopen parcheado con mocks)."""
import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tools import cms_tools, literature_tools

SEARCH_JSON = json.dumps(
    {
        "hits": {
            "total": 2,
            "hits": [
                {
                    "id": 1402954,
                    "metadata": {
                        "title": "DoubleMu primary dataset",
                        "type": "Dataset",
                        "experiment": "CMS",
                        "collision_information": {"energy": "7 TeV", "type": "pp"},
                        "date_created": ["2016-01-22"],
                    },
                },
                {
                    "id": 1402955,
                    "metadata": {
                        "title": "Mu primary dataset",
                        "collision_energy": ["8 TeV"],
                        "year": 2015,
                    },
                },
            ],
        }
    }
).encode("utf-8")

RECORD_JSON = json.dumps(
    {
        "id": "1402954",
        "links": {
            "self": "https://opendata.cern.ch/api/records/1402954",
            "bucket": "https://opendata.cern.ch/api/files/16b2fefb-917c-4a53-8e7b-175f1ba01c4e",
        },
        "metadata": {
            "$schema": "https://opendata.cern.ch/schema/records/record-v1.0.0.json",
            "recid": "1402954",
            "title": "DoubleMu primary dataset",
            "abstract": {
                "description": (
                    "<p>Datos de colisiones PP a 7 TeV.</p>"
                    '<p>Véase <a href="/about/CMS-Simulated-Dataset-Names">la guía</a>.</p>'
                )
            },
            "collision_information": {"energy": "7 TeV", "type": "pp"},
            "date_created": ["2016-01-22"],
            "distribution": {
                "formats": ["root"],
                "number_events": 1000,
                "number_files": 2,
                "size": 123560,
            },
            "files": [],
            "_file_indices": [
                {
                    "availability": {"online": 2},
                    "bucket": "16b2fefb-917c-4a53-8e7b-175f1ba01c4e",
                    "description": "DoubleMu file index (1 of 1) for access to data",
                    "key": "DoubleMu_file_index.json",
                    "number_files": 2,
                    "size": 123560,
                    "files": [
                        {
                            "availability": "online",
                            "checksum": "adler32:f0fb9713",
                            "filename": "DoubleMu.root",
                            "key": "DoubleMu_file_index.json_0",
                            "size": 123456,
                            "uri": "root://eospublic.cern.ch//eos/openData/2016/DoubleMu.root",
                        },
                        {"filename": "runinfo.csv", "key": "DoubleMu_file_index.json_1"},
                    ],
                }
            ],
        },
    }
).encode("utf-8")

METADATA_FILES_JSON = json.dumps(
    {
        "id": 999,
        "metadata": {
            "title": "Registro con archivos en metadata.files",
            "description": "Descripción con <b>etiquetas</b> HTML",
            "files": [
                {
                    "name": "MiniAOD.root",
                    "size_bytes": 42,
                    "url": "https://opendata.cern.ch/eos/openData/MiniAOD.root",
                }
            ],
        },
    }
).encode("utf-8")

SPARSE_JSON = json.dumps({"metadata": {"title": "Solo título"}}).encode("utf-8")

MIXED_EXPERIMENT_JSON = json.dumps(
    {
        "hits": {
            "total": 4,
            "hits": [
                {"id": 1, "metadata": {"title": "CMS dataset", "experiment": ["CMS"]}},
                {"id": 2, "metadata": {"title": "LHCb stream", "experiment": ["LHCb"]}},
                {"id": 3, "metadata": {"title": "registro sin experimento"}},
                {"id": 4, "metadata": {"title": "lista mixta", "experiment": ["LHCb", "CMS"]}},
            ],
        }
    }
).encode("utf-8")


def _fake_response(data: bytes, headers=None):
    """Response falso de urllib: soporta 'with', streaming por .read(n) y cabeceras."""
    headers = dict(headers or {})
    state = {"data": data}
    response = mock.MagicMock()
    response.__enter__.return_value = response
    response.headers = headers
    response.getheader = lambda name, default=None: headers.get(name, default)

    def read(n=-1):
        buf = state["data"]
        if not buf:
            return b""
        if isinstance(n, int) and n > 0:
            chunk, state["data"] = buf[:n], buf[n:]
            return chunk
        state["data"] = b""
        return buf

    response.read.side_effect = read
    return response


class SearchRecordsTest(unittest.TestCase):
    """Prueba search_records con un JSON del portal de ejemplo y sin red."""

    def test_parsea_hits_y_envia_parametros(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(SEARCH_JSON)) as m:
            rows = cms_tools.search_records("dimuon", max_results=2)

        self.assertEqual(len(rows), 2)
        first, second = rows
        self.assertEqual(
            sorted(first),
            sorted(["recid", "title", "year", "collision_energy", "url"]),
        )
        self.assertEqual(first["recid"], 1402954)
        self.assertEqual(first["title"], "DoubleMu primary dataset")
        self.assertEqual(first["year"], 2016)
        self.assertEqual(first["collision_energy"], "7 TeV")
        self.assertEqual(first["url"], "https://opendata.cern.ch/record/1402954")
        self.assertEqual(second["year"], 2015)
        self.assertEqual(second["collision_energy"], "8 TeV")

        request = m.call_args.args[0]
        query = urllib.parse.parse_qs(urllib.parse.urlparse(request.full_url).query)
        self.assertIn("opendata.cern.ch/api/records?", request.full_url)
        self.assertEqual(query["q"], ["(*dimuon*) AND experiment:CMS AND type.primary:Dataset"])
        self.assertEqual(query["size"], ["2"])
        self.assertNotIn("f", query)
        self.assertEqual(m.call_args.kwargs.get("timeout"), 15)
        self.assertIn("Mini-JFC", dict(request.header_items())["User-agent"])

    def test_envuelve_termino_simple_con_comodines(self):
        """Un término simple se envuelve como *término*; con '*', ':' o espacios se respeta tal cual."""
        casos = {
            "tautau": "(*tautau*)",
            "*HToTauTau*": "(*HToTauTau*)",
            "HToTauTau*": "(HToTauTau*)",
            "title:Z": "(title:Z)",
            "Z mass": "(Z mass)",
        }
        for entrada, esperado in casos.items():
            with self.subTest(entrada=entrada):
                with mock.patch(
                    "urllib.request.urlopen", return_value=_fake_response(SEARCH_JSON)
                ) as m:
                    cms_tools.search_records(entrada)

                query = urllib.parse.parse_qs(
                    urllib.parse.urlparse(m.call_args.args[0].full_url).query
                )
                self.assertEqual(
                    query["q"],
                    [f"{esperado} AND experiment:CMS AND type.primary:Dataset"],
                )

    def test_filtra_experimento_en_cliente(self):
        """Red de seguridad: se descartan los hits cuyo experiment no coincide (si el campo viene)."""
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(MIXED_EXPERIMENT_JSON)):
            rows = cms_tools.search_records("tautau")

        self.assertEqual([row["recid"] for row in rows], [1, 3, 4])

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(MIXED_EXPERIMENT_JSON)):
            rows = cms_tools.search_records("tautau", experiment="LHCb")

        # el 3 se conserva porque no trae el campo experiment
        self.assertEqual([row["recid"] for row in rows], [2, 3, 4])

    def test_filtros_y_max_results_personalizados(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(SEARCH_JSON)) as m:
            rows = cms_tools.search_records(
                "Z", experiment="ALICE", record_type="Documentation", max_results=3
            )

        query = urllib.parse.parse_qs(urllib.parse.urlparse(m.call_args.args[0].full_url).query)
        self.assertEqual(query["q"], ["(*Z*) AND experiment:ALICE AND type.primary:Documentation"])
        self.assertEqual(query["size"], ["3"])
        self.assertNotIn("f", query)
        # el primer hit declara experiment CMS: para ALICE se descarta; el segundo no trae el campo
        self.assertEqual([row["recid"] for row in rows], [1402955])

    def test_errores_claros(self):
        with mock.patch("urllib.request.urlopen") as m:
            with self.assertRaises(ValueError):
                cms_tools.search_records("   ")
            with self.assertRaises(ValueError):
                cms_tools.search_records("dimuon", max_results=0)
            self.assertEqual(m.call_count, 0)

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"")):
            with self.assertRaises(ValueError) as ctx:
                cms_tools.search_records("dimuon")
        self.assertIn("vac", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"<html>")):
            with self.assertRaises(ValueError) as ctx:
                cms_tools.search_records("dimuon")
        self.assertIn("JSON", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b'{"ok": true}')):
            with self.assertRaises(ValueError) as ctx:
                cms_tools.search_records("dimuon")
        self.assertIn("hits", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("sin red")):
            with self.assertRaises(ConnectionError) as ctx:
                cms_tools.search_records("dimuon")
        self.assertIn("fallo de red", str(ctx.exception))

        with mock.patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.HTTPError("http://x", 503, "caido", None, None),
        ):
            with self.assertRaises(ConnectionError) as ctx:
                cms_tools.search_records("dimuon")
        self.assertIn("503", str(ctx.exception))


class GetRecordTest(unittest.TestCase):
    """Prueba get_record con registros de ejemplo (archivos en _file_indices y en metadata.files)."""

    def test_archivos_en_file_indices(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(RECORD_JSON)) as m:
            record = cms_tools.get_record(1402954)

        self.assertEqual(record["recid"], "1402954")
        self.assertEqual(record["title"], "DoubleMu primary dataset")
        self.assertEqual(
            record["description"],
            "Datos de colisiones PP a 7 TeV. Véase la guía.",
        )
        self.assertEqual(record["year"], 2016)
        self.assertEqual(record["collision_energy"], "7 TeV")
        self.assertEqual(record["url"], "https://opendata.cern.ch/record/1402954")
        self.assertEqual(
            record["files"],
            [
                {
                    "name": "DoubleMu.root",
                    "size_bytes": 123456,
                    "uri": "root://eospublic.cern.ch//eos/openData/2016/DoubleMu.root",
                },
                {"name": "runinfo.csv", "size_bytes": None, "uri": None},
            ],
        )

        request = m.call_args.args[0]
        self.assertEqual(request.full_url, "https://opendata.cern.ch/api/records/1402954")
        self.assertEqual(m.call_args.kwargs.get("timeout"), 15)
        self.assertIn("Mini-JFC", dict(request.header_items())["User-agent"])

    def test_archivos_en_metadata_files(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(METADATA_FILES_JSON)):
            record = cms_tools.get_record(999)

        self.assertEqual(record["title"], "Registro con archivos en metadata.files")
        self.assertEqual(record["description"], "Descripción con etiquetas HTML")
        self.assertIsNone(record["year"])
        self.assertIsNone(record["collision_energy"])
        self.assertEqual(
            record["files"],
            [
                {
                    "name": "MiniAOD.root",
                    "size_bytes": 42,
                    "uri": "https://opendata.cern.ch/eos/openData/MiniAOD.root",
                }
            ],
        )

    def test_campos_ausentes_usan_none(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(SPARSE_JSON)):
            record = cms_tools.get_record("1")

        self.assertEqual(record["title"], "Solo título")
        self.assertIsNone(record["description"])
        self.assertIsNone(record["year"])
        self.assertIsNone(record["collision_energy"])
        self.assertEqual(record["files"], [])

    def test_errores_claros(self):
        with mock.patch("urllib.request.urlopen") as m:
            for recid in (None, "", "   "):
                with self.assertRaises(ValueError):
                    cms_tools.get_record(recid)
            self.assertEqual(m.call_count, 0)

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"")):
            with self.assertRaises(ValueError) as ctx:
                cms_tools.get_record(1402954)
        self.assertIn("vac", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"[]")):
            with self.assertRaises(ValueError) as ctx:
                cms_tools.get_record(1402954)
        self.assertIn("JSON", str(ctx.exception))

        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("sin red")):
            with self.assertRaises(ConnectionError) as ctx:
                cms_tools.get_record(1402954)
        self.assertIn("fallo de red", str(ctx.exception))

    def test_list_files_reutiliza_get_record(self):
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(RECORD_JSON)) as m:
            files = cms_tools.list_files(1402954)

        self.assertEqual(m.call_count, 1)
        self.assertEqual([f["name"] for f in files], ["DoubleMu.root", "runinfo.csv"])
        self.assertEqual(files[0]["size_bytes"], 123456)
        self.assertEqual(files[1]["size_bytes"], None)
        self.assertEqual(files[1]["uri"], None)


class UriConversionTest(unittest.TestCase):
    """Prueba la conversión de uris root:// del EOS a https://opendata.cern.ch."""

    def test_root_doble_barra(self):
        self.assertEqual(
            cms_tools._to_https("root://eospublic.cern.ch//eos/openData/x.root"),
            "https://opendata.cern.ch/eos/openData/x.root",
        )

    def test_root_barra_simple_y_otros_hosts(self):
        self.assertEqual(
            cms_tools._to_https("root://eos.cern.ch/eos/openData/x.root"),
            "https://opendata.cern.ch/eos/openData/x.root",
        )

    def test_https_y_rutas_se_conservan(self):
        self.assertEqual(
            cms_tools._to_https("https://opendata.cern.ch/eos/x.root"),
            "https://opendata.cern.ch/eos/x.root",
        )
        self.assertEqual(cms_tools._to_https(" /eos/x.root "), "/eos/x.root")


class DownloadFileTest(unittest.TestCase):
    """Prueba download_file con respuestas falsas, sin tocar la red."""

    ROOT_URI = "root://eospublic.cern.ch//eos/openData/CMS/2016/DoubleMu/DoubleMu.root"
    HTTPS_URI = "https://opendata.cern.ch/eos/openData/CMS/2016/DoubleMu/DoubleMu.root"

    def test_convierte_root_a_https_y_descarga(self):
        data = b"ROOT-FAKE-DATA"
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch(
                "urllib.request.urlopen",
                return_value=_fake_response(data, {"Content-Length": str(len(data))}),
            ) as m:
                local = cms_tools.download_file(self.ROOT_URI, tmp)

            path = Path(local)
            self.assertEqual(path.parent, Path(tmp))
            self.assertEqual(path.name, "DoubleMu.root")
            self.assertEqual(path.read_bytes(), data)

            request = m.call_args.args[0]
            self.assertEqual(request.full_url, self.HTTPS_URI)
            self.assertEqual(m.call_args.kwargs.get("timeout"), 15)
            self.assertIn("Mini-JFC", dict(request.header_items())["User-agent"])

    def test_uri_https_se_conserva(self):
        data = b"abc"
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("urllib.request.urlopen", return_value=_fake_response(data)) as m:
                local = cms_tools.download_file(self.HTTPS_URI, tmp)

            self.assertEqual(m.call_args.args[0].full_url, self.HTTPS_URI)
            self.assertEqual(Path(local).read_bytes(), data)

    def test_archivo_grande_sin_confirm_se_rechaza(self):
        with tempfile.TemporaryDirectory() as tmp:
            response = _fake_response(b"X" * 32, {"Content-Length": "900000000"})
            with mock.patch("urllib.request.urlopen", return_value=response) as m:
                with self.assertRaises(ValueError) as ctx:
                    cms_tools.download_file(self.ROOT_URI, tmp, max_bytes=500_000_000)

            message = str(ctx.exception)
            self.assertIn("900000000", message)
            self.assertIn("500000000", message)
            self.assertIn("confirm", message)
            self.assertEqual(response.read.call_count, 0)
            self.assertEqual(list(Path(tmp).iterdir()), [])
            self.assertEqual(m.call_args.kwargs.get("timeout"), 15)

    def test_archivo_grande_con_confirm_si_se_descarga(self):
        data = b"X" * 32
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch(
                "urllib.request.urlopen",
                return_value=_fake_response(data, {"Content-Length": "900000000"}),
            ):
                local = cms_tools.download_file(self.ROOT_URI, tmp, confirm=True)

            self.assertEqual(Path(local).read_bytes(), data)

    def test_max_bytes_pequeno_y_tamano_desconocido(self):
        data = b"Y" * 32
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch(
                "urllib.request.urlopen",
                return_value=_fake_response(data, {"Content-Length": str(len(data))}),
            ):
                with self.assertRaises(ValueError) as ctx:
                    cms_tools.download_file(self.ROOT_URI, tmp, max_bytes=10)
            self.assertIn("32", str(ctx.exception))
            self.assertIn("10", str(ctx.exception))
            self.assertEqual(list(Path(tmp).iterdir()), [])

            with mock.patch("urllib.request.urlopen", return_value=_fake_response(data)):
                with self.assertRaises(ValueError) as ctx:
                    cms_tools.download_file(self.ROOT_URI, tmp, max_bytes=10)
            self.assertIn("10", str(ctx.exception))
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_errores_de_red_sin_archivo_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("sin red")):
                with self.assertRaises(ConnectionError) as ctx:
                    cms_tools.download_file(self.ROOT_URI, tmp)
            self.assertIn("fallo de red", str(ctx.exception))
            self.assertEqual(list(Path(tmp).iterdir()), [])

            with mock.patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.HTTPError("http://x", 404, "no existe", None, None),
            ):
                with self.assertRaises(ConnectionError) as ctx:
                    cms_tools.download_file(self.ROOT_URI, tmp)
            self.assertIn("404", str(ctx.exception))
            self.assertEqual(list(Path(tmp).iterdir()), [])

            with mock.patch("urllib.request.urlopen", return_value=_fake_response(b"")):
                with self.assertRaises(ValueError) as ctx:
                    cms_tools.download_file(self.ROOT_URI, tmp)
            self.assertIn("vac", str(ctx.exception))
            self.assertEqual(list(Path(tmp).iterdir()), [])

            with self.assertRaises(ValueError):
                cms_tools.download_file("", tmp)


class LogRetrievalTest(unittest.TestCase):
    """El registro de descargas se reutiliza desde literature_tools (no se duplica)."""

    def test_reutiliza_log_retrieval(self):
        self.assertIs(cms_tools.log_retrieval, literature_tools.log_retrieval)

    def test_registra_en_retrieval_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "retrieval_log.md"
            cms_tools.log_retrieval(log, "dataset", "root://eospublic.cern.ch//eos/x.root", "/tmp/x.root", "explorar")
            lineas = log.read_text(encoding="utf-8").splitlines()

            self.assertEqual(len(lineas), 3)
            self.assertIn("dataset", lineas[2])
            self.assertIn("/tmp/x.root", lineas[2])


if __name__ == "__main__":
    unittest.main()
