"""Arma la web de Sur Padel a partir del catálogo del proveedor (con usuario desde 25/11/2026).

Uso: SUPPLIER_URL=https://... SUPPLIER_EMAIL=... SUPPLIER_PASSWORD=... python build.py
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

from fotos import limpiar
from pricing import precio

BASE = os.environ.get("SUPPLIER_URL", "").rstrip("/")
if not BASE:
    sys.exit("Falta la variable SUPPLIER_URL")

UA = {"User-Agent": "Mozilla/5.0 (compatible; SurPadelCatalog/1.0)"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def get_bytes(url: str) -> bytes:
    for intento in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if intento == 2:
                raise
            print(f"Reintentando {url}: {e}")
            time.sleep(3)
    return b""


def get(url: str) -> str:
    return get_bytes(url).decode("utf-8", "replace")


def foto_limpia(url: str, slug: str) -> str:
    """Si la foto no tiene fondo blanco, guarda una copia corregida y devuelve su ruta."""
    if not url:
        return url
    try:
        nueva = limpiar(get_bytes(url))
    except Exception as e:  # noqa: BLE001
        print(f"No se pudo revisar la foto de {slug}: {e}")
        return url
    if nueva is None:
        return url
    os.makedirs("_site/img", exist_ok=True)
    open(f"_site/img/{slug}.webp", "wb").write(nueva)
    return f"img/{slug}.webp"


def texto(fragmento: str) -> str:
    fragmento = re.sub(r"<!--.*?-->", "", fragmento, flags=re.S)
    fragmento = re.sub(r"<[^>]+>", " ", fragmento)
    return re.sub(r"\s+", " ", html.unescape(fragmento)).strip()


def estado(s: str) -> str:
    s = s.lower()
    if "sin stock" in s or "encargo" in s:
        return "e"
    if "ltima unidad" in s:
        return "u"
    if re.search(r"ltimas \d+ ?u", s):
        return "s"
    if "camino" in s:
        return "c"
    if "stock" in s:
        return "s"
    return "e"


def usd(valor: str) -> float:
    """'219' -> 219.0, '1.259' -> 1259.0, '99,50' -> 99.5"""
    if re.search(r"[.,]\d{2}$", valor):
        return float(re.sub(r"[.,]", "", valor[:-3]) + "." + valor[-2:])
    return float(re.sub(r"[.,]", "", valor))


def slugify(nombre: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def leer_catalogo() -> tuple[list[dict], float | None]:
    """25/11/2026: el proveedor cerró el catálogo con usuario y contraseña.
    Se entra con un navegador sin ventana (Playwright) usando SUPPLIER_EMAIL y
    SUPPLIER_PASSWORD, se lee /inventario y las fotos salen de /api/inventory/client-data.
    Cada tarjeta dice: <nombre> / <estado> / $<pesos> ARS / U$D <costo>."""
    from playwright.sync_api import sync_playwright

    email = os.environ.get("SUPPLIER_EMAIL", "")
    clave = os.environ.get("SUPPLIER_PASSWORD", "")
    if not (email and clave):
        sys.exit("Faltan SUPPLIER_EMAIL / SUPPLIER_PASSWORD; no se actualiza la web.")

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pag = nav.new_page()
        pag.goto(BASE + "/auth/login", wait_until="networkidle")
        pag.fill('input[type="email"]', email)
        pag.fill('input[type="password"]', clave)
        pag.click('button[type="submit"]')
        try:
            pag.wait_for_url("**/inventario**", timeout=30000)
        except Exception:  # noqa: BLE001
            nav.close()
            sys.exit("No se pudo iniciar sesión en el proveedor; no se actualiza la web.")
        pag.wait_for_function("document.body.innerText.includes('U$D')", timeout=60000)
        pag.wait_for_timeout(3000)
        lineas = [x.strip() for x in pag.inner_text("body").split("\n") if x.strip()]
        datos = pag.evaluate("fetch('/api/inventory/client-data').then(r => r.json())")
        nav.close()

    fotos = {p.get("name", "").strip().lower(): p.get("image_url") or ""
             for p in datos.get("products", [])}
    dolar = None
    if "Dólar blue" in lineas:
        m = re.search(r"[\d.]+", lineas[lineas.index("Dólar blue") + 1])
        if m:
            dolar = float(m.group(0).replace(".", ""))

    productos, vistos = [], set()
    for i in range(2, len(lineas) - 1):
        ars = re.fullmatch(r"\$([\d.]+) ARS", lineas[i])
        pu = re.fullmatch(r"U\$D\s*([\d.,]+)", lineas[i + 1])
        if not (ars and pu):
            continue
        nombre = re.sub(r"\s+", " ", lineas[i - 2]).strip()
        slug = slugify(nombre)
        if slug in vistos:
            continue
        vistos.add(slug)
        costo = usd(pu.group(1))
        if dolar is None and costo:
            valor = float(ars.group(1).replace(".", "")) / costo
            dolar = round(valor) if 300 < valor < 10_000 else None
        marca, _, modelo = nombre.partition(" ")
        if marca == "Generic":
            marca = "Otras"
        productos.append({"slug": slug, "marca": marca, "modelo": modelo, "costo": costo,
                          "st": estado(lineas[i - 1]), "foto_url": fotos.get(nombre.lower(), "")})
    return productos, dolar


def main() -> None:
    productos, dolar = leer_catalogo()
    print(f"Productos leídos: {len(productos)}")
    if len(productos) < 50:
        sys.exit("El catálogo vino incompleto; no se actualiza la web.")

    # Pedido de Nico (10/11/2026): no se muestran las "Por encargo" (desde 25/11 "Sin stock").
    # Quedan solo En stock, Última unidad y En camino.
    ocultas = sum(1 for p in productos if p["st"] == "e")
    productos = [p for p in productos if p["st"] != "e"]
    print(f"Ocultas por encargo: {ocultas}. Quedan: {len(productos)}")

    for i, p in enumerate(productos):
        p["foto"] = foto_limpia(p["foto_url"], p["slug"])
        if i % 50 == 0:
            print(f"Fotos: {i}/{len(productos)}")
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
    armar_guia(reemplazos["__LOGO__"])
    con_foto = sum(1 for d in datos if d[5])
    corregidas = sum(1 for d in datos if d[5].startswith("img/"))
    print(f"Listo: {len(datos)} paletas, {con_foto} con foto, {corregidas} con fondo corregido.")


def armar_guia(logo):
    """Arma la página de la Guía (guia/template.html) en _site/guia/ con sus imágenes."""
    import shutil
    plantilla = open("guia/template.html", encoding="utf-8").read().replace("__LOGO__", logo)
    page = "<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n" \
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n" + plantilla + "\n</html>\n"
    os.makedirs("_site/guia", exist_ok=True)
    open("_site/guia/index.html", "w", encoding="utf-8").write(page)
    shutil.copytree("guia/img", "_site/guia/img", dirs_exist_ok=True)


if __name__ == "__main__":
    main()
