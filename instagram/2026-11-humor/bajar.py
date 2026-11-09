"""Baja archivos sueltos (por ejemplo audios de ElevenLabs) a instagram/2026-11-humor/fuentes/."""
import json, pathlib, urllib.request, sys
AQUI = pathlib.Path(__file__).resolve().parent
lista = json.load(open(AQUI / "bajar.json"))
(AQUI / "fuentes").mkdir(exist_ok=True)
for it in lista:
    dest = AQUI / "fuentes" / it["nombre"]
    req = urllib.request.Request(it["url"], headers={"User-Agent": "Mozilla/5.0"})
    dest.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    print("ok", dest, dest.stat().st_size)
