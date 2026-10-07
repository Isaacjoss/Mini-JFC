#!/usr/bin/env python3
"""Crea una nueva carpeta de análisis a partir de src/templates/analysis_template."""
import argparse
import shutil
import sys
from pathlib import Path

TEMPLATE_FILES = (
    "CLAUDE.md",
    "prompt.md",
    "experiment_log.md",
    "retrieval_log.md",
    "analysis_config",
)
COPY_DIRS = ("agents", "conventions", "methodology")
PHASE_DIRS = (
    "phase1_strategy",
    "phase2_exploration",
    "phase3_processing",
    "phase4_validation",
    "phase5_documentation",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffolding de un análisis Mini-JFC.")
    parser.add_argument("nombre", help="nombre del análisis (se creara en analyses/<nombre>)")
    args = parser.parse_args()

    src_root = Path(__file__).resolve().parent
    project_root = src_root.parent
    template_dir = src_root / "templates" / "analysis_template"
    target = project_root / "analyses" / args.nombre

    if target.exists():
        print(f"error: el análisis ya existe: {target}", file=sys.stderr)
        return 1

    target.mkdir(parents=True)
    for name in TEMPLATE_FILES:
        shutil.copy2(template_dir / name, target / name)
    for name in COPY_DIRS:
        shutil.copytree(src_root / name, target / name)
    for name in PHASE_DIRS:
        (target / name).mkdir()
        (target / name / ".gitkeep").touch()

    print(f"análisis creado: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
