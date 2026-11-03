"""Baja los videos/imágenes de APIMart anotados en apimart/pedidos.json.

Los links de APIMart vencen en 24-72 hs y su servidor está bloqueado desde el
espacio de trabajo de Claude, así que los baja GitHub Actions y los guarda en
el repositorio. Solo baja los que todavía no existen en `destino`.
"""
import json, pathlib, sys, urllib.request

raiz = pathlib.Path(__file__).resolve().parent.parent
pedidos = json.loads((raiz / "apimart/pedidos.json").read_text(encoding="utf-8"))
errores = 0
for p in pedidos:
    destino = raiz / p["destino"]
    if destino.exists():
        print("ya está:", p["destino"])
        continue
    if not str(destino).startswith(str(raiz / "instagram")):
        print("destino fuera de instagram/, lo salteo:", p["destino"])
        errores += 1
        continue
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(p["url"], headers={"User-Agent": "surpadel-bajar/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            datos = r.read()
        if len(datos) < 10_000:
            raise ValueError(f"archivo muy chico ({len(datos)} bytes)")
        destino.write_bytes(datos)
        print(f"bajado: {p['destino']} ({len(datos)//1024} KB)")
    except Exception as e:
        print("error con", p["url"], "->", e)
        errores += 1
sys.exit(1 if errores else 0)
