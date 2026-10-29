# Candidatos de datasets CMS Open Data — H→ττ, canal μτ_h, 8 TeV (2012)

Fase 2 (Exploration). Búsqueda realizada **solo** con las tools del CLI
`scripts/mjfc.py cms ...` (`search`, `record`, `files`).
**Estado de descargas (2026-10-28):** ver §12 — descargados y verificados 12351, 12352,
12353, 12355, 12358 y 31102 (un archivo suelto de este último). Todos los `recid`, títulos,
URIs, números de archivos y tamaños proceden de la salida de esas tools.

> ## Decisión sobre este documento: **REVALIDADO** (no conservado tal cual, no reemplazado)
>
> - **Fecha de revalidación:** 2026-10-21.
> - **Config vigente** (`analyses/prueba/analysis_config`, modificado hoy): objetivo =
>   búsqueda de H→ττ; `energia_centro_de_masa_tev = 8`; `anio = 2012`; `canal = mu tau_h`.
>   Coincide con el análisis para el que se escribió este archivo, por lo que **se conserva
>   la estructura y la propuesta**, corrigiendo/añadiendo lo que las tools confirman.
> - **Qué se ha revalidado con tools:** `cms record <recid>` de 31127, 31133, 24416, 24417,
>   24460, 24418, 8001, 9743, 8000, 12351, 12352, 7731, 7730, 9863, 9864, 9865, 9587,
>   31102 y 1635/1654, y `cms files` completos de 31127 y 31102.
> - **Qué NO se ha podido revalidar:** los **tamaños totales** de 31133, 24416, 24417,
>   7731, 9863, 9864, 9865 y 9587 no se han re-sumado en esta sesión (listas de 157–4812
>   archivos); se mantienen las cifras de la sesión anterior y se marcan como tales. El
>   **tamaño del `*_merged.root` de 31133** tampoco se ha vuelto a leer.
> - **Novedad importante:** se ha localizado la familia de datasets reducidos
>   `AOD2NanoAODOutreachTool` (recids **12351–12368**), que incluye **diboson ZZ**, **W+jets**,
>   **DY**, **ttbar**, **VBF H→ττ** y datos **Run2012B/C_TauPlusX** en ROOT plano. Esto
>   **cambia la conclusión anterior** de que "no hay diboson 8 TeV" y de que "W/DY solo
>   existen en AODSIM".
> - **Sigue sin confirmarse:** el **año y la energía** de los recids 12351–12364 (la ficha
>   devuelve `year = null`, `collision_energy = null`). No se afirma que sean 8 TeV.

Los "tamaño total" son suma aritmética de los `size_bytes` devueltos por `cms files`.
Los registros derivados "Run1 NanoAOD-like" incluyen además un archivo `*_merged.root`
que **duplica** el contenido: se indica en cada fila cuando aplica y **no debe descargarse**.

---

## 1. Datos observados (colisiones, 2012, 8 TeV)

| Título | recid | Archivos | Tamaño total | Año | Energía | Notas |
|---|---|---|---|---|---|---|
| `Run2012B_SingleMu dataset in Run1 NanoAOD-like format` | 31127 | **107** (confirmado en `files_31127.json`: 106 sueltos + 1 `_merged`) | **no verificado** (ver nota) | 2012 | 8TeV | Formato ntuple ROOT "NanoAOD-like" (procesado desde AOD), legible sin CMSSW. `files_31127.json` contiene 107 entradas: 106 archivos sueltos y `Run2012B_SingleMu_merged.root` (duplicado del conjunto; no debe descargarse). **(a)** suma de los 106 sueltos: **no verificada**; **(b)** tamaño del `*_merged.root`: **no verificado**; **(c)** total de los 107: **no verificado**. La cifra anterior **273.2 GB** queda **obsoleta/incorrecta**, y la atribución de 136 604 190 299 B a "106 sueltos + merged" se retira: no se pudo re-sumar en esta sesión (ver nota al final de §1). Un archivo suelto típico ≈ 1.2–1.45 GB (los 9 primeros leídos: 1.19–1.42 GB); el menor visto es `67974E31-4159-4EE6-A6B0-4BD3A450B643.root` = 57 800 675 B (57.8 MB) |
| `Run2012C_SingleMu dataset in Run1 NanoAOD-like format` | 31133 | **157** (confirmado) | 438.1 GB *(cifra previa; no re-sumada)* | 2012 | 8TeV | Mismo formato. La descripción confirma que también incluye `Run2012C_SingleMu_merged.root` (duplicado); tamaño del merged **no re-leído** en esta sesión. Primer archivo: 1 438 349 338 B |
| `/SingleMu/Run2012A-22Jan2013-v1/AOD` | 24416 | **817** (confirmado) | 2 901.2 GB (cifra previa) | 2012 | 8TeV | AOD oficial, **requiere CMSSW**. Runs 190456–193621. Primer archivo: 3 558 557 450 B |
| `/Tau/Run2012A-22Jan2013-v1/AOD` | 24417 | **317** (confirmado) | 1 139.1 GB (cifra previa) | 2012 | 8TeV | AOD oficial del primary dataset Tau, **requiere CMSSW**. Primer archivo: 4 069 639 617 B |

### Datos observados adicionales (ahora sí consultados)

| Título | recid | Archivos | Año | Energía | Notas |
|---|---|---|---|---|---|
| `/SingleMu/Run2012D-22Jan2013-v1/AOD` | 24460 | **7 566** | 2012 | 8TeV | AOD, **requiere CMSSW**. Runs 203777–208686. Primer archivo: 3 363 640 629 B (**no verificado**: sin `files_24460.json`). Es el mayor de los SingleMu por nº de archivos: descartado para subconjunto mínimo |
| `/TauPlusX/Run2012A-22Jan2013-v1/AOD` | 24418 | **487** | 2012 | 8TeV | AOD, **requiere CMSSW**. Primer archivo: 4 103 950 516 B (**no verificado**: sin `files_24418.json`) |
| `Run2012B_TauPlusX ... reduced NanoAOD` | 12358 | 1 | **null** | **null** | Ver §7. 10 918 632 568 B |
| `Run2012C_TauPlusX ... reduced NanoAOD` | 12359 | 1 | **null** | **null** | Ver §7. 15 886 107 547 B |

Nota: en la familia "Run1 NanoAOD-like" **no existen** versiones derivadas de
`Run2012A_SingleMu` ni `Run2012D_SingleMu` (búsquedas `"Run2012A_SingleMu"` y
`"Run2012D_SingleMu"` → `[]`). Solo hay B (31127) y C (31133).

**Nota sobre los totales de 31127 (no verificados).** `files_31127.json` sí contiene los
107 `size_bytes`, pero las tools de esta fase no permiten sumarlos: `read` trunca la única
línea del JSON a 2000 caracteres, `cms files` vuelve a truncar la lista y el reglamento de la
fase prohíbe `python -c`, `jq`, `awk` y cualquier comando fuera del CLI (la shell rechaza esos
comandos con `permission.rejected`). Por eso las tres cifras —(a) suma de los 106 sueltos,
(b) tamaño del merged y (c) total de los 107— quedan como **no verificadas** y no se usan en
ninguna propuesta. `273.2 GB` y `136.60 GB` son cifras previas sin recálculo y no deben citarse
como tamaño del dataset.

## 2. Señal H→ττ (M = 125 GeV, 2012, 8 TeV)

| Título | recid | Archivos | Tamaño total | Año | Energía | Notas |
|---|---|---|---|---|---|---|
| `/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6-tauPolarOff/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM` | 8001 | **56** (confirmado) | 151.8 GB (cifra previa) | 2012 | 8TeV | Señal gluon-fusion, AODSIM → **requiere CMSSW**. Primer archivo: 2 359 475 980 B |
| `/VBF_HToTauTau_M-125_8TeV-powheg-pythia6-tauola-tauPolarOff/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM` | 9743 | **54** (confirmado) | 160.2 GB (cifra previa) | 2012 | 8TeV | Señal VBF, AODSIM → **requiere CMSSW**. Primer archivo: 4 237 687 609 B |
| `GluGluToHToTauTau dataset in reduced NanoAOD format for education and outreach` | 12351 | **1** (confirmado) | **196 517 149 B (0.197 GB)** | **null** | **null** | **Candidato ligero, pero no confirmado**: ROOT plano `GluGluToHToTauTau.root`. La ficha **sigue sin declarar año ni energía** (verificado hoy: `year: null`, `collision_energy: null`) |
| `VBF_HToTauTau dataset in reduced NanoAOD format for education and outreach` | **12352** (NUEVO) | **1** | **231 849 713 B (0.232 GB)** | **null** | **null** | Alternativa VBF ligera; misma incertidumbre de año/energía |

También existe `/GluGluToHToTauTau_M-125_8TeV-minloHJJ-pythia6-tauola/...` (recid **8000**,
2012, 8TeV, **44** archivos, primer archivo 2 412 668 060 B —verificado en
`files_8000.json`—, AODSIM) como variación alternativa.

## 3. Fondo Z→ττ (Drell–Yan, 2012, 8 TeV)

| Título | recid | Archivos | Tamaño total | Año | Energía | Notas |
|---|---|---|---|---|---|---|
| `/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball-tauola-tauPolarOff/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM` | 7731 | **2 467** (confirmado) | 9 153.0 GB (cifra previa) | 2012 | 8TeV | Muestra estándar DY con τola; AODSIM → **requiere CMSSW**. Primer archivo: 4 092 202 043 B |
| `/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_RD1_START53_V7N-v1/AODSIM` | 7730 | **2 419** (confirmado) | no disponible | 2012 | 8TeV | Alternativa sin τola; AODSIM. Primer archivo: 3 405 771 674 B (**no verificado**: sin `files_7730.json`) |
| `DYJetsToLL dataset in reduced NanoAOD format for education and outreach` | **12353** (NUEVO) | **1** | **9 247 252 629 B (9.25 GB)** | **null** | **null** | ROOT plano, **sin CMSSW**; al ser 1 solo archivo no se puede descargar parcialmente. Año/energía no declarados en la ficha |

## 4. Fondo W+jets (2012, 8 TeV)

| Título | recid | Archivos | Tamaño total | Año | Energía | Notas |
|---|---|---|---|---|---|---|
| `/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM` | 9863 | **2 773** (confirmado) | 9 737.5 GB (cifra previa) | 2012 | 8TeV | W+1 partón, AODSIM → CMSSW. Primer archivo: 2 740 353 494 B |
| `/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM` | 9864 | **2 606** (confirmado) | 10 416.4 GB (cifra previa) | 2012 | 8TeV | W+2 partones, AODSIM. Primer archivo: 4 102 197 448 B |
| `/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM` | 9865 | **1 715** (confirmado) | 5 361.8 GB (cifra previa) | 2012 | 8TeV | W+3 partones, AODSIM. Primer archivo: 2 668 071 203 B |
| `W1JetsToLNu ... reduced NanoAOD` | **12355** (NUEVO) | **1** | **10 731 401 995 B (10.73 GB)** | **null** | **null** | ROOT plano, sin CMSSW. Archivo único completo |
| `W2JetsToLNu ... reduced NanoAOD` | **12356** (NUEVO) | **1** | **12 161 887 620 B (12.16 GB)** (verificado: `files_12356.json`) | **null** | **null** | ROOT plano, sin CMSSW |
| `W3JetsToLNu ... reduced NanoAOD` | **12357** (NUEVO) | **1** | **6 544 850 738 B (6.54 GB)** (verificado: `files_12357.json`) | **null** | **null** | ROOT plano, sin CMSSW |

Sigue **sin localizarse** una muestra inclusiva `WJetsToLNu_*_8TeV` ni `W4JetsToLNu`
(ver §8). Solo existen las desglosadas W1/W2/W3 Jets.

## 5. Fondo ttbar (2012, 8 TeV)

| Título | recid | Archivos | Tamaño total | Año | Energía | Notas |
|---|---|---|---|---|---|---|
| `/TTJets_MassiveBinDECAY_8TeV-madgraph-gridpack/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM` | 9587 | **4 812** (confirmado) | 18 033.4 GB (cifra previa) | 2012 | 8TeV | AODSIM estándar 2012 → CMSSW. Primer archivo: 2 603 887 983 B |
| `TTbar_8TeV-Madspin_aMCatNLO-herwig dataset in Run1 NanoAOD-like format` | 31102 | **18** (confirmado) | **63 443 394 971 B (63.44 GB)** (recalculado) | 2012 | 8TeV | ROOT plano, sin CMSSW. **17 sueltos (31 721 642 985 B) + `MonteCarlo12_Summer12_DR53X_TTbar_8TeV-Madspin_aMCatNLO-herwig_merged.root` = 31 721 751 986 B (31.72 GB), duplicado.** Sueltos entre 1.67 y 2.00 GB |
| `TTbar dataset in reduced NanoAOD format for education and outreach` | **12354** (NUEVO) | **1** | **3 528 995 041 B (3.53 GB)** (verificado: `files_12354.json`) | **null** | **null** | ROOT plano, sin CMSSW. Más pequeño que 31102 (63.44 GB) pero mayor que **un** archivo suelto de 31102 (1.99 GB) |

## 6. Fondo diboson (WW, WZ, ZZ) — 8 TeV

**AODSIM 8 TeV: no encontrado.** Todas las búsquedas nuevas devolvieron `[]`
(`WW_8TeV`, `WZ_8TeV`, `ZZ_8TeV`, `WW_TuneZ2star`, `WZ_TuneZ2star`, `ZZ_TuneZ2star`,
`WW_TuneZ2_8TeV`, `WW_TuneZ2Star_8TeV`). `"WWTo"`, `"WZTo"` y `"ZZTo"` solo devuelven
muestras **13 TeV / 2016**. `"diboson"` solo devuelve Wprime 13 TeV.

**PERO sí existen alternativas reducidas en ROOT plano (NUEVO):**

| Título | recid | Archivos | Tamaño | Año | Energía | Notas |
|---|---|---|---|---|---|---|
| `ZZTo4mu dataset in reduced NanoAOD format for education and outreach` | 12362 | 1 | 184 624 480 B (0.185 GB) (verificado: `files_12362.json`) | **null** | **null** | ROOT plano, bajo `.../AOD2NanoAODOutreachTool/ForHiggsTo4Leptons/`. **No autorizado** |
| `ZZTo4e dataset in reduced NanoAOD format for education and outreach` | 12363 | 1 | 161 660 567 B (0.162 GB) (verificado: `files_12363.json`) | **null** | **null** | idem. **No autorizado** |
| `ZZTo2e2mu dataset in reduced NanoAOD format for education and outreach` | 12364 | 1 | 173 163 793 B (0.173 GB) (verificado: `files_12364.json`) | **null** | **null** | idem. **No autorizado** |
| `SMHiggsToZZTo4L ... reduced NanoAOD` | 12361 | 1 | 42 400 229 B (0.042 GB) (verificado: `files_12361.json`) | **null** | **null** | Señal de control H→ZZ→4ℓ, no es fondo de μτ_h. **No autorizado** |

**Corrección respecto a la versión anterior de este documento:** la afirmación "no hay
ningún candidato diboson 8 TeV" era válida **solo para AODSIM**. En formato reducido sí
hay ZZ (12362/12363/12364), con la salvedad de que la ficha **no declara año ni energía**.
No se han encontrado WW ni WZ reducidos (la familia outreach no los incluye).
Las únicas muestras WW/ZZ con año/energía explícitos siguen siendo **7 TeV (2011)** y
**no sirven** para este análisis:

| Título | recid | Año | Energía | Archivos |
|---|---|---|---|---|
| `/WW_TuneZ2_7TeV_pythia6_tauola/Summer11LegDR-PU_S13_START53_LV6-v1/AODSIM` | 1635 | 2011 | 7TeV | 219 (confirmado) |
| `/ZZ_TuneZ2_7TeV_pythia6_tauola/Summer11LegDR-PU_S13_START53_LV6-v1/AODSIM` | 1654 | 2011 | 7TeV | 228 (confirmado) |

## 7. Familia "reduced NanoAOD format for education and outreach" (NUEVA, recids 12351–12368)

Derivados de `AOD2NanoAODOutreachTool`: **un único archivo ROOT por muestra**, legible sin
CMSSW. Son la mejor opción para un análisis reducido, **con la reserva de que la ficha no
declara año ni energía** (`year = null`, `collision_energy = null` en todos los que se han
consultado). En los títulos de los datos aparece "Run2012B/Run2012C", pero eso es el nombre,
no un metadato verificado de energía.

| Proceso | recid | Archivo único | Tamaño |
|---|---|---|---|
| Señal ggF H→ττ | 12351 | `GluGluToHToTauTau.root` | 196 517 149 B (0.197 GB) |
| Señal VBF H→ττ | 12352 | `VBF_HToTauTau.root` | 231 849 713 B (0.232 GB) |
| DY / Z→ττ | 12353 | `DYJetsToLL.root` | 9 247 252 629 B (9.25 GB) |
| ttbar | 12354 | `TTbar.root` | 3 528 995 041 B (3.53 GB) |
| W+1 jet | 12355 | `W1JetsToLNu.root` | 10 731 401 995 B (10.73 GB) |
| W+2 jets | 12356 | `W2JetsToLNu.root` | 12 161 887 620 B (12.16 GB) |
| W+3 jets | 12357 | `W3JetsToLNu.root` | 6 544 850 738 B (6.54 GB) |
| Datos Run2012B TauPlusX | 12358 | `Run2012B_TauPlusX.root` | 10 918 632 568 B (10.92 GB) |
| Datos Run2012C TauPlusX | 12359 | `Run2012C_TauPlusX.root` | 15 886 107 547 B (15.89 GB) |
| ZZ→4μ | 12362 | `ZZTo4mu.root` | 184 624 480 B (0.185 GB) |
| ZZ→4e | 12363 | `ZZTo4e.root` | 161 660 567 B (0.162 GB) |
| ZZ→2e2μ | 12364 | `ZZTo2e2mu.root` | 173 163 793 B (0.173 GB) |
| H→ZZ→4ℓ (control) | 12361 | `SMHiggsToZZTo4L.root` | 42 400 229 B (0.042 GB) |
| Run2012C DoubleMuParked | 12366 | `Run2012C_DoubleMuParked.root` | 4 463 307 037 B (4.46 GB) |

**Trazabilidad de tamaños (§7):** los tamaños de 12354, 12356, 12357, 12359, 12361,
12362, 12363, 12364 y 12366 están verificados con las fichas `files_<recid>.json` guardadas en
`phase2_exploration/files/`. Los de 12351, 12352, 12353 y 12355 ya constaban en sus fichas.

También existen **12365** (`Run2012B_DoubleMuParked`), **12367** (`Run2012B_DoubleElectron`)
y **12368** (`Run2012C_DoubleElectron`); **tamaños no consultados** en esta sesión y **no
relevantes para μτ_h** (disparan en dimuón/dielectrón, no en el muón único del canal).

Cautela: al ser **un solo archivo por muestra**, no se puede descargar una fracción; el
mínimo descargable es la muestra entera.

## 8. Búsquedas sin resultados / incidencias

Búsquedas que devolvieron lista vacía `[]` (**esta sesión**):

- Diboson 8 TeV: `"WW_8TeV"`, `"WZ_8TeV"`, `"ZZ_8TeV"`, `"WW_TuneZ2star"`,
  `"WZ_TuneZ2star"`, `"ZZ_TuneZ2star"`, `"WW_TuneZ2_8TeV"`, `"WW_TuneZ2Star_8TeV"`.
- W+jets inclusivo: `"WJetsToLNu_8TeV"`, `"WJetsToLNu_TuneZ2Star_8TeV"`,
  `"W1JetsToLNu_8TeV"`.
- MuonEG 2012: `"MuonEG Run2012"`, `"TauPlusX Run2012"`, `"SingleMuon 2012"`.
- Datos derivados 2012A/2012D: `"Run2012A_SingleMu"`, `"Run2012D_SingleMu"`.

Búsquedas con resultados **solo de energías/años equivocados** (descartadas):
`"MuonEG"` → 2015/2016 (13 TeV, recids 24104, 24121, 30511, 30528, 30544, 30561, 31311);
`"WWTo"`, `"WZTo"`, `"ZZTo"` → 2016 (13 TeV); `"diboson"` → Wprime 13 TeV.

Búsquedas de la sesión anterior (se mantienen, no reintentadas): ver historial más abajo.
Siguen siendo válidas las conclusiones de que la búsqueda falla con cadenas genéricas
(`"Run2012"`, `"Summer12"`) y funciona mejor con el nombre completo de la muestra.

Fallos de tool registrados en `errores_tools.md` (sesión anterior, no reintentados):

- `cms search "Run2012" -n 30`: timeout de 120 s sin salida.
- `cms search "Summer12" -n 25`: `IncompleteRead(11576472 bytes read, 11463 more expected)`.

Búsquedas de la sesión anterior que devolvieron `[]` y **siguen sin repetirse**:
`"MuonEG 2012"`, `"HiggsToTauTau 2012"`, `"DYJetsToLL 2012"`, `"DYJetsToLL_M-50_8TeV"`,
`"W4JetsToLNu_TuneZ2Star_8TeV"`, `"GluGluToHToTauTau 8TeV"`, `"VBF_HToTauTau 8TeV"`,
`"8TeV dataset in Run1 NanoAOD"`. (Con el nombre completo sí funcionan: ya revalidado.)

## 9. Disco disponible (actualizado 2026-10-28)

`df -h` ejecutado hoy (2026-10-28) en la raíz del repo:

| Sistema | Tamaño | Usado | Disponible | Uso | Montaje |
|---|---|---|---|---|---|
| `/dev/sdd` | 1007 G | 7.0 G | **949 G** | 1 % | `/` |
| `D:\` | 895 G | 485 G | **411 G** | 55 % | `/mnt/d` |

- **Descargado y verificado:** **33 311 792 901 B (33.31 GB)** en 6 archivos, el mismo total
  que §10 y que `inventario_datos.md` §8: 12351 (196 517 149 B) + 12352 (231 849 713 B) +
  12358 (10 918 632 568 B) + 31102 (1 986 138 847 B) + 12355 (10 731 401 995 B) +
  12353 (9 247 252 629 B).
- **Destino:** `data/prueba/` (señal: 12351 y 12352, 428 366 862 B) sobre `/dev/sdd` (949 G
  libres) y `data/prueba_d/` → `/mnt/d/Mini-JFC/prueba` (disco D:, **411 G libres**) para
  12358, 31102, 12355 y 12353 (32 883 426 039 B).
- **Conclusión:** 411 G libres en D: y 949 G en `/` cubren de sobra el alcance ya descargado
  (33.31 GB). La antigua propuesta máxima de esta sección (Opción C) quedó **retirada** en §10
  y **no es el alcance vigente**; el alcance real y sus cifras son las de §10.
- **Instantánea histórica (2026-10-21, superada):** `df -h` daba 950 G libres en `/dev/sdd` y
  `data/` solo contenía `README.md` (aún no había datos descargados). Se conserva como
  histórico; no describe el estado actual.

## 10. Subconjunto autorizado y realmente descargado (actualizado 2026-10-28)

**Alcance aprobado por el usuario:** exactamente los recids **12351, 12352, 12353, 12355,
12358 y 31102** (de este último, **un único archivo suelto**). Quedan **fuera** del alcance
31127, los ZZ 12362/12363/12364 y cualquier `*_merged.root`.

| Proceso | recid | Archivo descargado | Destino | Tamaño declarado (`files_<recid>.json`) | Tamaño en disco (`stat -c '%s'`) | Estado |
|---|---|---|---|---|---|---|
| Señal ggF H→ττ | 12351 | `GluGluToHToTauTau.root` | `data/prueba/` | 196 517 149 B | 196 517 149 B | **completa** |
| Señal VBF H→ττ | 12352 | `VBF_HToTauTau.root` | `data/prueba/` | 231 849 713 B | 231 849 713 B | **completa** |
| Datos Run2012B TauPlusX | 12358 | `Run2012B_TauPlusX.root` | `data/prueba_d/` | 10 918 632 568 B | 10 918 632 568 B | **completa** |
| ttbar MC | 31102 | `24603428-8B2E-44B3-9E97-B991129E184D.root` — **un archivo suelto** de los 17; **nunca** el `_merged` | `data/prueba_d/` | 1 986 138 847 B | 1 986 138 847 B | **completa** |
| W+jets | 12355 | `W1JetsToLNu.root` | `data/prueba_d/` | 10 731 401 995 B | 10 731 401 995 B | **completa** |
| Z→ττ (DY) | 12353 | `DYJetsToLL.root` | `data/prueba_d/` | 9 247 252 629 B | 9 247 252 629 B | **completa** |
| **Total (6 muestras)** | | | | **33 311 792 901 B (33.31 GB)** | ídem | — |

Los seis archivos son **ROOT directo** (sin CMSSW) y están verificados por tamaño
(`size_bytes` = `stat -c '%s'`) y ausencia de `.aria2`. La suma de 33 311 792 901 B es
aritmética directa de los seis `size_bytes` de `files_12351.json`, `files_12352.json`,
`files_12353.json`, `files_12355.json`, `files_12358.json` y `files_31102.json`.

Reservas: (a) 12351/12352/12353/12355/12358 **no declaran año ni energía** en la ficha
(`year=null`, `collision_energy=null`); (b) 12353 y 12355 se descargaron enteros (archivo
único, sin descarga parcial); (c) 31102 es **un** archivo suelto de 17 y no representa la
muestra completa ni la luminosidad de 2012; (d) la luminosidad integrada sigue sin fuente.

### Opciones históricas (no seleccionadas)

Las antiguas **opciones B, C y D** de versiones previas de este documento **no son el alcance
aprobado** y se conservan solo como histórico:

- **No autorizadas:** el usuario autorizó únicamente 12351, 12352, 12353, 12355, 12358 y 31102.
- La antigua **"Opción C"** (24.34 GB) incluía **31127** y los ZZ **12362/12363/12364**, y
  **omitía 12358**: contradecía `prompt.md` y `strategy.md`, por lo que se retira.
- Ninguna opción aprobada incluye `*_merged.root`: el merged de 31127/31133/31102 duplica los
  sueltos y no debe descargarse.
- La **Opción D** (AODSIM: 8001/7731/9863/…) exigiría CMSSW y tampoco fue autorizada.
- Los tamaños de esas opciones históricas no se usan aquí; varios de ellos (p. ej. los totales
  de 31127) están marcados como **no verificados** en §1.

## 11. Clasificación de viabilidad

| recid | Formato | CMSSW | Tamaño mínimo útil | Viabilidad | Motivo |
|---|---|---|---|---|---|
| 31127 | ntuple ROOT (NanoAOD-like) | No | 1.42 GB (1 suelto) | **No autorizado** (viable técnicamente) | Datos 2012/8TeV confirmados; fuera del alcance aprobado |
| 31133 | ntuple ROOT (NanoAOD-like) | No | 1.44 GB (1 suelto) | **No autorizado** (viable técnicamente) | Idem, periodo C; fuera del alcance aprobado |
| 31102 | ntuple ROOT (NanoAOD-like) | No | 1.99 GB (1 suelto) | **Viable** | ttbar 2012/8TeV confirmado |
| 12351 | ROOT reducido | No | 0.197 GB | **Viable con reservas** | Año/energía no declarados (`null`) |
| 12352 | ROOT reducido | No | 0.232 GB | **Viable con reservas** | Idem |
| 12353 | ROOT reducido | No | 9.25 GB (entero) | **Viable con reservas** | Año/energía `null`; sin descarga parcial |
| 12354 | ROOT reducido | No | 3.53 GB (entero) | **Viable con reservas** | Año/energía `null`; 31102 es más barato por archivo suelto |
| 12355/12356/12357 | ROOT reducido | No | 6.5–12.2 GB (entero) | **Viable con reservas** | Año/energía `null`; descarga completa obligatoria |
| 12358/12359 | ROOT reducido | No | 10.9 / 15.9 GB | **12358 autorizado; 12359 no** | Año/energía `null`; los triggers del archivo son de muón (no de tau) |
| 12362/12363/12364 | ROOT reducido | No | 0.16–0.18 GB c/u | **No autorizado / descartado** | Único diboson disponible, pero el usuario no autorizó ZZ; año/energía `null` |
| 8001/8000/9743 | AODSIM | **Sí** | 2.36 / 2.41 / 4.24 GB (1 archivo) | **Viable solo con CMSSW** | Año/energía confirmados, pero formato AOD |
| 7731/7730 | AODSIM | **Sí** | 4.09 GB (7731; ficha) / 3.41 GB (7730; **no verificado**) | **Viable solo con CMSSW** | Idem |
| 9863/9864/9865 | AODSIM | **Sí** | 2.74 / 4.10 / 2.67 GB (1 archivo) | **Viable solo con CMSSW** | Idem |
| 9587 | AODSIM | **Sí** | 2.60 GB (1 archivo) | **Viable solo con CMSSW** | Idem; 31102/12354 son alternativas ROOT |
| 24416/24417/24460/24418 | AOD | **Sí** | ~3.4–4.1 GB (1 archivo; **no verificado** para 24460/24418) | **No viable para subconjunto mínimo** | AOD oficial, TB de escala; solo si se necesita reprocesar desde cero |
| 1635/1654 | AODSIM | Sí | — | **No viable** | **7 TeV / 2011**: energía y año incorrectos |
| 12365/12367/12368 | ROOT reducido | No | no consultado | **No relevante** | Datos de dimuón/dielectrón, no del canal μτ_h |

Alcance aprobado y descargado (§10): **12351 + 12352** (señal), **12358** (datos), **31102**
(un archivo suelto), **12355** (W+jets) y **12353** (DY), todos ROOT directo y sin CMSSW.
**31127 y los ZZ 12362/12363/12364 no están autorizados** y no forman parte de la propuesta;
las opciones B/C/D que los incluían son históricas. Solo si más adelante se exige
normalización rigurosa con año/energía confirmados habría que plantear AODSIM + CMSSW
(8001/7731/9863), lo que requeriría nueva autorización.

## 12. Estado real de las descargas (actualizado 2026-10-28)

Esta sección **sustituye** a las versiones anteriores de §12. Todos los archivos autorizados
están descargados, verificados por tamaño y explorados.

| recid | archivo | Estado | Destino | Tamaño declarado / en disco |
|---|---|---|---|---|
| 12351 | `GluGluToHToTauTau.root` | **Descargado y explorado** (2026-10-21) | `data/prueba/` | 196 517 149 / 196 517 149 B |
| 12352 | `VBF_HToTauTau.root` | **Descargado y explorado** (2026-10-21) | `data/prueba/` | 231 849 713 / 231 849 713 B |
| 12358 | `Run2012B_TauPlusX.root` | **Descargado y explorado** (2026-10-28) | `data/prueba_d/` | 10 918 632 568 / 10 918 632 568 B |
| 31102 | `24603428-8B2E-44B3-9E97-B991129E184D.root` (1 suelto) | **Descargado y explorado** (2026-10-28) | `data/prueba_d/` | 1 986 138 847 / 1 986 138 847 B |
| 12355 | `W1JetsToLNu.root` | **Descargado y explorado** (2026-10-28) | `data/prueba_d/` | 10 731 401 995 / 10 731 401 995 B |
| 12353 | `DYJetsToLL.root` | **Descargado y explorado** (2026-10-28; se borró antes el resto truncado de 119 673 824 B) | `data/prueba_d/` | 9 247 252 629 / 9 247 252 629 B |
| 31127, 31133, 12354, 12356, 12357, 12362–12364, 8001, 7731, 9863, 9587, 24416–24460 | ver §1–§7 | **No descargados** (ni autorizados) | — | — |

- `data/prueba_d/` es un enlace simbólico a `/mnt/d/Mini-JFC/prueba` (disco D:). Tras las
  descargas quedan **411 G libres** (55 % usado).
- `data/prueba/DYJetsToLL.root` (81 264 640 B) es el **resto incompleto** de la ejecución
  cancelada: **no es un dato válido** y no se incluye en el inventario (`errores_tools.md` §5).
- Verificación: tamaño en disco (`stat -c '%s'`) = `size_bytes` de `files_<recid>.json` y
  ausencia de `<archivo>.aria2`. No se calcularon hashes.
- Incidencias (colisión curl/aria2, reinicio del servidor, resto truncado):
  `phase2_exploration/errores_tools.md` §7. Detalle por archivo:
  `phase2_exploration/descargas.json`.
- Exploración de contenidos: `phase2_exploration/inventario_datos.md` §9–§13.

### 12.1 Huecos detectados (variables de `variables_de_interes` y metadatos)

Ninguno de los cuatro archivos nuevos cubre estos huecos; el detalle por archivo está en
`inventario_datos.md` §13.

1. **Pesos de MC / normalización:** no hay `genWeight`, `sumw`, `LHEWeight`, sección eficaz
   ni número de eventos generados en 12353, 12355 ni 31102. Las muestras MC **no se pueden
   normalizar** con el contenido descargado.
2. **Luminosidad integrada:** no está en la ficha ni en el ROOT (`analysis_config` sigue con
   `pendiente_de_fuente`).
3. **Año y energía:** las fichas de 12351–12364 devuelven `year=null` y
   `collision_energy=null`; el ROOT no contiene metadatos que lo confirmen. Para 12358, el
   rango de `run` (194 075–196 531) es consistente con 2012B, pero no prueba 8 TeV.
4. **Total de eventos:** `root summary` se detiene en 100 000; el total real no es
   verificable con las tools.
5. **Variables ausentes en 31102 (ttbar):** `Tau_relIso_all`, `Tau_idAntiMuLoose/Medium`,
   `Tau_idAntiEleLoose/Medium` y `Jet_puId` (solo existen `Tau_idIsoraw`,
   `Tau_idAntimutight`, `Tau_idAntieletight`).
6. **Datos (12358):** sin `GenPart_*` (esperado), sin triggers puros de tau y sin flags de
   MET filters; cubre solo Run2012B.
7. **Variables derivadas:** `m_vis`, `dR(mu,tau_h)`, `pT` del par, `dphi(mu,MET)` y masa
   transversa **no están almacenadas**; hay que calcularlas.
8. **Correcciones/calibración:** sin JEC/JER, sin MET filters y sin puntos de trabajo de
   b-tagging; `Jet_btag` es un valor crudo.
