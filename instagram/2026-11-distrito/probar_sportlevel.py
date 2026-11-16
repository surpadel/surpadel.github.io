"""Prueba de lectura de SportLevel desde GitHub Actions (no escribe nada en el repo).

Uso: python3 instagram/2026-11-distrito/probar_sportlevel.py
"""
import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "overgrip"))
import sportlevel  # noqa: E402

cr, zo = sportlevel.partidos("distrito-padel-center-open/distrito-padel-center-open-3")
print(f"Distrito Open 3: {len(cr)} cruces, {len(zo)} de zona")
for k, v in cr.items():
    if v["inst"] == "Final":
        print(k, json.dumps(v, ensure_ascii=False))
conf = json.loads((RAIZ / "overgrip" / "torneos.json").read_text())
avisos = sportlevel.buscar(conf, date.today())
print("\n".join(avisos) or "Sin torneos nuevos en la zona")
for c in conf:
    if c.get("fuente") == "sportlevel":
        print(c["id"], c["estado"], c["fechas"], c["organiza"])
