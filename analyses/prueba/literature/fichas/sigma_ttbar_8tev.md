# Ficha — Sección eficaz de ttbar, 8 TeV (recid 31102, `TTbar_8TeV-Madspin_aMCatNLO-herwig`)

Pregunta: ¿qué σ (en pb), con qué incertidumbre y para qué proceso exacto, corresponde a la
muestra de ttbar de 31102 (un archivo suelto), para poder escalarla?

## Referencia

1. **CERN Open Data, registro 31102** — "TTbar_8TeV-Madspin_aMCatNLO-herwig dataset in Run1
   NanoAOD-like format", CMS Open Data group. "Data recorded in 2012. Published in 2024."
   URL: https://opendata.cern.ch/record/31102
   - DOI: **`no consta`** (la página no muestra línea "Cite as"/DOI).
   - Etiquetas de la ficha: "Derived", "CMS", "8TeV", "pp", "CERN-LHC".
2. **Código del análisis de referencia de CERN Open Data** (única fuente leída que da el
   valor numérico de σ). `skim.cxx`, rama `2012`, repositorio
   `cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis`.
   - URL navegable: https://github.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/blob/2012/skim.cxx
   - Texto plano leído: https://raw.githubusercontent.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/2012/skim.cxx
   - Tipo: **código fuente** (no artículo revisado). Sin `arxiv_id`, sin DOI.
3. **CERN Open Data, registro 12350** (registro que enlaza el repositorio de código como
   "Source code repository"). DOI `10.7483/OPENDATA.CMS.GV20.PR5T`.
   URL: https://opendata.cern.ch/record/12350
4. **`README.md` del mismo repositorio**, rama `2012`:
   https://raw.githubusercontent.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/2012/README.md

## Qué se leyó

- Registro 31102: **página HTML completa** (descripción, dataset padre, "Dataset
  characteristics", validación, cómo usarlo).
- `skim.cxx`: **texto completo del archivo**, bloque `std::map eventWeights`.
- Registro 12350 y `README.md`: **texto completo** (contexto y advertencia de validez).
- **No se leyó** el twiki `StandardModelCrossSectionsat8TeV` (HTTP 401) ni ningún artículo
  de producción (PDF no legible por este modelo).

## Valores y cortes

| valor | unidad | cita textual | localización | estado |
|---|---|---|---|---|
| **225.2** | pb | `{"TTbar", 225.2 / 6423106.0 * integratedLuminosity},` | `skim.cxx`, `std::map eventWeights`, entrada `TTbar` | **dato publicado en código** (constante del análisis de referencia) |
| incertidumbre de σ | — | — | — | **`no consta`** |
| 6 423 106 | eventos generados | "6423106 events. 18 files. 29.5 MiB in total." | registro 31102, "Dataset characteristics" | dato publicado en la ficha del registro |
| 6 423 106.0 | denominador de N_gen | `225.2 / 6423106.0` | `skim.cxx`, misma línea | dato publicado en código; **coincide exactamente** con el nº de eventos del registro 31102 |
| proceso: `TTbar_8TeV-Madspin_aMCatNLO-herwig` | — | "This dataset was derived from: /TTbar_8TeV-Madspin_aMCatNLO-herwig/Summer12_DR53X-PU_S10_START53_V19-v2/AODSIM" | registro 31102, "Related datasets" | dato publicado en la ficha (nombre del dataset padre) |
| aMC@NLO + Herwig + MadSpin | — | "TTbar_8TeV-Madspin_aMCatNLO-herwig dataset in a NanoAOD-like research-level Ntuple format..." | registro 31102, título y descripción | dato publicado en la ficha (solo el nombre; la ficha **no** describe la cadena de generación) |
| ttbar inclusivo (todos los canales de decaimiento) | — | — | el nombre no lleva sufijo de canal (`dileptonic`, `semileptonic`) | **inferencia**; `no consta` en las fuentes leídas |
| 8 TeV | — | "Data recorded in 2012. Published in 2024." + etiqueta "8TeV" | registro 31102, cabecera y etiquetas | dato publicado en la ficha |

**Proceso exacto, según lo leído:** muestra de pares t-tbar a 8 TeV, generada con
aMC@NLO + Herwig y con MadSpin en el nombre del dataset padre
(`/TTbar_8TeV-Madspin_aMCatNLO-herwig/Summer12_DR53X-PU_S10_START53_V19-v2/AODSIM`). Que sea
**inclusiva** en canales de decaimiento (no dileptónica ni semileptónica exclusiva) es una
**inferencia** del nombre: no hay sufijo de canal y el número de eventos (6 423 106) es el de
la muestra completa. La ficha **no** describe la cadena de generación ni el orden.

## Limitaciones

- **Origen del valor: `skim.cxx` (código educativo), NO la ficha del recid 31102 ni una
  publicación.** 225.2 pb es una constante escrita a mano en ese archivo; ninguna de las
  fuentes oficiales leídas lo respalda.
- **La ficha del recid 31102 no declara sección eficaz.** Describe el formato y la
  procedencia, no el proceso ni σ.
- **El valor 225.2 pb está asociado en el código a la entrada `TTbar` del análisis de
  referencia**, cuya N_gen (6 423 106) coincide con la del registro 31102 y cuyo dataset padre
  es el mismo AODSIM. La equivalencia "esta σ es la de 31102" es por tanto una **inferencia
  por identidad de N_gen y de dataset padre**, no una declaración de la ficha.
- El valor procede de una **constante en código educativo**; `README.md`: "the analysis is not
  validated and should be used only for educational purposes, in particular since no
  systematic uncertainties are included."
- **Sin incertidumbre** y **sin orden perturbativo declarado** (aMC@NLO sugiere NLO, pero
  ninguna fuente leída lo afirma).
- **No consta** si la σ es inclusiva en decaimientos, ni el tratamiento de espines
  (MadSpin) en el valor, ni el corte en pT/η de los quarks b.
- **El archivo que se usará es un único suelto** de los 18 del registro (decisión del
  usuario): la σ es del proceso completo, no del subconjunto estadístico del archivo.
- No se pudo contrastar con `StandardModelCrossSectionsat8TeV` (HTTP 401) ni con el artículo
  de producción (PDF no legible).

## Uso en el análisis

Fase 3 (Processing). Responde a "¿con qué σ se normaliza el fondo ttbar de 31102?".
**No se aplica**: el análisis es cualitativo y este agente no normaliza. Queda documentado
como 225.2 pb para `TTbar` (aMC@NLO + Herwig, MadSpin), **sin incertidumbre ni orden
declarado**, con la equivalencia a 31102 marcada como inferencia.
