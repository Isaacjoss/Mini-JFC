	# Registro de experimentos

Una entrada por ejecución (phase3_processing) y por revisión (phase4_validation).

| fecha | fase | cambio | resultado | notas |
|-------|------|--------|-----------|-------|
| 2026-10-28 | phase3_processing | resumen de estado de la cadena `analysis` (a petición del usuario) | `select` y `hist` existen y pasan tests; `normalize`, `run` y las tools de tablas/figuras no existen | Detalle corto al final del archivo; `analyst` sigue bloqueado para la fase 3 |
| 2026-10-28 | phase3_processing | `literature_agent`: 4 fichas en `literature/fichas/` + 12 filas nuevas en `retrieval_log.md` (consolidadas en la tabla) | Luminosidad Run2012B **4,412 fb⁻¹** y σ: DY 3503,7 pb; W1Jets 6381,2 pb; ttbar 225,2 pb | **Ninguna cifra es de fuente oficial**: las cuatro salen de `skim.cxx` (repo educativo, "not validated"); ficha 12358 sin luminosidad; twiki de σ a 8 TeV da 401; LUM-13-001 solo metadatos; PDFs no legibles. `luminosidad_integrada_pb_minus1` sigue `pendiente_de_fuente` |
| 2026-10-28 | phase3_processing | alcance inicial fijado por el usuario: **comparación cualitativa solo de forma**, un histograma por muestra **normalizado a área unitaria**, sin apilar y sin escala absoluta; no se requiere luminosidad para esta comparación | Alcance registrado; `analyst` sigue bloqueado (la tool `analysis` solo ofrece `select`/cutflow, no histogramas) | No se delega fase 3. `luminosidad_integrada_pb_minus1` permanece `pendiente_de_fuente` |
| 2026-10-28 | phase3_processing | delegada al `literature_agent` la búsqueda con fuente verificable de: luminosidad integrada de Run2012B (12358) y secciones eficaces de DY (12353), W1Jets (12355) y ttbar (31102) | Pendiente del informe; fichas en `literature/fichas/` y filas en `retrieval_log.md` | Sin completar por memoria: lo que no conste se marca `no consta`. No se toca `analysis_config` |
| 2026-10-28 | phase2_exploration | revisión del `reviewer` (intento 3, tras 2 reintentos de corrección) | **PASS**: los 7 criterios de `phases.md` §2 cumplidos; `fase_actual` → `phase3_processing` | 1er FAIL: §10 con 31127/ZZ y sin 12358, tamaños sin ficha, 31102 sin lista de ramas, totales de 31127 incoherentes. 2º FAIL: §9 decía "0 GB descargados" y `retrieval_log.md` negaba otras descargas. Corregido por `data_agent`; 31102 con 928 ramas exactas (`files/branches_31102.json`) |
| 2026-10-28 | phase2_exploration | `data_agent` consolida `retrieval_log.md` (filas duplicadas/huérfanas, 8 eliminadas) y corrige coherencia documental | 6 filas, una por recid (12351, 12352, 12353, 31102, 12358, 12355) | Registrado en `errores_tools.md` §7.5/§7.7; sin pérdida de cifras |
| 2026-10-28 | phase2_exploration | tras el reinicio del servidor: reanudadas 12358/12355/12353 con `aria2c -c` (PIDs 701/702/704) desde sus `.aria2`; duplicados 713/715/717 eliminados; el `curl` congelado 1816 desapareció con el reinicio | **4/4 descargas completas**: 12358 10 918 632 568 B; 12355 10 731 401 995 B; 12353 9 247 252 629 B; 31102 1 986 138 847 B | Tamaño == `files_<recid>.json` y sin `.aria2` en las 4; integridad: los 6 ROOT abren el árbol `Events` (`root trees`) |
| 2026-10-27 | phase2_exploration | revisión de logs de descarga (12358/12355/12353) a las 22:27–22:28 | **sin errores ni segmentos atascados**: CN:8 en las tres y progreso continuo (12358 35% y 3,1 MiB/s; 12355 31% y 2,9 MiB/s; 12353 9% y 2,7 MiB/s) | No se reinició ningún aria2c; los 3 `.aria2` presentes son normales en curso |
| 2026-10-27 | phase2_exploration | `aria2c` instalado; `curl` de 12358 congelado (SIGSTOP, PID 1816) con 662 786 560 B; relanzadas 3 descargas en paralelo con `aria2c -c -x 8 -s 8 -k 10M`: 12358 (reanudada), 31102 y 12355 | 3 procesos vivos (PIDs 2830, 2831, 2833) | Parcial de 12358 reutilizado sin reiniciar; 12353 en espera de plaza |
| 2026-10-27 | phase2_exploration | medición a los 5 min del arranque de aria2 | **≈7,0–7,6 MB/s reales** (suma de progreso aria2) frente a 1,98 MB/s con 1 conexión; el `stat` marca 62,02 MB/s porque aria2 escribe 8 segmentos dispersos (archivos sparse) | Se mantiene aria2; umbral superado. Dato en `phase2_exploration/descargas.json` |
| 2026-10-27 | phase2_exploration | protocolo de descarga actualizado a `aria2c -c -x 8 -s 8 -k 10M` (8 conexiones, hasta 3 muestras en paralelo, orden 12358→31102→12355→12353, reutilizar parciales, verificación de tamaño, control de salud a 5 min y vuelta a `curl -C -` si no mejora) | OK | `.opencode/agents/data_agent.md`; `aria2c` **no instalado** y `sudo` pide contraseña: comando exacto `sudo apt install -y aria2` |
| 2026-10-27 | phase2_exploration | medición de referencia con la descarga en curso de 12358 (`curl -C -`, 1 conexión) | **1,98 MB/s** (62 310 912 B en 30 s; 567 267 840 B de 10 918 632 568 B) | PID 1816, 449 s de ejecución; sirve de umbral para el control de salud de aria2 |
| 2026-10-27 | phase2_exploration | decisión del usuario: protocolo de descarga genérico en `data_agent` (nohup + log en `analyses/<nombre>/logs/`, `curl -C -` reanudable, 5 reintentos con espera creciente, verificación contra `files_<recid>.json`, orden de prioridad, estado en `descargas.json`) y regla en `orchestrator`: los fallos de red no se consultan al usuario | OK | Editados `.opencode/agents/data_agent.md` (protocolo, permisos de shell y excepciones) y `.opencode/agents/orchestrator.md` (regla de descargas) |
| 2026-10-27 | phase2_exploration | `data_agent` relanzado en segundo plano: descargas en orden 12358 → 31102 → 12355 → 12353 a `data/prueba_d`, con re-descarga de 12353 (el anterior estaba truncado) | en curso | Sesión `ses_e7f8dd1b4ffeo7g0y38p8UqrVJ`; inventario y `candidatos_datasets.md` al terminar |
| 2026-10-27 | phase2_exploration | `data_agent`: descargas autorizadas (12353, 12355, 12358, 31102) a `data/prueba_d` + exploración e inventario | **PARCIAL / BLOQUEADO**: 12353 "OK" pero truncado en disco (119 673 824 B de 9 247 252 629 B); 12355 falló con `fallo de red ... The read operation timed out`; 12358 y 31102 no ejecutadas; sin exploración ni inventario nuevos | No se llamó al `reviewer`: la fase 2 no está completa. Detalle en `phase2_exploration/errores_tools.md` §5–§6 y `bloqueos.md` §5 |
| 2026-10-27 | phase2_exploration | diagnóstico del orquestador (solo lectura): `curl` descarga 250 MiB seguidos a ≈1.4 MB/s sin cortes; el truncamiento de 12353 es compatible con un corte del proceso a los 120 s, no con caída de red | 32.9 GB autorizados ≈ 5–6.5 h de descarga | `cms download` no verifica tamaño final ni reanuda |
| 2026-10-27 | phase2_exploration | revisión del estado tras la ejecución cancelada: fichas `record_*`/`files_*` en `phase2_exploration/files/` para 12350, 12351, 12352, 12353, 12355, 12358 y 31102; `data/prueba/DYJetsToLL.root` = 81 264 640 B (copia incompleta, no sirve); `retrieval_log.md` sin filas nuevas; `inventario_datos.md` solo cubre 12351/12352 | estado inventariado; nada que reutilizar como descarga válida |
| 2026-10-27 | phase2_exploration | preparado destino D: `data/prueba_d` -> `/mnt/d/Mini-JFC/prueba` (441 GB libres) para las descargas autorizadas | OK | Enlace dentro del workspace para no salir del sandbox |
| 2026-10-27 | phase1_strategy | `data_agent`: guardadas las fichas `record_<recid>.json` y `files_<recid>.json` de 12352, 12353, 12355 y 12358 en `phase2_exploration/files/`, sin descargar datos | OK (8 JSON) | Trazabilidad para el `planner`; `year` y `collision_energy` = `null` en las 4 fichas |
| 2026-10-27 | phase1_strategy | `planner`: `strategy.md` actualizado con las decisiones del usuario (alcance cualitativo solo en forma; 12351/12352; 12353; solo 12355; 31102 con un suelto y nunca el `_merged`; sin ZZ; datos 12358; sin descargas); `analysis_config` sin `TODO` | OK | `fase_actual` no modificada por el `planner` |
| 2026-10-27 | phase1_strategy | `reviewer` revisa la fase 1 | **PASS** (4/4 criterios) | Cierra la fase 1; `fase_actual` -> `phase2_exploration` |
| 2026-10-27 | phase1_strategy | intento de ciclo de fase 1 (decisiones de alcance cualitativo: 12351, 12352; fondos 12353, 12355, 31102 sin `_merged`, datos 12358; sin descargas) | bloqueado: error literal al delegar en `planner`: `Agent planner cannot run as a subagent` | No se escribió `strategy.md`, no se actualizó `analysis_config`, no se llamó al `reviewer`; `fase_actual` sin cambios |
| 2026-10-21 | phase1_strategy | intento de ciclo de fase 1 | bloqueado: la sesión no expone tool de delegación (`task`) | No se delegó en `data_agent` ni `planner`; no se llamó al `reviewer`; `fase_actual` sin cambios. Fichas ausentes en `phase2_exploration/files/`: 12352, 12353, 12354, 12355, 12356, 12357, 12358, 12362, 12363, 12364 |

## Estado de la cadena `analysis` (2026-10-28)

Resumen corto; el detalle vive en `src/tools/analysis_tools.py`, `scripts/mjfc.py` y `.opencode/agents/analyst.md`.

**Existen y pasan tests**
- `analysis select <inputs> --cuts cuts.json [--tree]`: cortes en orden restringido → cutflow JSON. Cada corte exige `source` en `cuts.json`.
- `analysis hist <inputs> --observable --bins --range [--tree] [--mode event|object] [--selection] [--cuts] [--weights] [--normalize none|area] [--object-cut --object-source]`: histograma con `bins` (edges/counts/underflow/overflow/nan), `sumw2` y `object_cut`.
- Reducciones jagged `any/all/count/max` dentro de expresiones (± avisos de listas vacías).
- Tests: 131 en `tests/test_analysis_tools.py` con `MJFC_REAL_ROOT=1`; suite completa 203 passed, 10 skipped.

**Faltan**
- `analysis normalize` — sin ella no hay pesos de normalización con fuente (fase 3 incompleta).
- `analysis run` — sin ella no se ejecuta código propio de `phase3_processing/`.
- `analysis compare`, `analysis table`, `analysis plot`, `analysis check`, `analysis audit`.
- Variables de dos colecciones (`mT`, `ΔR`, `Δφ`, `m_vis`) y `leading`: diseñadas, no implementadas.

**Decisiones aprobadas**
- `--normalize none` por defecto; `area` para comparar formas.
- `all([])=True`, `any([])=False`, `count([])=0`, `max([])=NaN` (fuera de bins, con aviso).
- Solo `count(mask)`, sin `count(field)`.
- `--object-cut` exige `--object-source` real, solo en `--mode object`, sin reducciones dentro y sobre la misma colección que la observable.
- La selección por evento (`--selection`/`--cuts`) se aplica antes del corte por objeto.

**Pendiente**
- Validar A (`--object-cut`) e implementar B (`leading`).
- Aprobar el texto del criterio 1 de fase 3 (comandos del CLI como código reproducible).
- Luminosidad: `luminosidad_integrada_pb_minus1 = pendiente_de_fuente`.

