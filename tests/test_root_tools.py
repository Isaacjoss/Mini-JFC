"""Tests de src/tools/root_tools.py sobre un ROOT temporal."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    import awkward as ak
    import numpy as np
    import uproot

    from src.tools import root_tools
except ImportError:  # pragma: no cover
    ak = None
    np = None
    uproot = None
    root_tools = None


@unittest.skipUnless(uproot is not None, "uproot no está instalado")
class RootToolsTest(unittest.TestCase):
    """Genera un ROOT temporal y prueba las 4 funciones."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "muestra.root"
        cls.pt = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
        cls.eta = [1.0, -1.5, 0.5, 2.0, -2.5, 3.0]
        cls.n = [1, 2, 3, 4, 5, 6]
        with uproot.recreate(cls.path) as f:
            f.mktree("events", {"pt": np.float64, "eta": np.float64, "n": np.int32})
            f["events"].extend(
                {
                    "pt": np.array(cls.pt, dtype=np.float64),
                    "eta": np.array(cls.eta, dtype=np.float64),
                    "n": np.array(cls.n, dtype=np.int32),
                }
            )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_list_trees(self):
        self.assertEqual(root_tools.list_trees(self.path), ["events"])

    def test_list_branches(self):
        tipos = root_tools.list_branches(self.path, "events")
        self.assertEqual(set(tipos), {"pt", "eta", "n"})
        self.assertTrue(all(isinstance(v, str) and v for v in tipos.values()))

    def test_read_sample(self):
        sample = root_tools.read_sample(self.path, "events", ["pt", "n"], n=3)
        self.assertEqual(sample, {"pt": [10.0, 20.0, 30.0], "n": [1, 2, 3]})
        completo = root_tools.read_sample(self.path, "events", ["eta"])
        self.assertEqual(len(completo["eta"]), 6)
        self.assertEqual(completo["eta"][0], 1.0)

    def test_branch_summary(self):
        s = root_tools.branch_summary(self.path, "events", "pt")
        self.assertEqual(s["events"], 6)
        self.assertEqual(s["min"], 10.0)
        self.assertEqual(s["max"], 60.0)
        self.assertAlmostEqual(s["mean"], 35.0)

    def test_branch_summary_con_n(self):
        s = root_tools.branch_summary(self.path, "events", "n", n=3)
        self.assertEqual(s["events"], 3)
        self.assertEqual(s["min"], 1)
        self.assertEqual(s["max"], 3)
        self.assertAlmostEqual(s["mean"], 2.0)

    def test_arbol_inexistente(self):
        for func, extra in (
            (root_tools.list_branches, ()),
            (root_tools.read_sample, (["pt"],)),
            (root_tools.branch_summary, ("pt",)),
        ):
            with self.assertRaises(KeyError):
                func(self.path, "no_existe", *extra)

    def test_rama_inexistente(self):
        with self.assertRaises(KeyError):
            root_tools.read_sample(self.path, "events", ["no_existe"])
        with self.assertRaises(KeyError):
            root_tools.branch_summary(self.path, "events", "no_existe")

    def test_archivo_no_existe(self):
        faltante = Path(self.tmp.name) / "no_existe.root"
        with self.assertRaises(FileNotFoundError):
            root_tools.list_trees(faltante)
        with self.assertRaises(FileNotFoundError):
            root_tools.list_branches(faltante, "events")
        with self.assertRaises(FileNotFoundError):
            root_tools.read_sample(faltante, "events", ["pt"])
        with self.assertRaises(FileNotFoundError):
            root_tools.branch_summary(faltante, "events", "pt")


if __name__ == "__main__":
    unittest.main()
