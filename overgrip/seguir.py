"""Seguimiento de torneos de OverGrip (parte pública) para Sur Padel.

Un solo pedido por torneo: la página de partidos pedida con el encabezado
"RSC: 1" devuelve todos los partidos de todas las categorías en JSON.
Se guardan solo los cruces (16avos en adelante) en formato compacto y se
anotan como novedades los partidos que terminaron desde la corrida anterior.

Uso: python3 overgrip/seguir.py TEO-CLI006-001 [OTRO-TORNEO ...]
"""
import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = "https://app.overgrip.com.ar/torneos/"
CARPETA = Path(__file__).parent / "datos"
TERMINADOS = {"Finalizado", "WO"}
ARG = timezone(timedelta(hours=-3))


def bajar(torneo):
    req = urllib.request.Request(
        BASE + torneo,
        headers={"RSC": "1", "User-Agent": "SurPadel/1.0 (+https://surpadel.com.ar)"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def extraer_partidos(texto):
    """Busca el arreglo "partidos":[{"codigo"...}] y lo recorta respetando comillas."""
    inicio = texto.find('"partidos":[{"codigo"')
    if inicio < 0:
        raise ValueError("No se encontró la lista de partidos")
    k = inicio + len('"partidos":')
    nivel, en_texto, j = 0, False, k
    while j < len(texto):
        c = texto[j]
        if en_texto:
            if c == "\\":
                j += 1
            elif c == '"':
                en_texto = False
        elif c == '"':
            en_texto = True
        elif c == "[":
            nivel += 1
        elif c == "]":
            nivel -= 1
            if nivel == 0:
                break
        j += 1
    return json.loads(texto[k : j + 1])


def compactar(p):
    return {
        "cat": p.get("categoria"),
        "inst": p.get("instancia"),
        "dia": p.get("diaISO"),
        "hora": p.get("hora"),
        "sede": p.get("sede"),
        "estado": p.get("estado"),
        "p1": " / ".join(p.get("pareja1") or []),
        "p2": " / ".join(p.get("pareja2") or []),
        "res": p.get("resultado") or "",
        "gan": p.get("ganador"),
    }


def seguir(torneo):
    partidos = extraer_partidos(bajar(torneo))
    cruces = {
        p["codigoCompleto"]: compactar(p)
        for p in partidos
        if p.get("instancia") != "Zona"
    }
    archivo = CARPETA / f"{torneo}.json"
    antes = json.loads(archivo.read_text()) if archivo.exists() else {}
    viejos = antes.get("cruces", {})
    nuevos = [
        dict(codigo=c, **d)
        for c, d in cruces.items()
        if d["estado"] in TERMINADOS
        and viejos.get(c, {}).get("estado") not in TERMINADOS
    ]
    ahora = datetime.now(ARG).strftime("%Y-%m-%d %H:%M")
    if cruces != viejos:
        archivo.write_text(
            json.dumps(
                {"torneo": torneo, "actualizado": ahora, "cruces": cruces},
                ensure_ascii=False, indent=0, sort_keys=True,
            )
        )
    if nuevos:
        nov = CARPETA / "novedades.json"
        lista = json.loads(nov.read_text()) if nov.exists() else []
        lista.append({"torneo": torneo, "hora": ahora, "partidos": nuevos})
        nov.write_text(json.dumps(lista[-50:], ensure_ascii=False, indent=1))
    print(f"{torneo}: {len(partidos)} partidos, {len(cruces)} cruces, {len(nuevos)} terminados nuevos")
    return len(nuevos)


if __name__ == "__main__":
    CARPETA.mkdir(parents=True, exist_ok=True)
    for t in sys.argv[1:] or ["TEO-CLI006-001"]:
        seguir(t)
