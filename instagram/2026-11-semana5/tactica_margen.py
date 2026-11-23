"""Reel 'Táctica Sur n.º 3: Ante la duda, con margen' (pedido de Nico 23/11: sin decir "alto", foco en el margen).
Reusa tactica_alto.py y cambia solo los textos.
Uso: FONTS_DIR=... LOGO_PNG=... python3 instagram/2026-11-semana5/tactica_margen.py [--fps 30] [--solo-tapa] [--cuadros 1,8,13]
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tactica_alto as alto
import tactica_medio as base

CAMBIOS_BODY = [
    ("N.º 3 · Más alto", "N.º 3 · Con margen"),
    ("Ante la duda<br><span>más alto</span>", "Ante la duda<br><span>con margen</span>"),
]
CAMBIOS_JS = [
    ("1 · MÁS ALTURA", "1 · MÁS MARGEN"),
    ("<span class=g>pasala alta</span><small>Con margen sobre la red, no rozándola</small>",
     "<span class=g>jugá con margen</span><small>Que pase lejos de la red, no rozándola</small>"),
]

def aplicar(texto, cambios):
    for a, b in cambios:
        assert texto.count(a) == 1, a
        texto = texto.replace(a, b)
    return texto

if __name__ == "__main__":
    base.NOMBRE = "tactica-sur-3-margen"
    base.HTML = alto.HTML
    base.BODY = aplicar(alto.BODY, CAMBIOS_BODY)
    base.JS = aplicar(alto.JS, CAMBIOS_JS)
    base.main()
