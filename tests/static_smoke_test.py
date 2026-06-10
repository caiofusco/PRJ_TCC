"""Validação estática rápida do MVP.
Execute após instalar dependências: python tests/static_smoke_test.py
"""
from pathlib import Path
import ast

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[1]

for path in ROOT.rglob("*.py"):
    if ".venv" in path.parts:
        continue
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

TEMPLATES = ROOT / "app" / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
for path in TEMPLATES.rglob("*.html"):
    env.parse(path.read_text(encoding="utf-8"))

required = [
    ROOT / "docker-compose.yml",
    ROOT / "requirements.txt",
    ROOT / "db" / "schema.sql",
    ROOT / "docs" / "ANALISE_COMPLETA_ARTIGO.md",
]
missing = [str(path) for path in required if not path.exists()]
if missing:
    raise SystemExit(f"Arquivos ausentes: {missing}")

print("OK - validação estática concluída")
