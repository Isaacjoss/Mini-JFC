#!/usr/bin/env python3
"""mjfc: CLI JSON sobre src/tools/ para que agentes LLM llamen las tools por shell.

Reglas de salida:
  * stdout: SIEMPRE JSON (`json.dumps(..., ensure_ascii=False)`), salvo en `--help`.
  * stderr + exit code 1: cualquier error, con un mensaje claro (prefijo "mjfc").
  * las listas con más de `--max-items` (defecto 20) elementos se recortan y se
    añade {"truncated": true, "total": N} para no gastar tokens.
La raíz del repo se añade a sys.path, así que funciona ejecutado desde cualquier carpeta.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.tools import cms_tools, literature_tools, web_tools  # noqa: E402

try:  # pyarrow (requirements.txt): opcional para el resto de comandos
    from src.tools import parquet_tools
except ImportError:  # pragma: no cover
    parquet_tools = None

try:  # uproot+awkward (requirements.txt): opcionales para el resto de comandos
    from src.tools import root_tools
except ImportError:  # pragma: no cover
    root_tools = None

try:  # numpy (dependencia de awkward): necesario para analysis
    from src.tools import analysis_tools
except ImportError:  # pragma: no cover
    analysis_tools = None

DEFAULT_MAX_ITEMS = 20
# Listas que forman parte del resultado de una tool y no deben recortarse con --max-items.
_PROTECTED_KEYS = frozenset(
    {"cuts", "inputs", "event_counts", "branches_used", "bins", "sumw2"}
)


# ---------------------------------------------------------------- utilidades


class _ArgumentParser(argparse.ArgumentParser):
    """ArgumentParser que reporta errores de uso en stderr con exit code 1 (no 2)."""

    def error(self, message: str):
        self.exit(1, f"{self.prog}: error: {message}\n")


def _require(module, name: str):
    """Devuelve el módulo de tools o un error claro si le falta una dependencia."""
    if module is None:
        raise RuntimeError(
            f"el módulo {name} no está disponible: falta una dependencia (ver requirements.txt)"
        )
    return module


def _truncate(result, max_items: int):
    """Recorta a max_items las listas largas (suelta o valores de un dict) y añade truncated/total."""
    if isinstance(result, list):
        if len(result) > max_items:
            return {"items": result[:max_items], "truncated": True, "total": len(result)}
        return result
    if isinstance(result, dict):
        out, total, truncated = {}, 0, False
        for key, value in result.items():
            if key in _PROTECTED_KEYS:
                out[key] = value
            elif isinstance(value, list) and len(value) > max_items:
                out[key] = value[:max_items]
                total = max(total, len(value))
                truncated = True
            else:
                out[key] = value
        if truncated:
            out["truncated"] = True
            out["total"] = total
        return out
    return result


def _emit(result, max_items: int) -> str:
    """JSON listo para stdout (sin gastar tokens en escapes ASCII)."""
    return json.dumps(_truncate(result, max_items), ensure_ascii=False)


# ---------------------------------------------------------------- handlers lit


def _lit_arxiv(args):
    kwargs = {"max_results": args.n}
    if args.cat:
        kwargs["cat"] = args.cat
    return literature_tools.search_arxiv(args.query, **kwargs)


def _lit_inspire(args):
    return literature_tools.search_inspire(args.query, max_results=args.n)


def _lit_fetch(args):
    return literature_tools.fetch_arxiv_text(args.arxiv_id, args.dest_dir)


def _lit_log(args):
    return literature_tools.log_retrieval(
        args.log_path, args.kind, args.source, args.local_path, args.reason
    )


# ---------------------------------------------------------------- handlers cms


def _cms_search(args):
    return cms_tools.search_records(args.query, max_results=args.n)


def _cms_record(args):
    return cms_tools.get_record(args.recid)


def _cms_files(args):
    return cms_tools.list_files(args.recid)


def _cms_download(args):
    kwargs = {"confirm": args.confirm}
    if args.max_bytes is not None:
        kwargs["max_bytes"] = args.max_bytes
    return cms_tools.download_file(args.uri, args.dest_dir, **kwargs)


# ---------------------------------------------------------------- handlers web


def _web_fetch(args):
    return web_tools.fetch_url(args.url, max_chars=args.max_chars)


def _web_save(args):
    return web_tools.save_text(sys.stdin.read(), args.dest_path)


# ---------------------------------------------------------------- handlers root


def _root_trees(args):
    return _require(root_tools, "root_tools").list_trees(args.path)


def _root_branches(args):
    return _require(root_tools, "root_tools").list_branches(args.path, args.tree)


def _root_sample(args):
    branches = [b.strip() for b in args.branches.split(",") if b.strip()]
    if not branches:
        raise ValueError("branches no puede estar vacío: usa una lista separada por comas")
    return _require(root_tools, "root_tools").read_sample(args.path, args.tree, branches, n=args.n)


def _root_summary(args):
    return _require(root_tools, "root_tools").branch_summary(args.path, args.tree, args.branch)


# ----------------------------------------------------------- handlers parquet


def _parquet_columns(args):
    return _require(parquet_tools, "parquet_tools").list_columns(args.path)


def _parquet_describe(args):
    return _require(parquet_tools, "parquet_tools").describe_file(args.path)


def _parquet_sample(args):
    return _require(parquet_tools, "parquet_tools").read_sample(args.path, n=args.n)


def _parquet_summary(args):
    return _require(parquet_tools, "parquet_tools").column_summary(args.path, args.column)


# ---------------------------------------------------------------- handlers analysis


def _analysis_select(args):
    return _require(analysis_tools, "analysis_tools").select(
        args.inputs,
        args.cuts,
        tree=args.tree,
        label=args.label,
        out=args.out,
    )


def _analysis_hist(args):
    return _require(analysis_tools, "analysis_tools").hist(
        args.inputs,
        args.observable,
        args.bins,
        args.range,
        tree=args.tree,
        mode=args.mode,
        selection=args.selection,
        cuts_path=args.cuts,
        weights=args.weights,
        normalize=args.normalize,
        object_cut=args.object_cut,
        object_source=args.object_source,
        label=args.label,
        out=args.out,
    )


# ------------------------------------------------------------------- parser


def _common_options() -> argparse.ArgumentParser:
    """Opciones compartidas: --max-items en la raíz y en cada subcomando (default SUPPRESS)."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--max-items",
        type=int,
        default=argparse.SUPPRESS,
        metavar="N",
        help=f"recorta toda lista a N elementos y añade truncated/total (defecto {DEFAULT_MAX_ITEMS})",
    )
    return parser


def build_parser() -> argparse.ArgumentParser:
    """Parser con subcomandos lit/cms/web/root/parquet; cada help es una línea pensada para un LLM."""
    common = _common_options()
    parser = _ArgumentParser(
        prog="mjfc",
        parents=[common],
        description=(
            "mjfc: ejecuta las tools de src/tools/ por shell. Salida SIEMPRE JSON en stdout "
            "(ensure_ascii=False); los errores van a stderr con exit code 1; las listas largas "
            f"se recortan a --max-items (defecto {DEFAULT_MAX_ITEMS})."
        ),
        epilog="Ejemplos: mjfc lit arxiv 'Higgs tau' -n 3 ; mjfc lit arxiv 'Higgs tau' --cat hep-ex ; "
        "mjfc parquet describe f.parquet ; mjfc --max-items 5 cms search tautau ; "
        "mjfc analysis select f.root --tree events --cuts cuts.json --out cutflow.json ; "
        "mjfc analysis hist f.root --tree events --observable MET_pt --bins 20 --range 0 200",
    )
    modules = parser.add_subparsers(
        dest="module",
        metavar="{lit,cms,web,root,parquet,analysis}",
        required=True,
    )

    # --- lit ---------------------------------------------------------------
    lit = modules.add_parser(
        "lit",
        parents=[common],
        help="Literatura: arXiv/INSPIRE (buscar, descargar PDF, log).",
        description="Literatura: busca en arXiv/INSPIRE, descarga PDFs y registra la recuperación.",
    )
    lit_cmds = lit.add_subparsers(
        dest="action", metavar="{arxiv,inspire,fetch,log}", required=True
    )
    p = lit_cmds.add_parser(
        "arxiv",
        parents=[common],
        help="Busca artículos en arXiv y devuelve una lista JSON de resultados.",
        description=(
            "Busca en la API de arXiv; salida: lista de "
            "{id,title,authors,n_authors,et_al,summary,url,pdf_url} (authors: máx. 3 nombres; "
            'summary: máx. 600 caracteres). Una consulta de texto libre se envía como '
            'all:"palabra" AND all:"palabra"; con prefijos (all:, ti:, abs:, cat:, au:) o '
            "AND/OR se respeta tal cual."
        ),
    )
    p.add_argument(
        "query",
        help='consulta de búsqueda: texto libre (p. ej. "Higgs tau" se busca como '
        'all:"Higgs" AND all:"tau") o con sintaxis arXiv (ti:, abs:, cat:, AND/OR)',
    )
    p.add_argument("-n", type=int, default=5, help="máximo de resultados (defecto 5)")
    p.add_argument(
        "--cat",
        default=None,
        metavar="CATEGORIA",
        help="categoría arXiv que se añade a la consulta como 'AND cat:CATEGORIA' "
        "(ej.: --cat hep-ex)",
    )
    p.set_defaults(func=_lit_arxiv, action="arxiv")

    p = lit_cmds.add_parser(
        "inspire",
        parents=[common],
        help="Busca artículos en INSPIRE y devuelve una lista JSON de resultados.",
        description=(
            "Busca en la API de INSPIRE; salida: lista de "
            "{recid,title,authors,n_authors,et_al,year,arxiv_id,url} (authors: máx. 3 nombres)."
        ),
    )
    p.add_argument("query", help="consulta de búsqueda (lenguaje INSPIRE)")
    p.add_argument("-n", type=int, default=5, help="máximo de resultados (defecto 5)")
    p.set_defaults(func=_lit_inspire, action="inspire")

    p = lit_cmds.add_parser(
        "fetch",
        parents=[common],
        help="Descarga el PDF de un id de arXiv en dest_dir.",
        description="Descarga el PDF de arXiv (id p. ej. 2301.00001) en dest_dir; salida: ruta local.",
    )
    p.add_argument("arxiv_id", help="id de arXiv (sin 'arXiv:')")
    p.add_argument("dest_dir", help="carpeta de destino (se crea si no existe)")
    p.set_defaults(func=_lit_fetch, action="fetch")

    p = lit_cmds.add_parser(
        "log",
        parents=[common],
        help="Añade una fila de auditoría a un retrieval_log.md.",
        description="Registra la descarga en un log Markdown; salida: la fila escrita.",
    )
    p.add_argument("log_path", help="ruta del retrieval_log.md (se crea con su encabezado)")
    p.add_argument("kind", help="tipo de fuente (p. ej. arxiv, cms, web)")
    p.add_argument("source", help="fuente o URL original")
    p.add_argument("local_path", help="ruta local guardada")
    p.add_argument("reason", help="motivo de la recuperación")
    p.set_defaults(func=_lit_log, action="log")

    # --- cms ---------------------------------------------------------------
    cms = modules.add_parser(
        "cms",
        parents=[common],
        help="CMS Open Data: buscar registros, fichas, archivos y descargar.",
        description="CMS Open Data (opendata.cern.ch): búsqueda de datasets, fichas y descargas.",
    )
    cms_cmds = cms.add_subparsers(
        dest="action", metavar="{search,record,files,download}", required=True
    )
    p = cms_cmds.add_parser(
        "search",
        parents=[common],
        help="Busca datasets de CMS y devuelve una lista JSON de resultados.",
        description="Busca registros en opendata.cern.ch; salida: lista de {recid,title,year,collision_energy,url}.",
    )
    p.add_argument("query", help="término de búsqueda (p. ej. tautau)")
    p.add_argument("-n", type=int, default=10, help="máximo de resultados (defecto 10)")
    p.set_defaults(func=_cms_search, action="search")

    p = cms_cmds.add_parser(
        "record",
        parents=[common],
        help="Ficha JSON de un registro CMS (título, año, energía y archivos).",
        description="Detalle de un registro CMS por recid; salida: {recid,title,description,year,collision_energy,files,url}.",
    )
    p.add_argument("recid", help="identificador del registro")
    p.set_defaults(func=_cms_record, action="record")

    p = cms_cmds.add_parser(
        "files",
        parents=[common],
        help="Lista los archivos de un registro CMS.",
        description="Archivos de un registro CMS; salida: lista de {name,size_bytes,uri}.",
    )
    p.add_argument("recid", help="identificador del registro")
    p.set_defaults(func=_cms_files, action="files")

    p = cms_cmds.add_parser(
        "download",
        parents=[common],
        help="Descarga un fichero de CMS en dest_dir (root:// se convierte a https://).",
        description="Descarga un uri de opendata.cern.ch en dest_dir; usa --confirm si supera --max-bytes.",
    )
    p.add_argument("uri", help="uri del fichero (http(s):// o root://)")
    p.add_argument("dest_dir", help="carpeta de destino (se crea si no existe)")
    p.add_argument("--confirm", action="store_true", help="forzar descarga aunque supere --max-bytes")
    p.add_argument(
        "--max-bytes",
        type=int,
        default=None,
        metavar="N",
        help="límite de tamaño en bytes sin confirm (por defecto el de la tool, 500000000)",
    )
    p.set_defaults(func=_cms_download, action="download")

    # --- web ---------------------------------------------------------------
    web = modules.add_parser(
        "web",
        parents=[common],
        help="Web genérica: página a texto plano y guardado desde stdin.",
        description="Web genérica (solo http/https): descarga texto de páginas y guarda texto.",
    )
    web_cmds = web.add_subparsers(dest="action", metavar="{fetch,save}", required=True)
    p = web_cmds.add_parser(
        "fetch",
        parents=[common],
        help="Descarga una URL y devuelve su texto plano sin HTML.",
        description="Descarga una URL http/https; salida: texto plano recortado a --max-chars.",
    )
    p.add_argument("url", help="URL http(s) a descargar")
    p.add_argument(
        "--max-chars",
        type=int,
        default=web_tools.DEFAULT_MAX_CHARS,
        metavar="N",
        help=f"máximo de caracteres del texto (defecto {web_tools.DEFAULT_MAX_CHARS})",
    )
    p.set_defaults(func=_web_fetch, action="fetch")

    p = web_cmds.add_parser(
        "save",
        parents=[common],
        help="Lee texto de stdin y lo guarda en dest_path.",
        description="Guarda el texto que llega por stdin en dest_path (crea carpetas); salida: la ruta escrita.",
    )
    p.add_argument("dest_path", help="ruta del fichero a escribir")
    p.set_defaults(func=_web_save, action="save")

    # --- root --------------------------------------------------------------
    root = modules.add_parser(
        "root",
        parents=[common],
        help="ROOT (uproot): árboles, ramas, muestras de eventos y resúmenes.",
        description="Archivos ROOT con uproot (sin PyROOT): lista árboles/ramas, lee eventos y resume ramas.",
    )
    root_cmds = root.add_subparsers(
        dest="action", metavar="{trees,branches,sample,summary}", required=True
    )
    p = root_cmds.add_parser(
        "trees",
        parents=[common],
        help="Lista los árboles de un archivo ROOT.",
        description="Lista los nombres de los árboles (TTree/TNtuple) de un archivo ROOT.",
    )
    p.add_argument("path", help="ruta del archivo ROOT")
    p.set_defaults(func=_root_trees, action="trees")

    p = root_cmds.add_parser(
        "branches",
        parents=[common],
        help="Dict {rama: tipo} del árbol indicado.",
        description="Ramas de un árbol ROOT; salida: dict {rama: tipo}.",
    )
    p.add_argument("path", help="ruta del archivo ROOT")
    p.add_argument("tree", help="nombre del árbol")
    p.set_defaults(func=_root_branches, action="branches")

    p = root_cmds.add_parser(
        "sample",
        parents=[common],
        help="Primeros eventos como dict {rama: lista}.",
        description="Lee eventos de un árbol ROOT; branches va separada por comas (p. ej. pt,eta).",
    )
    p.add_argument("path", help="ruta del archivo ROOT")
    p.add_argument("tree", help="nombre del árbol")
    p.add_argument("branches", help="ramas separadas por comas (p. ej. pt,eta)")
    p.add_argument("-n", type=int, default=1000, help="máximo de eventos (defecto 1000)")
    p.set_defaults(func=_root_sample, action="sample")

    p = root_cmds.add_parser(
        "summary",
        parents=[common],
        help="Min, max, media y nº de eventos de una rama numérica.",
        description="Resumen estadístico de una rama numérica de un árbol ROOT.",
    )
    p.add_argument("path", help="ruta del archivo ROOT")
    p.add_argument("tree", help="nombre del árbol")
    p.add_argument("branch", help="rama numérica a resumir")
    p.set_defaults(func=_root_summary, action="summary")

    # --- parquet -----------------------------------------------------------
    par = modules.add_parser(
        "parquet",
        parents=[common],
        help="Parquet (pyarrow): columnas, descripción, muestras y resúmenes.",
        description="Archivos Parquet con pyarrow: columnas, descripción, muestra de filas y resumen de columna.",
    )
    par_cmds = par.add_subparsers(
        dest="action", metavar="{columns,describe,sample,summary}", required=True
    )
    p = par_cmds.add_parser(
        "columns",
        parents=[common],
        help="Lista los nombres de las columnas de un Parquet.",
        description="Lista los nombres de las columnas de un archivo Parquet; salida: lista de strings.",
    )
    p.add_argument("path", help="ruta del archivo .parquet")
    p.set_defaults(func=_parquet_columns, action="columns")

    p = par_cmds.add_parser(
        "describe",
        parents=[common],
        help="Nº de filas, nº de columnas y tipo de cada columna.",
        description="Describe un Parquet; salida: {rows,columns,column_names,types}.",
    )
    p.add_argument("path", help="ruta del archivo .parquet")
    p.set_defaults(func=_parquet_describe, action="describe")

    p = par_cmds.add_parser(
        "sample",
        parents=[common],
        help="Primeras n filas de un Parquet como lista de dicts.",
        description="Muestra de filas de un Parquet; salida: lista de dicts {columna: valor}.",
    )
    p.add_argument("path", help="ruta del archivo .parquet")
    p.add_argument("-n", type=int, default=5, help="máximo de filas (defecto 5)")
    p.set_defaults(func=_parquet_sample, action="sample")

    p = par_cmds.add_parser(
        "summary",
        parents=[common],
        help="Min, max, media y nº de nulos de una columna numérica.",
        description="Resumen de una columna de un Parquet; salida: {column,type,numeric,rows,nulls,min,max,mean}.",
    )
    p.add_argument("path", help="ruta del archivo .parquet")
    p.add_argument("column", help="nombre de la columna")
    p.set_defaults(func=_parquet_summary, action="summary")

    # --- analysis ----------------------------------------------------------
    analysis = modules.add_parser(
        "analysis",
        parents=[common],
        help="Análisis: selección (cutflow) e histogramas sobre ROOT/Parquet.",
        description="Análisis: aplica cortes restringidos, cutflows e histogramas con trazabilidad.",
    )
    analysis_cmds = analysis.add_subparsers(
        dest="action", metavar="{select,hist}", required=True
    )
    p = analysis_cmds.add_parser(
        "select",
        parents=[common],
        help="Aplica cortes en orden y produce un cutflow JSON.",
        description=(
            "Aplica una lista de cortes [{name,expression,source}] a uno o varios archivos "
            "ROOT/Parquet del mismo formato; salida: cutflow JSON con passed, eficiencias y "
            "branches_used. --tree es obligatorio para ROOT. --out guarda el JSON completo."
        ),
    )
    p.add_argument(
        "inputs", nargs="+", help="archivo(s) .root o .parquet del mismo formato"
    )
    p.add_argument("--tree", default=None, help="árbol ROOT (obligatorio para .root)")
    p.add_argument("--cuts", required=True, help="JSON con [{name,expression,source}]")
    p.add_argument("--out", default=None, help="ruta del cutflow JSON (opcional)")
    p.add_argument("--label", default=None, help="etiqueta de la muestra (opcional)")
    p.set_defaults(func=_analysis_select, action="select")

    p = analysis_cmds.add_parser(
        "hist",
        parents=[common],
        help="Llena un histograma con selección, pesos y normalización.",
        description=(
            "Llena un histograma de una observable (expresión restringida) sobre uno o varios "
            "archivos ROOT/Parquet del mismo formato. --mode event: un valor por evento; "
            "--mode object: un valor por objeto de una rama jagged. --selection y --cuts se "
            "aplican por evento. --weights es un peso por evento. --object-cut filtra objetos "
            "de la misma colección que la observable (solo --mode object) y exige "
            "--object-source. --normalize none (defecto) o "
            "area (suma de los bins en rango = 1). Salida: bins (edges/counts/underflow/"
            "overflow/nan), sumw2 y object_cut. --out guarda el JSON completo."
        ),
    )
    p.add_argument(
        "inputs", nargs="+", help="archivo(s) .root o .parquet del mismo formato"
    )
    p.add_argument(
        "--observable",
        required=True,
        help="expresión de la variable a histogramar (p. ej. MET_pt o Muon_pt)",
    )
    p.add_argument("--bins", type=int, required=True, help="número de bins (>= 1)")
    p.add_argument(
        "--range",
        nargs=2,
        type=float,
        required=True,
        metavar=("LO", "HI"),
        help="rango del histograma: --range LO HI (LO < HI, ambos finitos)",
    )
    p.add_argument("--tree", default=None, help="árbol ROOT (obligatorio para .root)")
    p.add_argument(
        "--mode",
        choices=("event", "object"),
        default="event",
        help="event: un valor por evento (defecto); object: un valor por objeto",
    )
    p.add_argument(
        "--selection",
        default=None,
        help="expresión booleana por evento (admite any/all/count/max)",
    )
    p.add_argument(
        "--cuts",
        default=None,
        help="JSON con [{name,expression,source}]; se aplican todos, en orden",
    )
    p.add_argument(
        "--weights", default=None, help="expresión de peso por evento (por defecto 1)"
    )
    p.add_argument(
        "--object-cut",
        default=None,
        help="corte booleano por objeto de la misma colección (solo --mode object); "
        "exige --object-source",
    )
    p.add_argument(
        "--object-source",
        default=None,
        help="fuente del --object-cut (obligatoria; no vale TODO ni pendiente)",
    )
    p.add_argument(
        "--normalize",
        choices=("none", "area"),
        default="none",
        help="none: recuentos con peso (defecto); area: suma en rango = 1",
    )
    p.add_argument("--out", default=None, help="ruta del histograma JSON (opcional)")
    p.add_argument("--label", default=None, help="etiqueta de la muestra (opcional)")
    p.set_defaults(func=_analysis_hist, action="hist")

    return parser


# --------------------------------------------------------------------- main


def main(argv=None) -> int:
    """Ejecuta el CLI y devuelve el exit code (0 OK, 1 error)."""
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # --help (0) o error de uso (1)
        return exc.code if isinstance(exc.code, int) else 1

    command = " ".join(
        part for part in (getattr(args, "module", ""), getattr(args, "action", "")) if part
    )
    label = f"mjfc {command}" if command else "mjfc"
    try:
        max_items = int(getattr(args, "max_items", DEFAULT_MAX_ITEMS))
        if max_items < 1:
            raise ValueError(f"--max-items debe ser >= 1, recibido: {max_items}")
        line = _emit(args.func(args), max_items)
    except Exception as exc:  # cualquier fallo de las tools o de los argumentos
        print(f"{label}: error: {exc}", file=sys.stderr)
        return 1

    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
