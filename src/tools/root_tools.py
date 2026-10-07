"""Lectura exploratoria de archivos ROOT (ntuples) con uproot, sin PyROOT."""
from pathlib import Path

import awkward as ak
import uproot

_TREE_CLASSES = ("TTree", "TNtuple")


def _require_file(path) -> Path:
    """Devuelve el Path y falla con un error claro si el archivo no existe."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"el archivo ROOT no existe: {p}")
    return p


def _open(path):
    """Abre el archivo ROOT convirtiendo cualquier fallo en un error claro."""
    p = _require_file(path)
    try:
        return uproot.open(p)
    except Exception as exc:  # uproot usa excepciones distintas según el fichero
        raise ValueError(f"no se pudo abrir '{p}' como archivo ROOT: {exc}") from exc


def _tree_names(file) -> list:
    """Nombres de los árboles del archivo abierto (sin número de ciclo)."""
    nombres = (
        key.split(";")[0]
        for key, clase in file.classnames().items()
        if clase in _TREE_CLASSES
    )
    return list(dict.fromkeys(nombres))


def _get_tree(file, path, tree):
    """Devuelve el árbol pedido o un KeyError claro con los árboles disponibles."""
    name = str(tree).split(";")[0]
    nombres = _tree_names(file)
    if name not in nombres:
        raise KeyError(
            f"no existe el árbol '{name}' en {Path(path).name}; árboles: {nombres}"
        )
    return file[name]


def _flatten(values) -> list:
    """Aplana listas anidadas (p. ej. ramas vectoriales) en una lista plana."""
    plano = []
    for v in values:
        if isinstance(v, (list, tuple)):
            plano.extend(_flatten(v))
        else:
            plano.append(v)
    return plano


def _check_branches(tree, branches) -> list:
    """Valida que las ramas existan y devuelve sus nombres."""
    if isinstance(branches, str):
        branches = [branches]
    nombres = [str(b) for b in branches]
    disponibles = list(tree.keys())
    faltan = [b for b in nombres if b not in disponibles]
    if faltan:
        raise KeyError(f"la(s) rama(s) {faltan} no existen; ramas: {disponibles}")
    return nombres


def list_trees(path) -> list:
    """Lista los nombres de los árboles del archivo ROOT."""
    with _open(path) as file:
        return _tree_names(file)


def list_branches(path, tree) -> dict:
    """Dict {rama: tipo} con las ramas del árbol indicado."""
    with _open(path) as file:
        t = _get_tree(file, path, tree)
        return dict(t.typenames())


def read_sample(path, tree, branches, n=1000) -> dict:
    """Primeros n eventos como dict {rama: lista}."""
    if n < 0:
        raise ValueError(f"n debe ser >= 0, recibido: {n}")
    with _open(path) as file:
        t = _get_tree(file, path, tree)
        nombres = _check_branches(t, branches)
        stop = min(int(n), int(t.num_entries))
        arrays = t.arrays(nombres, entry_start=0, entry_stop=stop, library="ak")
        return {b: ak.to_list(arrays[b]) for b in nombres}


def branch_summary(path, tree, branch, n=100000) -> dict:
    """Min, max, media (mean) y nº de eventos leídos sobre las primeras n entradas."""
    if n < 0:
        raise ValueError(f"n debe ser >= 0, recibido: {n}")
    with _open(path) as file:
        t = _get_tree(file, path, tree)
        name = _check_branches(t, branch)[0]
        stop = min(int(n), int(t.num_entries))
        data = t.arrays([name], entry_start=0, entry_stop=stop, library="ak")[name]
        events = len(data)
        try:
            values = [float(v) for v in _flatten(ak.to_list(data))]
        except (TypeError, ValueError) as exc:
            raise TypeError(f"la rama '{name}' no es numérica: {exc}") from exc
        return {
            "branch": name,
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "mean": sum(values) / len(values) if values else None,
            "events": events,
        }
