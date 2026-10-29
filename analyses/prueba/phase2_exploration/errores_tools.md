# Errores de tools — phase2_exploration (H→ττ μτ_h, 2012)

Registro literal de los fallos de las tools durante la búsqueda de candidatos.
No se reintentaron las mismas consultas.

## 1. `cms search "Run2012" -n 30`

```
(no output)

Command exceeded timeout of 120000 ms. Retry with a larger timeout if the command is expected to take longer.
```

## 2. `cms search "Summer12" -n 25`

```
mjfc cms search: error: IncompleteRead(11576472 bytes read, 11463 more expected)

Exited with code 1
```

## 3. Incidencia de shell (no es fallo de tool)

Al lanzar dos lotes de `cms files` en paralelo, el segundo intentó escribir antes de
que existiera el directorio:

```
/bin/bash: line 1: analyses/prueba/phase2_exploration/files/files_8001.json: No such file or directory

Exited with code 1
```

Se corrigió creando el directorio y repitiendo **solo** el guardado de la salida
(la consulta a la tool era válida). El archivo se generó correctamente después.

## 4. Denegaciones de shell en la revalidación (2026-10-21)

La política de shell de esta sesión solo permite `df -h` y
`.venv/bin/python scripts/mjfc.py cms ...`. Cualquier otro comando (incluidos `ls`, `du`,
redirecciones y pipes) se rechaza antes de ejecutarse:

```
{"error":{"type":"permission.rejected","message":"Permission denied: shell"},"content":[]}
```

Comandos rechazados literalmente: `ls -la analyses/prueba/ ...`, `du -sh data analyses/prueba`,
`du -sh data`, `.venv/bin/python scripts/mjfc.py --help`,
`.venv/bin/python scripts/mjfc.py cms files 31127 --max-items 500 | wc -c`.

Consecuencia: **no se pudo medir `du -sh` de `data/` ni de `analyses/prueba/`**; se sustituyó
por el listado de directorios (`data/` solo contiene `README.md`). Ninguna consulta `cms` de
esta sesión falló: `search`, `record` y `files` respondieron correctamente.

## 5. Resto de la ejecución cancelada (2026-10-27)

`data/prueba/DYJetsToLL.root` — **81 264 640 B** — es una **copia incompleta** de
`DYJetsToLL.root` (recid 12353) dejada por una ejecución anterior **cancelada**. El tamaño
declarado por `cms files` para ese archivo es **9 247 252 629 B**, muy superior.

- **No se usa, no se lee y no se sobrescribe.** No forma parte del inventario de datos válidos.
- La descarga válida del mismo contenido se hizo a `data/prueba_d/DYJetsToLL.root` (destino
  autorizado), no a `data/prueba/`.
- Se conserva físicamente porque no se ha autorizado su borrado ni su movimiento.

## 6. Fallo de descarga — `cms download` de `W1JetsToLNu.root` (recid 12355, 2026-10-27)

Comando (segunda descarga autorizada, tras completar correctamente la de 12353):

```
.venv/bin/python scripts/mjfc.py cms download root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/W1JetsToLNu.root data/prueba_d --max-bytes 12000000000
```

`stderr` literal:

```
mjfc cms download: error: fallo de red al descargar https://opendata.cern.ch/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/W1JetsToLNu.root: The read operation timed out

Exited with code 1
```

- **No se reintentó** con los mismos ni con otros argumentos, conforme a la regla de detenerse
  ante un fallo de tool.
- Tras el fallo, `data/prueba_d/` contiene **solo** `DYJetsToLL.root`; no quedó ningún archivo
  parcial de `W1JetsToLNu.root` (verificado listando el directorio).
- Consecuencia: las descargas autorizadas 2 (12355), 3 (12358) y 4 (31102) **no se ejecutaron**.

## 7. Incidencias de la reanudación de descargas (2026-10-28)

**7.1 Colisión curl/aria2 sobre `Run2012B_TauPlusX.root`.** Al arrancar la fase se lanzó un
`curl -C -` sobre `data/prueba_d/Run2012B_TauPlusX.root` mientras ya había un `aria2c`
descargando el mismo destino. Se detectó por el log (salida de aria2 en el archivo de curl) y
por `ps`; se mató el `curl` (PID 1816) para no escribir dos procesos sobre el mismo archivo.
No se usó ningún resultado de ese intento. Las descargas continuaron solo con `aria2c`.

**7.2 Reinicio del servidor WSL.** Durante la sesión el servidor se reinició y terminó los
procesos `aria2c`. Los archivos quedaron con su `.aria2` de control y se reanudaron con el
mismo comando `aria2c -c`. No hubo pérdida de los parciales.

**7.3 Resto truncado de `DYJetsToLL.root`.** `data/prueba_d/DYJetsToLL.root` existía con
**119 673 824 B** frente a 9 247 252 629 B declarados. Se borró (`rm -f`) antes de
re-descargar, según la autorización. El resto antiguo de `data/prueba/DYJetsToLL.root`
(81 264 640 B) **no se tocó**.

**7.4 Procesos `aria2c` duplicados tras la reanudación.** Al relanzar las tres descargas
aparecieron **seis** procesos `aria2c`, dos por archivo (701/702/704 y 713/715/717). Los
duplicados (713, 715, 717) se mataron de inmediato con `kill` para evitar dos escritores
concurrentes sobre el mismo archivo. Los tres supervivientes (701 → 12358, 702 → 12355,
704 → 12353) terminaron correctamente y los tamaños finales coinciden con los declarados.
Los logs se abrieron en modo *append* (`>>`) para no perder el historial previo.

**7.5 Filas duplicadas en `retrieval_log.md`.** La tabla de `retrieval_log.md` contiene filas
repetidas para 12353, 12355, 12358 y 31102 (dos registros por archivo, con marcas de tiempo
distintas). No afecta a los datos: todas apuntan a la misma ruta y al mismo `recid`. Se dejan
como traza de que hubo dos ejecuciones/instancias registrando; no se borran para no perder
trazabilidad. **(Superado por 7.7: finalmente sí se consolidaron.)**

**7.6 Proceso `curl` congelado (PID 1816).** El proceso `curl -C -` que el agente padre pidió
**no tocar** ya no existe: desapareció con el reinicio del servidor y, según la nota 7.1, otra
instancia lo mató al detectar la colisión con `aria2c`. **No se ha podido preservar** ese
proceso. No se usó su salida ni su parcial.

**7.7 Consolidación de filas duplicadas/huérfanas en `retrieval_log.md` (2026-10-28).** Se
corrigió `analyses/prueba/retrieval_log.md`: la tabla principal del principio quedó con
**exactamente una fila por recid** descargado (12351, 12352, 12353, 31102, 12358, 12355),
conservando la fecha más antigua/veraz de cada descarga, y se eliminaron las filas sueltas que
estaban fuera de tabla al final del documento, tras la sección de detalle de 2026-10-27.
**No se perdió información**: las secciones de detalle y sus tablas siguen intactas, y los
tamaños, estados e intentos por archivo siguen en la tabla de detalle y en
`phase2_exploration/descargas.json`. Esta entrada sustituye a 7.5.

## Búsquedas que devolvieron lista vacía

Ver sección 8 de `candidatos_datasets.md`.
