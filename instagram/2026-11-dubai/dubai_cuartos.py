"""Dubái: los cuartos (12/11 noche, post de feed aprobado por Nico el 11/11). Copia de dubai_v2.py.

Feed 1080x1350. Corre en "Armar piezas" (FONTS_DIR y LOGO_PNG ya puestos).
"""
import os, sys, pathlib
R = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "overgrip/diseno"))
os.environ.setdefault("LOGO_PNG", str(R / "marca/logo-sur-padel-transparente.png"))
import gen
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
t = gen.THEMES["azul"]
r = gen.THEMES["rosa"]


def bg(f):
    return f"url(data:image/{'jpeg' if f.endswith('.jpg') else 'png'};base64,{gen.b64(R/'marca/fondos'/f)}) center/cover"


CSS = gen.FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{overflow:hidden;font-family:B;color:#fff;position:relative;background:#050b16}}
.bgimg{{position:absolute;inset:0}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,11,22,.9),rgba(5,11,22,.55) 30%,rgba(5,11,22,.7) 60%,rgba(5,11,22,.96))}}
.wrap{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center}}
.strip{{display:flex;height:62px;font-weight:700;letter-spacing:3px;text-transform:uppercase;font-size:24px;box-shadow:0 8px 30px rgba(0,0,0,.5)}}
.strip .a{{background:{t['hot']};color:#071528;display:flex;align-items:center;padding:0 40px 0 22px;font-family:BC;font-style:italic;font-weight:800;font-size:34px;clip-path:polygon(0 0,100% 0,92% 100%,0 100%)}}
.strip .b{{background:rgba(7,21,40,.92);border:1px solid rgba(255,255,255,.18);display:flex;align-items:center;padding:0 26px 0 30px;margin-left:-14px}}
.live{{display:inline-block;width:14px;height:14px;border-radius:50%;background:#e5322d;margin-right:12px;box-shadow:0 0 12px #e5322d}}
.metal{{font-family:BC;font-weight:800;font-style:italic;text-transform:uppercase;line-height:.9;text-align:center;
 background:linear-gradient(180deg,#fff 0%,#fff 45%,#c9d6e6 55%,#fff 100%);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 6px 20px rgba(0,0,0,.7))}}
.gold{{background:linear-gradient(180deg,#ffe9a8 0%,{t['hot']} 45%,#b77a00 58%,{t['hot']} 100%);-webkit-background-clip:text;color:transparent}}
.sub{{font-size:33px;font-weight:600;text-align:center;color:rgba(255,255,255,.92);line-height:1.3}}
.sub b{{color:{t['acc']}}}
.brand{{font-size:22px;letter-spacing:3px;color:rgba(255,255,255,.65)}}
.seed{{display:flex;align-items:center;width:100%;background:rgba(7,21,40,.86);border:1px solid rgba(255,255,255,.16);border-left:8px solid {t['hot']};height:100px}}
.seed .n{{width:96px;text-align:center;font-family:BC;font-style:italic;font-weight:800;font-size:58px;color:{t['hot']}}}
.seed .p{{flex:1;font-family:BC;font-style:italic;font-weight:800;font-size:50px;text-transform:uppercase;letter-spacing:1px}}
.seed .p em{{font-style:italic;color:{t['acc']}}}
.seed .f{{width:54px;height:36px;margin-right:30px;border-radius:4px;position:relative;
 background:linear-gradient(180deg,#74acdf 33.3%,#fff 33.3% 66.6%,#74acdf 66.6%);box-shadow:0 2px 8px rgba(0,0,0,.5)}}
.seed .f i{{position:absolute;left:50%;top:50%;width:10px;height:10px;margin:-5px;border-radius:50%;background:#f6b40e}}
.seed.rosa{{border-left-color:{r['hot']}}} .seed.rosa .n{{color:{r['hot']}}} .seed.rosa .p em{{color:{r['acc']}}}
.lab{{align-self:flex-start;font-weight:700;letter-spacing:5px;font-size:22px;text-transform:uppercase;color:{t['acc']};margin:0 0 10px 4px}}
.lab.rosa{{color:{r['acc']}}}
.opt{{display:flex;align-items:center;gap:24px;width:100%;background:rgba(7,21,40,.88);border:1px solid rgba(255,255,255,.16);padding:16px 28px;font-size:36px;font-weight:700}}
.opt span{{font-family:BC;font-style:italic;font-weight:800;font-size:56px;color:{t['hot']};width:40px}}
.stars{{position:absolute;right:70px;top:140px;opacity:.4}} .stars i{{position:absolute;color:{t['acc']};font-style:normal;font-size:20px}}
"""
STARS = '<div class=stars><i style="left:0;top:0">✦</i><i style="left:40px;top:60px">✦</i><i style="left:-30px;top:110px">✦</i><i style="left:20px;top:160px">✦</i></div>'
BRAND = '<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div>'


def seed(n, html, rosa=False):
    return f'<div class="seed {"rosa" if rosa else ""}"><div class=n>{n}</div><div class=p>{html}</div></div>'


CSS += f"""
.cr{{width:100%;background:rgba(7,21,40,.88);border:1px solid rgba(255,255,255,.16);border-left:8px solid {t['hot']};padding:14px 26px 16px}}
.cr.rosa{{border-left-color:{r['hot']}}}
.cr .hd{{display:flex;justify-content:space-between;font-weight:700;letter-spacing:4px;font-size:20px;text-transform:uppercase;color:{t['acc']};margin-bottom:6px}}
.cr.rosa .hd{{color:{r['acc']}}}
.cr .hd .tag{{color:#071528;background:{t['hot']};padding:2px 12px;letter-spacing:2px}}
.cr.rosa .hd .tag{{background:{r['hot']};color:#16071a}}
.cr .pp{{display:flex;align-items:center;gap:18px;font-family:BC;font-style:italic;font-weight:800;font-size:44px;text-transform:uppercase}}
.cr .pp .vs{{font-size:30px;color:rgba(255,255,255,.55)}}
.cr .pp em{{font-style:italic;color:{t['acc']}}}
.cr.rosa .pp em{{color:{r['acc']}}}
"""


def cruce(a, b, rosa=False, duelo=False):
    tag = '<span class=tag>Duelo argentino</span>' if duelo else '<span></span>'
    return (f'<div class="cr {"rosa" if rosa else ""}"><div class=hd><span>{"Damas" if rosa else "Caballeros"} · cuartos</span>{tag}</div>'
            f'<div class=pp><span>{a}</span><span class=vs>vs.</span><span>{b}</span></div></div>')


def cuartos():
    filas = (cruce("<em>Augsburger</em> / Lebrón", "<em>Tello</em> / <em>Arce</em>", duelo=True)
             + cruce("<em>Dal Bianco</em> / Abbate", "<em>Campagnolo</em> / Momo", duelo=True)
             + cruce("<em>Stupaczuk</em> / Sanz", "De Pascual / Garrido")
             + cruce("<em>Alfonso</em> / <em>Libaak</em>", "Bautista / Bergamini")
             + cruce("<em>Brea</em> / Triay", "<em>Jensen</em> / Icardo", rosa=True, duelo=True))
    return 1080, 1350, f"""<div class=bgimg style="background:{bg('fondo-18-terraza-ciudad.jpg')}"></div><div class=shade></div>{STARS}
<div class=wrap style="padding:64px 80px 50px">
 <div class=strip><div class=a>DUBÁI P1</div><div class=b><span class=live></span>Viernes · cuartos de final</div></div>
 <div class=metal style="font-size:100px;margin-top:34px">Cuartos con<br><span class=gold>sello argentino</span></div>
 <div class=sub style="margin-top:18px">Tres cruces entre argentinos:<br><b>ya hay semifinalistas asegurados</b></div>
 <div style="width:100%;display:flex;flex-direction:column;gap:14px;margin-top:30px">{filas}</div>
 <div style="margin-top:auto;display:flex;flex-direction:column;align-items:center;gap:8px">
  <div class=sub style="font-size:28px">Se juegan el viernes · los resultados, acá</div>{BRAND}</div>
</div>"""


with sync_playwright() as p:
    b = p.chromium.launch()
    for name, fn in [("dubai-cuartos.png", cuartos)]:
        W, H, body = fn()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body style='width:{W}px;height:{H}px'>{body}</body></html>")
        pg.wait_for_timeout(400); pg.screenshot(path=str(OUT / name)); pg.close(); print(OUT / name)
    b.close()
