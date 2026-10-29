# Inventario local de datos — verificación con shell habilitado

Fecha: 2026-10-21
Sesión: `data_agent` (fase 2 — Exploration)
Método: `find`/`ls` sobre el workspace y sobre ubicaciones habituales. Sin descargas.

## 1. Dentro del workspace `/home/isaac/Mini-JFC`

| Ruta | Formato | Tamaño | Observación |
|---|---|---|---|
| `/home/isaac/Mini-JFC/data/` | — | 8 KB (solo `README.md`) | Contiene únicamente `README.md` de 55 B: "Coloca aquí los datasets del análisis (ROOT/parquet)". **Carpeta vacía de datos.** |
| `/home/isaac/Mini-JFC/analyses/` | — | plantillas | Solo `.md`, `.py` de plantilla y `.gitkeep` en las 5 fases. Sin datos. |
| `/home/isaac/Mini-JFC/.venv/lib/python3.14/site-packages/pyarrow/tests/data/parquet/` | Parquet | 3.9–4.4 KB c/u (4 archivos) | **Fixtures de test de pyarrow** (`v0.7.1*.parquet`), no son datos de física. |

Resultado: **0 archivos `.root`** y **0 Parquet de física** en el workspace.

Configuración revisada:
- `README.md`: no indica ruta de datasets; el flujo descarga vía `scripts/mjfc.py cms download`.
- `analyses/prueba/analysis_config`: todos los campos en `TODO` (sin dataset asignado).
- `.gitignore`: excluye `*.root`, `*.parquet` y `analyses/*/data/` → los datos descargados no se versionan.
- `analyses/prueba/retrieval_log.md`: tabla vacía (ninguna recuperación registrada).

## 2. Fuera del workspace (hallazgo, FUERA DE ALCANCE)

Búsqueda en `/home/isaac` (maxdepth 4) y en `/tmp/opencode`:

| Ruta | Formato | Nº archivos | Tamaño total |
|---|---|---|---|
| `/home/isaac/mi-jupyter/search-for-dark-matter/output_raw/` | Parquet | 60 | 28.85 MB |
| `/home/isaac/mi-jupyter/search-for-dark-matter/` | ROOT | 0 | 0 B |

No existen `/home/isaac/data`, `/home/isaac/datasets`, `/data`, `/datasets` ni `/opt/data`.
`/tmp/opencode` solo contiene `agents.json` y `data_agent.orig.md` (configuración, no datos).

**Advertencia de alcance:** estos Parquet pertenecen a otro proyecto (búsqueda de materia oscura,
`mi-jupyter`) y están **fuera de `~/Mini-JFC/data/`**. Se listan solo como inventario; no se
inspeccionó su contenido ni se copiaron. Requieren autorización explícita del agente padre para usarse.

### 2.1 Contenido de `output_raw/` (inferido de nombres y `.manifest.json`)

60 archivos = 22 datasets base × 3 variantes de selección (`_raw`, `_electron`, `_0lep`),
excepto `SingleElectron` y `SingleMuon` (solo una variante) y `met` (una variante).
Cada entrada del `.manifest.json` declara `n_files: 20` (20 archivos ROOT de origen por dataset).

| Grupo | Archivos (variantes) | Interpretación |
|---|---|---|
| `WJets-HT70to100 … HT2500toInf` | 8 bins × 3 = 24 | W+jets simulado, binned en HT |
| `ttbar-semileptonic`, `ttbar-2l2nu` | 3 + 3 | tt̄ semileptónico y dileptónico |
| `t-channel-top`, `t-channel-antitop` | 3 + 3 | single top canal t |
| `ttW` | 3 | tt̄ + W |
| `WW`, `WZ`, `ZZ` | 3 + 3 + 3 | dibosones |
| `DYJets-Zpt200`, `Zvv-Zpt100to200`, `Zvv-Zpt200` | 3 + 3 + 3 | Drell-Yan / Z→νν |
| `SingleElectron`, `SingleMuon`, `met` | 1 + 1 + 1 | colisiones datos (2016) / MET |
| **Total** | **60** | 28.85 MB |

Archivos auxiliares: `.manifest.json` (2.8 KB, nº de archivos de origen por dataset),
`.sumw_1.json` (646 B) y `.sumw_20.json` (677 B) (sumas de pesos por dataset).
El proyecto de origen es un análisis de materia oscura sobre CMS Open Data 2016
(incluye `Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt`).

## 3. Conclusión

- No hay datasets utilizables dentro del workspace: `data/` está vacío.
- La única fuente local de Parquet de física está fuera del alcance permitido.
- Alternativa prevista por el proyecto: localizar y descargar datasets con
  `.venv/bin/python scripts/mjfc.py cms search "<query>"` → `cms files <recid>` → `cms download <uri> <dest_dir>`,
  guardando en `analyses/<analisis>/data/` o `data/` y registrando en `retrieval_log.md`.
- No se intentó ninguna descarga ni se ejecutaron tools ROOT/Parquet por ausencia de archivos.
