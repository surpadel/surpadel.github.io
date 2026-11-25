"""Historia "Gracias, Miguelito" (25/11). Usa el estilo del reel v3.
Uso: FONTS_DIR=... LOGO_PNG=... python3 historia_lamperti.py
"""
import pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import reel_lamperti_v3 as V  # noqa: E402

HTML = (V.fondo("lamperti-foto1.jpg", (760, 950, 330, "50% 25%"))
        + V.S
        + '<div class="c kick" style="top:1330px">Bahía Blanca · leyenda</div>'
        + '<div class="c metal" style="top:1400px;font-size:128px">Gracias, <span class=gold>Miguelito</span></div>'
        + '<div class="c kick" style="top:1600px;color:#fff">@lamperti.ml10</div>'
        + '<div class=c style="top:1670px"><span class=handle style="font-size:46px;margin-top:0">@surpadelstore · surpadel.com.ar</span></div>')

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(f"<html><head><meta charset=utf-8><style>{V.CSS2}</style></head><body>{HTML}</body></html>")
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(AQUI / "historia-lamperti.png"))
    b.close()
print("ok")
