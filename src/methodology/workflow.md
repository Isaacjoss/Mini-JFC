# Workflow (borrador breve)

- El **Orchestrator** coordina las 5 fases: decide en qué fase está el análisis y qué agente actúa.
- Los **agentes** (planner, literature_agent, data_agent, analyst, reviewer) deciden y ejecutan dentro de una fase: **no son fases**.
- Las **tools** (web, literature, cms, parquet, root, analysis) son capacidades que los agentes usan: **no son agentes**.
- **Bucle Validation -> fases anteriores**: si el reviewer detecta problemas, el Orchestrator reabre Strategy, Exploration o Processing y esa fase se repite.
- Cuando Validation pasa sin problemas, se pasa a Documentation y se cierra el análisis.

TODO: detallar handoffs, estado compartido y criterios de salida por fase.
