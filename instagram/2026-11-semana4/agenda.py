"""Semana 16-22/11: post 'Lo que queda del año' (mié 18/11 20:00). Agenda guardable: zona sur / La Plata + circuito.

Feed 1080x1350, estilo estadio de noche. Corre en "Armar piezas" (FONTS_DIR y LOGO_PNG ya puestos).
Salida: agenda-fin-de-ano.png en esta carpeta.
"""
import os, sys, pathlib
R = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "overgrip/diseno"))
os.environ.setdefault("LOGO_PNG", str(R / "marca/logo-sur-padel-transparente.png"))
import gen
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
t = gen.THEMES["azul"]

ZONA = [("20–23 NOV", "Animal 81", "y llaves 28 y 29/11"),
        ("21–23 NOV", "Metro Padel", "llaves"),
        ("21–22 NOV", "APB Master", "Berazategui"),
        ("4–13 DIC", "Retro Padel", "Los Hornos"),
        ("5–6 DIC", "Grand Master ALPHA", "La Plata")]
PRO = [("23–29 NOV", "Mexico Major", "Acapulco"),
       ("10–13 DIC", "Finals", "Barcelona · cierre del año")]

FONDO = gen.b64(R / "marca/fondos/fondo-12-club-canchas.jpg")

CSS = gen.FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;overflow:hidden;font-family:B;color:#fff;position:relative;background:#050b16}}
.bgimg{{position:absolute;inset:0;background:url(data:image/jpeg;base64,{FONDO}) center/cover}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,11,22,.92),rgba(5,11,22,.7) 30%,rgba(5,11,22,.8) 60%,rgba(5,11,22,.97))}}
.wrap{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;padding:60px 76px 46px}}
.strip{{display:flex;height:60px;font-weight:700;letter-spacing:3px;text-transform:uppercase;font-size:24px;box-shadow:0 8px 30px rgba(0,0,0,.5)}}
.strip .a{{background:{t['hot']};color:#071528;display:flex;align-items:center;padding:0 40px 0 22px;font-family:BC;font-style:italic;font-weight:800;font-size:34px;clip-path:polygon(0 0,100% 0,92% 100%,0 100%)}}
.strip .b{{background:rgba(7,21,40,.92);border:1px solid rgba(255,255,255,.18);display:flex;align-items:center;padding:0 26px 0 30px;margin-left:-14px}}
.metal{{font-family:BC;font-weight:800;font-style:italic;text-transform:uppercase;line-height:.9;text-align:center;
 background:linear-gradient(180deg,#fff 0%,#fff 45%,#c9d6e6 55%,#fff 100%);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 6px 20px rgba(0,0,0,.7))}}
.gold{{background:linear-gradient(180deg,#ffe9a8 0%,{t['hot']} 45%,#b77a00 58%,{t['hot']} 100%);-webkit-background-clip:text;color:transparent}}
.lab{{align-self:flex-start;font-weight:700;letter-spacing:5px;font-size:23px;text-transform:uppercase;color:{t['acc']};margin:0 0 10px 4px}}
.row{{display:flex;align-items:center;width:100%;height:82px;background:rgba(7,21,40,.88);border:1px solid rgba(255,255,255,.16);border-left:8px solid {t['acc']};margin-bottom:9px}}
.row.pro{{border-left-color:{t['hot']}}}
.row .d{{width:230px;padding-left:22px;font-family:BC;font-style:italic;font-weight:800;font-size:40px;color:{t['acc']};letter-spacing:1px}}
.row.pro .d{{color:{t['hot']}}}
.row .n{{flex:1;font-family:BC;font-style:italic;font-weight:800;font-size:46px;text-transform:uppercase}}
.row .s{{padding-right:24px;font-size:24px;font-weight:600;color:rgba(255,255,255,.7);text-align:right}}
.sub{{font-size:31px;font-weight:600;text-align:center;color:rgba(255,255,255,.92);line-height:1.3}}
.sub b{{color:{t['hot']}}}
.brand{{font-size:22px;letter-spacing:3px;color:rgba(255,255,255,.65)}}
.stars{{position:absolute;right:70px;top:150px;opacity:.4}} .stars i{{position:absolute;color:{t['acc']};font-style:normal;font-size:20px}}
"""
STARS = '<div class=stars><i style="left:0;top:0">✦</i><i style="left:40px;top:60px">✦</i><i style="left:-30px;top:110px">✦</i><i style="left:20px;top:160px">✦</i></div>'


def filas(lst, pro=False):
    return "".join(f'<div class="row {"pro" if pro else ""}"><div class=d>{d}</div><div class=n>{n}</div><div class=s>{s}</div></div>' for d, n, s in lst)


BODY = f"""<div class=bgimg></div><div class=shade></div>{STARS}
<div class=wrap>
 <div class=strip><div class=a>AGENDA</div><div class=b>Noviembre y diciembre</div></div>
 <div class=metal style="font-size:108px;margin-top:30px">Lo que queda<br>del <span class=gold>año</span></div>
 <div class=lab style="margin-top:34px">En la zona · sur y La Plata</div>
 {filas(ZONA)}
 <div class=lab style="margin-top:20px;color:{t['hot']}">Circuito profesional</div>
 {filas(PRO, True)}
 <div style="margin-top:auto;display:flex;flex-direction:column;align-items:center;gap:10px">
  <div class=sub><b>Guardalo</b> y seguinos: te contamos cada resultado</div>
  <div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>
</div>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body>{BODY}</body></html>")
    pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT / "agenda-fin-de-ano.png"))
    b.close()
print(OUT / "agenda-fin-de-ano.png")
