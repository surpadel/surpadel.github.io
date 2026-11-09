"""Muestra del plan semana 9-15/11: portada Táctica Sur n.º 1, carrusel 'Cuidá tu paleta' y reel 'Elegí con la Guía'."""
import os, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "overgrip/diseno"))
os.environ.setdefault("LOGO_PNG", str(pathlib.Path(__file__).resolve().parents[2] / "marca/logo-sur-padel-transparente.png"))
import gen
from playwright.sync_api import sync_playwright

R = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).parent
t = gen.THEMES["azul"]

def bg(f):
    return f"url(data:image/{'jpeg' if f.endswith('.jpg') else 'png'};base64,{gen.b64(R/'marca/fondos'/f)}) center/cover"

CSS = gen.FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{overflow:hidden;font-family:B;color:#fff;position:relative;background:#050b16}}
.bgimg{{position:absolute;inset:0}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,11,22,.85),rgba(5,11,22,.45) 35%,rgba(5,11,22,.55) 65%,rgba(5,11,22,.95))}}
.wrap{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center}}
.strip{{display:flex;height:64px;font-weight:700;letter-spacing:3px;text-transform:uppercase;font-size:24px;box-shadow:0 8px 30px rgba(0,0,0,.5)}}
.strip .a{{background:{t['hot']};color:#071528;display:flex;align-items:center;padding:0 40px 0 22px;font-family:BC;font-style:italic;font-weight:800;font-size:34px;clip-path:polygon(0 0,100% 0,92% 100%,0 100%)}}
.strip .b{{background:rgba(7,21,40,.92);border:1px solid rgba(255,255,255,.18);display:flex;align-items:center;padding:0 26px 0 30px;margin-left:-14px}}
.metal{{font-family:BC;font-weight:800;font-style:italic;text-transform:uppercase;line-height:.9;text-align:center;
 background:linear-gradient(180deg,#fff 0%,#fff 45%,#c9d6e6 55%,#fff 100%);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 6px 20px rgba(0,0,0,.7))}}
.gold{{background:linear-gradient(180deg,#ffe9a8 0%,{t['hot']} 45%,#b77a00 58%,{t['hot']} 100%);-webkit-background-clip:text;color:transparent}}
.sub{{font-size:34px;font-weight:600;text-align:center;color:rgba(255,255,255,.9);line-height:1.3}}
.kick{{font-weight:700;letter-spacing:8px;font-size:26px;color:{t['acc']};text-transform:uppercase}}
.brand{{font-size:22px;letter-spacing:3px;color:rgba(255,255,255,.6)}}
.logo{{width:110px;height:110px;filter:drop-shadow(0 6px 24px rgba(0,0,0,.6))}}
.stars{{position:absolute;right:70px;top:150px;opacity:.4}} .stars i{{position:absolute;color:{t['acc']};font-style:normal;font-size:20px}}
"""
STARS = '<div class=stars><i style="left:0;top:0">✦</i><i style="left:40px;top:60px">✦</i><i style="left:-30px;top:110px">✦</i><i style="left:20px;top:160px">✦</i></div>'
LOGO = f'<img class=logo src="data:image/png;base64,{gen.LOGO}">'

def court():
    # media cancha vista desde arriba (10 m x 10 m), red arriba, pared de fondo abajo
    W, H = 760, 760; s = W / 10
    sv = 6.95 * s  # línea de saque a 6,95 m de la red
    z = [  # (desde, hasta, color, texto)
        (0, 3.2 * s, "rgba(242,178,28,.45)", "RED · ATAQUE"),
        (3.2 * s, sv + 0.6 * s, "rgba(116,180,232,.25)", "TRANSICIÓN"),
        (sv + 0.6 * s, H, "rgba(7,21,40,.45)", "FONDO · DEFENSA"),
    ]
    rects = "".join(f'<rect x=0 y={a} width={W} height={b-a} fill="{c}"/>' for a, b, c, _ in z)
    labels = "".join(f'<text x={W/2} y={(a+b)/2+14} text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=46 fill="#fff" style="letter-spacing:2px">{l}</text>' for a, b, _, l in z)
    lines = (f'<rect x=2 y=2 width={W-4} height={H-4} fill=none stroke="#fff" stroke-width="5" />'
             f'<line x1=0 y1={sv} x2={W} y2={sv} stroke="#fff" stroke-width="5" />'
             f'<line x1={W/2} y1=0 x2={W/2} y2={sv} stroke="#fff" stroke-width="5" />'
             f'<line x1=-20 y1=0 x2={W+20} y2=0 stroke="#fff" stroke-width=12 stroke-dasharray="6 6"/>')
    players = (f'<circle cx={W*0.16} cy={1.8*s} r=22 fill="{t["hot"]}" stroke="#071528" stroke-width="5" />'
               f'<circle cx={W*0.84} cy={8.9*s} r=22 fill="{t["hot"]}" stroke="#071528" stroke-width="5" />'
               f'<path d="M{W*0.84} {8.5*s} C {W*0.84} {6*s}, {W*0.76} {4.5*s}, {W*0.76} {3.1*s}" fill=none stroke="#fff" stroke-width=6 stroke-dasharray="14 10" marker-end="url(#ar)"/>')
    return (f'<svg width={W} height={H+30} viewBox="0 -15 {W} {H+30}" style="filter:drop-shadow(0 20px 40px rgba(0,0,0,.6));transform:perspective(1400px) rotateX(18deg)">'
            f'<defs><marker id=ar markerWidth=8 markerHeight=8 refX=4 refY=4 orient=auto><path d="M0 0L8 4L0 8z" fill="#fff"/></marker></defs>'
            f'<rect x=0 y=0 width={W} height={H} fill="{t["court2"]}"/>{rects}{lines}{labels}{players}</svg>')

def tactica():
    return 1080, 1920, f"""<div class=bgimg style="background:{bg('fondo-04-cenital.jpg')}"></div><div class=shade></div>{STARS}
<div class=wrap style="padding:120px 70px 110px">
 <div class=strip><div class=a>TÁCTICA SUR</div><div class=b>N.º 1</div></div>
 <div class=metal style="font-size:118px;margin-top:46px">Las 3 zonas<br><span class=gold>de la cancha</span></div>
 <div class=sub style="margin-top:26px">Saber dónde estás te dice qué pelota jugar</div>
 <div style="margin-top:40px">{court()}</div>
 <div style="margin-top:auto;display:flex;flex-direction:column;align-items:center;gap:14px">{LOGO}<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>
</div>"""

def cuidado():
    items = ["Nada de auto al sol", "Protector en el borde", "Funda siempre", "Overgrip al día", "No la golpees contra el piso"]
    li = "".join(f'<div style="display:flex;align-items:center;gap:22px;background:rgba(7,21,40,.85);border:1px solid rgba(255,255,255,.16);border-left:8px solid {t["hot"]};padding:16px 26px;width:100%;font-size:36px;font-weight:700"><span style="font-family:BC;font-style:italic;font-weight:800;font-size:50px;color:{t["hot"]}">{i+1}</span>{x}</div>' for i, x in enumerate(items))
    return 1080, 1350, f"""<div class=bgimg style="background:{bg('fondo-23-vestuario-banco.png')}"></div><div class=shade></div>{STARS}
<div class=wrap style="padding:70px 90px 60px">
 <div class=kick>Útil para tu juego</div>
 <div class=metal style="font-size:120px;margin-top:20px">Cuidá tu <span class=gold>paleta</span></div>
 <div class=sub style="margin-top:14px;font-size:32px">5 hábitos que le estiran la vida</div>
 <div style="margin-top:44px;width:100%;display:flex;flex-direction:column;gap:16px">{li}</div>
 <div style="margin-top:auto;display:flex;align-items:center;gap:20px"><div class=brand>Deslizá → · @SURPADELSTORE · SURPADEL.COM.AR</div></div>
</div>"""

def guia():
    meters = [("Control", 82), ("Potencia", 45), ("Peso", 60)]
    m = "".join(f'<div style="width:100%"><div style="display:flex;justify-content:space-between;font-size:34px;font-weight:700;margin-bottom:10px"><span>{n}</span><span style="color:{t["acc"]}">{"●"*round(v/20)}{"○"*(5-round(v/20))}</span></div><div style="height:22px;border-radius:11px;background:rgba(255,255,255,.15)"><div style="height:100%;width:{v}%;border-radius:11px;background:linear-gradient(90deg,{t["court"]},{t["acc"]})"></div></div></div>' for n, v in meters)
    return 1080, 1920, f"""<div class=bgimg style="background:{bg('fondo-06-final-spot.jpg')}"></div><div class=shade></div>{STARS}
<div class=wrap style="padding:160px 90px 110px">
 <div class=kick>¿Empezás o subís de nivel?</div>
 <div class=metal style="font-size:130px;margin-top:30px">¿Qué paleta<br>va con <span class=gold>tu juego?</span></div>
 <div class=sub style="margin-top:30px">Forma, goma y peso, en 20 segundos</div>
 <div style="margin-top:90px;width:100%;display:flex;flex-direction:column;gap:40px;background:rgba(7,21,40,.8);border:1px solid rgba(255,255,255,.16);border-radius:14px;padding:50px 50px">{m}
  <div style="font-family:BC;font-style:italic;font-weight:800;font-size:56px;text-align:center;color:{t['hot']}">REDONDA · INICIACIÓN</div></div>
 <div style="margin-top:auto;display:flex;flex-direction:column;align-items:center;gap:14px"><div class=sub style="font-size:32px">La guía completa: <b style="color:{t['acc']}">link en la bio</b></div>{LOGO}</div>
</div>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, fn in [("muestra-tactica-sur-1.png", tactica), ("muestra-cuidado-paleta.png", cuidado), ("muestra-reel-guia.png", guia)]:
        W, H, body = fn()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body style='width:{W}px;height:{H}px'>{body}</body></html>")
        pg.wait_for_timeout(400); pg.screenshot(path=str(OUT / name)); pg.close(); print(OUT / name)
    b.close()
