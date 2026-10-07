import os
from pathlib import Path

# Create directories
dirs = [
    "src/agents",
    "src/conventions",
    "src/methodology",
    "src/templates/analysis_template",
    "src/tools",
    "analyses",
    "scripts",
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

def write_file(path, content):
    Path(path).write_text(content.strip() + "\n", encoding="utf-8")

# requirements.txt
write_file("requirements.txt", """
# Requirements para Mini-JFC
# Por el momento, el proyecto no cuenta con dependencias externas obligatorias.
# No se utilizan frameworks de agentes (como LangChain, LangGraph o CrewAI) en esta etapa para mantener el diseño simple y transparente.
""")

# README.md
write_file("README.md", """
# Mini-JFC (Just Furnish Context - Versión Educativa)

Mini-JFC es una versión educativa y simplificada inspirada en el framework **JFC (Just Furnish Context, MIT)** para análisis autónomos de física de altas energías, especializada en **CMS Open Data**.

El objetivo de este proyecto es permitir que un conjunto de agentes autónomos colaboren para llevar a cabo un análisis de física de partículas basado en un objetivo físico proporcionado por el usuario (por ejemplo, reconstrucción de bosones, búsqueda de resonancias, etc.). Los agentes buscarán de forma autónoma literatura, documentación y datasets relevantes, y ejecutarán las fases del análisis.

## Estructura del Proyecto

El diseño de Mini-JFC se fundamenta en la clara separación de responsabilidades:
- **Agentes (Deciden y Ejecutan):** Entidades lógicas que toman decisiones estratégicas basándose en sus roles y objetivos.
- **Tools (Capacidades):** Funciones y utilidades específicas que los agentes pueden invocar para interactuar con el entorno (búsqueda web, lectura de datos ROOT, consultas de CMS Open Data, etc.).
- **Methodology (Metodología):** Directrices de cómo se debe estructurar y llevar a cabo el flujo de análisis científico.
- **Conventions (Convenciones):** Reglas específicas del experimento CMS Open Data para asegurar la validez física y técnica.

Toda la literatura científica recuperada de forma autónoma por los agentes se almacenará directamente en el directorio del análisis correspondiente (`analyses/<nombre>/`) y se registrará en el archivo `retrieval_log.md` para mantener la trazabilidad.

## Las 5 Fases del Análisis

El flujo de trabajo se divide en 5 fases secuenciales e iterativas:
1. **Strategy (Estrategia):** Entender el objetivo físico planteado, diseñar un plan de análisis inicial y determinar qué información requiere el sistema.
2. **Exploration (Exploración):** Buscar datasets de CMS Open Data, inspeccionar archivos (ROOT/Parquet), identificar variables físicas clave y verificar la viabilidad de los datos.
3. **Processing (Procesamiento):** Ejecutar el código de análisis, aplicar cortes de selección física, producir histogramas y generar resultados preliminares.
4. **Validation (Validación):** Revisar rigurosamente el código, la consistencia física de los histogramas y los resultados. Permite retroalimentar y regresar a fases anteriores ante inconsistencias.
5. **Documentation (Documentación):** Documentar detalladamente la metodología y hallazgos, registrar la literatura utilizada y generar un informe final comprensible.
""")

# gitkeep files
write_file("analyses/.gitkeep", "")
write_file("scripts/.gitkeep", "")

# src/__init__.py
write_file("src/__init__.py", '"""\\nMini-JFC: Versión educativa y simplificada de JFC para análisis autónomos de CMS Open Data.\\n"""')

# src/agents/__init__.py
write_file("src/agents/__init__.py", '"""\\nMódulo de Agentes de Mini-JFC.\\n"""')

# src/agents files
write_file("src/agents/orchestrator.py", '"""\\nOrchestrator Agent: Coordina las fases del análisis y gestiona el flujo de trabajo general.\\n"""\\n# TODO: not implemented yet')
write_file("src/agents/planner.py", '"""\\nPlanner Agent: Diseña y estructura el plan detallado del análisis de física de partículas.\\n"""\\n# TODO: not implemented yet')
write_file("src/agents/literature_agent.py", '"""\\nLiterature Agent: Determina qué literatura científica buscar, recuperar y utilizar para guiar el análisis.\\n"""\\n# TODO: not implemented yet')
write_file("src/agents/data_agent.py", '"""\\nData Agent: Descubre, explora y valida datasets de CMS Open Data aptos para el análisis físico.\\n"""\\n# TODO: not implemented yet')
write_file("src/agents/analyst.py", '"""\\nAnalyst Agent: Ejecuta las tareas técnicas de procesamiento, cortes físicos y generación de histogramas.\\n"""\\n# TODO: not implemented yet')
write_file("src/agents/reviewer.py", '"""\\nReviewer Agent: Valida el código, la consistencia física de los cortes, histogramas y resultados obtenidos.\\n"""\\n# TODO: not implemented yet')

# src/tools/__init__.py
write_file("src/tools/__init__.py", '"""\\nMódulo de Herramientas (Tools) de Mini-JFC.\\n"""')

# src/tools files
write_file("src/tools/web_tools.py", '"""\\nWeb Tools: Funciones para el acceso genérico a recursos web.\\n"""\\n# TODO: not implemented yet')
write_file("src/tools/literature_tools.py", '"""\\nLiterature Tools: Funciones específicas para la búsqueda, filtrado y recuperación de literatura científica.\\n"""\\n# TODO: not implemented yet')
write_file("src/tools/cms_tools.py", '"""\\nCMS Tools: Utilidades para interactuar con el portal de CMS Open Data y sus metadatos.\\n"""\\n# TODO: not implemented yet')
write_file("src/tools/parquet_tools.py", '"""\\nParquet Tools: Lectura y manipulación eficiente de archivos en formato Apache Parquet.\\n"""\\n# TODO: not implemented yet')
write_file("src/tools/root_tools.py", '"""\\nROOT Tools: Utilidades para la lectura y análisis de archivos ROOT tradicionales (TTree, TH1, etc.).\\n"""\\n# TODO: not implemented yet')
write_file("src/tools/analysis_tools.py", '"""\\nAnalysis Tools: Funciones auxiliares para cómputos estadísticos, ajuste de curvas y generación de gráficos.\\n"""\\n# TODO: not implemented yet')

# src/conventions/cms.md
write_file("src/conventions/cms.md", """
# Convenciones de CMS Open Data

Este documento establece las convenciones y directrices recomendadas para el análisis de datos abiertos de CMS.

## Nomenclatura de Datasets
<!-- TODO: Definir reglas de nombres para MC y Collision Data -->

## Unidades Físicas
<!-- TODO: Definir unidades de energía (GeV), momento (GeV/c), masa (GeV/c²), etc. -->

## Convenciones de Selección y Reconstrucción
<!-- TODO: Directrices para la identificación de leptones, jets, missing ET, etc. -->
""")

# src/methodology/phases.md
write_file("src/methodology/phases.md", """
# Fases de la Metodología de Mini-JFC

El proceso de análisis autónomo se estructura de forma estricta en las siguientes 5 fases:

## 1. Strategy (Estrategia)
- **Objetivo:** Comprender la física detrás del objetivo del usuario, diseñar el plan estratégico del análisis y delimitar qué información bibliográfica o técnica se necesita.
- **Acciones principales:** Conceptualización del proceso, definición de la señal y los fondos, diseño de la estrategia de selección y creación de un plan de trabajo detallado.

## 2. Exploration (Exploración)
- **Objetivo:** Identificar, ubicar y auditar los datos necesarios para el análisis.
- **Acciones principales:** Búsqueda de datasets en el portal CMS Open Data, exploración técnica de archivos ROOT o Parquet, verificación del número de eventos, identificación de las ramas (branches) útiles y confirmación de que el dataset contiene las variables requeridas.

## 3. Processing (Procesamiento)
- **Objetivo:** Ejecutar la reducción de datos y producir los resultados físicos y estadísticos primarios.
- **Acciones principales:** Implementación de la lógica de análisis, aplicación de cortes de selección y aislamiento, procesamiento masivo de datos y generación de histogramas/gráficos de resultados.

## 4. Validation (Validación)
- **Objetivo:** Asegurar la calidad, validez metodológica y consistencia científica de los resultados obtenidos.
- **Acciones principales:** Revisión del código (detección de bugs), auditoría de la física aplicada (comportamiento de histogramas, conservación de energía-momento, etc.) y toma de decisiones para iterar o regresar a fases anteriores en caso de anomalías.

## 5. Documentation (Documentación)
- **Objetivo:** Formalizar el conocimiento generado y registrar la trazabilidad científica.
- **Acciones principales:** Redacción de la metodología del análisis, generación del informe final con gráficos, y consolidación de la literatura científica utilizada en la justificación física.
""")

# src/methodology/workflow.md
write_file("src/methodology/workflow.md", """
# Flujo de Trabajo y Coordinación (Workflow)

## El Rol de la Orquestación
El **Orchestrator** es el único encargado de dirigir y coordinar la transición entre las 5 fases metodológicas definidas. 
- Los **Agentes** no representan fases; son entidades lógicas que ejecutan tareas específicas dentro de las fases bajo la dirección del Orchestrator.
- Las **Tools** no son agentes; son interfaces técnicas sin capacidad de decisión de las cuales los agentes se sirven.

```
                  ┌──────────────────────┐
                  │ 1. Phase: Strategy   │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │2. Phase: Exploration │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │3. Phase: Processing  │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ 4. Phase: Validation │◄──────┐
                  └──────────┬───────────┘       │
                             │                   │ (En caso de fallo o
                             ├───────────────────┘  inconsistencia)
                             │
                             ▼
                  ┌──────────────────────┐
                  │5. Phase:Documentation│
                  └──────────────────────┘
```

El ciclo de validación es fundamental: si durante la fase de **Validation** se detecta un error de física, falta de datos, o código defectuoso, el orquestador redirige el flujo de manera controlada hacia la fase correspondiente (ej. Exploration si faltaban variables, o Processing si el corte fue erróneo) para corregir el análisis antes de su documentación final.
""")

# Templates files
write_file("src/templates/analysis_template/CLAUDE.md", """
# Guía del Análisis - CLAUDE

## Resumen del Análisis
<!-- TODO: Describir el propósito y resultados clave de este análisis -->

## Comandos de Ejecución
<!-- TODO: Instrucciones paso a paso para compilar o ejecutar el código -->

## Notas Técnicas y de Entorno
<!-- TODO: Detallar dependencias y requisitos técnicos específicos -->
""")

write_file("src/templates/analysis_template/prompt.md", """
# Prompts de Análisis

## Objetivo Físico Inicial
<!-- TODO: Registrar el prompt o instrucción original del usuario -->

## Directrices para Agentes
<!-- TODO: Notas especiales o restricciones para los prompts de los agentes -->
""")

write_file("src/templates/analysis_template/experiment_log.md", """
# Registro de Experimentos

## Historial de Corridas e Iteraciones
<!-- TODO: Registrar ejecuciones, cortes físicos ensayados y cambios en el código -->

| Iteración | Fecha | Modificaciones / Cortes | Resultados / Observaciones |
|-----------|-------|-------------------------|----------------------------|
| 001       | -     | -                       | -                          |
""")

write_file("src/templates/analysis_template/retrieval_log.md", """
# Registro de Recuperación de Literatura

Este log registra de manera exhaustiva toda la literatura, documentación y datasets buscados, consultados o recuperados de forma autónoma durante el transcurso de este análisis.

| fecha | tipo (paper/doc/dataset) | fuente/URL | ruta local | motivo |
|---|---|---|---|---|
""")

write_file("src/templates/analysis_template/analysis_config", """
# Configuración General del Análisis de Mini-JFC
# Este archivo define las variables fundamentales y configuraciones del proceso.

# TODO: Configurar nombre de la señal física
signal_name = "Signal_Placeholder"

# TODO: Configurar rango de masa o región de interés
mass_range_min = 0.0
mass_range_max = 0.0

# TODO: Especificar datasets base a procesar
datasets_list = []
""")

# src/scaffold_analysis.py
write_file("src/scaffold_analysis.py", """
import argparse
import shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Scaffold de una nueva estructura de análisis en Mini-JFC."
    )
    parser.add_argument(
        "nombre",
        help="Nombre del análisis a crear (se ubicará en analyses/<nombre>/)"
    )
    args = parser.parse_args()

    # Rutas base
    workspace_dir = Path(__file__).resolve().parent.parent
    analysis_dir = workspace_dir / "analyses" / args.nombre
    templates_dir = workspace_dir / "src" / "templates" / "analysis_template"
    src_dir = workspace_dir / "src"

    if analysis_dir.exists():
        print(f"Error: El análisis '{args.nombre}' ya existe en {analysis_dir}.")
        exit(1)

    print(f"Creando nuevo análisis '{args.nombre}' en: {analysis_dir}")

    try:
        # 1. Crear el directorio principal del análisis
        analysis_dir.mkdir(parents=True, exist_ok=False)

        # 2. Copiar los archivos de templates/analysis_template/ al directorio del análisis
        if templates_dir.exists():
            for item in templates_dir.iterdir():
                if item.is_file():
                    shutil.copy(item, analysis_dir / item.name)
        else:
            print(f"Advertencia: Directorio de plantillas no encontrado en {templates_dir}")

        # 3. Copiar agents/, conventions/ y methodology/ desde src/ al directorio de análisis
        for folder_name in ["agents", "conventions", "methodology"]:
            src_folder = src_dir / folder_name
            dest_folder = analysis_dir / folder_name
            if src_folder.exists():
                shutil.copytree(src_folder, dest_folder)

        # 4. Crear las carpetas de fases con un archivo .gitkeep dentro
        fases = [
            "phase1_strategy",
            "phase2_exploration",
            "phase3_processing",
            "phase4_validation",
            "phase5_documentation"
        ]

        for fase in fases:
            fase_dir = analysis_dir / fase
            fase_dir.mkdir(parents=True, exist_ok=True)
            (fase_dir / ".gitkeep").touch()

        print("¡Scaffold del análisis completado exitosamente!")

    except Exception as e:
        print(f"Error al estructurar el análisis: {e}")
        # Intentar limpiar la carpeta a medio crear si hay error
        if analysis_dir.exists():
            shutil.rmtree(analysis_dir, ignore_errors=True)
        exit(1)

if __name__ == "__main__":
    main()
""")

print("Setup completed successfully!")
