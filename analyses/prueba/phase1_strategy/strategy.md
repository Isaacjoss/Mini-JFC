# Fase 1 — Estrategia del análisis `prueba`

Análisis: H→ττ en el canal μτ_h con CMS Open Data de 2012.
Fecha de esta revisión: 2026-10-27 (sustituye a la versión de 2026-10-21). Autor: `planner` (fase 1).

Fuentes usadas: `prompt.md` (ambas secciones), `analysis_config`, `experiment_log.md`,
`src/methodology/phases.md` (§1), `phase2_exploration/candidatos_datasets.md`,
`phase2_exploration/inventario_datos.md`, `retrieval_log.md` y las fichas de
`phase2_exploration/files/` (`record_12352.json`, `files_12352.json`, `record_12353.json`,
`files_12353.json`, `record_12355.json`, `files_12355.json`, `record_12358.json`,
`files_12358.json`, `files_12351.json`, `files_31102.json`).

La referencia externa citada por nombre es CMS HIG-13-004 (arXiv:1401.5041), citada en
`prompt.md` junto con el récord 12350 de CERN Open Data como modelo de alcance cualitativo.
**No se ha descargado ni leído el texto del paper en esta sesión**: cualquier valor que
dependa de él queda "pendiente de fuente" hasta que conste en `retrieval_log.md`.

Estado del `analysis_config` al cerrar la fase: no queda ninguna clave en `TODO`; no se ha
modificado `fase_actual` (sigue en `phase1_strategy`, lo avanza el orquestador).

## Objetivo

Búsqueda de H→ττ en el canal μτ_h con CMS Open Data de 2012: reconstruir la cinemática del
canal (un muón + un τ hadrónico) y comparar la forma de las distribuciones de los datos
reales con la de las muestras simuladas de señal y de fondo. Caso de validación cualitativo,
siguiendo libremente HIG-13-004 / arXiv:1401.5041.

## Alcance

**Alcance elegido: CUALITATIVO** (fijado en `prompt.md`, "Objetivo dado por el usuario" y
"Instrucciones"). Incluye:

- Reconstrucción del canal μτ_h (un muón + un τ_h) y de sus variables cinemáticas.
- Comparación datos/MC **solo en forma**: distribuciones normalizadas (o con el mismo número
  de entradas) de datos reales frente a señal ggF, señal VBF, Z→ττ, W+jets (solo W1) y ttbar.
- Cutflow por corte como control del efecto de la selección.
- Comentario cualitativo de compatibilidad con las muestras de señal H→ττ. La masa de
  125 GeV se toma de HIG-13-004 (citado por nombre en `prompt.md`) y queda **pendiente de
  confirmar en el texto**.

**NO incluye** (fuera de alcance por decisión explícita del usuario):

- **Ajuste estadístico** de ningún tipo: sin verosimilitud, sin límites de sección eficaz,
  sin significancia, sin exclusión ni descubrimiento. El usuario lo fija como "segunda meta,
  fuera de este alcance".
- **Incertidumbres sistemáticas** de ningún tipo (ni teóricas, ni experimentales, ni de
  normalización).
- **Fondo diboson ZZ**: los recids 12362/12363/12364 quedan **excluidos** por decisión del
  usuario.
- **W2JetsToLNu (12356) y W3JetsToLNu (12357)**: excluidos; W+jets se representa solo con
  W1JetsToLNu (12355).
- Correcciones de escala de energía de jets, MET filters y reweighting de pila (PU): no
  pedidas, y los archivos reducidos no contienen pesos ni la información necesaria
  (`inventario_datos.md` §3 y §5).
- Canales eτ_h, τ_hτ_h, VH o cualquier otro distinto de μτ_h.
- Reprocesado desde AOD/AODSIM con CMSSW.
- Estimación de fondos data-driven (fake rate, OS/SS).
- **Cualquier descarga no autorizada**: no se descarga nada sin aprobación explícita.

## Datasets necesarios

Un dataset por proceso, exactamente la lista fijada por el usuario en `prompt.md`. Los
`recid` proceden de `phase2_exploration/candidatos_datasets.md` y de las fichas de
`phase2_exploration/files/`. El `data_agent` es quien asigna el dataset definitivo y ejecuta
las descargas (con autorización previa). No se proponen datasets alternativos.

| Proceso | recid | Archivo | Tamaño | Estado / fuente del dato |
|---|---|---|---|---|
| Señal ggF H→ττ | **12351** | `GluGluToHToTauTau.root` | 196 517 149 B (0.197 GB) — `files_12351.json` | **Descargado** en `data/prueba/` (`retrieval_log.md`). Año/energía: **no verificado** (no hay `record_12351.json` guardado) |
| Señal VBF H→ττ | **12352** | `VBF_HToTauTau.root` | 231 849 713 B (0.232 GB) — `record_12352.json` / `files_12352.json` | **Descargado** en `data/prueba/` (`retrieval_log.md`). `year = null`, `collision_energy = null` (`record_12352.json`) |
| Fondo Z→ττ (DYJetsToLL) | **12353** | `DYJetsToLL.root` | 9 247 252 629 B (9.25 GB) — `record_12353.json` / `files_12353.json` | Pendiente de descarga (archivo único, sin descarga parcial). `year = null`, `collision_energy = null` |
| Fondo W+jets | **12355** | `W1JetsToLNu.root` | 10 731 401 995 B (10.73 GB) — `record_12355.json` / `files_12355.json` | Pendiente de descarga (archivo único). **Solo W1Jets**; W2/W3 excluidos por decisión del usuario. `year = null`, `collision_energy = null` |
| Fondo ttbar | **31102** | **un único archivo suelto** de los listados en `files_31102.json` (p. ej. `24603428-8B2E-44B3-9E97-B991129E184D.root`, 1 986 138 847 B) | ≈1.7–2.0 GB el suelto — `files_31102.json` | Pendiente de descarga. **Se usa UN archivo suelto; NUNCA el `*_merged.root`** (el merged duplica el contenido: 17 sueltos + merged = 63 443 394 971 B, `candidatos_datasets.md` §5). Año/energía del registro: **no verificado** (no hay `record_31102.json` guardado); el path del fichero contiene `_8TeV` (`files_31102.json`, **inferido** del nombre) |
| Datos reales Run2012B_TauPlusX | **12358** | `Run2012B_TauPlusX.root` | 10 918 632 568 B (10.92 GB) — `record_12358.json` / `files_12358.json` | Pendiente de descarga (archivo único). `year = null`, `collision_energy = null`. Dispara en tau, no en muón → ver riesgos |

Todos los ficheros son ROOT plano tipo "reduced NanoAOD" (árbol `Events`), legibles sin
CMSSW.

**Volumen de descarga pendiente:** ≈32.9 GB (suma aritmética de los tamaños citados para
12353 + 12355 + 12358 + un suelto de 31102), más los 0.428 GB ya descargados. Casi todos los
archivos superan el límite por defecto de la tool (500 MB), por lo que requieren `--confirm`
o un `--max-bytes` explícito autorizado. Disco libre registrado: 950 GB
(`candidatos_datasets.md` §9).

## Selección prevista

Objetos y cortes para el canal μτ_h. **Estado de las fuentes:** `prompt.md` solo fija el
canal; **no fija cortes**. Los valores deducidos del nombre de un trigger se marcan
"inferido"; el resto son propuesta provisional del planificador y quedan **pendiente de
fuente** (contrastar con HIG-13-004) antes de aplicarlos en fase 3.

### Objetos

| Objeto | Definición propuesta | Fuente / estado |
|---|---|---|
| Muón | `Muon_tightId == 1` + aislamiento relativo (`Muon_pfRelIso03_all`) | Ramas confirmadas en 12351/12352 (`inventario_datos.md` §3); umbral de aislamiento **pendiente de fuente** |
| τ_h | `Tau_idIsoMedium` (+ `Tau_idAntiMu*`, `Tau_idAntiEle*`), `Tau_decayMode` | Ramas confirmadas; combinación y umbral **pendiente de fuente** |
| Jet | `Jet_pt`, `Jet_eta`, `Jet_puId`, `Jet_btag` (contaje / etiquetado VBF, no selección del canal) | Ramas confirmadas |
| MET | `MET_pt`, `MET_phi` | Ramas confirmadas |

### Cortes

| # | Corte | Valor propuesto | Fuente / estado |
|---|---|---|---|
| 1 | Trigger de muón (MC y datos, si existe la rama) | `HLT_IsoMu24_eta2p1` OR `HLT_IsoMu24` | Ramas confirmadas en 12351/12352; pT(μ)>24 GeV **inferido del trigger** |
| 2 | Trigger alternativo μ+τ | `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` | Rama confirmada; pT(μ)>17, pT(τ)>20, \|η_μ\|<2.1 **inferido del trigger** |
| 3 | Calidad de muón | `Muon_tightId == 1` + aislamiento relativo pequeño | **pendiente de fuente** |
| 4 | pT(μ) | > 20–25 GeV | **pendiente de fuente**; debe ser ≥ el umbral del trigger aplicado |
| 5 | \|η(μ)\| | < 2.1 | **inferido** del sufijo `eta2p1` del trigger |
| 6 | pT(τ_h) | > 20 GeV | **inferido del trigger** (`LooseIsoPFTau20`); valor exacto de HIG-13-004 **pendiente de fuente** |
| 7 | \|η(τ_h)\| | < 2.3 | **pendiente de fuente** (propuesta habitual) |
| 8 | ID del τ_h | `Tau_idIsoMedium==1` + `Tau_idAntiMu*` + `Tau_idAntiEle*` | Ramas confirmadas; combinación exacta **pendiente de fuente** |
| 9 | Carga opuesta | `Muon_charge * Tau_charge < 0` | Criterio estándar del canal; **pendiente de fuente** para HIG-13-004 |
| 10 | ΔR(μ, τ_h) | > 0.5 | **pendiente de fuente** |
| 11 | Vértice primario | `PV_npvs` > 0 (y \|PV_z\| < 24 cm si se necesita) | Rama confirmada; valor **pendiente de fuente** |
| 12 | Región de señal m_vis | ventana alrededor de 125 GeV para el contaje final | **pendiente de fuente** (la ventana exacta no se fija aquí) |

Notas de implementación previstas para fase 3:

- Cortes 1–2 con lógica OR en MC. En MC las ramas `HLT_*` existen, pero **no consta que el
  derivado incluya emulación del trigger**; si no la incluye, no se exigirá trigger en MC
  (comprobación previa en fase 3).
- En datos (12358) el trigger de muón puede no estar preseleccionado porque el primary
  dataset es TauPlusX; ver riesgo 2 y la pregunta abierta correspondiente.

## Variables de interés

Lista exacta (es la que se copia a `variables_de_interes` en `analysis_config`; ya coincide
con la del config, sin discrepancias):

- Muón: `Muon_pt`, `Muon_eta`, `Muon_phi`, `Muon_mass`, `Muon_charge`,
  `Muon_pfRelIso03_all`, `Muon_tightId`, `Muon_dxy`, `Muon_dz`
- τ_h: `Tau_pt`, `Tau_eta`, `Tau_phi`, `Tau_mass`, `Tau_charge`, `Tau_decayMode`,
  `Tau_relIso_all`, `Tau_idIsoMedium`, `Tau_idIsoTight`, `Tau_idAntiMuLoose`,
  `Tau_idAntiMuTight`, `Tau_idAntiEleLoose`, `Tau_idAntiEleMedium`
- MET: `MET_pt`, `MET_phi`
- Jets: `Jet_pt`, `Jet_eta`, `Jet_phi`, `Jet_btag`, `Jet_puId`
- Evento: `PV_npvs`, `nMuon`, `nTau`, `nJet`, `HLT_IsoMu24_eta2p1`, `HLT_IsoMu24`,
  `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`
- Derivadas: masa visible `m_vis(μ, τ_h)`, ΔR(μ, τ_h), pT del par μτ_h, Δφ(μ, MET),
  MET transverse mass
- MC truth (solo muestras simuladas): `GenPart_pt`, `GenPart_eta`, `GenPart_phi`,
  `GenPart_pdgId`, `GenPart_status`

Todas las ramas están confirmadas en los dos archivos ya descargados
(`inventario_datos.md` §3, 69 ramas). Se asume —**pendiente de verificar en fase 2**— que
12353, 12355, 12358 y 31102 exponen las mismas ramas.

## Normalización

| Elemento | Necesario para | Disponibilidad / fuente |
|---|---|---|
| Sección eficaz (σ) por proceso | escalar MC a luminosidad | **pendiente de fuente**: no está en los archivos ni en las fichas guardadas; requeriría HIG-13-004 o documentación del récord, registrada en `retrieval_log.md` |
| Luminosidad integrada | escalar datos/MC | **pendiente de fuente**: `candidatos_datasets.md` §10 y `inventario_datos.md` §5 confirman que ni la ficha ni el ROOT la contienen; además los datos son un solo archivo de Run2012B |
| Nº de eventos generados / suma de pesos (N_gen, `sumw`) | σ·L/N_gen | **no disponible**: `inventario_datos.md` §3 y §5 confirman ausencia de `genWeight`/`sumw` y de cualquier rama de pesos |
| Peso por evento | normalización | **no disponible** (misma razón) |

Consecuencia, coherente con el alcance cualitativo fijado por el usuario: **la comparación
datos/MC es solo en forma** (distribuciones normalizadas a la unidad o a un mismo número de
entradas), no en escala absoluta. La normalización absoluta queda explícitamente fuera de
alcance y no se usará para ninguna afirmación cuantitativa. Si más adelante se pidiera
escala absoluta, habría que resolver σ, L y N_gen con fuentes citadas antes de fase 3.

## Método estadístico

- **Ninguno inferencial.** Sin ajuste, sin verosimilitud, sin límites, sin significancias y
  sin sistemáticos (fijado por `prompt.md`).
- Tratamiento previsto: conteos y histogramas de las variables de interés para datos y para
  cada muestra MC; cutflow por corte; comparación cualitativa de formas (incluida la
  comparación de formas normalizadas).
- Cualquier cociente datos/MC que se muestre será descriptivo y en forma normalizada, y se
  etiquetará como tal.

## Riesgos y preguntas abiertas

### Decisiones cerradas por el usuario (2026-10-27)

Quedan **cerradas** y no se replantean en fases posteriores:

1. **Alcance cualitativo**: cinemática y comparación datos/MC **solo en forma**, sin ajuste
   estadístico y sin sistemáticos.
2. **Señal**: 12351 (ggF) y 12352 (VBF).
3. **Fondos**: 12353 (DYJetsToLL), **solo** 12355 (W1JetsToLNu; W2/W3 fuera) y 31102
   (ttbar) con **un único archivo suelto**, **nunca** el `_merged`.
4. **Sin ZZ**: 12362/12363/12364 excluidos.
5. **Datos reales**: 12358 (Run2012B_TauPlusX).
6. **Descargas**: ninguna sin aprobación explícita del usuario.

### Riesgos abiertos

1. **Año y energía no confirmados en las fichas.** `record_12352.json`, `record_12353.json`,
   `record_12355.json` y `record_12358.json` devuelven `year = null` y
   `collision_energy = null`; 12351 y 31102 no tienen `record_<recid>.json` guardado
   (**no verificado**). El contenido ROOT tampoco lo permite (`inventario_datos.md` §5). El
   "2012 / 8 TeV" se apoya en el título del récord y en HIG-13-004, no en un metadato →
   **pendiente**. Además, **requiere que `data_agent` guarde la ficha de 12351** y **la de
   31102** (`record_12351.json`, `record_31102.json`) para poder citar sus metadatos.
2. **Los datos pedidos no coinciden con el trigger del canal.** 12358 (TauPlusX) es un
   primary dataset disparado en tau, mientras el canal μτ_h selecciona por muón; no consta
   qué caminos de trigger contiene el derivado. Riesgo de preselección incompatible o de
   pérdida de aceptancia. No se proponen datasets alternativos: la decisión es del usuario.
3. **Cortes sin fuente verificada.** `prompt.md` no fija cortes y el texto de HIG-13-004 no
   está descargado. Todos los cortes de la tabla que no se deducen del nombre de un trigger
   están **pendiente de fuente**.
4. **Sin σ, sin L y sin N_gen.** Impide cualquier normalización absoluta y obliga a la
   comparación en forma (ver Normalización). Consecuencia aceptada del alcance cualitativo.
5. **Autorización de descarga pendiente.** Faltan ≈32.9 GB (12353, 12355, 12358 y un suelto
   de 31102) y casi todos superan el límite de 500 MB de la tool. Sin autorización explícita,
   la fase 3 solo podría ejecutarse con las dos señales ya descargadas.
6. **Un solo archivo de datos.** 12358 es un archivo único de Run2012B: no representa toda
   la luminosidad de 2012 y no se puede subdividir la descarga.
7. **Un solo archivo suelto de ttbar.** El suelto elegido de 31102 (≈1.7–2.0 GB de 31.7 GB
   de sueltos) es una fracción pequeña de la muestra; su tamaño y estadística son limitados.
   La elección del archivo concreto corresponde a `data_agent`, con la prohibición explícita
   del `_merged`.
8. **Posible tope de 100 000 eventos** en `root summary` (`inventario_datos.md` §7): el
   número real de eventos por archivo está sin verificar.
9. **Ramas no verificadas en los archivos aún no descargados** (12353, 12355, 12358, 31102):
   la lista de variables se ha validado solo en 12351/12352.
10. **Trigger en MC no confirmado.** Las ramas `HLT_*` existen en el árbol, pero no consta
    que el derivado incluya emulación del trigger; exigirlo en MC podría vaciar la muestra.
11. **`event` no es monótono** en los archivos de señal (`inventario_datos.md` §7): no
    usarlo como índice ni para deduplicar sin comprobación.
12. **Masa del Higgs y ventana de señal** (125 GeV y ancho de ventana): tomadas de
    HIG-13-004 por nombre, **pendiente de fuente** hasta leer el texto.

### Preguntas abiertas (para el agente padre)

- ¿Se acepta "2012 / 8 TeV" como hipótesis de trabajo pese a `year`/`collision_energy` nulos
  en las fichas, citando HIG-13-004 y el título del récord? ¿O se exige una fuente
  verificable antes de fase 3?
- ¿Cómo se trata la preselección por trigger de 12358 (tau) en un canal seleccionado por
  muón? (Sin proponer datasets alternativos: la decisión de alcance es del usuario.)
- ¿Qué fuente se usa para fijar los cortes de selección, dado que HIG-13-004 no se ha
  descargado? ¿Se autoriza su descarga/lectura y su registro en `retrieval_log.md`?
- ¿Se autoriza la descarga de ≈32.9 GB de fondos y datos (con `--confirm` o `--max-bytes`
  explícito)? Sin ella, la fase 3 queda limitada a las dos muestras de señal.
