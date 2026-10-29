# Workflow (borrador breve)

- El **Orchestrator** coordina las 5 fases: decide en qué fase está el análisis y qué agente actúa.
- Los **agentes** (planner, literature_agent, data_agent, analyst, reviewer) deciden y ejecutan dentro de una fase: **no son fases**.
- Las **tools** (web, literature, cms, parquet, root, analysis) son capacidades que los agentes usan: **no son agentes**.
- **Bucle Validation -> fases anteriores**: si el reviewer detecta problemas, el Orchestrator reabre Strategy, Exploration o Processing y esa fase se repite.
- Cuando Validation pasa sin problemas, se pasa a Documentation y se cierra el análisis.

## Handoffs y estado compartido

- El estado vive en archivos de `analyses/<nombre>/`, no en la conversación: `fase_actual` en `analysis_config` y el historial en `experiment_log.md`.
- Cada fase la ejecuta un agente y la revisa el `reviewer`; el Orchestrator solo avanza de fase tras un `PASS`.
- Los criterios de salida de cada fase están en `src/methodology/phases.md`; el reviewer los usa para emitir PASS o FAIL.
- Máximo 2 reintentos por fase; al tercer fallo el Orchestrator se detiene y reporta al usuario.
