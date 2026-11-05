"""Post de feed 'Dato del Mundial' (1080x1350), estilo circuito pro.

Uso: FONTS_DIR=... LOGO_PNG=marca/logo-sur-padel-transparente.png \
     python3 instagram/2026-11-mundial/dato.py datos.json salida.png
datos.json: {"etiqueta": "Dato del Mundial", "numero": "24/24", "titulo": "...", "texto": "...",
             "filas": [["Caballeros", "12 de 12"], ["Damas", "12 de 12"]]}
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import formaciones as F  # noqa: E402
from formaciones import premier  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def post(d):
    t, r = premier.T["azul"], premier.T["rosa"]
    css = premier.base_css(t, 1080, 1350, F.FONDO) + f"""
.wrap{{padding:90px 80px 70px}}
.num{{font-family:BC;font-style:italic;font-weight:800;font-size:300px;line-height:.9;margin-top:40px;
 background:linear-gradient(180deg,#ffe28a,{t['hot']} 55%,#a8730b);-webkit-background-clip:text;color:transparent;
 filter:drop-shadow(0 8px 24px rgba(0,0,0,.6))}}
.tt{{font-family:BC;font-style:italic;font-weight:800;font-size:76px;text-transform:uppercase;text-align:center;line-height:1}}
.tx{{margin-top:22px;font-size:34px;line-height:1.35;color:#dfe9f5;text-align:center;max-width:860px}}
.rows{{display:flex;gap:24px;margin-top:40px;width:100%}}
.rw{{flex:1;border-radius:18px;padding:22px 26px;background:rgba(11,29,54,.82);border:2px solid {t['acc']}55;
 display:flex;align-items:center;justify-content:space-between}}
.rw.rosa{{border-color:{r['hot']}88}}
.rw span{{font-weight:700;letter-spacing:3px;text-transform:uppercase;font-size:24px;color:{t['acc']}}}
.rw.rosa span{{color:{r['acc']}}}
.rw b{{font-family:BC;font-style:italic;font-weight:800;font-size:54px}}
"""
    rows = "".join(f'<div class="rw {"rosa" if i else ""}"><span>{a}</span><b>{b}</b></div>'
                   for i, (a, b) in enumerate(d.get("filas", [])))
    body = (f'<div class=strip><div class=a>Mundial</div><div class=b>{d["etiqueta"]}</div></div>'
            f'<div class=num>{d["numero"]}</div><div class=tt>{d["titulo"]}</div>'
            f'<div class=tx>{d["texto"]}</div><div class=rows>{rows}</div>'
            '<div class=foot><div class=cred>Selección <b>@padel_apa</b> · Mundial <b>@padelfip</b></div>'
            '<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>')
    return css, f'{premier.deco(t)}<div class=wrap>{body}</div>'


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    css, body = post(d)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{css}</style></head><body>{body}</body></html>")
        pg.wait_for_timeout(300)
        pg.screenshot(path=sys.argv[2])
        b.close()
    print(sys.argv[2])
