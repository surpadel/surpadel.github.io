"""Arma la web de Sur Padel a partir del catálogo público del proveedor.

Uso: SUPPLIER_URL=https://... python build.py
Genera _site/index.html. Si el catálogo no se puede leer bien, termina con error
y la web publicada anterior queda como está.
"""
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.request

from pricing import precio

BASE = os.environ.get("SUPPLIER_URL", "").rstrip("/")
if not BASE:
    sys.exit("Falta la variable SUPPLIER_URL")

UA = {"User-Agent": "Mozilla/5.0 (compatible; SurPadelCatalog/1.0)"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def get(url: str) -> str:
    for intento in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            if intento == 2:
                raise
            print(f"Reintentando {url}: {e}")
            time.sleep(3)
    return ""


def texto(fragmento: str) -> str:
    fragmento = re.sub(r"<!--.*?-->", "", fragmento, flags=re.S)
    fragmento = re.sub(r"<[^>]+>", " ", fragmento)
    return re.sub(r"\s+", " ", html.unescape(fragmento)).strip()


def estado(s: str) -> str:
    s = s.lower()
    if "ltima" in s:
        return "u"
    if "camino" in s:
        return "c"
    if "stock" in s:
        return "s"
    return "e"


def leer_catalogo() -> list[dict]:
    pagina = re.sub(r"<!--.*?-->", "", get(BASE + "/"), flags=re.S)
    productos, vistos = [], set()
    for slug, interior in re.findall(r'<a[^>]+href="[^"]*/catalogo/([a-z0-9-]+)"[^>]*>(.*?)</a>', pagina, flags=re.S):
        t = texto(interior)
        m = re.match(r"^(.+?)\s+[—–-]\s+USD\s+([\d.,]+)\s+\((.+)\)$", t)
        if not m or slug in vistos:
            continue
        vistos.add(slug)
        nombre, costo, st = m.group(1), float(m.group(2).replace(",", "")), m.group(3)
        marca, _, modelo = nombre.partition(" ")
        if marca == "Generic":
            marca = "Otras"
        productos.append({"slug": slug, "marca": marca, "modelo": modelo, "costo": costo, "st": estado(st)})
    return productos


def leer_ficha(slug: str) -> str:
    try:
        return get(f"{BASE}/catalogo/{slug}")
    except Exception as e:  # noqa: BLE001
        print(f"Sin ficha para {slug}: {e}")
        return ""


def dolar_desde_ficha(ficha: str) -> float | None:
    limpio = texto(ficha)
    ars = re.search(r"\$\s?([\d.]+)\s*ARS", limpio)
    usd = re.search(r"U\$D\s*([\d.,]+)", limpio)
    if not (ars and usd):
        return None
    valor = float(ars.group(1).replace(".", "")) / float(usd.group(1).replace(",", ""))
    return round(valor) if 300 < valor < 10_000 else None


def foto(ficha: str) -> str:
    m = re.search(r'https://[^"\'\s]+/product-images/[^"\'\s]+?\.(?:webp|jpe?g|png)', ficha)
    return html.unescape(m.group(0)) if m else ""


def main() -> None:
    productos = leer_catalogo()
    print(f"Productos leídos: {len(productos)}")
    if len(productos) < 50:
        sys.exit("El catálogo vino incompleto; no se actualiza la web.")

    dolar = None
    for i, p in enumerate(productos):
        ficha = leer_ficha(p["slug"])
        p["foto"] = foto(ficha)
        if dolar is None:
            dolar = dolar_desde_ficha(ficha)
        if i % 50 == 0:
            print(f"Fichas: {i}/{len(productos)}")
        time.sleep(0.3)
    if dolar is None:
        sys.exit("No se pudo leer el tipo de cambio; no se actualiza la web.")
    print(f"Dólar: {dolar}")

    datos = []
    for p in productos:
        ars, usd = precio(p["costo"], dolar)
        datos.append([p["marca"], p["modelo"], ars, usd, p["st"], p["foto"]])

    hoy = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3)))
    plantilla = open("template.html", encoding="utf-8").read()
    reemplazos = {
        "__DATA__": json.dumps(datos, ensure_ascii=False, separators=(",", ":")),
        "__DATE__": f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}",
        "__RATE_FMT__": f"{dolar:,.0f}".replace(",", "."),
        "__RATE_DATE__": f"{hoy.day}/{hoy.month}",
        "__RATE__": str(dolar),
        "__LOGO__": open("logo.txt", encoding="utf-8").read().strip(),
    }
    for clave, valor in reemplazos.items():
        plantilla = plantilla.replace(clave, valor)
    page = "<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n" \
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n" + plantilla + "\n</html>\n"
    os.makedirs("_site", exist_ok=True)
    open("_site/index.html", "w", encoding="utf-8").write(page)
    con_foto = sum(1 for d in datos if d[5])
    print(f"Listo: {len(datos)} paletas, {con_foto} con foto.")


if __name__ == "__main__":
    main()
