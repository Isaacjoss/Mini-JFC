"""Tests de scripts/mjfc.py (CLI JSON), sin internet: tools parcheadas con unittest.mock.

Comprueba: salida JSON en stdout, recorte con --max-items, exit code 1 en error
y una ejecución real sin red (`parquet columns` sobre un Parquet temporal).
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import mjfc  # noqa: E402  (scripts/mjfc.py, ejecutable desde cualquier carpeta)

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:  # pragma: no cover
    pa = None
    pq = None


def run_cli(argv, stdin_text=""):
    """Llama a mjfc.main(argv) y devuelve (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        with mock.patch.object(sys, "stdin", io.StringIO(stdin_text)):
            code = mjfc.main(argv)
    return code, out.getvalue(), err.getvalue()


class CliJsonTest(unittest.TestCase):
    """Salida JSON, recorte de listas y manejo de errores."""

    def test_lit_arxiv_devuelve_json_utf8(self):
        resultados = [{"id": "1", "title": "Física de partículas ñ", "authors": ["áé"]}]
        with mock.patch.object(
            mjfc.literature_tools, "search_arxiv", return_value=resultados
        ) as fake:
            code, out, err = run_cli(["lit", "arxiv", "higgs", "-n", "3"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(fake.call_args.args, ("higgs",))
        self.assertEqual(fake.call_args.kwargs, {"max_results": 3})
        self.assertIn("ñ", out)  # ensure_ascii=False: sin escapes \\u00f1
        self.assertEqual(json.loads(out), resultados)

    def test_lit_arxiv_pasa_la_opcion_cat(self):
        with mock.patch.object(
            mjfc.literature_tools, "search_arxiv", return_value=[]
        ) as fake:
            code, out, err = run_cli(["lit", "arxiv", "Higgs tau", "-n", "2", "--cat", "hep-ex"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(fake.call_args.args, ("Higgs tau",))
        self.assertEqual(fake.call_args.kwargs, {"max_results": 2, "cat": "hep-ex"})

    def test_max_items_recorta_lista_larga(self):
        items = [{"id": str(i)} for i in range(45)]
        with mock.patch.object(mjfc.literature_tools, "search_inspire", return_value=items):
            code, out, err = run_cli(["--max-items", "10", "lit", "inspire", "q"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["truncated"], True)
        self.assertEqual(payload["total"], 45)
        self.assertEqual(len(payload["items"]), 10)
        self.assertEqual(payload["items"][0], {"id": "0"})

    def test_max_items_defecto_20(self):
        items = [i for i in range(25)]
        with mock.patch.object(mjfc.cms_tools, "list_files", return_value=items):
            code, out, _ = run_cli(["cms", "files", "1"])
        payload = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual(payload["truncated"], True)
        self.assertEqual(payload["total"], 25)
        self.assertEqual(len(payload["items"]), 20)

    def test_max_items_en_el_subcomando_y_recorte_de_dict(self):
        registro = {"recid": 1, "title": "x", "files": [{"name": f"f{i}"} for i in range(30)]}
        with mock.patch.object(mjfc.cms_tools, "get_record", return_value=registro):
            code, out, _ = run_cli(["cms", "record", "1", "--max-items", "7"])
        payload = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual(payload["recid"], 1)
        self.assertEqual(len(payload["files"]), 7)
        self.assertEqual(payload["truncated"], True)
        self.assertEqual(payload["total"], 30)

    def test_lista_corta_no_se_recorta(self):
        with mock.patch.object(
            mjfc.literature_tools, "search_arxiv", return_value=[{"id": "1"}, {"id": "2"}]
        ):
            code, out, _ = run_cli(["lit", "arxiv", "q"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), [{"id": "1"}, {"id": "2"}])

    def test_error_exit_code_1_en_stderr(self):
        with mock.patch.object(
            mjfc.literature_tools,
            "search_arxiv",
            side_effect=ValueError("query no puede estar vacía"),
        ):
            code, out, err = run_cli(["lit", "arxiv", "  "])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("error", err)
        self.assertIn("query no puede estar vacía", err)
        self.assertIn("lit arxiv", err)

    def test_error_de_uso_exit_code_1(self):
        code, out, err = run_cli(["lit"])  # falta el subcomando
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("error", err)

    @unittest.skipUnless(pa is not None, "pyarrow no está instalado")
    def test_error_archivo_parquet_inexistente_sin_red(self):
        code, out, err = run_cli(["parquet", "columns", "no_existe.parquet"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("no_existe.parquet", err)

    def test_web_save_lee_stdin(self):
        with mock.patch.object(
            mjfc.web_tools, "save_text", return_value="/tmp/salida.txt"
        ) as fake:
            code, out, _ = run_cli(["web", "save", "/tmp/salida.txt"], stdin_text="hola")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), "/tmp/salida.txt")
        fake.assert_called_once_with("hola", "/tmp/salida.txt")

    def test_cms_download_pasa_confirm_y_max_bytes(self):
        with mock.patch.object(
            mjfc.cms_tools, "download_file", return_value="/tmp/d/f.root"
        ) as fake:
            code, out, _ = run_cli(
                ["cms", "download", "root://eos/x", "/tmp/d", "--confirm", "--max-bytes", "123"]
            )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), "/tmp/d/f.root")
        fake.assert_called_once_with(
            "root://eos/x", "/tmp/d", max_bytes=123, confirm=True
        )

    def test_root_sample_separa_branches_por_coma(self):
        sample = {"pt": [1.0, 2.0], "eta": [0.1, 0.2]}
        fake_tools = mock.Mock()
        fake_tools.read_sample.return_value = sample
        with mock.patch.object(mjfc, "root_tools", fake_tools):
            code, out, _ = run_cli(["root", "sample", "f.root", "tree", "pt,eta", "-n", "50"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), sample)
        fake_tools.read_sample.assert_called_once_with(
            "f.root", "tree", ["pt", "eta"], n=50
        )

    def test_help_de_subcomando_describe_una_linea(self):
        code, out, err = run_cli(["lit", "arxiv", "--help"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("arXiv", out)
        self.assertIn("--max-items", out)

    def test_help_de_lit_arxiv_documenta_cat_con_ejemplo(self):
        code, out, err = run_cli(["lit", "arxiv", "--help"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("--cat", out)
        self.assertIn("hep-ex", out)  # el ejemplo --cat hep-ex
        # el ejemplo también aparece en los ejemplos de la ayuda general
        code, out, _ = run_cli(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("--cat", out)
        self.assertIn("hep-ex", out)

    def test_json_en_una_sola_linea(self):
        with mock.patch.object(mjfc.web_tools, "fetch_url", return_value="texto plano"):
            code, out, _ = run_cli(["web", "fetch", "https://example.com"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 1)
        self.assertEqual(json.loads(out), "texto plano")


@unittest.skipUnless(pa is not None, "pyarrow no está instalado")
class CliParquetRealTest(unittest.TestCase):
    """Ejecución real del CLI sobre un Parquet temporal, sin red."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "muestra.parquet"
        pq.write_table(
            pa.table({"pt": [10.0, 20.0, None], "eta": [1.0, -1.5, 0.5], "n": [1, 2, 3]}),
            cls.path,
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_parquet_columns(self):
        code, out, err = run_cli(["parquet", "columns", str(self.path)])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(json.loads(out), ["pt", "eta", "n"])

    def test_parquet_describe_y_summary(self):
        code, out, _ = run_cli(["parquet", "describe", str(self.path)])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["rows"], 3)
        self.assertEqual(payload["column_names"], ["pt", "eta", "n"])

        code, out, _ = run_cli(["parquet", "summary", str(self.path), "pt"])
        self.assertEqual(code, 0)
        summary = json.loads(out)
        self.assertTrue(summary["numeric"])
        self.assertEqual(summary["nulls"], 1)
        self.assertEqual(summary["min"], 10.0)
        self.assertEqual(summary["max"], 20.0)


if __name__ == "__main__":
    unittest.main()
