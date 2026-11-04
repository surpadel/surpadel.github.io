"""Historia 'Hoy juega Argentina' del Mundial (estilo circuito pro), con banderas.

Uso: FONTS_DIR=... LOGO_PNG=marca/logo-sur-padel-transparente.png \
     python3 instagram/2026-11-mundial/agenda.py datos.json salida.png
datos.json: {"jornada": "Jornada 3", "titulo": "Hoy juega <span class=gold>Argentina</span>",
             "sub": "Último partido de la fase de grupos",
             "partidos": [{"rama": "Damas", "tema": "rosa", "rival": "Francia", "fp": "fr",
                           "hora": "8:00", "nota": "Grand Stand 2"}, ...]}
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import formaciones as F  # noqa: E402
from formaciones import premier  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def historia(d):
    t, r = premier.T["azul"], premier.T["rosa"]
    css = premier.base_css(t, 1080, 1920, F.FONDO) + f"""
.wrap{{padding:150px 70px 120px}}
.flag{{position:relative;flex:none;width:96px;height:64px;border-radius:6px;box-shadow:0 0 0 2px rgba(255,255,255,.3)}}
.card{{width:100%;margin-top:46px;background:rgba(11,29,54,.82);border:2px solid {t['acc']}55;border-radius:22px;overflow:hidden}}
.card .hd{{display:flex;justify-content:space-between;padding:14px 28px;font-weight:700;letter-spacing:4px;font-size:24px;
 text-transform:uppercase;background:linear-gradient(90deg,{t['court2']},{t['court']})}}
.card.rosa .hd{{background:linear-gradient(90deg,{r['court2']},{r['court']})}}
.vs{{display:flex;align-items:center;justify-content:space-between;padding:34px 34px 10px}}
.side{{display:flex;flex-direction:column;align-items:center;gap:14px;font-family:BC;font-style:italic;font-weight:800;
 font-size:44px;text-transform:uppercase;width:300px}}
.x{{font-family:BC;font-style:italic;font-weight:800;font-size:56px;color:{t['acc']}}}
.hora{{text-align:center;font-family:BC;font-style:italic;font-weight:800;font-size:120px;line-height:1;color:{t['hot']};padding:6px 0 4px}}
.card.rosa .hora{{color:{r['hot']}}}
.hn{{text-align:center;font-size:26px;letter-spacing:3px;text-transform:uppercase;color:#cfe0f3;padding-bottom:30px}}
.sub{{margin-top:22px;font-size:34px;color:#dfe9f5;text-align:center}}
"""
    cards = ""
    for p in d["partidos"]:
        cards += (f'<div class="card {p.get("tema", "azul")}"><div class=hd><span>{p["rama"]}</span><span>{p.get("nota", "")}</span></div>'
                  f'<div class=vs><div class=side>{F.bandera("ar").replace("class=flag", "class=flag")}Argentina</div>'
                  f'<div class=x>vs</div><div class=side>{F.bandera(p["fp"])}{p["rival"]}</div></div>'
                  f'<div class=hora>{p["hora"]}</div><div class=hn>{p.get("hn", "Hora argentina")}</div></div>')
    body = (f'<div class=strip><div class=a>Mundial</div><div class=b>Doha · {d["jornada"]}</div></div>'
            f'<div class=metal style="font-size:120px;margin-top:40px">{d["titulo"]}</div>'
            f'<div class=sub>{d.get("sub", "")}</div>{cards}'
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
