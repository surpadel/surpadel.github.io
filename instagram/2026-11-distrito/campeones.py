"""Campeones del Distrito Padel Center Open 3 (SportLevel, 15/11/2026).

Se sumó al seguimiento el día de las finales, así que los campeones se arman a
mano con el mismo diseño de las historias automáticas (overgrip/historias.py).
Salida: instagram/overgrip/SL-distrito-padel-center-open-3/campeones-*.png

Uso: python3 instagram/2026-11-distrito/campeones.py [azul|rosa ...]
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "overgrip"))
import historias  # noqa: E402

DATOS = json.loads((Path(__file__).parent / "campeones.json").read_text())
TORNEO = "SL-distrito-padel-center-open-3"


def trabajo(rama):
    d = DATOS[rama]
    inst = historias.INSTANCIAS["Final"]
    return {
        "torneo": TORNEO, "corto": "Distrito Open 3", "organiza": "distritopadelcenteropen",
        "fuente": "sportlevel", "tema": rama,
        "fondo": f"../../marca/fondos/{inst[3] if rama == 'rosa' else inst[2]}",
        "strip": "Finales" + (" · Damas" if rama == "rosa" else ""),
        "titulo": "Las <span class=gold>campeonas</span>" if rama == "rosa" else inst[1],
        "partidos": d["partidos"],
        "archivo": f"{TORNEO}/campeones-{rama}.png",
    }


if __name__ == "__main__":
    ramas = sys.argv[1:] or ["azul", "rosa"]
    historias.dibujar([trabajo(r) for r in ramas])
