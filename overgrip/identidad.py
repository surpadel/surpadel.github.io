"""Identidad visual por torneo: cada torneo tiene su propio fondo (uno para
caballeros y otro para damas, más
una versión de festejo para las finales) y lo usa en todas sus historias.

El fondo queda guardado en torneos.json ("fondos": {"azul": ..., "rosa": ...}).
buscar.py se lo asigna a cada torneo nuevo eligiendo el menos usado entre los
torneos que se juegan en fechas cercanas, para que dos torneos del mismo fin de
semana no se repitan.
Si a un torneo le falta, se elige uno fijo a partir de su id (nunca cambia).
"""
import zlib
from datetime import date, timedelta

AZUL = [
    "fondo-01-arena-tribuna.jpg", "fondo-12-club-canchas.jpg", "fondo-04-cenital.jpg",
    "fondo-09-publico.jpg", "fondo-08-cancha-mojada.jpg", "fondo-02-red-arena.jpg",
    "fondo-25-club-industrial.png", "fondo-13-reflejos.jpg", "fondo-10-tunel.jpg",
    "fondo-18-terraza-ciudad.jpg", "fondo-07-vidrio-lluvia.jpg", "fondo-30-club-barrio-noche.png",
    "fondo-11-esquina.jpg", "fondo-20-camara-tv.jpg", "fondo-29-tinglado-barrio.png",
    "fondo-05-focos.jpg",
]
ROSA = ["fondo-15-rosa-arena.jpg", "fondo-33-rosa-tribuna.jpg", "fondo-16-rosa-red.jpg",
        "fondo-34-rosa-cenital.jpg", "fondo-27-rosa-neon.png", "fondo-35-rosa-lluvia.jpg",
        "fondo-37-rosa-club.jpg", "fondo-38-rosa-focos.jpg", "fondo-36-rosa-tunel.jpg",
        "fondo-17-rosa-cesped.jpg"]
# finales: versión de festejo (confeti, fuegos, foco), también una por torneo
FINAL_AZUL = ["fondo-39-final-azul-podio.jpg", "fondo-40-final-azul-fuegos.jpg",
              "fondo-41-final-azul-spot.jpg", "fondo-14-campeones-confeti.jpg"]
FINAL_ROSA = ["fondo-42-final-rosa-confeti.jpg", "fondo-43-final-rosa-fuegos.jpg",
              "fondo-44-final-rosa-spot.jpg"]
POOL = {"azul": AZUL, "rosa": ROSA, "final_azul": FINAL_AZUL, "final_rosa": FINAL_ROSA}


def fondo(c, rama, final=False):
    """Archivo de fondo (dentro de marca/fondos/) del torneo para la rama.
    final=True: la versión de festejo para las historias de campeones."""
    rama = ("final_" if final else "") + ("rosa" if rama == "rosa" else "azul")
    elegido = (c.get("fondos") or {}).get(rama)
    if elegido:
        return elegido
    pool = POOL[rama]
    return pool[zlib.crc32(str(c.get("id", "")).encode()) % len(pool)]


def vigente(c, hoy):
    if not c.get("fechas"):
        return c.get("estado") != "Finalizado"
    return date.fromisoformat(c["fechas"][-1]) >= hoy - timedelta(days=3)


def cruzan(a, b, hoy):
    """¿Los dos torneos se juegan cerca en el tiempo (pueden salir historias el mismo día)?"""
    if not a.get("fechas") or not b.get("fechas"):
        return vigente(b, hoy)
    ini_a, fin_a = date.fromisoformat(a["fechas"][0]), date.fromisoformat(a["fechas"][-1])
    ini_b, fin_b = date.fromisoformat(b["fechas"][0]), date.fromisoformat(b["fechas"][-1])
    return ini_a <= fin_b + timedelta(days=3) and ini_b <= fin_a + timedelta(days=3)


def asignar(conf, hoy):
    """Completa "fondos" a los torneos que no lo tienen. Devuelve los ids tocados."""
    tocados = []
    for c in conf:
        if all(c.get("fondos", {}).get(r) for r in POOL):
            continue
        otros = [x for x in conf if x is not c and x.get("fondos") and cruzan(c, x, hoy)]
        nuevos = dict(c.get("fondos") or {})
        for rama, pool in POOL.items():
            if nuevos.get(rama):
                continue
            usos = {f: sum(1 for x in otros if x["fondos"].get(rama) == f) for f in pool}
            nuevos[rama] = min(pool, key=lambda f: (usos[f], pool.index(f)))
        c["fondos"] = nuevos
        tocados.append(c["id"])
    return tocados
