"""Lectura exploratoria de archivos Parquet (solo pyarrow)."""
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

IS_NUMERIC = (pa.types.is_integer, pa.types.is_floating, pa.types.is_decimal)


def _require_file(path) -> Path:
    """Devuelve el Path y falla con un error claro si el archivo no existe."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"el archivo Parquet no existe: {p}")
    return p


def list_columns(path) -> list:
    """Lista los nombres de las columnas del archivo."""
    schema = pq.ParquetFile(_require_file(path)).schema_arrow
    return list(schema.names)


def describe_file(path) -> dict:
    """Nº de filas, nº de columnas y tipo de cada columna."""
    pf = pq.ParquetFile(_require_file(path))
    schema = pf.schema_arrow
    names = list(schema.names)
    return {
        "rows": pf.metadata.num_rows,
        "columns": len(names),
        "column_names": names,
        "types": {name: str(schema.field(name).type) for name in names},
    }


def read_sample(path, n: int = 5) -> list:
    """Primeras n filas del archivo como lista de dicts."""
    if n < 0:
        raise ValueError(f"n debe ser >= 0, recibido: {n}")
    table = pq.read_table(_require_file(path))
    return table.slice(0, n).to_pylist()


def column_summary(path, column: str) -> dict:
    """Min, max, media y nº de nulos de una columna numérica."""
    p = _require_file(path)
    names = list(pq.ParquetFile(p).schema_arrow.names)
    if column not in names:
        raise KeyError(f"la columna '{column}' no está en {p.name}; columnas: {names}")

    col = pq.read_table(p, columns=[column]).column(column)
    numeric = any(is_type(col.type) for is_type in IS_NUMERIC)
    summary = {
        "column": column,
        "type": str(col.type),
        "numeric": numeric,
        "rows": len(col),
        "nulls": col.null_count,
        "min": None,
        "max": None,
        "mean": None,
    }
    if numeric and col.null_count < len(col):
        summary["min"] = pc.min(col).as_py()
        summary["max"] = pc.max(col).as_py()
        summary["mean"] = pc.mean(pc.cast(col, pa.float64())).as_py()
    return summary
