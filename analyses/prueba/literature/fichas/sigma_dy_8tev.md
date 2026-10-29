# Ficha — Sección eficaz de DY → ℓℓ, 8 TeV (recid 12353, `DYJetsToLL.root`)

Pregunta: ¿qué σ (en pb), con qué incertidumbre y para qué proceso exacto, corresponde a la
muestra `DYJetsToLL` de 12353, para poder escalarla?

## Referencia

1. **CERN Open Data, registro 12353** — "DYJetsToLL dataset in reduced NanoAOD format for
   education and outreach", Wunsch, Stefan (2019).
   DOI `10.7483/OPENDATA.CMS.SRRA.2GON`. URL: https://opendata.cern.ch/record/12353
2. **Código del análisis de referencia de CERN Open Data** (única fuente leída que da el
   valor numérico de σ). `skim.cxx`, rama `2012`, repositorio
   `cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis`.
   - URL navegable: https://github.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/blob/2012/skim.cxx
   - Texto plano leído: https://raw.githubusercontent.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/2012/skim.cxx
   - Tipo: **código fuente** (no artículo revisado). Sin `arxiv_id`, sin DOI.
3. **CERN Open Data, registro 12350** — "Analysis of Higgs boson decays to two tau leptons
   using data and simulation of events at the CMS detector from 2012", Wunsch, Stefan (2019).
   DOI `10.7483/OPENDATA.CMS.GV20.PR5T`. URL: https://opendata.cern.ch/record/12350
   (registro que enlaza el repositorio de código como "Source code repository").
4. **`README.md` del mismo repositorio**, rama `2012`:
   https://raw.githubusercontent.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/2012/README.md

## Qué se leyó

- Registro 12353: **página HTML completa** (descripción, dataset padre, "Dataset
  characteristics", semántica de variables, validación).
- `skim.cxx`: **texto completo del archivo**, en particular el bloque `std::map
  eventWeights` donde está el valor de σ.
- Registro 12350 y `README.md`: **texto completo** de ambos (contexto y advertencia de
  validez).
- **No se leyó** el twiki `StandardModelCrossSectionsat8TeV` (HTTP 401) ni ningún artículo
  de producción (los PDF no son legibles por este modelo).

## Valores y cortes

| valor | unidad | cita textual | localización | estado |
|---|---|---|---|---|
| **3503.7** | pb | `{"DYJetsToLL", 3503.7 / 30458871.0 * integratedLuminosity},` | `skim.cxx`, `std::map eventWeights`, entrada `DYJetsToLL` | **dato publicado en código** (constante del análisis de referencia) |
| incertidumbre de σ | — | — | — | **`no consta`** (el archivo no da error teórico ni de PDF) |
| 30 458 871 | eventos generados | "30458871 events. 1 file. 8.6 GiB in total." | registro 12353, "Dataset characteristics" | dato publicado en la ficha del registro |
| 30 458 871.0 | denominador de N_gen | `3503.7 / 30458871.0` | `skim.cxx`, misma línea | dato publicado en código; **coincide exactamente** con el nº de eventos del registro 12353 → la σ corresponde a este archivo |
| proceso: `DYJetsToLL_M-50` | — | "This dataset was derived from: /DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_RD1_START53_V7N-v1/AODSIM" | registro 12353, "Related datasets" | dato publicado en la ficha (nombre del dataset padre) |
| m_ℓℓ > 50 GeV | — | — | se deduce del sufijo `M-50` del nombre del dataset padre | **inferencia** (la ficha no enuncia el corte) |
| LO (madgraph) | — | — | se deduce de `madgraph` en el nombre del dataset padre | **inferencia**; el orden no consta en ninguna fuente leída |
| inclusivo en jets extra | — | — | el nombre no lleva sufijo de multiplicidad de jets (a diferencia de `W1Jets`, `W2Jets`) | **inferencia**; `no consta` el número de jets extra permitidos |
| Z/γ* inclusivo | — | — | — | **`no consta`** (ninguna fuente leída lo afirma) |

**Proceso exacto que cubre la muestra, según lo leído:** muestra denominada `DYJetsToLL`
cuyo dataset padre es `/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/...` a 8 TeV. Que
sea Drell-Yan con masa del par leptónico por encima de 50 GeV y generación madgraph a LO son
**inferencias del nombre**, no afirmaciones de la ficha. La muestra contiene **tanto Z→ττ
como Z→ℓℓ**: el análisis de referencia la procesa dos veces, como `ZLL` y como `ZTT`,
separadas por `gen_match` (`("DYJetsToLL", "ZLL")`, `("DYJetsToLL", "ZTT")` en
`histograms.py`), no por muestra distinta.

## Limitaciones

- **Origen del valor: `skim.cxx` (código educativo), NO la ficha del recid 12353 ni una
  publicación.** 3503.7 pb es una constante escrita a mano en ese archivo; ninguna de las
  fuentes oficiales leídas lo respalda.
- **La ficha del recid 12353 no declara sección eficaz**: su texto se limita a "Dataset in
  reduced NanoAOD format for education and outreach derived from the primary dataset in AOD
  format linked below." No hay campo de σ ni de incertidumbre.
- El valor 3503.7 pb procede de una **constante escrita a mano en código educativo**, no de
  una publicación ni de un twiki oficial. El `README.md` advierte: "the analysis is not
  validated and should be used only for educational purposes, in particular since no
  systematic uncertainties are included."
- **Sin incertidumbre** (ni PDF, ni escala, ni orden superior): no se puede asignar error a
  la normalización con esta fuente.
- **Sin orden perturbativo declarado**: "madgraph" indica el generador, no el orden. No se
  puede afirmar LO/NLO con las fuentes leídas.
- **No consta** si la σ es para Z/γ* inclusivo, ni el corte exacto en m_ℓℓ, ni el tratamiento
  de jets extra. Cualquier uso de 3503.7 pb debe declararse como "σ del análisis de
  referencia para `DYJetsToLL` (M-50, madgraph)", sin más precisiones.
- No se pudo contrastar con `StandardModelCrossSectionsat8TeV` (HTTP 401) ni con el artículo
  de producción (PDF no legible).

## Uso en el análisis

Fase 3 (Processing). Responde a la pregunta "¿con qué σ se normaliza el fondo DY de 12353?".
**No se aplica** aquí: el análisis es cualitativo (forma, área unitaria) y este agente no
normaliza. Queda documentado como 3503.7 pb **sin incertidumbre y sin orden declarado**, para
que el planner/analyst decidan si lo usan o exigen antes una fuente oficial.
