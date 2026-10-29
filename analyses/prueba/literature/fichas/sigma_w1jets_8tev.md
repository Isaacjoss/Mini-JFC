# Ficha — Sección eficaz de W+jets, `W1JetsToLNu`, 8 TeV (recid 12355)

Pregunta: ¿qué σ (en pb), con qué incertidumbre y para qué proceso exacto, corresponde a la
muestra `W1JetsToLNu` de 12355, para poder escalarla?

## Referencia

1. **CERN Open Data, registro 12355** — "W1JetsToLNu dataset in reduced NanoAOD format for
   education and outreach", Wunsch, Stefan (2019).
   DOI `10.7483/OPENDATA.CMS.QQZ2.FJZ3`. URL: https://opendata.cern.ch/record/12355
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

- Registro 12355: **página HTML completa** (descripción, dataset padre, "Dataset
  characteristics", semántica de variables, validación).
- `skim.cxx`: **texto completo del archivo**, bloque `std::map eventWeights`.
- Registro 12350 y `README.md`: **texto completo** (contexto y advertencia de validez).
- **No se leyó** el twiki `StandardModelCrossSectionsat8TeV` (HTTP 401) ni ningún artículo
  de producción (PDF no legible por este modelo).

## Valores y cortes

| valor | unidad | cita textual | localización | estado |
|---|---|---|---|---|
| **6381.2** | pb | `{"W1JetsToLNu", 6381.2 / 29784800.0 * integratedLuminosity},` | `skim.cxx`, `std::map eventWeights`, entrada `W1JetsToLNu` | **dato publicado en código** (constante del análisis de referencia) |
| incertidumbre de σ | — | — | — | **`no consta`** |
| 29 784 800 | eventos generados | "29784800 events. 1 file. 10.0 GiB in total." | registro 12355, "Dataset characteristics" | dato publicado en la ficha del registro |
| 29 784 800.0 | denominador de N_gen | `6381.2 / 29784800.0` | `skim.cxx`, misma línea | dato publicado en código; **coincide exactamente** con el nº de eventos del registro 12355 → la σ corresponde a este archivo |
| proceso: `W1JetsToLNu` | — | "This dataset was derived from: /W1JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM" | registro 12355, "Related datasets" | dato publicado en la ficha (nombre del dataset padre) |
| W→ℓν + exactamente 1 jet (exclusiva) | — | — | se deduce del nombre `W1JetsToLNu` (frente a `W2JetsToLNu`, `W3JetsToLNu`, que el análisis de referencia trata como muestras separadas) | **inferencia**; la ficha no enuncia la multiplicidad de jets |
| LO (madgraph) | — | — | se deduce de `madgraph` en el nombre del dataset padre | **inferencia**; el orden no consta en ninguna fuente leída |

**Proceso exacto, según lo leído:** muestra `W1JetsToLNu` con dataset padre
`/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/...` a 8 TeV. Que sea W→ℓν con **exactamente un jet
extra, inclusiva en el sabor del leptón**, es una **inferencia del nombre**: el "1" indica la
multiplicidad de partones/jets y `ToLNu` que el W decae a un leptón y un neutrino (los tres
sabores, ya que no hay sufijo `ToMuNu`/`ToENu`). La ficha no lo declara.

## Limitaciones

- **Origen del valor: `skim.cxx` (código educativo), NO la ficha del recid 12355 ni una
  publicación.** 6381.2 pb es una constante escrita a mano en ese archivo; ninguna de las
  fuentes oficiales leídas lo respalda.
- **La ficha del recid 12355 no declara sección eficaz**: solo "Dataset in reduced NanoAOD
  format for education and outreach derived from the primary dataset in AOD format linked
  below."
- El valor 6381.2 pb procede de una **constante en código educativo**; `README.md`: "the
  analysis is not validated and should be used only for educational purposes, in particular
  since no systematic uncertainties are included."
- **Sin incertidumbre** y **sin orden perturbativo declarado**.
- **No consta** el corte en pT/η de los partones al generar, ni si el "1 jet" es a nivel de
  partones o de jets reconstruidos. Tampoco consta el rango de masa del W.
- El análisis usa **solo W1Jets** (decisión del usuario); esta σ **no** cubre W2/W3, de modo
  que la suma de W+jets queda incompleta por construcción. No se propone completarla.
- No se pudo contrastar con `StandardModelCrossSectionsat8TeV` (HTTP 401) ni con el artículo
  de producción (PDF no legible).

## Uso en el análisis

Fase 3 (Processing). Responde a "¿con qué σ se normaliza el fondo W+jets de 12355?".
**No se aplica**: el análisis es cualitativo y este agente no normaliza. Queda documentado
como 6381.2 pb para `W1JetsToLNu` (1 jet, madgraph), **sin incertidumbre ni orden declarado**.
