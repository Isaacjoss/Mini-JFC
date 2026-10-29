# Registro de recuperación de literatura y documentos

Todo lo recuperado por los agentes se registra aquí. Los documentos (papers, documentación) se guardan en `analyses/<nombre>/`; los datasets se guardan en `data/<nombre>/`.

| fecha | tipo (paper/doc/dataset) | fuente/URL | ruta local | motivo |
|-------|--------------------------|------------|------------|--------|
| 2026-10-21 14:01:58 | dataset | https://opendata.cern.ch/record/12351 | data/prueba/GluGluToHToTauTau.root | Señal H→ττ (gluon fusion) para validación 2012/8 TeV, canal μτ_h |
| 2026-10-21 14:06:46 | dataset | https://opendata.cern.ch/record/12352 | data/prueba/VBF_HToTauTau.root | Señal H→ττ (VBF) para validación 2012/8 TeV, canal μτ_h |
| 2026-10-27 21:48:52 | dataset | https://opendata.cern.ch/record/12353 | data/prueba_d/DYJetsToLL.root | Fondo Z->tautau (DYJetsToLL) en ROOT reducido para validacion 2012/8 TeV, canal mu tau_h; descarga autorizada 2026-10-27 |
| 2026-10-27 22:23:54 | dataset | https://opendata.cern.ch/record/31102 | data/prueba_d/24603428-8B2E-44B3-9E97-B991129E184D.root | Fondo ttbar (TTbar_8TeV-Madspin_aMCatNLO-herwig, Run1 NanoAOD-like) para validacion 2012/8 TeV, canal mu tau_h; descarga autorizada 2026-10-27 via aria2c |
| 2026-10-28 13:03:39 | dataset | https://opendata.cern.ch/record/12358 | data/prueba_d/Run2012B_TauPlusX.root | Datos observados Run2012B_TauPlusX (ROOT reducido) para validacion 2012/8 TeV, canal mu tau_h; descarga autorizada 2026-10-27 via aria2c |
| 2026-10-28 13:03:39 | dataset | https://opendata.cern.ch/record/12355 | data/prueba_d/W1JetsToLNu.root | Fondo W+jets W1JetsToLNu (ROOT reducido) para validacion 2012/8 TeV, canal mu tau_h; descarga autorizada 2026-10-27 via aria2c |
| 2026-10-28 13:48:17 | web | https://raw.githubusercontent.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/2012/skim.cxx | analyses/prueba/literature/fichas/luminosidad_run2012b.md | Codigo del analisis de referencia (rama 2012): fuente de L(Run2012B)=4.412 fb-1 y de las sigma 3503.7/6381.2/225.2 pb. Texto plano leido; ficha sin PDF |
| 2026-10-28 13:48:17 | web | https://opendata.cern.ch/record/12358 | analyses/prueba/literature/fichas/luminosidad_run2012b.md | Ficha web del recid 12358 (Run2012B_TauPlusX): eventos, dataset padre y validacion; NO declara luminosidad integrada. Ficha sin PDF |
| 2026-10-28 13:48:20 | web | https://opendata.cern.ch/record/12353 | analyses/prueba/literature/fichas/sigma_dy_8tev.md | Ficha web del recid 12353 (DYJetsToLL): 30458871 eventos y dataset padre /DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/; NO declara seccion eficaz. Ficha sin PDF |
| 2026-10-28 13:48:20 | web | https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-13-004/index.html | analyses/prueba/literature/fichas/luminosidad_run2012b.md | Pagina publica HIG-13-004: solo abstract (19.7 fb-1 a 8 TeV, total del analisis; no desglose por run). Ficha sin PDF |
| 2026-10-28 13:48:24 | web | https://opendata.cern.ch/record/31102 | analyses/prueba/literature/fichas/sigma_ttbar_8tev.md | Ficha web del recid 31102 (TTbar_8TeV-Madspin_aMCatNLO-herwig): 6423106 eventos, 8TeV, dataset padre AODSIM; NO declara seccion eficaz. Ficha sin PDF |
| 2026-10-28 13:48:24 | web | https://opendata.cern.ch/record/12355 | analyses/prueba/literature/fichas/sigma_w1jets_8tev.md | Ficha web del recid 12355 (W1JetsToLNu): 29784800 eventos y dataset padre /W1JetsToLNu_TuneZ2Star_8TeV-madgraph/; NO declara seccion eficaz. Ficha sin PDF |
| 2026-10-28 13:48:27 | web | https://raw.githubusercontent.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/2012/README.md | analyses/prueba/literature/fichas/sigma_dy_8tev.md | README del repositorio: advertencia de que el analisis no esta validado y es solo educativo. Texto plano leido; ficha sin PDF |
| 2026-10-28 13:48:28 | web | https://opendata.cern.ch/record/12350 | analyses/prueba/literature/fichas/sigma_dy_8tev.md | Registro del analisis de referencia H->tautau 2012: enlaza el repositorio de codigo usado como fuente de sigma y L. Ficha sin PDF |
| 2026-10-28 13:48:30 | arxiv | https://arxiv.org/abs/1401.5041v2 | analyses/prueba/literature/fichas/luminosidad_run2012b.md | Solo resumen/abstract leido (4.9 fb-1 a 7 TeV y 19.7 fb-1 a 8 TeV); el texto completo no se pudo leer |
| 2026-10-28 13:48:30 | web | https://twiki.cern.ch/twiki/bin/view/CMSPublic/LumiPublicResults | analyses/prueba/literature/fichas/luminosidad_run2012b.md | Pagina publica de luminosidad CMS leida completa: seccion 2012 solo con graficos, sin tabla numerica ni desglose por run. Ficha sin PDF |
| 2026-10-28 13:48:32 | arxiv | https://arxiv.org/abs/1401.5041 | analyses/prueba/literature/pdfs/1401.5041.pdf | PDF descargado con lit fetch pero NO legible por este modelo (sin soporte de entrada PDF); su contenido no se cita |
| 2026-10-28 13:50:53 | inspire | https://inspirehep.net/literature/1260876 | analyses/prueba/literature/fichas/luminosidad_run2012b.md | Metadatos INSPIRE del CMS-PAS-LUM-13-001 (recid 1260876): titulo, report number y PDF adjunto LUM-13-001-pas.pdf; abstract no recuperable (HTML con JS, JSON truncado) y PDF no leido. NO da cifra de Run2012B. Ficha sin PDF |

## Detalle de la descarga autorizada (2026-10-21)

**Alcance de la autorización del agente padre:** solo los archivos de los recids
**12351** y **12352** (señal H→ττ, ~0.43 GB en total), en `data/prueba/`.
En la autorización del 2026-10-21 no se descargó ningún otro archivo; las descargas
posteriores (12358, 31102, 12355 y 12353) se autorizaron por separado el 2026-10-27 y constan
en la tabla de arriba y en el detalle siguiente.

**Herramienta y comandos usados** (desde la raíz del repo `/home/isaac/Mini-JFC`):

1. `.venv/bin/python scripts/mjfc.py cms files 12352`
   → `[{"name": "VBF_HToTauTau.root", "size_bytes": 231849713, "uri": "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/VBF_HToTauTau.root"}]`
2. `.venv/bin/python scripts/mjfc.py cms download root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/GluGluToHToTauTau.root data/prueba --max-bytes 500000000`
   → `"data/prueba/GluGluToHToTauTau.root"`
3. `.venv/bin/python scripts/mjfc.py cms download root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/VBF_HToTauTau.root data/prueba --max-bytes 500000000`
   → `"data/prueba/VBF_HToTauTau.root"`
4. `.venv/bin/python scripts/mjfc.py lit log analyses/prueba/retrieval_log.md dataset ...`
   (dos veces, una por archivo; generan las filas de la tabla anterior)

No se usó `--confirm`: ambos archivos están por debajo del límite de 500 000 000 B.

**Archivos descargados:**

| recid | archivo | URI | Tamaño declarado (`cms files`) | Tamaño en disco |
|---|---|---|---|---|
| 12351 | `data/prueba/GluGluToHToTauTau.root` | `root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/GluGluToHToTauTau.root` | 196 517 149 B (0.197 GB) | 196 517 149 B |
| 12352 | `data/prueba/VBF_HToTauTau.root` | `root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/VBF_HToTauTau.root` | 231 849 713 B (0.232 GB) | 231 849 713 B |
| — | **total** | | **428 366 862 B (0.428 GB)** | **428 366 862 B** |

`data/prueba/GluGluToHToTauTau.root` contenía una copia incompleta previa de 64 225 280 B;
se volvió a descargar el archivo oficial (la tool sobrescribe el destino) y el tamaño final
coincide exactamente con el declarado.

**Propósito:** disponer de las dos muestras de señal H→ττ en formato reducido (ROOT plano,
sin CMSSW) para la exploración de la fase 2 (inventario de árboles/ramas y comprobación de
si el contenido permite confirmar año y energía). Ver `phase2_exploration/inventario_datos.md`.

**Integridad:** ambos archivos se abren correctamente con `root trees` (árbol `Events`) y
`root branches` (69 ramas), sin errores de lectura. No se calcularon hashes: el CLI `mjfc`
no expone esa función.

## Detalle de la descarga autorizada (2026-10-27)

**Alcance de la autorización del agente padre:** 4 archivos concretos, en `data/prueba_d/`
(enlace simbólico a `/mnt/d/Mini-JFC/prueba`, disco D:). **Nunca** el `*_merged.root`.
Total autorizado ≈ 32.88 GB (4 archivos).

**Herramienta:** `aria2c -c -x 8 -s 8 -k 10M --file-allocation=none
--auto-file-renaming=false --max-tries=5 --retry-wait=30 --connect-timeout=30 --timeout=60`,
hasta 3 muestras en paralelo, con `nohup` y log en `analyses/prueba/logs/`. Un intento
adicional con `curl -C -` sobre `Run2012B_TauPlusX.root` se canceló al detectar que
colisionaba con el `aria2c` ya activo sobre el mismo destino; no se usó su resultado.

**Resultado real (2026-10-28):** los 4 archivos están **completos**. Durante la sesión el
servidor WSL se reinició y las descargas en curso se reanudaron con `aria2c -c` desde los
parciales; la comprobación final es tamaño en disco = `size_bytes` de `files_<recid>.json`
**y** ausencia de `<archivo>.aria2`.

| recid | archivo | ruta local | tamaño declarado (`cms files`, en bytes) | tamaño en disco (B) | estado |
|---|---|---|---|---|---|
| 12358 | `Run2012B_TauPlusX.root` | `data/prueba_d/Run2012B_TauPlusX.root` | 10 918 632 568 | 10 918 632 568 | **Completa** |
| 31102 | `24603428-8B2E-44B3-9E97-B991129E184D.root` | `data/prueba_d/24603428-8B2E-44B3-9E97-B991129E184D.root` | 1 986 138 847 | 1 986 138 847 | **Completa** |
| 12355 | `W1JetsToLNu.root` | `data/prueba_d/W1JetsToLNu.root` | 10 731 401 995 | 10 731 401 995 | **Completa** |
| 12353 | `DYJetsToLL.root` | `data/prueba_d/DYJetsToLL.root` | 9 247 252 629 | 9 247 252 629 | **Completa** (se borró antes el resto truncado de 119 673 824 B) |

Avisos sobre la tabla:

- Los tamaños declarados proceden de `cms files` (guardados en
  `phase2_exploration/files/files_<recid>.json`); los tamaños en disco se midieron con
  `stat -c '%s'`. Los cuatro coinciden exactamente.
- No se calcularon hashes: el CLI `mjfc` no expone esa función.
- `data/prueba/DYJetsToLL.root` (81 264 640 B) **no** es esta descarga: es el resto incompleto
  de la ejecución cancelada, registrado en `errores_tools.md` §5 y excluido del inventario.
- `df -h` tras las descargas: `/mnt/d` (D:) con **411 G disponibles** (55 % usado). Antes de
  empezar había 441 G libres; el descenso (~30 GB) es coherente con los 32.88 GB descargados
  menos el truncado eliminado.
- Estado detallado por archivo (intentos, incidencias): `phase2_exploration/descargas.json`.
