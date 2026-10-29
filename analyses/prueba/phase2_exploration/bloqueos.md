# Fase 2 — Bloqueos y errores de la sesión

## 0. RESUELTO (2026-10-21): bloqueo por `analysis_config` sin rellenar

El bloqueo descrito en la sección 4 **ya no aplica**. `analyses/prueba/analysis_config`
(modificado hoy) contiene los cuatro campos mínimos exigidos:

- `objetivo_fisico = Búsqueda del bosón de Higgs en el decaimiento H -> tau tau`
- `energia_centro_de_masa_tev = 8`
- `anio = 2012`
- `canal = mu tau_h`

`dataset`, `luminosidad_integrada_pb_minus1` y `variables_de_interes` siguen en `TODO`,
lo que **no impide** ejecutar los pasos 1–5 (búsqueda, viabilidad, disco y propuesta), pero
sí impide fijar la luminosidad integrada de la propuesta. Se ha ejecutado la revalidación
de candidatos sobre esa base; ver `candidatos_datasets.md` (marcado como REVALIDADO).
El resto de este archivo se conserva como historial y **puede estar desactualizado**: en
esta sesión la shell sí permite `df -h` y el CLI `mjfc cms ...` (sigue denegando `ls`,
`du` y el resto de comandos).

## 1. Herramienta de shell bloqueada

Toda ejecución de shell (necesaria para `ls`, `du`, `file`, `.venv/bin/python scripts/mjfc.py ...`)
falla con:

```
{"error":{"type":"permission.rejected","message":"Permission denied: shell"},"content":[]}
```

Comando intentado (literal): `ls -la /home/isaac/Mini-JFC`

Sin shell no se puede:
- ejecutar `cms search` / `cms record` / `cms files` para localizar datasets en el portal CMS Open Data;
- ejecutar `root trees` / `root branches` / `root sample` / `root summary`;
- ejecutar `parquet describe` / `parquet columns` / `parquet summary`;
- usar alternativas `python3 -c` con uproot, ni `file`/`du`.

## 2. Acceso fuera del workspace denegado

`glob` sobre `/home/isaac` con patrones `**/*.root` y `**/*.parquet`:

```
{"error":{"type":"permission.rejected","message":"Permission denied: external_directory"},"content":[]}
```

Por tanto no se puede comprobar si hay datasets descargados en `$HOME` o en `/tmp`.

## 3. Sin datasets locales

Búsqueda `**/*` (incluyendo ocultos) en `/home/isaac/Mini-JFC`: 0 archivos `.root`, 0 `.parquet`,
0 ficheros de datos en cualquier otro formato (solo código, tests, plantillas y `.venv`).

## Nota de política

No se reintentó ningún comando ni se alteraron rutas/argumentos, según las reglas del subagente.

---

## 4. Bloqueo de la ronda solicitada (pasos 1–5): `analysis_config` sin rellenar

Fecha: 2026-10-21. Petición recibida: ejecutar los pasos 1–5 del flujo estándar
(leer config → buscar candidatos → clasificar viabilidad → comprobar disco → escribir
`candidatos_datasets.md`) y detenerse antes de cualquier descarga.

Estado real de `analyses/prueba/analysis_config` (leído completo, 11 líneas): **todos los
campos de contenido siguen en `TODO`**.

Campos clave exigidos por el flujo y su estado:

| Campo exigido | Clave en el config | Valor actual | Estado |
|---|---|---|---|
| Proceso físico | `objetivo_fisico` | `TODO` | **Falta** |
| Energía de colisión | `energia_centro_de_masa_tev` | `TODO` | **Falta** |
| Año | (no existe clave propia; no consta en `notas`) | `notas = TODO` | **Falta** |
| Canal | (no existe clave propia; no consta en `notas`) | `notas = TODO` | **Falta** |

Otros campos también vacíos: `nombre`, `dataset`, `luminosidad_integrada_pb_minus1`,
`variables_de_interes`. Además `fase_actual = phase1_strategy`, es decir, el propio config
declara que la fase 1 (estrategia) no está cerrada.

Comprobación cruzada: `analyses/prueba/prompt.md` también tiene `## Objetivo dado por el
usuario` y `## Instrucciones` en `TODO`, por lo que no hay ninguna fuente autorizada de la
que tomar los cuatro campos.

### Consecuencia

- Paso 1 (leer y resumir config): **no ejecutable**, no hay parámetros que resumir.
- Paso 2 (buscar candidatos): **no ejecutado**. Cualquier búsqueda implicaría elegir
  proceso/energía/año, lo que está prohibido.
- Paso 3 (clasificar viabilidad): **no ejecutado**, no hay candidatos nuevos que clasificar.
- Paso 4 (comprobar disco): **no ejecutado**; además no habría subconjunto que dimensionar.
- Paso 5 (escribir `candidatos_datasets.md`): **no ejecutado**. El archivo existente
  (H→ττ μτ_h, 8 TeV, 2012, de una sesión anterior) **no se ha modificado ni sobrescrito**.

No se ha ejecutado ninguna descarga ni ninguna tool `cms`/`root`/`parquet` en esta ronda.

### Qué hace falta para desbloquear

Que el agente planificador rellene en `analysis_config`, como mínimo:
`objetivo_fisico`, `energia_centro_de_masa_tev` y, en `notas` (o clave equivalente),
el **año** y el **canal**; y preferiblemente `dataset`, `luminosidad_integrada_pb_minus1`
y `variables_de_interes`.

### Nota sobre el `candidatos_datasets.md` existente

El archivo actual describe un análisis H→ττ en el canal μτ_h a 8 TeV (2012) y una propuesta
de subconjunto mínimo (~3.5–10 GB según se incluyan o no muestras AODSIM). Se deja intacto
porque **no está respaldado por el config vigente**; si el planificador confirma que ese es
el análisis buscado, habría que volcar esos parámetros al config y entonces reutilizar o
revalidar esa propuesta.

---

## 5. BLOQUEO ACTIVO (2026-10-27): descarga autorizada interrumpida por fallo de red

Contexto: el agente padre autorizó 4 descargas concretas en `data/prueba_d/` (recids 12353,
12355, 12358, 31102; ≈32.88 GB), en serie y con `--max-bytes 12000000000`.

Secuencia real:

1. **12353 `DYJetsToLL.root`** → **OK** (`cms download` devolvió `data/prueba_d/DYJetsToLL.root`).
2. **12355 `W1JetsToLNu.root`** → **FALLO de tool**:
   `mjfc cms download: error: fallo de red al descargar https://opendata.cern.ch/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/W1JetsToLNu.root: The read operation timed out` (código de salida 1).
3. **12358 y 31102** → **no ejecutadas** (parada obligatoria tras el fallo).

### Consecuencia

- **No hay datos de colisiones** (`Run2012B_TauPlusX`, 12358) ni **fondo W+jets** (12355) ni
  **ttbar** (31102) en local. Sin ellos no se puede contrastar señal con fondo ni con datos
  observados en el canal μτ_h.
- `data/prueba_d/DYJetsToLL.root` (12353) **está descargado pero no explorado**: al detenerse
  la sesión no se ejecutaron `root trees/branches/summary` sobre él, así que su estructura
  (árboles, ramas, events) es **desconocida** y no figura en `inventario_datos.md` §1–§7
  (solo hay un aviso en §8).
- No se completaron los puntos 3–4 ni 6 de la instrucción del padre (exploración de los
  archivos nuevos, comprobación de ramas de trigger/muón/tau en 12358, lista de huecos de
  `variables_de_interes`).

### Qué hace falta para desbloquear

1. Autorización para **reintentar** la descarga de 12355 (el fallo fue de red, no de
   argumentos) y, si se autoriza, continuar con 12358 y 31102.
2. O bien autorización explícita para **saltar** 12355 y descargar solo 12358 y 31102.
3. Después, reanudar la exploración de 12353 y de los archivos que se descarguen.

### Restricciones respetadas

- No se reintentó ningún comando ni se cambiaron rutas/argumentos.
- `data/prueba/DYJetsToLL.root` (81 264 640 B, resto incompleto de la ejecución cancelada) no
  se ha usado, leído, movido ni sobrescrito.
- No se descargó ningún `*_merged.root` ni nada fuera de los 4 archivos autorizados.
