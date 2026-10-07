# Convenciones CMS Open Data

Convenciones que seguirán los agentes y las tools al trabajar con CMS Open Data. Borrador.

## Nomenclatura de datasets
TODO

## Unidades
TODO

## Convenciones de CMS Open Data
TODO

## Búsqueda en CMS Open Data

### Nombres de dataset

Los datasets simulados de CMS siguen el patrón `/Proceso_Masa_Energia_Generador/Campaña/FORMATO`, por ejemplo:

- `/ZHToTauTau_M125_CP5_13TeV-powheg-pythia8/RunIISummer20UL16DRv1-PU2016_106X/`
- `/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17DR/`

Es decir: proceso físico (HToTauTau, TT, …), masa, energía del collider y generador Monte Carlo; después la campaña de producción (RunIISummer…, RunIIFall…) y el formato del fichero.

### Comodines

El portal hace coincidencia exacta: un término sin comodines inicial no encuentra nada (`HToTauTau*` → 0 resultados).
Los comodines deben **envolver** el término: usa `*HToTauTau*`, no `HToTauTau*`.
La tool `search_records` envuelve automáticamente los términos simples como `*término*`; si la consulta ya lleva `*` o `:`, se respeta tal cual.

### Formatos y tamaños

- `AODSIM` / `AOD`: formatos completos; un dataset de estos puede pesar **GB** (incluso cientos de GB). Comprueba `size` antes de descargar.
- `NANOAODSIM` / `NanoAOD`: formato comprimido y mucho **más ligero**; es el recomendado para análisis rápidos.

### Energías de centro de masa

Hay datasets de **8 TeV (2012)** y de **13 TeV** (Run 2, 2015-2018); los datos de 2010-2011 son de 7 TeV.
Comprueba la energía (`collision_energy`) del registro antes de combinar muestras.

### Filtros de la API

El parámetro `f=experiment:CMS` de la URL está **ignorado** por opendata.cern.ch; el filtro correcto va dentro de `q`, por ejemplo:

```
q=(*tautau*) AND experiment:CMS AND type.primary:Dataset
```

`search_records` construye ese `q` y, además, filtra en cliente los registros cuyo `experiment` no coincida.
