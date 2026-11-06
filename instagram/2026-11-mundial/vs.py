"""Historia 'cara a cara' del Mundial: parejas enfrentadas por partido, sin fotos de jugadores.

Formato inspirado en las placas VS de los medios, con nombres grandes y banderas
(sin fotos: derechos de imagen, ver reglas de contenido).

Uso: FONTS_DIR=... LOGO_PNG=marca/logo-sur-padel-transparente.png \
     python3 instagram/2026-11-mundial/vs.py datos.json salida.png
datos.json: {"jornada": "Semifinal", "rival": "Italia", "fp": "it", "tema": "azul",
             "titulo": "Cara a <span class=gold>cara</span>", "sub": "...",
             "partidos": [{"n": 1, "hora": "12:00", "ar": ["Augsburger", "Di Nenno"], "ri": ["Montiel", "Abbate"]}, ...],
             "aviso": {"tema": "rosa", "a": "Damas", "b": "Texto"}}
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import formaciones as F  # noqa: E402
from formaciones import premier  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

FONDO = "../../marca/fondos/fondo-05-focos.jpg"


def historia(d):
    t, r = premier.T[d.get("tema", "azul")], premier.T["rosa"]
    css = premier.base_css(t, 1080, 1920, d.get("fondo", FONDO)) + f"""
.wrap{{padding:130px 60px 110px}}
.flag{{position:relative;flex:none;width:84px;height:56px;border-radius:6px;box-shadow:0 0 0 2px rgba(255,255,255,.3)}}
.top{{display:flex;align-items:center;gap:22px;margin-top:40px;font-family:BC;font-style:italic;font-weight:800;font-size:44px;text-transform:uppercase}}
.top .v{{color:{t['hot']}}}
.sub{{margin-top:14px;font-size:32px;color:#dfe9f5;text-align:center}}
.m{{width:100%;margin-top:34px;position:relative}}
.m .hd{{display:flex;align-items:stretch;height:58px}}
.m .num{{background:{t['hot']};color:#071528;font-family:BC;font-style:italic;font-weight:800;font-size:40px;display:flex;align-items:center;
 padding:0 40px 0 24px;clip-path:polygon(0 0,100% 0,90% 100%,0 100%)}}
.m .hr{{background:rgba(7,21,40,.92);border:1px solid rgba(255,255,255,.18);margin-left:-12px;display:flex;align-items:center;padding:0 24px 0 30px;
 font-weight:700;font-size:24px;letter-spacing:3px;text-transform:uppercase;clip-path:polygon(5% 0,100% 0,100% 100%,0 100%)}}
.m .bd{{display:flex;align-items:center;background:linear-gradient(90deg,rgba(29,92,173,.55),rgba(7,21,40,.88) 42%,rgba(7,21,40,.88) 58%,rgba(120,20,30,.45));
 border:1px solid rgba(255,255,255,.16);border-radius:0 14px 14px 14px;padding:26px 26px;box-shadow:0 12px 34px rgba(0,0,0,.5)}}
.pr{{flex:1;display:flex;flex-direction:column;gap:4px}}
.pr.r{{align-items:flex-end;text-align:right}}
.pr .flag{{margin-bottom:10px}}
.nm{{font-family:BC;font-style:italic;font-weight:800;font-size:62px;line-height:.95;text-transform:uppercase;white-space:nowrap}}
.pr.r .nm{{color:#dbe4ef}}
.x{{flex:none;width:120px;text-align:center;font-family:BC;font-style:italic;font-weight:800;font-size:86px;line-height:1}}
.aviso{{width:100%;margin-top:40px;display:flex;align-items:stretch;border-radius:14px;overflow:hidden;box-shadow:0 12px 34px rgba(0,0,0,.5)}}
.aviso .a{{background:linear-gradient(90deg,{r['court2']},{r['court']});font-family:BC;font-style:italic;font-weight:800;font-size:38px;
 text-transform:uppercase;display:flex;align-items:center;padding:0 26px}}
.aviso .b{{flex:1;background:rgba(42,14,39,.9);border:1px solid {r['acc']}66;border-left:none;border-radius:0 14px 14px 0;padding:18px 24px;font-size:30px;line-height:1.25}}
.aviso .b b{{color:{r['acc']}}}
"""
    fl = F.bandera
    ms = ""
    for p in d["partidos"]:
        ms += (f'<div class=m><div class=hd><div class=num>Partido {p["n"]}</div><div class=hr>{p["hora"]}</div></div>'
               f'<div class=bd><div class=pr>{fl("ar")}<div class=nm>{p["ar"][0]}</div><div class=nm>{p["ar"][1]}</div></div>'
               f'<div class="x gold">VS</div>'
               f'<div class="pr r">{fl(d["fp"])}<div class=nm>{p["ri"][0]}</div><div class=nm>{p["ri"][1]}</div></div></div></div>')
    av = d.get("aviso")
    aviso = f'<div class=aviso><div class=a>{av["a"]}</div><div class=b>{av["b"]}</div></div>' if av else ""
    body = (f'<div class=strip><div class=a>Mundial</div><div class=b>Doha · {d["jornada"]} · Caballeros</div></div>'
            f'<div class=metal style="font-size:130px;margin-top:44px">{d["titulo"]}</div>'
            f'<div class=top>{fl("ar")}Argentina<span class=v>vs</span>{d["rival"]}{fl(d["fp"])}</div>'
            f'<div class=sub>{d.get("sub", "")}</div>{ms}{aviso}'
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
