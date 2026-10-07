# Mini-JFC

Mini-JFC es una versión educativa y simplificada, inspirada en el framework JFC (Just Furnish Context, MIT), para análisis autónomos de física de altas energías, especializada en **CMS Open Data**. Es un proyecto propio: no copia código de JFC.

## Cómo funciona

- El usuario da principalmente un **objetivo físico**: qué medir o estudiar.
- A partir de él, los agentes buscarán de forma autónoma **literatura, documentación y datasets**.
- La literatura recuperada se guardará en `analyses/<nombre>/` y se registrará en `retrieval_log.md`.

## Separación de responsabilidades

- **src/agents/** — deciden y ejecutan: orchestrator (coordina las fases), planner, literature_agent, data_agent, analyst, reviewer.
- **src/tools/** — capacidades que los agentes usan: web, literatura, CMS Open Data, Parquet, ROOT, análisis.
- **src/methodology/** — cómo se desarrolla el análisis (fases y workflow).
- **src/conventions/** — convenciones de CMS Open Data.

## Las 5 fases

1. **Strategy**: entender el objetivo, crear el plan y determinar qué información necesita el sistema.
2. **Exploration**: buscar datasets, explorar ROOT/Parquet e identificar variables.
3. **Processing**: ejecutar el análisis, aplicar selecciones y producir histogramas y resultados.
4. **Validation**: revisar código, física y resultados; permite volver a fases anteriores.
5. **Documentation**: documentar metodología y resultados, registrar la literatura usada y generar el informe final.

Ver `src/methodology/phases.md` y `src/methodology/workflow.md`.

## Crear un análisis

```
python src/scaffold_analysis.py <nombre>
```

Crea `analyses/<nombre>/` con las plantillas, las copias de agents/conventions/methodology y las carpetas de las 5 fases.
