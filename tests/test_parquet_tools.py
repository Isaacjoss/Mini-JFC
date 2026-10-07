"""Tests de src/tools/parquet_tools.py sobre un Parquet temporal."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    import pyarrow as pa
    import pyarrow.parquet as pq

    from src.tools import parquet_tools
except ImportError:  # pragma: no cover
    pa = None
    pq = None
    parquet_tools = None


@unittest.skipUnless(pa is not None, "pyarrow no está instalado")
class ParquetToolsTest(unittest.TestCase):
    """Genera un Parquet temporal y prueba las 4 funciones."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "muestra.parquet"
        cls.table = pa.table(
            {
                "pt": [10.0, 20.0, None, 40.0, 50.0, 60.0],
                "eta": [1.0, -1.5, 0.5, 2.0, -2.5, 3.0],
                "n": [1, 2, 3, 4, 5, 6],
                "label": ["a", "b", "c", "d", "e", "f"],
            }
        )
        pq.write_table(cls.table, cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_list_columns(self):
        self.assertEqual(
            parquet_tools.list_columns(self.path), ["pt", "eta", "n", "label"]
        )

    def test_describe_file(self):
        info = parquet_tools.describe_file(self.path)
        self.assertEqual(info["rows"], 6)
        self.assertEqual(info["columns"], 4)
        self.assertEqual(info["column_names"], ["pt", "eta", "n", "label"])
        self.assertEqual(
            info["types"],
            {"pt": "double", "eta": "double", "n": "int64", "label": "string"},
        )

    def test_read_sample(self):
        rows = parquet_tools.read_sample(self.path, n=3)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], {"pt": 10.0, "eta": 1.0, "n": 1, "label": "a"})
        self.assertEqual(len(parquet_tools.read_sample(self.path)), 5)

    def test_column_summary_numerica(self):
        s = parquet_tools.column_summary(self.path, "pt")
        self.assertTrue(s["numeric"])
        self.assertEqual(s["rows"], 6)
        self.assertEqual(s["nulls"], 1)
        self.assertEqual(s["min"], 10.0)
        self.assertEqual(s["max"], 60.0)
        self.assertAlmostEqual(s["mean"], 36.0)

    def test_column_summary_no_numerica(self):
        s = parquet_tools.column_summary(self.path, "label")
        self.assertFalse(s["numeric"])
        self.assertIsNone(s["min"])
        self.assertEqual(s["nulls"], 0)

    def test_column_inexistente(self):
        with self.assertRaises(KeyError):
            parquet_tools.column_summary(self.path, "no_existe")

    def test_archivo_no_existe(self):
        faltante = Path(self.tmp.name) / "no_existe.parquet"
        for func in (
            parquet_tools.list_columns,
            parquet_tools.describe_file,
            parquet_tools.read_sample,
        ):
            with self.assertRaises(FileNotFoundError):
                func(faltante)
        with self.assertRaises(FileNotFoundError):
            parquet_tools.column_summary(faltante, "pt")


if __name__ == "__main__":
    unittest.main()
