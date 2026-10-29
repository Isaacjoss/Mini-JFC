# Ficha — Luminosidad integrada de Run2012B (datos 12358, `Run2012B_TauPlusX`)

Pregunta: ¿cuál es la luminosidad integrada del periodo Run2012B, con incertidumbre y
condición, para poder escalar los datos de 12358?

## Referencia

1. **Código del análisis de referencia de CERN Open Data** (única fuente que da un valor
   numérico para Run2012B). Archivo `skim.cxx`, rama `2012`, repositorio
   `cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis`.
   - URL navegable: https://github.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/blob/2012/skim.cxx
   - URL del texto plano leído: https://raw.githubusercontent.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/2012/skim.cxx
   - Autoría del archivo: `no consta` en el propio archivo (el registro 12350 atribuye el
     análisis a "Wunsch, Stefan").
   - Año: `no consta` en el archivo; el registro que lo enlaza (12350) es de 2019.
   - Tipo: **código fuente**, no artículo revisado por pares. Sin `arxiv_id`, sin `recid`,
     sin DOI.
2. **CERN Open Data, registro 12358** — "Run2012B_TauPlusX dataset in reduced NanoAOD format
   for education and outreach", Wunsch, Stefan (2019).
   DOI `10.7483/OPENDATA.CMS.H95X.G286`. URL: https://opendata.cern.ch/record/12358
3. **CMS HIG-13-004, página pública de resultados** — "Evidence for the 125 GeV Higgs boson
   decaying to a pair of tau leptons", CMS Collaboration, 20 January 2014, J. High Energy
   Phys. 05 (2014) 104. URL:
   https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-13-004/index.html
   Artículo completo: arXiv:1401.5041 (PDF descargado en
   `analyses/prueba/literature/pdfs/1401.5041.pdf`, **no legible** por este modelo; su
   contenido no se cita).
4. **INSPIRE-HEP, registro `recid` 1260876** — "CMS Luminosity Based on Pixel Cluster
   Counting - Summer 2013 Update", CMS Collaboration, 2013. Número de reporte
   **`CMS-PAS-LUM-13-001`**. URL: https://inspirehep.net/literature/1260876
   - PDF asociado en INSPIRE: `LUM-13-001-pas.pdf`
     (https://inspirehep.net/files/eac6ba954e070f828f9f1bd9830085fe) — **no descargado ni
     leído** (este modelo no puede leer PDF; ver Limitaciones).
   - Solo **metadatos**: no se recuperó el abstract (ver "Qué se leyó").

## Qué se leyó

- `skim.cxx`: **texto completo del archivo** (leído por HTTP como texto plano desde
  `raw.githubusercontent.com`, rama `2012`). Es la fuente del valor de luminosidad.
- Registro 12358: **página HTML completa** del registro (metadatos, "Dataset
  characteristics", semántica de variables, sección "How were these data validated?").
  No se leyó ningún PDF asociado.
- HIG-13-004: **solo el resumen/abstract** de la página pública de resultados (texto HTML).
  El artículo completo no se pudo leer (ver Limitaciones).
- `CMS-PAS-LUM-13-001`: **solo metadatos de INSPIRE** (título, número de reporte, año y
  existencia del PDF `LUM-13-001-pas.pdf`). No se recuperó el abstract: la página HTML de
  INSPIRE devuelve "INSPIRE You need to enable JavaScript to run this app." y la respuesta
  JSON de la API (`/api/literature/1260876`) quedó truncada antes del campo de abstract. El
  PDF no se descargó (no legible por este modelo).
- No se leyó el twiki `StandardModelCrossSectionsat8TeV` (HTTP 401).

## Valores y cortes

| valor | unidad | cita textual | localización | estado |
|---|---|---|---|---|
| **4.412** | fb⁻¹ | `//const float integratedLuminosity = 4.412 * 1000.0; // Run2012B only` | `skim.cxx`, bloque de declaración de `integratedLuminosity`, inmediatamente antes de `std::map eventWeights` | **dato publicado en código** (constante del análisis de referencia); no es valor de artículo revisado |
| 7.055 | fb⁻¹ | `//const float integratedLuminosity = 7.055 * 1000.0; // Run2012C only` | misma línea siguiente de `skim.cxx` | dato publicado en código (contexto; no es Run2012B) |
| 11.467 | fb⁻¹ | `const float integratedLuminosity = 11.467 * 1000.0; // Run2012B+C` | línea activa del mismo bloque de `skim.cxx` | dato publicado en código (contexto: valor que usa el análisis de referencia; **no** es Run2012B) |
| 4412 | pb⁻¹ | `4.412 * 1000.0` | misma línea de `skim.cxx`: el código multiplica por 1000 para pasar de fb⁻¹ a pb⁻¹ (la σ se usa en pb) | **inferencia aritmética** sobre un valor del código: la conversión la hace el propio archivo, pero la cifra "4412" no aparece escrita |
| incertidumbre de 4.412 | — | — | — | **`no consta`** (el archivo no da error ni incertidumbre) |
| condición (validated / delivered) | — | — | — | **`no consta`** para el valor 4.412; el código solo lo etiqueta `Run2012B only` |
| **19.7** | fb⁻¹ | "The dataset corresponds to an integrated luminosity of 4.9 fb⁻¹ at a centre-of-mass energy of 7 TeV, and 19.7 fb⁻¹ at 8 TeV." | HIG-13-004, página pública de resultados, **Abstract** | dato publicado (resumen) — **es el total de 8 TeV del análisis HIG-13-004, NO Run2012B** |
| 4.9 | fb⁻¹ | misma frase | HIG-13-004, Abstract | dato publicado (resumen) — total a 7 TeV; no aplica a este análisis |
| 35 647 508 | eventos | "35647508 events. 1 file. 10.2 GiB in total." | registro 12358, sección "Dataset characteristics" | dato publicado en la ficha del registro (no es luminosidad) |
| — | — | "These data were derived from the primary datasets linked below using only the validated runs. No further validation was done for the output." | registro 12358, sección "How were these data validated?" | dato publicado en la ficha; se refiere a la **selección de runs validados**, **no** a la calibración de luminosidad ni a un valor integrado |
| luminosidad integrada de Run2012B | fb⁻¹ | — | — | **`no consta`** en ninguna fuente oficial localizada (CMS-PAS-LUM-13-001 solo metadatos; twiki público solo gráficos; registro 12358 sin valor) |

**Cifra que corresponde a Run2012B:** **4.412 fb⁻¹** (4412 pb⁻¹), de `skim.cxx`
(`// Run2012B only`). Es la única cifra etiquetada explícitamente como Run2012B en las
fuentes leídas y **no está confirmada por ninguna fuente oficial**. El total de 2012 publicado
por CMS en HIG-13-004 es 19.7 fb⁻¹ a 8 TeV y **no** debe usarse como luminosidad de 12358.

## Limitaciones

- **No se localizó ninguna fuente oficial con el desglose por periodo / Run2012B.** Se
  intentaron tres vías: (a) `CMS-PAS-LUM-13-001` vía INSPIRE (solo metadatos: título, número
  de reporte y PDF adjunto; abstract no recuperable y PDF no legible); (b) la página pública
  de luminosidad de CMS (`LumiPublicResults`), cuya sección de 2012 contiene únicamente
  gráficos, sin tabla numérica ni desglose por *run range*; (c) la documentación de CERN Open
  Data (`https://opendata.cern.ch/docs/` → **HTTP 404**, y el intento sobre
  `https://opendata.cern.ch/docs` fue denegado por permisos de la tool). **La única cifra
  disponible para Run2012B es 4.412 fb⁻¹, del código educativo `skim.cxx`, que no está
  validada.**
- **El valor 4.412 fb⁻¹ no procede de una publicación ni de la ficha del recid 12358.**
  Procede de una constante escrita a mano en el código de un análisis **educativo**. El
  `README.md` del mismo repositorio declara: "the analysis is not validated and should be
  used only for educational purposes, in particular since no systematic uncertainties are
  included." Por tanto: valor **no validado por CMS** y **sin incertidumbre**.
- **No consta la condición del número**: no se especifica si es luminosidad entregada
  ("delivered"), registrada ("recorded") o validada para física, ni qué calibración
  (HFOC/PCC) ni qué versión de reconstrucción se usó.
- **No hay desglose por rangos de runs dentro de Run2012B** ni corrección por la
  preselección del primary dataset `/TauPlusX/Run2012B-22Jan2013-v1/AOD` (dispara en tau,
  no en muón). El valor es del periodo completo, no del subconjunto que pase el trigger del
  canal μτ_h.
- **`CMS-PAS-LUM-13-001` no aportó cifra**: se localizó en INSPIRE (recid 1260876, report
  number confirmado, 2013), pero solo se obtuvieron metadatos. El abstract no se pudo
  recuperar (HTML de INSPIRE requiere JavaScript; el JSON de la API quedó truncado antes del
  campo `abstracts`) y el PDF `LUM-13-001-pas.pdf` no es legible por este modelo. Por tanto
  **`no consta`** si ese PAS contiene el desglose por periodo (Run2012A/B/C/D) o solo el total
  de 2012, y tampoco consta la incertidumbre oficial.
- **El twiki público de luminosidad** (`https://twiki.cern.ch/twiki/bin/view/CMSPublic/LumiPublicResults`)
  se leyó completo: la sección "2012 proton-proton 8 TeV collisions" **solo contiene
  gráficos** ("Luminosity versus day", "Cumulative day-by-day integrated luminosity, 2012",
  "Peak day-by-day instantaneous luminosity, 2012", "Average pileup in 2012"), **sin tabla
  numérica** de luminosidad integrada ni desglose por run. El twiki
  `StandardModelCrossSectionsat8TeV` devolvió **HTTP 401**.
- **Consistencia interna, no verificación independiente:** 4.412 + 7.055 = 11.467, que es
  exactamente el valor `Run2012B+C` del mismo archivo. Coherente, pero es la misma fuente.
- **No se puede concluir** que 4.412 fb⁻¹ sea la luminosidad correcta para normalizar 12358
  en este análisis: falta confirmación oficial (PAS/twiki) y falta el efecto de la
  preselección por trigger.

## Uso en el análisis

Fase 3 (Processing). Deja **localizada** una cifra de luminosidad de Run2012B para una
eventual normalización absoluta. **No se aplica** en esta fase: el alcance es cualitativo
(histogramas normalizados a área unitaria) y el `analysis_config` mantiene
`luminosidad_integrada_pb_minus1 = pendiente_de_fuente`, que este agente no puede modificar.
Si el planner decidiera usarla, debería registrar 4412 pb⁻¹ como **valor sin incertidumbre y
no validado**, o exigir antes una fuente oficial.
