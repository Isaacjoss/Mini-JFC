"""Selección de eventos y cutflow sobre ROOT/Parquet con expresiones restringidas.

Semántica de operadores (la de numpy):

* ``and``, ``or`` y ``not`` son siempre lógicos.
* ``&``, ``|`` y ``~`` son lógicos con operandos booleanos y bit a bit con enteros.

Reducciones de listas por evento (ramas jagged):

* ``any(x)``: ``True`` si algún elemento es verdadero; lista vacía → ``False``.
* ``all(x)``: ``True`` si todos los elementos son verdaderos; lista vacía → ``True``.
* ``count(x)``: nº de elementos ``True`` de una máscara booleana; lista vacía → ``0``.
* ``max(x)``: máximo de la lista; lista vacía → ``NaN`` (no falla).

Las cuatro reducciones avisan en ``warnings`` de cuántos eventos tenían la lista vacía.

Selección del objeto líder por evento:

* ``leading(values, order, mask)``: valor de ``values`` del objeto con mayor ``order``
  entre los que cumplen ``mask``. Empate → primera posición de la lista. Ningún objeto
  cumple la máscara (o lista vacía) → ``NaN`` y aviso en ``warnings``.
  ``values``, ``order`` y ``mask`` deben ser listas del mismo nivel y de la misma
  colección (mismo número de objetos por evento); ``order`` debe ser numérico y finito
  (los objetos con ``order`` no finito no son candidatos) y ``mask`` booleana.
"""
from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import numpy as np

_FUNCTIONS = {
    "abs": np.abs,
    "sqrt": np.sqrt,
    "log": np.log,
    "log10": np.log10,
    "exp": np.exp,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arctan": np.arctan,
    "minimum": np.minimum,
    "maximum": np.maximum,
    "where": np.where,
    "clip": np.clip,
}
_CONSTANTS = {"pi": math.pi, "e": math.e}
# Reducciones de listas por evento: no son ufuncs, se evalúan aparte.
_REDUCTIONS = frozenset({"any", "all", "count", "max"})
_LEADING = "leading"
_ALLOWED_CALLS = frozenset(_FUNCTIONS) | _REDUCTIONS | {_LEADING}

_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.UnaryOp,
    ast.BinOp,
    ast.Compare,
    ast.Name,
    ast.Constant,
    ast.Call,
    ast.Load,
    ast.And,
    ast.Or,
    ast.Not,
    ast.USub,
    ast.UAdd,
    ast.Invert,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.BitAnd,
    ast.BitOr,
    ast.BitXor,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
)
_BINOPS = {
    ast.Add: np.add,
    ast.Sub: np.subtract,
    ast.Mult: np.multiply,
    ast.Div: np.true_divide,
    ast.FloorDiv: np.floor_divide,
    ast.Mod: np.mod,
    ast.Pow: np.power,
    ast.BitAnd: np.bitwise_and,
    ast.BitOr: np.bitwise_or,
    ast.BitXor: np.bitwise_xor,
}
_UNARY = {
    ast.Not: np.logical_not,
    ast.USub: np.negative,
    ast.UAdd: np.positive,
    ast.Invert: np.invert,
}
_COMPARE = {
    ast.Eq: np.equal,
    ast.NotEq: np.not_equal,
    ast.Lt: np.less,
    ast.LtE: np.less_equal,
    ast.Gt: np.greater,
    ast.GtE: np.greater_equal,
}
_BAD_SOURCES = {"todo", "pendiente", "pendiente de fuente", "sin fuente", "n/a", "na"}


class Diagnostics:
    """Acumula avisos de una evaluación (listas vacías y objetos líder ausentes)."""

    def __init__(self):
        self._empty = {}
        self._without_object = {}

    def record_empty(self, name, label, n_empty, n_events):
        """Suma eventos con lista vacía para la reducción ``name(label)``."""
        key = (name, label)
        total_empty, total_events = self._empty.get(key, (0, 0))
        self._empty[key] = (
            total_empty + int(n_empty),
            total_events + int(n_events),
        )

    def record_without_object(self, name, label, n_missing, n_events):
        """Suma eventos sin ningún objeto que pase la máscara de ``name(label)``."""
        key = (name, label)
        total_missing, total_events = self._without_object.get(key, (0, 0))
        self._without_object[key] = (
            total_missing + int(n_missing),
            total_events + int(n_events),
        )

    def warnings(self) -> list:
        """Avisos de listas vacías y de eventos sin objeto líder, en orden estable."""
        empty = [
            f"{name}({label}): {n_empty} de {n_events} eventos con lista vacía"
            for (name, label), (n_empty, n_events) in sorted(self._empty.items())
            if n_empty
        ]
        without_object = [
            f"{name}({label}): {n_missing} de {n_events} eventos sin objeto que pase la máscara"
            for (name, label), (n_missing, n_events) in sorted(
                self._without_object.items()
            )
            if n_missing
        ]
        return empty + without_object

    def empty_counts(self) -> dict:
        """Recuentos crudos ``{'name(label)': n_empty}`` (para tests y documentación)."""
        return {
            f"{name}({label})": n_empty
            for (name, label), (n_empty, _) in self._empty.items()
            if n_empty
        }

    def without_object_counts(self) -> dict:
        """Recuentos crudos ``{'name(label)': n_missing}`` (para tests y documentación)."""
        return {
            f"{name}({label})": n_missing
            for (name, label), (n_missing, _) in self._without_object.items()
            if n_missing
        }


def _label(node) -> str:
    """Texto de la subexpresión, para identificar la reducción en los avisos."""
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - unparse es estable en Python >= 3.9
        return type(node).__name__


def _inner_primitive(array) -> str:
    """Tipo primitivo del contenido de un array de awkward (p. ej. 'float32', 'bool')."""
    import awkward as ak

    tipo = array.type
    while not isinstance(tipo, ak.types.NumpyType) and hasattr(tipo, "content"):
        tipo = tipo.content
    return getattr(tipo, "primitive", "")


def _is_numeric_primitive(primitive: str) -> bool:
    """True si el tipo primitivo de awkward es numérico o booleano."""
    try:
        dtype = np.dtype(primitive)
    except TypeError:
        return False
    return bool(np.issubdtype(dtype, np.number) or np.issubdtype(dtype, np.bool_))


def _reduction(name, operand, label, diagnostics, n_events):
    """Aplica ``any/all/count/max`` a la lista interna de cada evento."""
    import awkward as ak

    if not isinstance(operand, ak.Array):
        raise ValueError(
            f"la reducción '{name}({label})' necesita una lista por evento (rama jagged); "
            "un array plano ya es escalar por evento"
        )
    if operand.ndim < 2:
        raise ValueError(
            f"la reducción '{name}({label})' necesita una lista por evento (rama jagged); "
            "un array plano ya es escalar por evento"
        )
    if operand.ndim > 2:
        raise ValueError(
            f"la reducción '{name}({label})' solo admite listas de un nivel "
            f"(la rama tiene ndim={operand.ndim})"
        )

    counts = ak.num(operand, axis=1)
    n_empty = int(ak.sum(counts == 0)) if len(counts) else 0
    diagnostics.record_empty(name, label, n_empty, n_events)

    if name == "count":
        primitive = _inner_primitive(operand)
        if primitive != "bool":
            raise ValueError(
                f"count({label}) necesita una máscara booleana (tipo {primitive or '?'}); "
                "usa count(rama > umbral) o count(any(...))"
            )
        return np.asarray(ak.to_numpy(ak.sum(operand, axis=1)), dtype=np.int64)

    try:
        if name == "any":
            return np.asarray(ak.to_numpy(ak.any(operand, axis=1)), dtype=bool)
        if name == "all":
            return np.asarray(ak.to_numpy(ak.all(operand, axis=1)), dtype=bool)
        value = ak.max(operand, axis=1, mask_identity=True)
        return np.asarray(ak.to_numpy(ak.fill_none(value, np.nan)))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"no se puede aplicar {name}({label}): {exc}") from exc


def _leading(values, order, mask, label, diagnostics, n_events):
    """Objeto líder por evento: valor con mayor ``order`` entre los que pasan ``mask``.

    Empate → primera posición. Sin candidatos (lista vacía, máscara sin ``True`` u
    ``order`` no finito) → ``NaN`` y aviso. Exige listas de un nivel de la misma
    colección para los tres argumentos.
    """
    import awkward as ak

    operands = (
        ("values", values),
        ("order", order),
        ("mask", mask),
    )
    for name, operand in operands:
        if not isinstance(operand, ak.Array) or operand.ndim < 2:
            raise ValueError(
                f"la reducción 'leading({label})' necesita una lista por evento (rama "
                f"jagged); el argumento '{name}' ya es escalar por evento"
            )
        if operand.ndim > 2:
            raise ValueError(
                f"la reducción 'leading({label})' solo admite listas de un nivel "
                f"(el argumento '{name}' tiene ndim={operand.ndim})"
            )

    for name, operand in operands[:2]:
        primitive = _inner_primitive(operand)
        if not _is_numeric_primitive(primitive):
            raise ValueError(
                f"leading({label}): el argumento '{name}' no es numérico "
                f"(tipo {primitive or '?'})"
            )
    primitive = _inner_primitive(mask)
    if primitive != "bool":
        raise ValueError(
            f"leading({label}) necesita una máscara booleana para 'mask' "
            f"(tipo {primitive or '?'}); usa una comparación o una rama booleana"
        )

    counts = [
        np.asarray(ak.num(operand, axis=1), dtype=np.int64)
        for _, operand in operands
    ]
    if not (np.array_equal(counts[0], counts[1]) and np.array_equal(counts[0], counts[2])):
        raise ValueError(
            f"leading({label}) no usa la misma colección: el número de objetos por "
            "evento no coincide entre 'values', 'order' y 'mask'"
        )
    counts = counts[0]

    n_events = int(n_events)
    if counts.size != n_events:
        raise ValueError(
            f"leading({label}) tiene {counts.size} eventos; se esperaban {n_events}"
        )

    try:
        flat_values = np.asarray(
            ak.to_numpy(ak.flatten(values, axis=1)), dtype=float
        )
        flat_order = np.asarray(ak.to_numpy(ak.flatten(order, axis=1)), dtype=float)
        flat_mask = np.asarray(ak.to_numpy(ak.flatten(mask, axis=1)), dtype=bool)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"no se puede aplicar leading({label}): {exc}"
        ) from exc

    n_events = int(n_events)
    event_index = np.repeat(np.arange(n_events, dtype=np.int64), counts)
    candidates = flat_mask & np.isfinite(flat_order)

    event_max = np.full(n_events, -np.inf, dtype=float)
    if candidates.any():
        np.maximum.at(event_max, event_index[candidates], flat_order[candidates])
    has_leader = event_max > -np.inf

    # Primera posición del máximo dentro de cada evento (empate → índice menor).
    best_index = np.full(n_events, flat_order.size, dtype=np.int64)
    is_best = candidates & (flat_order == event_max[event_index])
    if is_best.any():
        positions = np.arange(flat_order.size, dtype=np.int64)
        np.minimum.at(best_index, event_index[is_best], positions[is_best])

    result = np.full(n_events, np.nan, dtype=float)
    if has_leader.any():
        result[has_leader] = flat_values[best_index[has_leader]]

    n_without = int((~has_leader).sum())
    diagnostics.record_without_object("leading", label, n_without, n_events)
    return result


def _parse_expression(expression) -> ast.Expression:
    """Parsea una expresión y rechaza cualquier nodo fuera de la lista permitida."""
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("la expresión de un corte no puede estar vacía")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"expresión no válida '{expression}': {exc.msg}") from exc
    for node in ast.walk(tree):
        if type(node) not in _ALLOWED_NODES:
            raise ValueError(
                f"expresión no permitida en '{expression}': {type(node).__name__}"
            )
    return tree


def _collect_names(tree: ast.Expression) -> set:
    """Nombres de rama usados por la expresión (excluye funciones y constantes)."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("solo se permiten llamadas a funciones por nombre")
            if node.func.id not in _ALLOWED_CALLS:
                raise ValueError(f"función no permitida: '{node.func.id}'")
            if node.keywords:
                raise ValueError(f"la función '{node.func.id}' no admite argumentos con nombre")
    return {name for name in names if name not in _ALLOWED_CALLS and name not in _CONSTANTS}


def _eval_node(node, arrays: dict, diagnostics: Diagnostics, n_events: int):
    """Evalúa un nodo AST con arrays de numpy/awkward; no ejecuta Python arbitrario."""
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value
        raise ValueError(
            f"constante no permitida: {value!r} (solo números o booleanos)"
        )
    if isinstance(node, ast.Name):
        if node.id in arrays:
            return arrays[node.id]
        if node.id in _CONSTANTS:
            return _CONSTANTS[node.id]
        raise KeyError(f"la rama o constante '{node.id}' no existe")
    if isinstance(node, ast.BoolOp):
        values = [_eval_node(value, arrays, diagnostics, n_events) for value in node.values]
        result = values[0]
        for value in values[1:]:
            result = (
                np.logical_and(result, value)
                if isinstance(node.op, ast.And)
                else np.logical_or(result, value)
            )
        return result
    if isinstance(node, ast.UnaryOp):
        return _UNARY[type(node.op)](_eval_node(node.operand, arrays, diagnostics, n_events))
    if isinstance(node, ast.BinOp):
        return _BINOPS[type(node.op)](
            _eval_node(node.left, arrays, diagnostics, n_events),
            _eval_node(node.right, arrays, diagnostics, n_events),
        )
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, arrays, diagnostics, n_events)
        result = True
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval_node(comparator, arrays, diagnostics, n_events)
            result = np.logical_and(result, _COMPARE[type(op)](left, right))
            left = right
        return result
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_CALLS:
            name = getattr(node.func, "id", type(node.func).__name__)
            raise ValueError(f"función no permitida: '{name}'")
        if node.func.id == _LEADING:
            if len(node.args) != 3:
                raise ValueError(
                    f"'leading()' necesita exactamente tres argumentos "
                    f"(values, order, mask); recibió {len(node.args)}"
                )
            values, order, mask = (
                _eval_node(arg, arrays, diagnostics, n_events) for arg in node.args
            )
            return _leading(
                values,
                order,
                mask,
                ", ".join(_label(arg) for arg in node.args),
                diagnostics,
                n_events,
            )
        if node.func.id in _REDUCTIONS:
            if len(node.args) != 1:
                raise ValueError(
                    f"'{node.func.id}()' necesita exactamente un argumento; "
                    f"recibió {len(node.args)}"
                )
            operand = _eval_node(node.args[0], arrays, diagnostics, n_events)
            return _reduction(
                node.func.id,
                operand,
                _label(node.args[0]),
                diagnostics,
                n_events,
            )
        args = [_eval_node(arg, arrays, diagnostics, n_events) for arg in node.args]
        try:
            return _FUNCTIONS[node.func.id](*args)
        except TypeError as exc:
            raise ValueError(
                f"argumentos no válidos para '{node.func.id}()': {exc}"
            ) from exc
    raise ValueError(f"expresión no permitida: {type(node).__name__}")


def _to_numpy(result):
    """Convierte el resultado de una expresión a numpy; rechaza listas por evento."""
    import awkward as ak

    if isinstance(result, ak.Array):
        try:
            result = ak.to_numpy(result)
        except Exception as exc:
            raise ValueError(
                "la expresión devuelve una lista por evento; redúcela con "
                "any(...), all(...), count(...) o max(...)"
            ) from exc
    return result


def _to_mask(result, n_events: int) -> np.ndarray:
    """Convierte el resultado de una expresión en una máscara booleana de n_events."""
    result = _to_numpy(result)
    if isinstance(result, (bool, np.bool_)):
        return np.full(int(n_events), bool(result), dtype=bool)
    arr = np.asarray(result)
    if arr.ndim == 0:
        if arr.dtype != np.bool_:
            raise ValueError(
                f"la expresión debe devolver un booleano por evento (tipo {arr.dtype})"
            )
        return np.full(int(n_events), bool(arr), dtype=bool)
    if arr.ndim != 1 or arr.shape[0] != int(n_events):
        raise ValueError(
            f"la expresión devuelve forma {arr.shape}; se esperaba ({int(n_events)},)"
        )
    if arr.dtype != np.bool_:
        raise ValueError(
            f"la expresión debe devolver un booleano por evento (tipo {arr.dtype})"
        )
    return arr.astype(bool, copy=False)


def _eval_expression(
    tree: ast.Expression,
    arrays: dict,
    n_events: int,
    diagnostics: Diagnostics | None = None,
):
    """Evalúa un AST validado y devuelve el valor crudo (numpy o awkward)."""
    diagnostics = diagnostics if diagnostics is not None else Diagnostics()
    with np.errstate(divide="ignore", invalid="ignore"):
        return _eval_node(tree.body, arrays, diagnostics, int(n_events))


def _eval_parsed(
    tree: ast.Expression,
    arrays: dict,
    n_events: int,
    diagnostics: Diagnostics | None = None,
):
    """Evalúa un AST ya validado y devuelve una máscara booleana de n_events."""
    return _to_mask(_eval_expression(tree, arrays, n_events, diagnostics), n_events)


def evaluate_raw(expression, arrays: dict, n_events=None, diagnostics=None):
    """Evalúa una expresión restringida sin convertir a numpy ni forzar booleano.

    Necesario para ``hist --mode object``: la observable sigue siendo una lista por evento.
    """
    tree = _parse_expression(expression)
    if n_events is None:
        n_events = len(next(iter(arrays.values()))) if arrays else 1
    return _eval_expression(tree, arrays, int(n_events), diagnostics)


def evaluate(expression, arrays: dict, n_events=None, diagnostics=None):
    """Evalúa una expresión restringida y devuelve el resultado sin forzar booleano.

    Útil para ``hist`` (p. ej. ``count(Muon_pt > 20)`` devuelve un entero por evento).
    Los avisos de reducciones se acumulan en ``diagnostics`` si se pasa uno.
    """
    return _to_numpy(evaluate_raw(expression, arrays, n_events, diagnostics))


def evaluate_expression(expression, arrays: dict, n_events=None, diagnostics=None) -> np.ndarray:
    """Evalúa una expresión restringida contra arrays y devuelve la máscara booleana."""
    tree = _parse_expression(expression)
    if n_events is None:
        n_events = len(next(iter(arrays.values()))) if arrays else 1
    return _eval_parsed(tree, arrays, int(n_events), diagnostics)


def load_cuts(path) -> list:
    """Carga y valida cuts.json: lista de {name, expression, source} con fuente real."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"el archivo de cortes no existe: {p}")
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"el archivo de cortes no es JSON válido: {exc}") from exc
    if isinstance(payload, dict):
        payload = payload.get("cuts")
        if payload is None:
            raise ValueError(
                "el JSON de cortes debe ser una lista o un objeto con la clave 'cuts'"
            )
    if not isinstance(payload, list):
        raise ValueError("el JSON de cortes debe ser una lista")

    cuts = []
    seen = set()
    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict):
            raise ValueError(f"el corte #{index} no es un objeto")
        for key in ("name", "expression", "source"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"el corte #{index} no tiene '{key}' (texto no vacío)")
        name = item["name"].strip()
        if name in seen:
            raise ValueError(f"nombre de corte duplicado: '{name}'")
        seen.add(name)
        source = item["source"].strip()
        if source.lower() in _BAD_SOURCES:
            raise ValueError(
                f"el corte '{name}' necesita una fuente real, no '{source}'"
            )
        cuts.append(
            {
                "name": name,
                "expression": item["expression"].strip(),
                "source": source,
            }
        )
    return cuts


def _detect_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".root":
        return "root"
    if suffix == ".parquet":
        return "parquet"
    raise ValueError(f"formato no soportado: '{path}' (usa .root o .parquet)")


def _check_array(array, branch: str) -> np.ndarray:
    arr = np.asarray(array)
    if arr.ndim != 1:
        raise TypeError(
            f"la rama '{branch}' no es escalar (ndim={arr.ndim}); usa any/all/count/max para reducirla"
        )
    if not (np.issubdtype(arr.dtype, np.number) or np.issubdtype(arr.dtype, np.bool_)):
        raise TypeError(f"la rama '{branch}' no es numérica (tipo {arr.dtype})")
    return arr


def _check_jagged(array, branch: str):
    """Valida que una rama jagged sea numérica o booleana y la devuelve sin aplanar."""
    primitive = _inner_primitive(array)
    if not _is_numeric_primitive(primitive):
        raise TypeError(
            f"la rama '{branch}' no es numérica (tipo {primitive or '?'}); "
            "no se puede usar en reducciones ni en hist"
        )
    return array


def _prepare_root_array(values, branch: str):
    """Convierte una rama ROOT: escalar → numpy 1D; jagged → awkward (sin aplanar)."""
    import awkward as ak

    if isinstance(values, ak.Array) and values.ndim > 1:
        return _check_jagged(values, branch)
    return _awkward_to_numpy(values, branch)


def _awkward_to_numpy(values, branch: str) -> np.ndarray:
    import awkward as ak

    try:
        array = ak.to_numpy(values)
    except Exception as exc:
        raise TypeError(
            f"la rama '{branch}' es vectorial o irregular; usa --mode object en hist "
            "o redúcela con any/all/count/max"
        ) from exc
    return _check_array(array, branch)


def _read_root(path: Path, tree, names: list):
    import uproot

    if not path.is_file():
        raise FileNotFoundError(f"el archivo ROOT no existe: {path}")
    try:
        handle = uproot.open(path)
    except Exception as exc:
        raise ValueError(f"no se pudo abrir '{path}' como ROOT: {exc}") from exc
    with handle:
        tree_name = str(tree).split(";")[0]
        available = [
            key.split(";")[0]
            for key, klass in handle.classnames().items()
            if klass in ("TTree", "TNtuple")
        ]
        if tree_name not in available:
            raise KeyError(
                f"no existe el árbol '{tree_name}' en {path.name}; árboles: {available}"
            )
        obj = handle[tree_name]
        n_events = int(obj.num_entries)
        if not names:
            return {}, n_events
        branches = list(obj.keys())
        missing = [name for name in names if name not in branches]
        if missing:
            raise KeyError(
                f"la(s) rama(s) {missing} no existen en '{tree_name}'; ramas: {branches}"
            )
        arrays = obj.arrays(names, library="ak")
        return {name: _prepare_root_array(arrays[name], name) for name in names}, n_events


def _read_parquet(path: Path, names: list):
    import pyarrow.parquet as pq

    if not path.is_file():
        raise FileNotFoundError(f"el archivo Parquet no existe: {path}")
    parquet = pq.ParquetFile(path)
    n_events = int(parquet.metadata.num_rows)
    if not names:
        return {}, n_events
    available = list(parquet.schema_arrow.names)
    missing = [name for name in names if name not in available]
    if missing:
        raise KeyError(f"la(s) columna(s) {missing} no existen; columnas: {available}")
    table = pq.read_table(path, columns=names)
    arrays = {}
    for name in names:
        column = table.column(name)
        if column.null_count:
            raise ValueError(
                f"la columna '{name}' tiene {column.null_count} nulos; no se admiten nulos"
            )
        values = column.to_numpy(zero_copy_only=False)
        if getattr(values, "dtype", None) == object:
            import awkward as ak

            arrays[name] = _check_jagged(ak.from_arrow(column), name)
        else:
            arrays[name] = _check_array(values, name)
    return arrays, n_events


def _write_json(path, payload: dict):
    p = Path(path)
    if p.exists() and p.is_dir():
        raise IsADirectoryError(f"la ruta de salida es un directorio: {p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def select(inputs, cuts_path, tree=None, label=None, out=None) -> dict:
    """Aplica cortes en orden a uno o varios inputs y devuelve el cutflow."""
    raw_inputs = [inputs] if isinstance(inputs, (str, Path)) else list(inputs)
    paths = [Path(item) for item in raw_inputs]
    if not paths:
        raise ValueError("se necesita al menos un input ROOT o Parquet")
    if out is not None and not str(out).strip():
        raise ValueError("--out no puede estar vacío")

    formats = {_detect_format(path) for path in paths}
    if len(formats) != 1:
        raise ValueError(
            "todos los inputs deben ser del mismo formato (todos .root o todos .parquet)"
        )
    fmt = formats.pop()

    tree_name = None
    if fmt == "root":
        if tree is None or not str(tree).strip():
            raise ValueError("--tree es obligatorio para archivos ROOT")
        tree_name = str(tree).strip()
    elif tree is not None and str(tree).strip():
        raise ValueError("--tree solo aplica a archivos ROOT")

    cuts = load_cuts(cuts_path)
    parsed = []
    branch_names = set()
    for cut in cuts:
        expression_tree = _parse_expression(cut["expression"])
        names = _collect_names(expression_tree)
        parsed.append((cut, expression_tree, names))
        branch_names |= names
    branch_names = sorted(branch_names)

    counts = [0] * len(cuts)
    total_events = 0
    event_counts = []
    diagnostics = Diagnostics()
    for path in paths:
        if fmt == "root":
            arrays, n_events = _read_root(path, tree_name, branch_names)
        else:
            arrays, n_events = _read_parquet(path, branch_names)
        total_events += n_events
        event_counts.append({"input": str(path), "events": n_events})
        mask = np.ones(n_events, dtype=bool)
        for index, (_, expression_tree, _) in enumerate(parsed):
            mask = np.logical_and(
                mask, _eval_parsed(expression_tree, arrays, n_events, diagnostics)
            )
            counts[index] += int(mask.sum())

    cuts_out = []
    previous = total_events
    for cut, passed in zip(cuts, counts):
        cuts_out.append(
            {
                "name": cut["name"],
                "expression": cut["expression"],
                "source": cut["source"],
                "passed": passed,
                "relative_efficiency": (passed / previous) if previous else 0.0,
                "cumulative_efficiency": (passed / total_events)
                if total_events
                else 0.0,
            }
        )
        previous = passed

    warnings = []
    if not cuts:
        warnings.append("sin cortes: el cutflow solo cuenta el total de eventos")
    if total_events == 0:
        warnings.append("los inputs no tienen eventos")
    warnings.extend(
        f"el input '{item['input']}' no tiene eventos"
        for item in event_counts
        if item["events"] == 0
    )
    warnings.extend(diagnostics.warnings())

    result = {
        "label": str(label).strip()
        if label is not None and str(label).strip()
        else "+".join(path.stem for path in paths),
        "format": fmt,
        "tree": tree_name,
        "inputs": [str(path) for path in paths],
        "event_counts": event_counts,
        "total_events": total_events,
        "cuts": cuts_out,
        "final_events": counts[-1] if cuts else total_events,
        "branches_used": branch_names,
        "warnings": warnings,
    }
    if out is not None:
        _write_json(out, result)
    return result


def _hist_format_and_tree(paths, tree):
    """Formato común de los inputs y nombre de árbol validado."""
    formats = {_detect_format(path) for path in paths}
    if len(formats) != 1:
        raise ValueError(
            "todos los inputs deben ser del mismo formato (todos .root o todos .parquet)"
        )
    fmt = formats.pop()
    if fmt == "root":
        if tree is None or not str(tree).strip():
            raise ValueError("--tree es obligatorio para archivos ROOT")
        return fmt, str(tree).strip()
    if tree is not None and str(tree).strip():
        raise ValueError("--tree solo aplica a archivos ROOT")
    return fmt, None


def _hist_range(range_) -> tuple:
    """Valida --range y devuelve (lo, hi) finitos con lo < hi."""
    try:
        lo, hi = (float(range_[0]), float(range_[1]))
    except (TypeError, ValueError, IndexError) as exc:
        raise ValueError("--range necesita dos números: --range LO HI") from exc
    if not (np.isfinite(lo) and np.isfinite(hi)):
        raise ValueError(f"--range debe ser finito, recibido: [{lo}, {hi}]")
    if lo >= hi:
        raise ValueError(f"--range necesita LO < HI, recibido: [{lo}, {hi}]")
    return lo, hi


def _hist_object_cut(object_cut, object_source, mode):
    """Valida --object-cut/--object-source y devuelve el AST del corte por objeto."""
    if object_cut is None and object_source is None:
        return None
    if object_cut is None:
        raise ValueError("--object-source requiere --object-cut")
    if object_source is None or not str(object_source).strip():
        raise ValueError("--object-cut requiere --object-source (fuente no vacía)")
    source = str(object_source).strip()
    if source.lower() in _BAD_SOURCES:
        raise ValueError(
            f"--object-cut necesita una fuente real, no '{source}'"
        )
    if mode != "object":
        raise ValueError("--object-cut solo aplica a --mode object")
    tree = _parse_expression(object_cut)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and (node.func.id in _REDUCTIONS or node.func.id == _LEADING)
        ):
            raise ValueError(
                f"--object-cut no admite '{node.func.id}()': "
                "el corte es por objeto, no por evento"
            )
    return tree


def _hist_values(values, mask, n_events, mode, object_mask=None):
    """Valores que entran al histograma (evento u objeto) y sus estadísticas.

    Devuelve ``(valores, objetos_por_evento, stats)``. ``stats`` solo se rellena
    con ``object_mask`` (``--object-cut``): objetos antes/después y eventos sin objetos.
    """
    import awkward as ak

    if mode == "event":
        try:
            flat = _to_numpy(values)
        except ValueError as exc:
            raise ValueError(
                "en --mode event la observable debe ser escalar por evento; "
                "para ramas jagged usa --mode object"
            ) from exc
        if np.isscalar(flat) or np.asarray(flat).ndim == 0:
            flat = np.full(n_events, float(flat))
        arr = np.asarray(flat)
        if arr.ndim != 1 or arr.shape[0] != n_events:
            raise ValueError(
                f"la observable devuelve forma {arr.shape}; se esperaba ({n_events},)"
            )
        return arr[mask], None, None

    if not isinstance(values, ak.Array) or values.ndim != 2:
        raise ValueError(
            "--mode object necesita una observable jagged (una lista por evento)"
        )
    selected = values[mask]
    stats = None
    if object_mask is not None:
        if not isinstance(object_mask, ak.Array) or object_mask.ndim != 2:
            raise ValueError(
                "--object-cut debe devolver una máscara booleana por objeto "
                "(una lista por evento)"
            )
        selected_mask = object_mask[mask]
        if _inner_primitive(selected_mask) != "bool":
            raise ValueError(
                "--object-cut debe devolver un booleano por objeto "
                f"(tipo {_inner_primitive(selected_mask) or '?'})"
            )
        counts = np.asarray(ak.num(selected, axis=1), dtype=np.int64)
        mask_counts = np.asarray(ak.num(selected_mask, axis=1), dtype=np.int64)
        if not np.array_equal(counts, mask_counts):
            raise ValueError(
                "--object-cut no usa la misma colección que la observable: "
                "el número de objetos por evento no coincide"
            )
        selected = selected[selected_mask]
        per_event = np.asarray(ak.num(selected, axis=1), dtype=np.int64)
        stats = {
            "objects_before": int(counts.sum()),
            "objects_after": int(per_event.sum()),
            "events_without_objects": int((per_event == 0).sum()),
        }
    else:
        per_event = np.asarray(ak.num(selected, axis=1), dtype=np.int64)
    try:
        flat = ak.to_numpy(ak.flatten(selected, axis=1))
    except Exception as exc:  # listas con None o tipos no numéricos
        raise ValueError(
            f"no se puede aplanar la observable en --mode object: {exc}"
        ) from exc
    return np.asarray(flat), per_event, stats


def hist(
    inputs,
    observable,
    bins,
    range_,
    tree=None,
    mode="event",
    selection=None,
    cuts_path=None,
    weights=None,
    normalize="none",
    object_cut=None,
    object_source=None,
    label=None,
    out=None,
) -> dict:
    """Llena un histograma con selección y pesos, por evento o por objeto.

    ``mode="event"``: un valor por evento (la observable debe ser escalar).
    ``mode="object"``: un valor por objeto; la observable debe ser una lista por evento.
    ``object_cut``: máscara booleana por objeto de la misma colección (solo ``mode="object"``);
    exige ``object_source`` con la fuente del corte.
    ``normalize="none"`` devuelve los recuentos con peso; ``"area"`` escala el
    histograma (bins y flujos) para que la suma en rango sea 1.
    """
    raw_inputs = [inputs] if isinstance(inputs, (str, Path)) else list(inputs)
    paths = [Path(item) for item in raw_inputs]
    if not paths:
        raise ValueError("se necesita al menos un input ROOT o Parquet")
    if out is not None and not str(out).strip():
        raise ValueError("--out no puede estar vacío")
    if mode not in ("event", "object"):
        raise ValueError(f"--mode no válido: '{mode}' (usa event u object)")
    if normalize not in ("none", "area"):
        raise ValueError(f"--normalize no válido: '{normalize}' (usa none o area)")
    try:
        n_bins = int(bins)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"--bins debe ser un entero >= 1, recibido: {bins!r}") from exc
    if n_bins < 1:
        raise ValueError(f"--bins debe ser un entero >= 1, recibido: {n_bins}")
    lo, hi = _hist_range(range_)
    fmt, tree_name = _hist_format_and_tree(paths, tree)
    object_cut_tree = _hist_object_cut(object_cut, object_source, mode)

    observable_tree = _parse_expression(observable)
    branch_names = set(_collect_names(observable_tree))
    if object_cut_tree is not None:
        branch_names |= _collect_names(object_cut_tree)
    selection_tree = None
    if selection is not None and str(selection).strip():
        selection_tree = _parse_expression(selection)
        branch_names |= _collect_names(selection_tree)
    weights_tree = None
    if weights is not None and str(weights).strip():
        weights_tree = _parse_expression(weights)
        branch_names |= _collect_names(weights_tree)
    cuts = load_cuts(cuts_path) if cuts_path is not None else []
    parsed_cuts = []
    for cut in cuts:
        cut_tree = _parse_expression(cut["expression"])
        branch_names |= _collect_names(cut_tree)
        parsed_cuts.append((cut, cut_tree))
    branch_names = sorted(branch_names)

    edges = np.linspace(lo, hi, n_bins + 1)
    counts = np.zeros(n_bins, dtype=float)
    sumw2 = np.zeros(n_bins, dtype=float)
    flows = {"underflow": 0.0, "overflow": 0.0, "nan": 0.0}
    flows_sumw2 = {"underflow": 0.0, "overflow": 0.0, "nan": 0.0}
    nan_entries = 0
    diagnostics = Diagnostics()
    total_events = 0
    selected_events = 0
    entries = 0
    sumw = 0.0
    objects_before = 0
    objects_after = 0
    events_without_objects = 0

    for path in paths:
        if fmt == "root":
            arrays, n_events = _read_root(path, tree_name, branch_names)
        else:
            arrays, n_events = _read_parquet(path, branch_names)
        total_events += n_events

        mask = np.ones(n_events, dtype=bool)
        for _, cut_tree in parsed_cuts:
            mask = np.logical_and(
                mask, _eval_parsed(cut_tree, arrays, n_events, diagnostics)
            )
        if selection_tree is not None:
            mask = np.logical_and(
                mask, _eval_parsed(selection_tree, arrays, n_events, diagnostics)
            )
        selected_events += int(mask.sum())

        raw_values = _eval_expression(
            observable_tree, arrays, n_events, diagnostics
        )
        object_mask = None
        if object_cut_tree is not None:
            object_mask = _eval_expression(
                object_cut_tree, arrays, n_events, diagnostics
            )
        values, per_event, object_stats = _hist_values(
            raw_values, mask, n_events, mode, object_mask
        )
        if object_stats is not None:
            objects_before += object_stats["objects_before"]
            objects_after += object_stats["objects_after"]
            events_without_objects += object_stats["events_without_objects"]

        if weights_tree is not None:
            raw_weights = _to_numpy(
                _eval_expression(weights_tree, arrays, n_events, diagnostics)
            )
            weight_values = np.asarray(raw_weights, dtype=float)
            if weight_values.ndim == 0:
                weight_values = np.full(n_events, float(weight_values))
            if weight_values.shape != (n_events,):
                raise ValueError(
                    f"los pesos devuelven forma {weight_values.shape}; "
                    f"se esperaba ({n_events},)"
                )
            if not np.isfinite(weight_values).all():
                raise ValueError("los pesos deben ser finitos (sin NaN ni inf)")
        else:
            weight_values = np.ones(n_events, dtype=float)

        if mode == "object":
            weights_per_value = np.repeat(weight_values[mask], per_event)
        else:
            weights_per_value = weight_values[mask]

        values = np.asarray(values, dtype=float)
        if values.shape != weights_per_value.shape:
            raise ValueError(
                f"valores y pesos tienen formas distintas: {values.shape} y "
                f"{weights_per_value.shape}"
            )

        is_nan = np.isnan(values)
        nan_weights = weights_per_value[is_nan]
        nan_entries += int(is_nan.sum())
        flows["nan"] += float(nan_weights.sum())
        flows_sumw2["nan"] += float((nan_weights ** 2).sum())

        values = values[~is_nan]
        weights_per_value = weights_per_value[~is_nan]
        under = values < lo
        over = values >= hi
        inside = ~(under | over)
        flows["underflow"] += float(weights_per_value[under].sum())
        flows["overflow"] += float(weights_per_value[over].sum())
        flows_sumw2["underflow"] += float((weights_per_value[under] ** 2).sum())
        flows_sumw2["overflow"] += float((weights_per_value[over] ** 2).sum())
        if inside.any():
            chunk, _ = np.histogram(values[inside], bins=edges, weights=weights_per_value[inside])
            chunk2, _ = np.histogram(
                values[inside], bins=edges, weights=weights_per_value[inside] ** 2
            )
            counts += chunk
            sumw2 += chunk2

        entries += int(values.size + is_nan.sum())
        sumw += float(weights_per_value.sum() + nan_weights.sum())

    warnings = diagnostics.warnings()
    if total_events == 0:
        warnings.append("los inputs no tienen eventos")
    if selected_events == 0:
        warnings.append("ningún evento pasa la selección")
    if entries == 0:
        warnings.append("el histograma está vacío: no hay entradas")
    if nan_entries:
        warnings.append(
            f"{nan_entries} entradas con NaN excluidas de los bins "
            "(contadas en bins.nan, no en underflow/overflow)"
        )
    if object_cut_tree is not None and events_without_objects:
        warnings.append(
            f"--object-cut: {events_without_objects} de {selected_events} eventos "
            "seleccionados sin objetos que pasen el corte"
        )

    scale = 1.0
    if normalize == "area":
        integral = float(counts.sum())
        if integral != 0.0 and np.isfinite(integral):
            scale = 1.0 / integral
        else:
            warnings.append(
                "no se puede normalizar a área (suma de pesos en rango = 0); "
                "se devuelven los recuentos sin escalar"
            )

    if scale != 1.0:
        counts = counts * scale
        sumw2 = sumw2 * scale * scale
        flows = {key: value * scale for key, value in flows.items()}
        flows_sumw2 = {key: value * scale * scale for key, value in flows_sumw2.items()}
        sumw *= scale

    result = {
        "label": str(label).strip()
        if label is not None and str(label).strip()
        else "+".join(path.stem for path in paths),
        "format": fmt,
        "tree": tree_name,
        "inputs": [str(path) for path in paths],
        "mode": mode,
        "observable": str(observable).strip(),
        "selection": str(selection).strip()
        if selection is not None and str(selection).strip()
        else None,
        "cuts": cuts,
        "weights": str(weights).strip()
        if weights is not None and str(weights).strip()
        else None,
        "object_cut": None
        if object_cut_tree is None
        else {
            "expression": str(object_cut).strip(),
            "source": str(object_source).strip(),
            "events_without_objects": events_without_objects,
            "objects_before": objects_before,
            "objects_after": objects_after,
        },
        "normalize": normalize,
        "events": total_events,
        "selected_events": selected_events,
        "entries": entries,
        "sumw": float(sumw),
        "scale": float(scale),
        "bins": {
            "count": n_bins,
            "range": [lo, hi],
            "edges": [float(edge) for edge in edges],
            "counts": [float(value) for value in counts],
            "underflow": float(flows["underflow"]),
            "overflow": float(flows["overflow"]),
            "nan": float(flows["nan"]),
        },
        "sumw2": {
            "counts": [float(value) for value in sumw2],
            "underflow": float(flows_sumw2["underflow"]),
            "overflow": float(flows_sumw2["overflow"]),
            "nan": float(flows_sumw2["nan"]),
        },
        "warnings": warnings,
    }
    if out is not None:
        _write_json(out, result)
    return result
