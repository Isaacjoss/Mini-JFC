
# Criterios de salida por fase

Cada criterio debe poder comprobarse leyendo archivos de `analyses/<nombre>/`.

## 1. Strategy
- `analysis_config` tiene `objetivo_fisico`, `energia_centro_de_masa_tev`, `anio` y `canal` distintos de `TODO`.
- Existe `phase1_strategy/strategy.md` con: objetivo, alcance (qué incluye y qué NO), datasets necesarios, selección prevista, variables de interés, normalización, método estadístico, riesgos y preguntas abiertas.
- `strategy.md` declara el alcance elegido (cualitativo o estadístico) tal como lo fija `prompt.md`.
- Todo dato no confirmado en fuente aparece marcado como "inferido" o "pendiente".

## 2. Exploration
- `phase2_exploration/candidatos_datasets.md` tiene ficha completa por candidato, la propuesta de subconjunto y el estado real de las descargas (coherente con `retrieval_log.md`).
- Cada tamaño citado en la propuesta tiene su salida de `cms files` o `cms record` guardada en `phase2_exploration/files/`, o está marcado "no verificado".
- `phase2_exploration/inventario_datos.md` lista árboles y ramas de cada archivo descargado, tal como los devolvieron las tools, con el nº total de eventos y la cobertura de cada resumen.
- Cada descarga tiene su fila en `retrieval_log.md`, y el tamaño registrado coincide con el declarado en la salida guardada de `cms files`.
- Hay una lista de huecos: variables de `variables_de_interes` que no están en los datos (pesos, normalización, etc.).
- Las advertencias de las tools están recogidas.

## 3. Processing
- Existe código en `phase3_processing/` y un comando documentado que lo reproduce.
- La selección aplicada coincide con `strategy.md`; cualquier desviación está justificada.
- Hay cutflow, histogramas y resultados guardados como archivos.
- La normalización (sección eficaz, luminosidad, eventos generados) está documentada con su fuente. Ningún valor aparece sin fuente.

## 4. Validation
- Existe `phase4_validation/validation_report.md` con las comprobaciones hechas y su resultado.
- Cada problema abierto indica a qué fase se vuelve (1, 2 o 3).
- Los resultados de fase 3 se reprodujeron o contrastaron con una referencia citada.

## 5. Documentation
- Existe un documento final en `phase5_documentation/` con metodología, resultados, limitaciones y referencias.
- Cada cifra del documento remite a un archivo de resultados.
- Las fuentes citadas constan en `retrieval_log.md`.
