"""Tests de analysis select: expresiones, cutflow ROOT/Parquet y CLI."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

try:
    import numpy as np

    from src.tools import analysis_tools
except ImportError:  # pragma: no cover
    np = None
    analysis_tools = None

try:
    import awkward as ak
except ImportError:  # pragma: no cover
    ak = None

try:
    import uproot
except ImportError:  # pragma: no cover
    uproot = None

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:  # pragma: no cover
    pa = None
    pq = None

import mjfc  # noqa: E402


DATA = {
    "pt": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
    "eta": [1.0, -1.5, 0.5, 2.0, -2.5, 3.0],
    "n": [1, 2, 3, 4, 5, 6],
    "flag": [1, 0, 1, 1, 0, 1],
}
CUTS = [
    {"name": "pt20", "expression": "pt > 20", "source": "strategy.md#seleccion"},
    {"name": "eta25", "expression": "abs(eta) < 2.5", "source": "paper#tabla1"},
    {"name": "even", "expression": "n % 2 == 0", "source": "paper#seccion3"},
]


def _write_parquet(path, data=None):
    data = DATA if data is None else data
    pq.write_table(pa.table(data), path)


def _write_root(path, data=None):
    data = DATA if data is None else data
    types = {
        key: np.float64 if isinstance(values[0], float) else np.int32
        for key, values in data.items()
    }
    with uproot.recreate(path) as handle:
        handle.mktree("events", types)
        handle["events"].extend(
            {key: np.array(values, dtype=types[key]) for key, values in data.items()}
        )


def _write_cuts(path, cuts=None):
    cuts = CUTS if cuts is None else cuts
    path.write_text(json.dumps(cuts), encoding="utf-8")


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = mjfc.main(argv)
    return code, out.getvalue(), err.getvalue()


@unittest.skipUnless(np is not None, "numpy no está instalado")
class ExpressionTest(unittest.TestCase):
    """Expresiones restringidas: casos válidos y rechazos de seguridad."""

    def setUp(self):
        self.arrays = {key: np.array(values) for key, values in DATA.items()}
        self.n_events = len(DATA["pt"])

    def mask(self, expression):
        return analysis_tools.evaluate_expression(
            expression, self.arrays, self.n_events
        )

    def test_comparacion_simple(self):
        self.assertEqual(
            self.mask("pt > 20").tolist(),
            [False, False, True, True, True, True],
        )

    def test_and_logico(self):
        self.assertEqual(self.mask("pt > 20 and abs(eta) < 2.5").sum(), 2)

    def test_comparacion_encadenada(self):
        self.assertEqual(self.mask("0 < pt < 50").sum(), 4)

    def test_funcion_sqrt(self):
        self.assertEqual(self.mask("sqrt(pt) > 5").sum(), 4)

    def test_funcion_where(self):
        self.assertEqual(self.mask("where(flag, pt, 0) > 20").sum(), 3)

    def test_not_logico(self):
        self.assertEqual(self.mask("not flag").sum(), 2)

    def test_and_booleano(self):
        self.assertEqual(self.mask("(flag != 0) & (pt > 20)").sum(), 3)

    def test_or_booleano(self):
        self.assertEqual(self.mask("(flag != 0) | (pt > 20)").sum(), 5)

    def test_invert_booleano(self):
        self.assertEqual(self.mask("~(flag != 0)").sum(), 2)

    def test_and_entero_bit_a_bit(self):
        # n = [1..6]: n & 1 solo es 1 para 1, 3 y 5.
        self.assertEqual(self.mask("(n & 1) == 1").sum(), 3)
        # n & 2 es 2 para 2, 3 y 6 (con lógica sería verdadero para todo n != 0).
        self.assertEqual(self.mask("(n & 2) == 2").sum(), 3)

    def test_or_entero_bit_a_bit(self):
        # n | 1 es 3 solo para n = 2 (2|1) y n = 3 (3|1).
        self.assertEqual(self.mask("(n | 1) == 3").sum(), 2)

    def test_xor_entero_bit_a_bit(self):
        # n ^ 1 es 2 solo para n = 3.
        self.assertEqual(self.mask("(n ^ 1) == 2").sum(), 1)

    def test_xor_booleano(self):
        self.assertEqual(self.mask("(flag != 0) ^ (pt > 20)").sum(), 2)

    def test_invert_entero_bit_a_bit(self):
        # ~n = -n-1; para n = 1 da -2. Con lógica, ~n sería un booleano.
        self.assertEqual(self.mask("(~n) == -2").sum(), 1)
        self.assertEqual(self.mask("(~n) < 0").sum(), 6)

    def test_and_entero_devuelve_entero(self):
        with self.assertRaisesRegex(ValueError, "booleano"):
            self.mask("n & 1")

    def test_and_entero_booleano_bit_a_bit(self):
        # numpy: int & bool es bit a bit (bool se promociona a 0/1) y devuelve entero.
        # n & (pt > 20) da [0, 0, 1, 0, 1, 0]; solo n=3 y n=5 valen 1.
        self.assertEqual(self.mask("(n & (pt > 20)) == 1").sum(), 2)

    def test_modulo(self):
        self.assertEqual(self.mask("n % 2 == 0").sum(), 3)

    def test_constante_booleana(self):
        self.assertEqual(self.mask("True").sum(), 6)

    def test_constante_pi(self):
        self.assertEqual(self.mask("pi > 3").sum(), 6)

    def test_rechaza_atributo(self):
        with self.assertRaisesRegex(ValueError, "Attribute"):
            self.mask("pt.__class__")

    def test_rechaza_subindice(self):
        with self.assertRaisesRegex(ValueError, "Subscript"):
            self.mask("pt[0]")

    def test_rechaza_lambda(self):
        with self.assertRaisesRegex(ValueError, "Lambda"):
            self.mask("(lambda x: x)(pt)")

    def test_rechaza_import(self):
        with self.assertRaisesRegex(ValueError, "función no permitida"):
            self.mask("__import__('os')")

    def test_rechaza_string(self):
        with self.assertRaisesRegex(ValueError, "constante no permitida"):
            self.mask("pt > 'a'")

    def test_rechaza_rama_inexistente(self):
        with self.assertRaises(KeyError):
            self.mask("no_existe > 0")

    def test_rechaza_funcion_inexistente(self):
        with self.assertRaisesRegex(ValueError, "función no permitida"):
            self.mask("foo(pt) > 0")

    def test_rechaza_resultado_no_booleano(self):
        with self.assertRaisesRegex(ValueError, "booleano"):
            self.mask("pt + 1")


@unittest.skipUnless(pa is not None and pq is not None, "pyarrow no está instalado")
class ParquetCutflowTest(unittest.TestCase):
    """Cutflow real sobre un Parquet temporal de 6 eventos."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.parquet = cls.dir / "events.parquet"
        _write_parquet(cls.parquet)
        cls.cuts = cls.dir / "cuts.json"
        _write_cuts(cls.cuts)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_cutflow(self):
        result = analysis_tools.select([str(self.parquet)], str(self.cuts))
        self.assertEqual(result["format"], "parquet")
        self.assertIsNone(result["tree"])
        self.assertEqual(result["total_events"], 6)
        self.assertEqual([cut["passed"] for cut in result["cuts"]], [4, 2, 1])
        self.assertEqual(result["final_events"], 1)
        self.assertEqual(result["branches_used"], ["eta", "n", "pt"])
        self.assertAlmostEqual(result["cuts"][0]["relative_efficiency"], 4 / 6)
        self.assertAlmostEqual(result["cuts"][0]["cumulative_efficiency"], 4 / 6)
        self.assertAlmostEqual(result["cuts"][1]["relative_efficiency"], 2 / 4)
        self.assertAlmostEqual(result["cuts"][1]["cumulative_efficiency"], 2 / 6)
        self.assertAlmostEqual(result["cuts"][2]["relative_efficiency"], 1 / 2)
        self.assertAlmostEqual(result["cuts"][2]["cumulative_efficiency"], 1 / 6)

    def test_out_escribe_json(self):
        out = self.dir / "sub" / "cutflow.json"
        result = analysis_tools.select(
            [str(self.parquet)], str(self.cuts), out=str(out)
        )
        self.assertTrue(out.is_file())
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), result)

    def test_multiples_inputs(self):
        second = self.dir / "second.parquet"
        _write_parquet(
            second,
            {"pt": [20.0, 30.0], "eta": [0.0, 0.0], "n": [1, 2], "flag": [1, 1]},
        )
        result = analysis_tools.select(
            [str(self.parquet), str(second)],
            str(self.cuts),
        )
        self.assertEqual(result["total_events"], 8)
        self.assertEqual([cut["passed"] for cut in result["cuts"]], [5, 3, 2])
        self.assertEqual(result["final_events"], 2)

    def test_sin_cortes(self):
        cuts = self.dir / "empty.json"
        _write_cuts(cuts, [])
        result = analysis_tools.select([str(self.parquet)], str(cuts))
        self.assertEqual(result["cuts"], [])
        self.assertEqual(result["final_events"], 6)
        self.assertIn("sin cortes", result["warnings"][0])

    def test_label(self):
        result = analysis_tools.select(
            [str(self.parquet)], str(self.cuts), label="mi-muestra"
        )
        self.assertEqual(result["label"], "mi-muestra")
        default = analysis_tools.select([str(self.parquet)], str(self.cuts))
        self.assertEqual(default["label"], "events")

    def test_source_obligatoria(self):
        cuts = self.dir / "no_source.json"
        _write_cuts(cuts, [{"name": "x", "expression": "pt > 0"}])
        with self.assertRaisesRegex(ValueError, "source"):
            analysis_tools.select([str(self.parquet)], str(cuts))

    def test_source_todo_rechazada(self):
        cuts = self.dir / "todo.json"
        _write_cuts(
            cuts, [{"name": "x", "expression": "pt > 0", "source": "TODO"}]
        )
        with self.assertRaisesRegex(ValueError, "fuente real"):
            analysis_tools.select([str(self.parquet)], str(cuts))

    def test_nombres_duplicados(self):
        cuts = self.dir / "duplicados.json"
        _write_cuts(
            cuts,
            [
                {"name": "x", "expression": "pt > 0", "source": "s1"},
                {"name": "x", "expression": "pt > 20", "source": "s2"},
            ],
        )
        with self.assertRaisesRegex(ValueError, "duplicado"):
            analysis_tools.select([str(self.parquet)], str(cuts))

    def test_rama_inexistente(self):
        cuts = self.dir / "missing.json"
        _write_cuts(
            cuts, [{"name": "x", "expression": "no_existe > 0", "source": "s"}]
        )
        with self.assertRaises(KeyError):
            analysis_tools.select([str(self.parquet)], str(cuts))

    def test_tree_en_parquet(self):
        with self.assertRaisesRegex(ValueError, "solo aplica"):
            analysis_tools.select(
                [str(self.parquet)], str(self.cuts), tree="events"
            )

    def test_nulos_rechazados(self):
        path = self.dir / "nulls.parquet"
        _write_parquet(
            path,
            {"pt": [10.0, None, 30.0], "eta": [0.0, 0.0, 0.0]},
        )
        cuts = self.dir / "pt.json"
        _write_cuts(cuts, [{"name": "x", "expression": "pt > 20", "source": "s"}])
        with self.assertRaisesRegex(ValueError, "nulos"):
            analysis_tools.select([str(path)], str(cuts))

    def test_json_invalido(self):
        cuts = self.dir / "bad.json"
        cuts.write_text("{", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "JSON"):
            analysis_tools.select([str(self.parquet)], str(cuts))

    def test_formato_dict_con_cuts(self):
        cuts = self.dir / "dict.json"
        cuts.write_text(json.dumps({"cuts": CUTS}), encoding="utf-8")
        result = analysis_tools.select([str(self.parquet)], str(cuts))
        self.assertEqual(result["final_events"], 1)


@unittest.skipUnless(
    uproot is not None and np is not None, "uproot no está instalado"
)
class RootCutflowTest(unittest.TestCase):
    """Cutflow real sobre un ROOT temporal de 6 eventos."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.root = cls.dir / "events.root"
        _write_root(cls.root)
        cls.cuts = cls.dir / "cuts.json"
        _write_cuts(cls.cuts)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_cutflow(self):
        result = analysis_tools.select(
            [str(self.root)], str(self.cuts), tree="events"
        )
        self.assertEqual(result["format"], "root")
        self.assertEqual(result["tree"], "events")
        self.assertEqual(result["total_events"], 6)
        self.assertEqual([cut["passed"] for cut in result["cuts"]], [4, 2, 1])
        self.assertEqual(result["final_events"], 1)

    def test_tree_obligatorio(self):
        with self.assertRaisesRegex(ValueError, "tree"):
            analysis_tools.select([str(self.root)], str(self.cuts))

    def test_arbol_inexistente(self):
        with self.assertRaises(KeyError):
            analysis_tools.select(
                [str(self.root)], str(self.cuts), tree="no_existe"
            )

    def test_rama_inexistente(self):
        cuts = self.dir / "missing.json"
        _write_cuts(
            cuts, [{"name": "x", "expression": "no_existe > 0", "source": "s"}]
        )
        with self.assertRaises(KeyError):
            analysis_tools.select(
                [str(self.root)], str(cuts), tree="events"
            )

    @unittest.skipUnless(ak is not None, "awkward no está instalado")
    def test_rama_vectorial_rechazada(self):
        with self.assertRaisesRegex(TypeError, "vectorial"):
            analysis_tools._awkward_to_numpy(ak.Array([[1.0, 2.0], [3.0]]), "jet_pt")


@unittest.skipUnless(
    np is not None and pa is not None and pq is not None,
    "pyarrow/numpy no están instalados",
)
class CliAnalysisSelectTest(unittest.TestCase):
    """CLI analysis select: JSON, --out, errores y protección de la lista de cortes."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.parquet = cls.dir / "events.parquet"
        _write_parquet(cls.parquet)
        cls.cuts = cls.dir / "cuts.json"
        _write_cuts(cls.cuts)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_select_cli(self):
        out = self.dir / "cutflow.json"
        code, stdout, stderr = run_cli(
            [
                "analysis",
                "select",
                str(self.parquet),
                "--cuts",
                str(self.cuts),
                "--out",
                str(out),
            ]
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["final_events"], 1)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), payload)

    def test_max_items_no_trunca_cuts(self):
        code, stdout, _ = run_cli(
            [
                "--max-items",
                "1",
                "analysis",
                "select",
                str(self.parquet),
                "--cuts",
                str(self.cuts),
            ]
        )
        self.assertEqual(code, 0)
        payload = json.loads(stdout)
        self.assertEqual(len(payload["cuts"]), 3)

    def test_error_source(self):
        cuts = self.dir / "no_source.json"
        _write_cuts(cuts, [{"name": "x", "expression": "pt > 0"}])
        code, stdout, stderr = run_cli(
            ["analysis", "select", str(self.parquet), "--cuts", str(cuts)]
        )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("source", stderr)

    def test_error_cuts_inexistente(self):
        code, stdout, stderr = run_cli(
            [
                "analysis",
                "select",
                str(self.parquet),
                "--cuts",
                str(self.dir / "no_existe.json"),
            ]
        )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("cortes", stderr)

    def test_help(self):
        code, stdout, stderr = run_cli(["analysis", "select", "--help"])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("cutflow", stdout)
        self.assertIn("--tree", stdout)


JAGGED = {
    "muon_pt": [[10.0, 40.0], [], [30.0]],
    "muon_flag": [[True, False], [], [True]],
    "met": [50.0, 50.0, 10.0],
}


def _write_root_jagged(path):
    """ROOT temporal con una rama jagged y dos escalares."""
    with uproot.recreate(path) as handle:
        handle.mktree(
            "events",
            {"muon_pt": "var * float64", "muon_flag": "var * bool", "met": "float64"},
        )
        handle["events"].extend(
            {
                "muon_pt": ak.Array(JAGGED["muon_pt"]),
                "muon_flag": ak.Array(JAGGED["muon_flag"]),
                "met": np.array(JAGGED["met"], dtype=np.float64),
            }
        )


@unittest.skipUnless(
    np is not None and ak is not None, "numpy/awkward no están instalados"
)
class JaggedReductionTest(unittest.TestCase):
    """any/all/count/max sobre listas por evento: semántica y avisos."""

    def setUp(self):
        self.arrays = {
            "muon_pt": ak.Array(JAGGED["muon_pt"]),
            "muon_flag": ak.Array(JAGGED["muon_flag"]),
            "met": np.array(JAGGED["met"]),
        }
        self.n_events = len(JAGGED["met"])

    def value(self, expression, diagnostics=None):
        return analysis_tools.evaluate(
            expression, self.arrays, self.n_events, diagnostics
        )

    def mask(self, expression, diagnostics=None):
        return analysis_tools.evaluate_expression(
            expression, self.arrays, self.n_events, diagnostics
        )

    def test_any(self):
        result = self.mask("any(muon_pt > 20)")
        self.assertEqual(result.tolist(), [True, False, True])
        self.assertEqual(result.dtype, np.bool_)

    def test_all(self):
        result = self.mask("all(muon_pt > 20)")
        self.assertEqual(result.tolist(), [False, True, True])

    def test_count(self):
        result = self.value("count(muon_pt > 20)")
        self.assertEqual(result.tolist(), [1, 0, 1])
        self.assertTrue(np.issubdtype(result.dtype, np.integer))

    def test_max_con_vacio_es_nan(self):
        result = self.value("max(muon_pt)")
        self.assertTrue(np.isnan(result[1]))
        np.testing.assert_allclose(result[[0, 2]], [40.0, 30.0])

    def test_max_nan_no_falla_en_comparacion(self):
        self.assertEqual(self.mask("max(muon_pt) > 35").tolist(), [True, False, False])

    def test_any_lista_vacia_es_false(self):
        self.assertEqual(self.mask("any(muon_flag)").tolist(), [True, False, True])
        self.assertEqual(self.mask("any(muon_pt > 1000)").tolist(), [False, False, False])

    def test_all_lista_vacia_es_true(self):
        self.assertEqual(self.mask("all(muon_pt > 1000)").tolist(), [False, True, False])

    def test_count_lista_vacia_es_cero(self):
        self.assertEqual(self.value("count(muon_flag)").tolist(), [1, 0, 1])

    def test_avisa_de_listas_vacias(self):
        diagnostics = analysis_tools.Diagnostics()
        self.mask("any(muon_pt > 20)", diagnostics)
        self.mask("all(muon_pt > 20)", diagnostics)
        self.value("count(muon_pt > 20)", diagnostics)
        self.value("max(muon_pt)", diagnostics)
        self.assertEqual(
            diagnostics.empty_counts(),
            {
                "any(muon_pt > 20)": 1,
                "all(muon_pt > 20)": 1,
                "count(muon_pt > 20)": 1,
                "max(muon_pt)": 1,
            },
        )
        self.assertEqual(len(diagnostics.warnings()), 4)
        self.assertIn("1 de 3 eventos con lista vacía", diagnostics.warnings()[0])

    def test_sin_listas_vacias_no_avisa(self):
        diagnostics = analysis_tools.Diagnostics()
        arrays = {"flag": ak.Array([[True], [False], [True]])}
        analysis_tools.evaluate("count(flag)", arrays, 3, diagnostics)
        self.assertEqual(diagnostics.warnings(), [])

    def test_anidado_mas_de_un_nivel_rechazado(self):
        arrays = {"x": ak.Array([[[1.0, 2.0], [3.0]], [], [[4.0]]])}
        with self.assertRaisesRegex(ValueError, "un nivel"):
            analysis_tools.evaluate("max(x)", arrays, 3)

    def test_count_exige_mascara_booleana(self):
        with self.assertRaisesRegex(ValueError, "máscara booleana"):
            self.value("count(muon_pt)")

    def test_reduccion_exige_lista_por_evento(self):
        with self.assertRaisesRegex(ValueError, "lista por evento"):
            self.value("count(met > 20)")
        with self.assertRaisesRegex(ValueError, "lista por evento"):
            self.value("any(met > 20)")

    def test_arity_de_reducciones(self):
        for expression in ("any()", "all(muon_pt, 2)", "count(muon_pt, 2)"):
            with self.assertRaisesRegex(ValueError, "exactamente un argumento"):
                self.value(expression)

    def test_resultado_jagged_sin_reducir_rechazado(self):
        with self.assertRaisesRegex(ValueError, "redúcela"):
            self.mask("muon_pt > 20")

    def test_reducciones_no_son_ramas(self):
        self.assertEqual(
            analysis_tools._collect_names(
                analysis_tools._parse_expression("count(muon_pt > 20) > 0")
            ),
            {"muon_pt"},
        )


LEADING = {
    "value": [[10.0, 20.0, 5.0], [], [30.0, 30.0], [7.0]],
    "order": [[2.0, 2.0, 1.0], [], [1.0, 1.0], [3.0]],
    "mask": [[True, True, True], [], [True, False], [False]],
}


@unittest.skipUnless(
    np is not None and ak is not None, "numpy/awkward no están instalados"
)
class LeadingTest(unittest.TestCase):
    """leading(values, order, mask): objeto líder por evento y sus avisos."""

    def setUp(self):
        self.arrays = {key: ak.Array(values) for key, values in LEADING.items()}
        self.n_events = len(LEADING["value"])

    def value(self, expression="leading(value, order, mask)", diagnostics=None):
        return analysis_tools.evaluate(
            expression, self.arrays, self.n_events, diagnostics
        )

    def test_elige_mayor_order(self):
        self.assertEqual(self.value().tolist()[0], 10.0)
        self.assertEqual(self.value().tolist()[2], 30.0)

    def test_empate_primera_posicion(self):
        # Evento 0: order [2, 2, 1] y values [10, 20, 5]; el líder es el primero.
        self.assertEqual(self.value()[0], 10.0)

    def test_sin_objeto_es_nan(self):
        result = self.value()
        self.assertTrue(np.isnan(result[1]))
        self.assertTrue(np.isnan(result[3]))
        self.assertEqual(result.dtype, np.float64)

    def test_sin_objeto_avisa(self):
        diagnostics = analysis_tools.Diagnostics()
        self.value(diagnostics=diagnostics)
        self.assertEqual(
            diagnostics.without_object_counts(),
            {"leading(value, order, mask)": 2},
        )
        self.assertEqual(
            diagnostics.warnings(),
            [
                "leading(value, order, mask): 2 de 4 eventos sin objeto que pase la "
                "máscara"
            ],
        )
        self.assertEqual(diagnostics.empty_counts(), {})

    def test_mascara_filtra_candidatos(self):
        arrays = {
            "v": ak.Array([[1.0, 2.0], [3.0]]),
            "o": ak.Array([[5.0, 4.0], [1.0]]),
            "m": ak.Array([[False, True], [False]]),
        }
        result = analysis_tools.evaluate(
            "leading(v, o, m)", arrays, 2
        )
        np.testing.assert_allclose(result, [2.0, np.nan], equal_nan=True)

    def test_order_no_finito_no_es_candidato(self):
        arrays = {
            "v": ak.Array([[1.0, 2.0]]),
            "o": ak.Array([[float("nan"), 3.0]]),
            "m": ak.Array([[True, True]]),
        }
        np.testing.assert_allclose(
            analysis_tools.evaluate("leading(v, o, m)", arrays, 1), [2.0]
        )
        only_nan = dict(arrays, o=ak.Array([[float("nan"), float("inf")]]))
        diagnostics = analysis_tools.Diagnostics()
        np.testing.assert_allclose(
            analysis_tools.evaluate("leading(v, o, m)", only_nan, 1, diagnostics),
            [np.nan],
            equal_nan=True,
        )
        self.assertEqual(
            diagnostics.without_object_counts(), {"leading(v, o, m)": 1}
        )

    def test_aridad_tres(self):
        for expression in (
            "leading(value)",
            "leading(value, order)",
            "leading(value, order, mask, 1)",
        ):
            with self.assertRaisesRegex(ValueError, "tres argumentos"):
                analysis_tools.evaluate(expression, self.arrays, self.n_events)

    def test_counts_distintos_rechazados(self):
        for arrays in (
            {
                "v": ak.Array([[1.0, 2.0]]),
                "o": ak.Array([[1.0, 2.0, 3.0]]),
                "m": ak.Array([[True, True]]),
            },
            {
                "v": ak.Array([[1.0, 2.0]]),
                "o": ak.Array([[1.0, 2.0]]),
                "m": ak.Array([[True]]),
            },
        ):
            with self.assertRaisesRegex(ValueError, "misma colección"):
                analysis_tools.evaluate("leading(v, o, m)", arrays, 1)

    def test_mas_de_un_nivel_rechazado(self):
        arrays = {
            "v": ak.Array([[[1.0], [2.0]], [[3.0]]]),
            "o": ak.Array([[[1.0], [2.0]], [[3.0]]]),
            "m": ak.Array([[[True], [True]], [[True]]]),
        }
        with self.assertRaisesRegex(ValueError, "un nivel"):
            analysis_tools.evaluate("leading(v, o, m)", arrays, 2)

    def test_lista_por_evento_obligatoria(self):
        arrays = {
            "v": np.array([1.0, 2.0]),
            "o": ak.Array([[1.0], [2.0]]),
            "m": ak.Array([[True], [True]]),
        }
        with self.assertRaisesRegex(ValueError, "lista por evento"):
            analysis_tools.evaluate("leading(v, o, m)", arrays, 2)

    def test_mascara_booleana_obligatoria(self):
        with self.assertRaisesRegex(ValueError, "máscara booleana"):
            analysis_tools.evaluate(
                "leading(value, order, order)", self.arrays, self.n_events
            )


@unittest.skipUnless(
    np is not None and ak is not None and uproot is not None,
    "uproot/awkward no están instalados",
)
class JaggedSelectTest(unittest.TestCase):
    """select con una rama jagged: reducciones en cortes y avisos en el cutflow."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.root = cls.dir / "jagged.root"
        _write_root_jagged(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_cortes_con_reducciones(self):
        cuts = self.dir / "jagged_cuts.json"
        _write_cuts(
            cuts,
            [
                {
                    "name": "un_muon_pt20",
                    "expression": "count(muon_pt > 20) >= 1",
                    "source": "test#jagged",
                },
                {"name": "met15", "expression": "met > 15", "source": "test#jagged"},
            ],
        )
        result = analysis_tools.select([str(self.root)], str(cuts), tree="events")
        self.assertEqual(result["total_events"], 3)
        self.assertEqual([cut["passed"] for cut in result["cuts"]], [2, 1])
        self.assertEqual(result["final_events"], 1)
        self.assertIn("count(muon_pt > 20): 1 de 3 eventos con lista vacía", result["warnings"])

    def test_max_en_corte(self):
        cuts = self.dir / "max_cuts.json"
        _write_cuts(
            cuts,
            [
                {
                    "name": "max_pt35",
                    "expression": "max(muon_pt) > 35",
                    "source": "test#jagged",
                }
            ],
        )
        result = analysis_tools.select([str(self.root)], str(cuts), tree="events")
        self.assertEqual(result["final_events"], 1)
        self.assertIn("max(muon_pt): 1 de 3 eventos con lista vacía", result["warnings"])

    def test_jagged_sin_reducir_rechazado(self):
        cuts = self.dir / "raw_cuts.json"
        _write_cuts(
            cuts,
            [
                {
                    "name": "raw",
                    "expression": "muon_pt > 20",
                    "source": "test#jagged",
                }
            ],
        )
        with self.assertRaisesRegex(ValueError, "redúcela"):
            analysis_tools.select([str(self.root)], str(cuts), tree="events")

    def test_corte_con_leading(self):
        cuts = self.dir / "leading_cuts.json"
        _write_cuts(
            cuts,
            [
                {
                    "name": "lider_pt20",
                    "expression": "leading(muon_pt, muon_pt, muon_flag) > 20",
                    "source": "test#leading",
                }
            ],
        )
        result = analysis_tools.select([str(self.root)], str(cuts), tree="events")
        self.assertEqual(result["total_events"], 3)
        self.assertEqual(result["final_events"], 1)
        self.assertIn(
            "leading(muon_pt, muon_pt, muon_flag): 1 de 3 eventos sin objeto que "
            "pase la máscara",
            result["warnings"],
        )


REAL_ROOT = (
    REPO_ROOT
    / "data"
    / "prueba_d"
    / "24603428-8B2E-44B3-9E97-B991129E184D.root"
)
REAL_TREE = "Events"
REAL_ENABLED = os.environ.get("MJFC_REAL_ROOT") == "1"


@unittest.skipUnless(
    REAL_ENABLED
    and REAL_ROOT.is_file()
    and np is not None
    and ak is not None
    and uproot is not None,
    "integración 31102 desactivada: define MJFC_REAL_ROOT=1 y descarga el archivo",
)
class Real31102ReductionTest(unittest.TestCase):
    """Compara las reducciones con un cálculo independiente sobre el 31102 real."""

    N_ENTRIES = 5000

    @classmethod
    def setUpClass(cls):
        with uproot.open(REAL_ROOT) as handle:
            tree = handle[REAL_TREE]
            arrays = tree.arrays(
                ["MET_pt", "Muon_pt"], entry_stop=cls.N_ENTRIES, library="ak"
            )
        cls.met = np.asarray(ak.to_numpy(arrays["MET_pt"]))
        cls.muon_pt = arrays["Muon_pt"]
        cls.lists = ak.to_list(cls.muon_pt)
        cls.n_events = len(cls.met)

    def value(self, expression, diagnostics=None):
        return analysis_tools.evaluate(
            expression,
            {"MET_pt": self.met, "Muon_pt": self.muon_pt},
            self.n_events,
            diagnostics,
        )

    def mask(self, expression, diagnostics=None):
        return analysis_tools.evaluate_expression(
            expression,
            {"MET_pt": self.met, "Muon_pt": self.muon_pt},
            self.n_events,
            diagnostics,
        )

    def test_fichero_y_ramas(self):
        self.assertEqual(self.n_events, self.N_ENTRIES)
        self.assertEqual(self.met.shape, (self.N_ENTRIES,))
        self.assertEqual(self.muon_pt.ndim, 2)

    def test_count_independiente(self):
        expected = [sum(1 for pt in event if pt > 20.0) for event in self.lists]
        self.assertEqual(self.value("count(Muon_pt > 20)").tolist(), expected)

    def test_any_all_independientes(self):
        expected_any = [any(pt > 20.0 for pt in event) for event in self.lists]
        expected_all = [all(pt > 20.0 for pt in event) for event in self.lists]
        self.assertEqual(self.mask("any(Muon_pt > 20)").tolist(), expected_any)
        self.assertEqual(self.mask("all(Muon_pt > 20)").tolist(), expected_all)

    def test_max_independiente(self):
        expected = [max(event) if event else np.nan for event in self.lists]
        np.testing.assert_allclose(
            self.value("max(Muon_pt)"), expected, equal_nan=True
        )

    def test_avisos_de_listas_vacias(self):
        diagnostics = analysis_tools.Diagnostics()
        self.value("count(Muon_pt > 20)", diagnostics)
        expected_empty = sum(1 for event in self.lists if not event)
        self.assertGreater(expected_empty, 0)
        self.assertEqual(
            diagnostics.empty_counts(), {"count(Muon_pt > 20)": expected_empty}
        )
        self.assertEqual(
            diagnostics.warnings(),
            [
                f"count(Muon_pt > 20): {expected_empty} de {self.n_events} "
                "eventos con lista vacía"
            ],
        )

    def test_select_sobre_fichero_completo(self):
        cuts = Path(tempfile.mkdtemp()) / "real_cuts.json"
        _write_cuts(
            cuts,
            [
                {
                    "name": "un_muon_pt20",
                    "expression": "count(Muon_pt > 20) >= 1",
                    "source": "test#31102",
                }
            ],
        )
        result = analysis_tools.select([str(REAL_ROOT)], str(cuts), tree=REAL_TREE)
        self.assertEqual(result["total_events"], 402010)
        with uproot.open(REAL_ROOT) as handle:
            all_muons = handle[REAL_TREE].arrays(["Muon_pt"], library="ak")["Muon_pt"]
        expected = int(ak.sum(ak.any(all_muons > 20.0, axis=1)))
        self.assertEqual(result["final_events"], expected)
        empty = int(ak.sum(ak.num(all_muons, axis=1) == 0))
        self.assertIn(
            f"count(Muon_pt > 20): {empty} de 402010 eventos con lista vacía",
            result["warnings"],
        )
        cuts.unlink()


HIST = {
    "met": [10.0, 20.0, 30.0, 40.0, 50.0],
    "met_nan": [float("nan"), 20.0, 30.0, 40.0, 50.0],
    "muon_pt": [[10.0, 40.0], [], [30.0], [25.0], [5.0]],
    "muon_eta": [[0.5, 1.8], [], [1.9], [-2.2], [0.1]],
    "muon_tightId": [[1, 1], [], [1], [1], [0]],
    "tau_pt": [[5.0], [], [7.0, 8.0], [], [1.0]],
    "weight": [1.0, 2.0, 1.0, 1.0, 1.0],
    "weight_bad": [1.0, float("nan"), 1.0, 1.0, 1.0],
}


def _write_hist_root(path):
    with uproot.recreate(path) as handle:
        handle.mktree(
            "events",
            {
                "met": "float64",
                "met_nan": "float64",
                "muon_pt": "var * float64",
                "muon_eta": "var * float64",
                "muon_tightId": "var * int32",
                "tau_pt": "var * float64",
                "weight": "float64",
                "weight_bad": "float64",
            },
        )
        handle["events"].extend(
            {
                "met": np.array(HIST["met"]),
                "met_nan": np.array(HIST["met_nan"]),
                "muon_pt": ak.Array(HIST["muon_pt"]),
                "muon_eta": ak.Array(HIST["muon_eta"]),
                "muon_tightId": ak.Array(HIST["muon_tightId"]),
                "tau_pt": ak.Array(HIST["tau_pt"]),
                "weight": np.array(HIST["weight"]),
                "weight_bad": np.array(HIST["weight_bad"]),
            }
        )


def _write_hist_parquet(path, data=None):
    data = HIST if data is None else data
    pq.write_table(
        pa.table(
            {
                "met": pa.array(data["met"]),
                "met_nan": pa.array(data["met_nan"]),
                "muon_pt": pa.array(data["muon_pt"]),
                "muon_eta": pa.array(data["muon_eta"]),
                "muon_tightId": pa.array(data["muon_tightId"]),
                "tau_pt": pa.array(data["tau_pt"]),
                "weight": pa.array(data["weight"]),
                "weight_bad": pa.array(data["weight_bad"]),
            }
        ),
        path,
    )


@unittest.skipUnless(
    np is not None and ak is not None and uproot is not None,
    "uproot/awkward no están instalados",
)
class HistTestCase(unittest.TestCase):
    """Fixtures ROOT/Parquet compartidas por los tests de hist."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.root = cls.dir / "hist.root"
        cls.parquet = cls.dir / "hist.parquet"
        _write_hist_root(cls.root)
        _write_hist_parquet(cls.parquet)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def hist(self, observable, bins, range_, **kwargs):
        kwargs.setdefault("tree", "events")
        return analysis_tools.hist(
            [str(self.root)], observable, bins, range_, **kwargs
        )


class HistEventModeTest(HistTestCase):
    """Modo evento: bins, flujos, pesos, sumw2 y normalización."""

    def test_bins_y_edges(self):
        result = self.hist("met", 5, [0.0, 60.0])
        self.assertEqual(result["mode"], "event")
        self.assertEqual(result["observable"], "met")
        self.assertEqual(result["events"], 5)
        self.assertEqual(result["selected_events"], 5)
        self.assertEqual(result["entries"], 5)
        self.assertEqual(result["bins"]["count"], 5)
        self.assertEqual(result["bins"]["range"], [0.0, 60.0])
        self.assertEqual(result["bins"]["edges"], [0.0, 12.0, 24.0, 36.0, 48.0, 60.0])
        self.assertEqual(result["bins"]["counts"], [1.0, 1.0, 1.0, 1.0, 1.0])
        self.assertEqual(result["bins"]["underflow"], 0.0)
        self.assertEqual(result["bins"]["overflow"], 0.0)
        self.assertEqual(result["bins"]["nan"], 0.0)
        self.assertEqual(result["sumw"], 5.0)
        self.assertEqual(result["normalize"], "none")
        self.assertEqual(result["scale"], 1.0)

    def test_underflow_overflow(self):
        result = self.hist("met", 3, [15.0, 45.0])
        self.assertEqual(result["bins"]["counts"], [1.0, 1.0, 1.0])
        self.assertEqual(result["bins"]["underflow"], 1.0)
        self.assertEqual(result["bins"]["overflow"], 1.0)
        self.assertEqual(result["entries"], 5)

    def test_nan_fuera_de_bins(self):
        result = self.hist("met_nan", 5, [0.0, 60.0])
        self.assertEqual(result["bins"]["nan"], 1.0)
        self.assertEqual(result["bins"]["counts"], [0.0, 1.0, 1.0, 1.0, 1.0])
        self.assertEqual(result["bins"]["underflow"], 0.0)
        self.assertEqual(result["bins"]["overflow"], 0.0)
        self.assertEqual(result["entries"], 5)
        self.assertTrue(any("NaN" in warning for warning in result["warnings"]))

    def test_pesos_y_sumw2(self):
        result = self.hist("met", 5, [0.0, 60.0], weights="weight")
        self.assertEqual(result["bins"]["counts"], [1.0, 2.0, 1.0, 1.0, 1.0])
        self.assertEqual(result["sumw"], 6.0)
        self.assertEqual(result["sumw2"]["counts"], [1.0, 4.0, 1.0, 1.0, 1.0])

    def test_peso_escalar(self):
        result = self.hist("met", 5, [0.0, 60.0], weights="2")
        self.assertEqual(result["bins"]["counts"], [2.0, 2.0, 2.0, 2.0, 2.0])
        self.assertEqual(result["sumw2"]["counts"], [4.0, 4.0, 4.0, 4.0, 4.0])

    def test_peso_no_finito_rechazado(self):
        with self.assertRaisesRegex(ValueError, "finitos"):
            self.hist("met", 5, [0.0, 60.0], weights="weight_bad")

    def test_normalize_area(self):
        result = self.hist("met", 5, [0.0, 60.0], normalize="area")
        self.assertAlmostEqual(sum(result["bins"]["counts"]), 1.0)
        self.assertAlmostEqual(result["scale"], 1.0 / 5.0)
        self.assertAlmostEqual(result["sumw"], 1.0)
        for count, sumw2 in zip(result["bins"]["counts"], result["sumw2"]["counts"]):
            self.assertAlmostEqual(sumw2, count * count)

    def test_normalize_area_incluye_flujos(self):
        result = self.hist("met", 3, [15.0, 45.0], normalize="area")
        self.assertAlmostEqual(sum(result["bins"]["counts"]), 1.0)
        self.assertAlmostEqual(result["bins"]["underflow"], 1.0 / 3.0)
        self.assertAlmostEqual(result["bins"]["overflow"], 1.0 / 3.0)

    def test_histograma_vacio(self):
        result = self.hist("met", 5, [0.0, 60.0], selection="met < 0")
        self.assertEqual(result["entries"], 0)
        self.assertEqual(result["selected_events"], 0)
        self.assertTrue(any("vacío" in warning for warning in result["warnings"]))
        area = self.hist("met", 5, [0.0, 60.0], selection="met < 0", normalize="area")
        self.assertEqual(area["scale"], 1.0)
        self.assertTrue(any("normalizar a área" in w for w in area["warnings"]))

    def test_rango_invalido(self):
        for range_ in ([50.0, 10.0], [10.0, 10.0], [float("nan"), 10.0], [0.0, float("inf")]):
            with self.assertRaises(ValueError):
                self.hist("met", 5, range_)

    def test_bins_invalido(self):
        for bins in (0, -3):
            with self.assertRaisesRegex(ValueError, "bins"):
                self.hist("met", bins, [0.0, 60.0])

    def test_modo_y_normalizacion_invalidos(self):
        with self.assertRaisesRegex(ValueError, "mode"):
            self.hist("met", 5, [0.0, 60.0], mode="objeto")
        with self.assertRaisesRegex(ValueError, "normalize"):
            self.hist("met", 5, [0.0, 60.0], normalize="suma")

    def test_observable_jagged_en_modo_evento(self):
        with self.assertRaisesRegex(ValueError, "mode object"):
            self.hist("muon_pt", 5, [0.0, 60.0])

    def test_observable_plana_en_modo_objeto(self):
        with self.assertRaisesRegex(ValueError, "jagged"):
            self.hist("met", 5, [0.0, 60.0], mode="object")

    def test_rama_inexistente(self):
        with self.assertRaises(KeyError):
            self.hist("no_existe", 5, [0.0, 60.0])

    def test_out_escribe_json(self):
        out = self.dir / "out" / "hist.json"
        result = self.hist("met", 5, [0.0, 60.0], out=str(out))
        self.assertTrue(out.is_file())
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), result)

    def test_multiples_inputs(self):
        second = self.dir / "hist2.root"
        with uproot.recreate(second) as handle:
            handle.mktree(
                "events",
                {"met": "float64", "met_nan": "float64", "muon_pt": "var * float64",
                 "weight": "float64", "weight_bad": "float64"},
            )
            handle["events"].extend(
                {
                    "met": np.array([10.0, 20.0]),
                    "met_nan": np.array([float("nan"), 20.0]),
                    "muon_pt": ak.Array([[1.0], []]),
                    "weight": np.array([1.0, 1.0]),
                    "weight_bad": np.array([1.0, 1.0]),
                }
            )
        result = analysis_tools.hist(
            [str(self.root), str(second)], "met", 5, [0.0, 60.0], tree="events"
        )
        self.assertEqual(result["events"], 7)
        self.assertEqual(result["bins"]["counts"], [2.0, 2.0, 1.0, 1.0, 1.0])
        self.assertEqual(sum(result["bins"]["counts"]), 7.0)

    def test_tree_obligatorio(self):
        with self.assertRaisesRegex(ValueError, "tree"):
            analysis_tools.hist([str(self.root)], "met", 5, [0.0, 60.0])


class HistObjectModeTest(HistTestCase):
    """Modo objeto: un valor por elemento de la lista de cada evento."""

    def test_aplana_todos_los_objetos(self):
        result = self.hist("muon_pt", 5, [0.0, 50.0], mode="object")
        self.assertEqual(result["mode"], "object")
        self.assertEqual(result["entries"], 5)
        self.assertEqual(result["bins"]["counts"], [1.0, 1.0, 1.0, 1.0, 1.0])
        self.assertEqual(result["bins"]["underflow"], 0.0)
        self.assertEqual(result["bins"]["overflow"], 0.0)

    def test_listas_vacias_no_entran(self):
        result = self.hist("muon_pt", 5, [0.0, 50.0], mode="object")
        self.assertEqual(result["selected_events"], 5)
        self.assertEqual(result["entries"], 5)
        self.assertEqual(result["warnings"], [])

    def test_seleccion_por_evento(self):
        result = self.hist(
            "muon_pt", 5, [0.0, 50.0], mode="object", selection="met > 15"
        )
        self.assertEqual(result["selected_events"], 4)
        self.assertEqual(result["entries"], 3)
        self.assertEqual(result["bins"]["counts"], [1.0, 0.0, 1.0, 1.0, 0.0])

    def test_pesos_se_replican_por_objeto(self):
        result = self.hist(
            "muon_pt",
            5,
            [0.0, 50.0],
            mode="object",
            selection="met > 15",
            weights="met / 10",
        )
        # Eventos 1..4 con pesos 2,3,4,5; objetos 30 (w3), 25 (w4) y 5 (w5).
        self.assertEqual(result["bins"]["counts"], [5.0, 0.0, 4.0, 3.0, 0.0])
        self.assertEqual(result["sumw"], 12.0)
        self.assertEqual(result["sumw2"]["counts"], [25.0, 0.0, 16.0, 9.0, 0.0])

    def test_pesos_jagged_rechazados(self):
        with self.assertRaisesRegex(ValueError, "lista por evento"):
            self.hist("muon_pt", 5, [0.0, 50.0], mode="object", weights="muon_pt")


class HistObjectCutTest(HistTestCase):
    """--object-cut con --object-source: corte por objeto y sus estadísticas."""

    CUT = "muon_pt > 20 and abs(muon_eta) < 2.1 and muon_tightId == 1"
    SOURCE = "strategy.md#tabla-cortes-fila-5"

    def hist_object(self, **kwargs):
        kwargs.setdefault("mode", "object")
        kwargs.setdefault("tree", "events")
        kwargs.setdefault("object_cut", self.CUT)
        kwargs.setdefault("object_source", self.SOURCE)
        return self.hist("muon_pt", 5, [0.0, 50.0], **kwargs)

    def test_corte_por_objeto(self):
        result = self.hist_object()
        self.assertEqual(result["mode"], "object")
        self.assertEqual(result["entries"], 2)
        self.assertEqual(result["bins"]["counts"], [0.0, 0.0, 0.0, 1.0, 1.0])
        self.assertEqual(
            result["object_cut"],
            {
                "expression": "muon_pt > 20 and abs(muon_eta) < 2.1 and muon_tightId == 1",
                "source": self.SOURCE,
                "events_without_objects": 3,
                "objects_before": 5,
                "objects_after": 2,
            },
        )

    def test_aviso_eventos_sin_objetos(self):
        result = self.hist_object()
        self.assertIn(
            "--object-cut: 3 de 5 eventos seleccionados sin objetos que pasen el corte",
            result["warnings"],
        )

    def test_sin_eventos_sin_objetos_no_avisa(self):
        result = self.hist_object(
            selection="met > 15 and count(muon_pt > 0) > 0",
            object_cut="muon_pt > 0",
        )
        self.assertEqual(result["selected_events"], 3)
        self.assertEqual(result["object_cut"]["events_without_objects"], 0)
        self.assertFalse(
            any("--object-cut" in warning for warning in result["warnings"])
        )

    def test_seleccion_por_evento_antes_del_corte(self):
        result = self.hist_object(selection="met > 15")
        self.assertEqual(result["selected_events"], 4)
        self.assertEqual(result["entries"], 1)
        self.assertEqual(result["object_cut"]["objects_before"], 3)
        self.assertEqual(result["object_cut"]["objects_after"], 1)
        self.assertEqual(result["object_cut"]["events_without_objects"], 3)

    def test_pesos_solo_de_objetos_supervivientes(self):
        result = self.hist_object(weights="met / 10")
        # Evento 0: muón de 40 con peso 1; evento 2: muón de 30 con peso 3.
        self.assertEqual(result["bins"]["counts"], [0.0, 0.0, 0.0, 3.0, 1.0])
        self.assertEqual(result["sumw"], 4.0)
        self.assertEqual(result["sumw2"]["counts"], [0.0, 0.0, 0.0, 9.0, 1.0])

    def test_sin_corte_por_objeto(self):
        result = self.hist("muon_pt", 5, [0.0, 50.0], mode="object")
        self.assertIsNone(result["object_cut"])

    def test_source_obligatoria(self):
        with self.assertRaisesRegex(ValueError, "object-source"):
            self.hist_object(object_source=None)

    def test_source_requiere_corte(self):
        with self.assertRaisesRegex(ValueError, "requiere --object-cut"):
            self.hist_object(object_cut=None)

    def test_source_todo_rechazada(self):
        with self.assertRaisesRegex(ValueError, "fuente real"):
            self.hist_object(object_source="TODO")

    def test_solo_en_modo_objeto(self):
        with self.assertRaisesRegex(ValueError, "mode object"):
            self.hist_object(mode="event")

    def test_reduccion_prohibida(self):
        with self.assertRaisesRegex(ValueError, "por objeto, no por evento"):
            self.hist_object(object_cut="count(muon_pt > 20) > 0")

    def test_mascara_no_booleana(self):
        with self.assertRaisesRegex(ValueError, "booleano por objeto"):
            self.hist_object(object_cut="muon_pt")

    def test_rama_escalar_rechazada(self):
        with self.assertRaisesRegex(ValueError, "por objeto"):
            self.hist_object(object_cut="met > 0")

    def test_coleccion_distinta_rechazada(self):
        with self.assertRaisesRegex(ValueError, "misma colección"):
            self.hist_object(object_cut="tau_pt > 0")


class HistSelectionTest(HistTestCase):
    """Selección con expresiones, reductions y cuts.json."""

    def test_seleccion_con_count(self):
        result = self.hist(
            "muon_pt",
            5,
            [0.0, 50.0],
            mode="object",
            selection="count(muon_pt > 20) >= 1",
        )
        self.assertEqual(result["selected_events"], 3)
        self.assertEqual(result["entries"], 4)
        self.assertEqual(result["bins"]["counts"], [0.0, 1.0, 1.0, 1.0, 1.0])
        self.assertTrue(
            any("count(muon_pt > 20): 1 de 5" in w for w in result["warnings"])
        )

    def test_cuts_json(self):
        cuts = self.dir / "hist_cuts.json"
        _write_cuts(
            cuts,
            [{"name": "met15", "expression": "met > 15", "source": "test#hist"}],
        )
        result = self.hist("met", 5, [0.0, 60.0], cuts_path=str(cuts))
        self.assertEqual(result["selected_events"], 4)
        self.assertEqual([cut["name"] for cut in result["cuts"]], ["met15"])
        self.assertEqual(result["bins"]["counts"], [0.0, 1.0, 1.0, 1.0, 1.0])

    def test_seleccion_y_cuts_se_combinan(self):
        cuts = self.dir / "hist_cuts2.json"
        _write_cuts(
            cuts,
            [{"name": "met20", "expression": "met > 20", "source": "test#hist"}],
        )
        result = self.hist(
            "met", 5, [0.0, 60.0], cuts_path=str(cuts), selection="met < 45"
        )
        self.assertEqual(result["selected_events"], 2)
        self.assertEqual(result["bins"]["counts"], [0.0, 0.0, 1.0, 1.0, 0.0])

    def test_cuts_sin_source(self):
        cuts = self.dir / "hist_cuts_bad.json"
        _write_cuts(cuts, [{"name": "x", "expression": "met > 0"}])
        with self.assertRaisesRegex(ValueError, "source"):
            self.hist("met", 5, [0.0, 60.0], cuts_path=str(cuts))

    def test_leading_en_modo_evento(self):
        result = self.hist(
            "leading(muon_pt, muon_pt, muon_tightId == 1)", 5, [0.0, 50.0]
        )
        self.assertEqual(result["mode"], "event")
        self.assertEqual(result["entries"], 5)
        self.assertEqual(result["bins"]["nan"], 2.0)
        self.assertEqual(result["bins"]["counts"], [0.0, 0.0, 1.0, 1.0, 1.0])
        self.assertIn(
            "leading(muon_pt, muon_pt, muon_tightId == 1): 2 de 5 eventos sin "
            "objeto que pase la máscara",
            result["warnings"],
        )


@unittest.skipUnless(
    np is not None and ak is not None and pa is not None and pq is not None,
    "pyarrow/awkward no están instalados",
)
class HistParquetTest(unittest.TestCase):
    """hist sobre Parquet: evento, objeto y varias entradas."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.parquet = cls.dir / "hist.parquet"
        _write_hist_parquet(cls.parquet)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_evento(self):
        result = analysis_tools.hist(
            [str(self.parquet)], "met", 5, [0.0, 60.0]
        )
        self.assertEqual(result["format"], "parquet")
        self.assertIsNone(result["tree"])
        self.assertEqual(result["bins"]["counts"], [1.0, 1.0, 1.0, 1.0, 1.0])

    def test_objeto(self):
        result = analysis_tools.hist(
            [str(self.parquet)], "muon_pt", 5, [0.0, 50.0], mode="object"
        )
        self.assertEqual(result["entries"], 5)
        self.assertEqual(result["bins"]["counts"], [1.0, 1.0, 1.0, 1.0, 1.0])

    def test_tree_prohibido(self):
        with self.assertRaisesRegex(ValueError, "solo aplica"):
            analysis_tools.hist(
                [str(self.parquet)], "met", 5, [0.0, 60.0], tree="events"
            )

    def test_objeto_con_object_cut(self):
        result = analysis_tools.hist(
            [str(self.parquet)],
            "muon_pt",
            5,
            [0.0, 50.0],
            mode="object",
            object_cut="muon_pt > 20 and abs(muon_eta) < 2.1 and muon_tightId == 1",
            object_source="test#object-cut",
        )
        self.assertEqual(result["object_cut"]["objects_before"], 5)
        self.assertEqual(result["object_cut"]["objects_after"], 2)
        self.assertEqual(result["bins"]["counts"], [0.0, 0.0, 0.0, 1.0, 1.0])


@unittest.skipUnless(
    np is not None and pa is not None and pq is not None,
    "pyarrow/numpy no están instalados",
)
class CliAnalysisHistTest(unittest.TestCase):
    """CLI analysis hist: JSON, --out, --max-items y errores."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.parquet = cls.dir / "hist.parquet"
        _write_hist_parquet(cls.parquet)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_hist_cli(self):
        code, stdout, stderr = run_cli(
            [
                "analysis",
                "hist",
                str(self.parquet),
                "--observable",
                "met",
                "--bins",
                "5",
                "--range",
                "0",
                "60",
            ]
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["bins"]["count"], 5)
        self.assertEqual(payload["bins"]["counts"], [1.0, 1.0, 1.0, 1.0, 1.0])
        self.assertEqual(payload["normalize"], "none")

    def test_max_items_no_trunca_bins(self):
        code, stdout, _ = run_cli(
            [
                "--max-items",
                "1",
                "analysis",
                "hist",
                str(self.parquet),
                "--observable",
                "met",
                "--bins",
                "5",
                "--range",
                "0",
                "60",
            ]
        )
        self.assertEqual(code, 0)
        payload = json.loads(stdout)
        self.assertEqual(len(payload["bins"]["counts"]), 5)
        self.assertEqual(len(payload["bins"]["edges"]), 6)
        self.assertEqual(len(payload["sumw2"]["counts"]), 5)

    def test_out(self):
        out = self.dir / "hist.json"
        code, stdout, _ = run_cli(
            [
                "analysis",
                "hist",
                str(self.parquet),
                "--observable",
                "met",
                "--bins",
                "3",
                "--range",
                "15",
                "45",
                "--normalize",
                "area",
                "--out",
                str(out),
            ]
        )
        self.assertEqual(code, 0)
        payload = json.loads(stdout)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), payload)
        self.assertAlmostEqual(sum(payload["bins"]["counts"]), 1.0)

    def test_error_bins(self):
        code, stdout, stderr = run_cli(
            [
                "analysis",
                "hist",
                str(self.parquet),
                "--observable",
                "met",
                "--bins",
                "0",
                "--range",
                "0",
                "60",
            ]
        )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("bins", stderr)

    def test_object_cut_cli(self):
        code, stdout, stderr = run_cli(
            [
                "analysis",
                "hist",
                str(self.parquet),
                "--observable",
                "muon_pt",
                "--mode",
                "object",
                "--bins",
                "5",
                "--range",
                "0",
                "50",
                "--object-cut",
                "muon_pt > 20 and abs(muon_eta) < 2.1 and muon_tightId == 1",
                "--object-source",
                "strategy.md#tabla-cortes-fila-5",
            ]
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["entries"], 2)
        self.assertEqual(
            payload["object_cut"]["source"], "strategy.md#tabla-cortes-fila-5"
        )
        self.assertEqual(payload["object_cut"]["objects_after"], 2)

    def test_object_cut_sin_source_cli(self):
        code, stdout, stderr = run_cli(
            [
                "analysis",
                "hist",
                str(self.parquet),
                "--observable",
                "muon_pt",
                "--mode",
                "object",
                "--bins",
                "5",
                "--range",
                "0",
                "50",
                "--object-cut",
                "muon_pt > 20",
            ]
        )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("object-source", stderr)

    def test_help(self):
        code, stdout, stderr = run_cli(["analysis", "hist", "--help"])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("--normalize", stdout)
        self.assertIn("--mode", stdout)


REAL_HIST_ROOT = (
    REPO_ROOT
    / "data"
    / "prueba_d"
    / "24603428-8B2E-44B3-9E97-B991129E184D.root"
)


@unittest.skipUnless(
    REAL_ENABLED
    and REAL_HIST_ROOT.is_file()
    and np is not None
    and ak is not None
    and uproot is not None,
    "integración 31102 desactivada: define MJFC_REAL_ROOT=1 y descarga el archivo",
)
class Real31102HistTest(unittest.TestCase):
    """hist sobre TODOS los eventos del 31102 contra un cálculo independiente."""

    CUTS = [
        {
            "name": "un_muon_pt20",
            "expression": "count(Muon_pt > 20) >= 1",
            "source": "test#31102",
        }
    ]

    @classmethod
    def setUpClass(cls):
        with uproot.open(REAL_HIST_ROOT) as handle:
            arrays = handle[REAL_TREE].arrays(
                ["MET_pt", "Muon_pt", "Muon_eta", "Muon_tightId"], library="ak"
            )
        cls.met = np.asarray(ak.to_numpy(arrays["MET_pt"]))
        cls.muon_pt = arrays["Muon_pt"]
        cls.muon_eta = arrays["Muon_eta"]
        cls.muon_tight = arrays["Muon_tightId"]
        cls.n_events = len(cls.met)
        cls.mask = np.asarray(ak.to_numpy(ak.any(cls.muon_pt > 20.0, axis=1)))
        cls.tmp = tempfile.TemporaryDirectory()
        cls.cuts = Path(cls.tmp.name) / "real_hist_cuts.json"
        _write_cuts(cls.cuts, cls.CUTS)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def histogram(self, observable, bins, range_, mode="event"):
        return analysis_tools.hist(
            [str(REAL_HIST_ROOT)],
            observable,
            bins,
            range_,
            tree=REAL_TREE,
            mode=mode,
            cuts_path=str(self.cuts),
        )

    def test_met_modo_evento(self):
        bins, range_ = 20, [0.0, 200.0]
        result = self.histogram("MET_pt", bins, range_)
        values = self.met[self.mask]
        expected, _ = np.histogram(values, bins=bins, range=range_)
        self.assertEqual(result["events"], 402010)
        self.assertEqual(result["selected_events"], int(self.mask.sum()))
        self.assertEqual(result["entries"], len(values))
        self.assertEqual(result["bins"]["counts"], [float(v) for v in expected])
        self.assertEqual(result["bins"]["underflow"], float((values < range_[0]).sum()))
        self.assertEqual(result["bins"]["overflow"], float((values >= range_[1]).sum()))
        self.assertEqual(result["bins"]["nan"], float(np.isnan(values).sum()))
        self.assertEqual(result["sumw"], float(len(values)))

    def test_muon_pt_modo_objeto(self):
        bins, range_ = 30, [0.0, 60.0]
        result = self.histogram("Muon_pt", bins, range_, mode="object")
        values = np.asarray(ak.to_numpy(ak.flatten(self.muon_pt[self.mask])))
        expected, _ = np.histogram(values, bins=bins, range=range_)
        self.assertEqual(result["mode"], "object")
        self.assertEqual(result["entries"], len(values))
        self.assertEqual(result["bins"]["counts"], [float(v) for v in expected])
        self.assertEqual(result["bins"]["underflow"], float((values < range_[0]).sum()))
        self.assertEqual(result["bins"]["overflow"], float((values >= range_[1]).sum()))
        self.assertEqual(result["bins"]["nan"], float(np.isnan(values).sum()))
        self.assertEqual(result["sumw"], float(len(values)))
        self.assertEqual(result["sumw2"]["counts"], result["bins"]["counts"])

    def test_muon_pt_modo_objeto_con_object_cut(self):
        bins, range_ = 30, [0.0, 60.0]
        result = analysis_tools.hist(
            [str(REAL_HIST_ROOT)],
            "Muon_pt",
            bins,
            range_,
            tree=REAL_TREE,
            mode="object",
            cuts_path=str(self.cuts),
            object_cut="Muon_pt > 20 and abs(Muon_eta) < 2.1 and Muon_tightId",
            object_source="test#31102-object-cut",
        )

        selected_pt = self.muon_pt[self.mask]
        selected_eta = self.muon_eta[self.mask]
        selected_id = self.muon_tight[self.mask]
        object_mask = (
            (selected_pt > 20.0)
            & (np.abs(selected_eta) < 2.1)
            & selected_id
        )
        filtered = selected_pt[object_mask]
        values = np.asarray(ak.to_numpy(ak.flatten(filtered, axis=1)))
        expected, _ = np.histogram(values, bins=bins, range=range_)
        expected_without = int(ak.sum(ak.num(filtered, axis=1) == 0))

        self.assertEqual(result["entries"], len(values))
        self.assertEqual(result["bins"]["counts"], [float(v) for v in expected])
        self.assertEqual(result["bins"]["underflow"], float((values < range_[0]).sum()))
        self.assertEqual(result["bins"]["overflow"], float((values >= range_[1]).sum()))
        self.assertEqual(
            result["object_cut"]["objects_before"],
            int(ak.sum(ak.num(selected_pt, axis=1))),
        )
        self.assertEqual(
            result["object_cut"]["objects_after"], int(ak.sum(ak.num(filtered, axis=1)))
        )
        self.assertEqual(
            result["object_cut"]["events_without_objects"], expected_without
        )
        self.assertIn(
            f"--object-cut: {expected_without} de {int(self.mask.sum())} eventos "
            "seleccionados sin objetos que pasen el corte",
            result["warnings"],
        )

    def test_met_area(self):
        result = analysis_tools.hist(
            [str(REAL_HIST_ROOT)],
            "MET_pt",
            20,
            [0.0, 200.0],
            tree=REAL_TREE,
            cuts_path=str(self.cuts),
            normalize="area",
        )
        self.assertAlmostEqual(sum(result["bins"]["counts"]), 1.0, places=12)
        total = (
            sum(result["bins"]["counts"])
            + result["bins"]["underflow"]
            + result["bins"]["overflow"]
            + result["bins"]["nan"]
        )
        self.assertAlmostEqual(result["sumw"], total, places=12)


if __name__ == "__main__":
    unittest.main()
