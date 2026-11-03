"""Historia 'Así formó Argentina' del Mundial (estilo circuito pro).

Una historia por jornada con las 3 parejas de caballeros y las 3 de damas
y sus marcadores. Se publica junto con el reel de la jornada (pedido de Nico, 3/11).

Uso: FONTS_DIR=... LOGO_PNG=marca/logo-sur-padel-transparente.png \
     python3 instagram/2026-11-mundial/formaciones.py datos.json salida.png
datos.json: {"jornada": "Jornada 2", "titulo": "Así formó <span class=gold>Argentina</span>",
             "bloques": [{"rama": "Caballeros", "tema": "azul", "rival": "Países Bajos", "serie": "3-0",
                          "partidos": [{"g": "Tapia / Libaak", "p": "Países Bajos", "s": "6/4 6/2"}, ...]}, ...]}
"""
import json, pathlib, sys
RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "overgrip" / "diseno"))
import gen, premier  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

FONDO = "../../marca/fondos/fondo-01-arena-tribuna.jpg"


def historia(d):
    t = premier.T["azul"]
    r = premier.T["rosa"]
    css = premier.base_css(t, 1080, 1920, FONDO) + f"""
.wrap{{padding:120px 70px 120px}}
.blk{{width:100%;margin-top:30px}}
.bh{{display:flex;justify-content:space-between;align-items:baseline;font-family:BC;font-style:italic;font-weight:800;
 text-transform:uppercase;font-size:46px;margin-bottom:10px}}
.bh small{{font-family:B;font-style:normal;font-weight:700;font-size:24px;letter-spacing:3px;color:{t['acc']}}}
.list{{display:flex;flex-direction:column;gap:10px}}
.row{{height:56px}} .row .nm{{font-size:29px}} .set{{width:58px;font-size:36px}}
.sb .hd{{padding:4px 16px;font-size:18px}}
.rosa .sb .hd{{background:linear-gradient(90deg,{r['court2']},{r['court']})}}
.rosa .set.won{{background:{r['hot']};color:#16071a}} .rosa .row .tri{{border-left-color:{r['hot']}}}
.rosa .bh small{{color:{r['acc']}}}
.foot{{gap:10px}}
"""
    blks = ""
    for b in d["bloques"]:
        cards = "".join(premier.scoreboard(m, f"Partido {i + 1}") for i, m in enumerate(b["partidos"]))
        blks += (f'<div class="blk {b.get("tema", "azul")}"><div class=bh><span>{b["rama"]} · '
                 f'<span class=gold>{b["serie"]}</span></span><small>vs {b["rival"]}</small></div>'
                 f'<div class=list>{cards}</div></div>')
    body = (f'<div class=strip><div class=a>Mundial</div><div class=b>Doha · {d["jornada"]}</div></div>'
            f'<div class=metal style="font-size:110px;margin-top:34px">{d["titulo"]}</div>'
            f'{blks}'
            '<div class=foot><div class=cred>Selección <b>@padel_apa</b> · Mundial <b>@padelfip</b></div>'
            '<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>')
    return css, f'{premier.deco(t)}<div class=wrap>{body}</div>'


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    css, body = historia(d)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{css}</style></head><body>{body}</body></html>")
        pg.wait_for_timeout(300)
        pg.screenshot(path=sys.argv[2])
        b.close()
    print(sys.argv[2])
