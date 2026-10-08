"""Reglas de precio de Sur Padel.

- Margen sobre el costo del proveedor: mínimo 25%, máximo 30% (nunca más de 30%).
- El precio en pesos es redondo: se busca el número más alto dentro de ese rango
  que sea múltiplo de 10.000; si no hay, de 5.000; si no hay, de 1.000.
- El precio en dólares se deriva del precio en pesos y se muestra sin decimales.
"""
import math

MARGEN_MIN = 0.25
MARGEN_MAX = 0.30
PASOS = (10_000, 5_000, 1_000)


def precio(costo_usd: float, dolar: float) -> tuple[int, int]:
    """Devuelve (precio_ars, precio_usd) para un costo en USD y una cotización."""
    piso = costo_usd * (1 + MARGEN_MIN) * dolar
    techo = costo_usd * (1 + MARGEN_MAX) * dolar
    for paso in PASOS:
        ars = math.floor(techo / paso) * paso
        if ars >= piso:
            break
    else:
        ars = math.floor(techo / 1_000) * 1_000  # caso extremo: nunca pasarse del 30%
    return ars, round(ars / dolar)
