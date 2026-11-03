"""Carrusel 'Control o potencia' (4 láminas 1080x1350), estilo Sur Padel."""
import base64, pathlib, sys
from playwright.sync_api import sync_playwright

S = pathlib.Path(__file__).parent
REPO = pathlib.Path("/home/claude/repo")
F = S / "f/node_modules/@fontsource"
OUT = S / "carrusel"; OUT.mkdir(exist_ok=True)

def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()
def font(fam, path, w, st): return f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,{b64(F/path)});font-weight:{w};font-style:{st}}}"
FONTS = "".join([
    font("BC", "barlow-condensed/files/barlow-condensed-latin-800-italic.woff2", 800, "italic"),
    font("BC", "barlow-condensed/files/barlow-condensed-latin-700-italic.woff2", 700, "italic"),
    font("B", "barlow/files/barlow-latin-500-normal.woff2", 500, "normal"),
    font("B", "barlow/files/barlow-latin-700-normal.woff2", 700, "normal"),
])
LOGO = b64(REPO / "marca/logo-sur-padel-transparente.png")

def fondo(n): return b64(REPO / f"marca/fondos/{n}")

CSS = FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;background:#071528;color:#fff;font-family:B}
.bg{position:absolute;inset:0;background-size:cover;background-position:center}
.dark{position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,21,40,.55) 0%,rgba(7,21,40,.80) 45%,rgba(7,21,40,.96) 100%)}
.wrap{position:absolute;inset:0;padding:90px 84px;display:flex;flex-direction:column}
.tag{font-family:BC;font-weight:700;font-style:italic;font-size:34px;letter-spacing:3px;color:#74b4e8;text-transform:uppercase}
h1{font-family:BC;font-weight:800;font-style:italic;font-size:150px;line-height:.9;text-transform:uppercase;margin-top:24px}
h2{font-family:BC;font-weight:800;font-style:italic;font-size:110px;line-height:.92;text-transform:uppercase}
.gold{color:#f2b21c}
.sub{font-size:42px;line-height:1.3;margin-top:36px;color:#dfe9f5;max-width:880px}
ul{list-style:none;margin-top:40px}
li{font-size:40px;line-height:1.28;padding:22px 0 22px 64px;position:relative;border-bottom:2px solid rgba(116,180,232,.25)}
li:before{content:"";position:absolute;left:0;top:34px;width:30px;height:30px;border-radius:50%;background:#f2b21c}
.foot{margin-top:auto;display:flex;align-items:center;justify-content:space-between}
.foot img{width:120px}
.handle{font-family:BC;font-weight:700;font-style:italic;font-size:32px;color:#74b4e8;letter-spacing:1px}
.n{font-family:BC;font-weight:700;font-style:italic;font-size:30px;color:rgba(255,255,255,.6)}
.stripe{position:absolute;left:0;right:0;top:0;height:10px;background:linear-gradient(90deg,#74b4e8 0 33%,#fff 33% 66%,#74b4e8 66%)}
.shape{position:absolute;right:110px;top:760px;opacity:.95;transform:scale(1.25);transform-origin:top right}
.swipe{font-family:BC;font-weight:700;font-style:italic;font-size:40px;color:#f2b21c;margin-top:50px}
.meter{margin-top:56px}
.mlab{display:flex;justify-content:space-between;font-family:BC;font-weight:700;font-style:italic;font-size:34px;text-transform:uppercase;color:#74b4e8;letter-spacing:2px}
.bar{position:relative;height:22px;margin:22px 0 18px;border-radius:11px;background:linear-gradient(90deg,#74b4e8,#1d5cad 50%,#f2b21c)}
.dot{position:absolute;top:50%;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;background:#fff;border:10px solid #f2b21c;box-shadow:0 0 0 8px rgba(242,178,28,.25)}
.stops{display:flex;justify-content:space-between;font-size:30px;color:rgba(255,255,255,.55)}
.stops b{color:#fff}
.cards{display:flex;gap:20px;margin-top:90px}
.card{flex:1;background:rgba(11,29,54,.78);border:2px solid rgba(116,180,232,.35);border-radius:18px;padding:34px 26px}
.card .k{font-size:26px;color:#74b4e8;text-transform:uppercase;letter-spacing:2px;font-weight:700}
.card .v{font-family:BC;font-weight:800;font-style:italic;font-size:52px;margin-top:8px;text-transform:uppercase}
.row{display:flex;align-items:center;gap:40px;margin-top:44px}
.col{flex:1;display:flex;flex-direction:column;gap:20px}
.col .card{padding:24px 28px}
.ill{width:300px;display:flex;flex-direction:column;align-items:center}
.leg{margin-top:26px;font-size:28px;color:#dfe9f5;display:flex;align-items:center;gap:12px}
.leg .sw{width:26px;height:26px;border-radius:50%;border:3px dashed #f2b21c;background:rgba(242,178,28,.35)}
.trio{display:flex;justify-content:space-between;align-items:flex-end;margin-top:60px;padding:0 20px}
.trio div{display:flex;flex-direction:column;align-items:center;gap:18px;font-family:BC;font-weight:700;font-style:italic;font-size:36px;text-transform:uppercase;color:#74b4e8}
.cta{margin-top:44px;display:inline-block;background:#f2b21c;color:#071528;font-family:BC;font-weight:800;font-style:italic;font-size:46px;padding:20px 40px;border-radius:14px;text-transform:uppercase}
"""


def meter(pos, sel):
    names=["Redonda","Lágrima","Diamante"]
    st="".join(f"<b>{n}</b>" if n==sel else f"<span>{n}</span>" for n in names)
    return f'''<div class="meter"><div class="mlab"><span>Control</span><span>Potencia</span></div>
<div class="bar"><div class="dot" style="left:{pos}%"></div></div><div class="stops">{st}</div></div>'''

def cards(items):
    return '<div class="cards">'+"".join(f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div></div>' for k,v in items)+'</div>'

# Ilustración de paleta (gráfica, no realista), hecha con código.
HEADS = {
    "redonda": "M150 10 C238 10 288 80 288 172 C288 262 228 330 150 344 C72 330 12 262 12 172 C12 80 62 10 150 10 Z",
    "lagrima": "M150 8 C232 8 282 72 284 158 C286 238 236 312 150 344 C64 312 14 238 16 158 C18 72 68 8 150 8 Z",
    "diamante": "M150 6 C196 6 228 30 262 88 C290 136 294 176 280 214 C256 274 206 322 150 346 C94 322 44 274 20 214 C6 176 10 136 38 88 C72 30 104 6 150 6 Z",
}
SWEET = {"redonda": (150, 190, 86), "lagrima": (150, 158, 70), "diamante": (150, 118, 56)}

def paddle(kind, width=300, sweet=True, uid=""):
    k = kind + uid
    d = HEADS[kind]; sx, sy, sr = SWEET[kind]
    holes = "".join(f'<circle cx="{x}" cy="{y}" r="5.2"/>' for y in range(60, 300, 24) for x in range(66 + (12 if (y // 24) % 2 else 0), 240, 24))
    glow = f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="url(#sw{k})"/><circle cx="{sx}" cy="{sy}" r="{sr}" fill="none" stroke="#f2b21c" stroke-width="3" stroke-dasharray="8 8" opacity=".9"/>' if sweet else ""
    return f'''<svg width="{width}" height="{width*560/300:.0f}" viewBox="0 0 300 560" style="overflow:visible">
<defs>
 <linearGradient id="face{k}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a6cc4"/><stop offset=".55" stop-color="#1d5cad"/><stop offset="1" stop-color="#0b1d36"/></linearGradient>
 <linearGradient id="rim{k}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9fd0f5"/><stop offset=".5" stop-color="#74b4e8"/><stop offset="1" stop-color="#3f7fc0"/></linearGradient>
 <radialGradient id="sw{k}"><stop offset="0" stop-color="#f2b21c" stop-opacity=".75"/><stop offset=".6" stop-color="#f2b21c" stop-opacity=".25"/><stop offset="1" stop-color="#f2b21c" stop-opacity="0"/></radialGradient>
 <linearGradient id="shine{k}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <clipPath id="cl{k}"><path d="{d}" transform="translate(150 175) scale(.86) translate(-150 -175)"/></clipPath>
 <filter id="sh{k}" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="18" stdDeviation="16" flood-color="#000" flood-opacity=".55"/></filter>
</defs>
<g filter="url(#sh{k})">
 <path d="M112 330 L134 412 L166 412 L188 330 L170 336 L150 392 L130 336 Z" fill="url(#rim{k})"/>
 <rect x="126" y="404" width="48" height="146" rx="16" fill="#0b1d36" stroke="#74b4e8" stroke-width="4"/>
 {"".join(f'<path d="M128 {y} L172 {y+16}" stroke="#74b4e8" stroke-width="3" opacity=".55"/>' for y in range(418, 540, 20))}
 <rect x="122" y="536" width="56" height="20" rx="8" fill="#f2b21c"/>
 <path d="{d}" fill="url(#face{k})" stroke="url(#rim{k})" stroke-width="12"/>
 <path d="{d}" fill="none" stroke="#071528" stroke-width="2" transform="translate(150 175) scale(.93) translate(-150 -175)" opacity=".6"/>
 <g clip-path="url(#cl{k})" fill="#071528" opacity=".55">{holes}</g>
 {glow}
 <path d="{d}" fill="url(#shine{k})"/>
 <path d="M150 60 l7 16 h17 l-14 10 5 17 -15 -10 -15 10 5 -17 -14 -10 h17 z" fill="#f2b21c" opacity="{0 if sweet else .95}"/>
</g></svg>'''

def ficha(meter_html, items, kind):
    col = "".join(f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in items)
    return f'''{meter_html}<div class="row"><div class="col">{col}</div><div class="ill">{paddle(kind, 290)}
<div class="leg"><span class="sw"></span>Punto dulce</div></div></div>'''

def page(body, bg, n):
    return f"""<html><head><style>{CSS}</style></head><body>
<div class="bg" style="background-image:url(data:image/jpeg;base64,{fondo(bg)})"></div><div class="dark"></div><div class="stripe"></div>
<div class="wrap">{body}
<div class="foot"><span class="handle">@surpadelstore · surpadel.com.ar</span><span class="n">{n}/4</span><img src="data:image/png;base64,{LOGO}"></div></div></body></html>"""

L = [
    (page(f"""<div class="tag">Guía rápida · Sur Padel</div>
<h1>¿Control<br>o <span class="gold">potencia</span>?</h1>
<div class="sub">La pregunta que más nos hacen. En 3 láminas te decimos cuál va con tu juego.</div>
<div class="trio"><div>{paddle("redonda",230,False,"a")}Redonda</div><div>{paddle("lagrima",230,False,"a")}Lágrima</div><div>{paddle("diamante",230,False,"a")}Diamante</div></div>
<div class="swipe">Deslizá →</div>""", "fondo-05-focos.jpg", 1), "1-portada.png"),
    (page(f"""<div class="tag">Si buscás control</div>
<h2>Forma <span class="gold">redonda</span></h2>
{ficha(meter(6,"Redonda"),[("Punto dulce","Grande"),("Balance","Bajo"),("Perdona","Mucho"),("Ideal para","Drive e iniciación")],"redonda")}""", "fondo-03-cesped-linea.jpg", 2), "2-control.png"),
    (page(f"""<div class="tag">Si buscás potencia</div>
<h2>Forma <span class="gold">diamante</span></h2>
{ficha(meter(94,"Diamante"),[("Punto dulce","Chico y arriba"),("Balance","Alto"),("Pide","Técnica"),("Ideal para","Revés que define")],"diamante")}""", "fondo-01-arena-tribuna.jpg", 3), "3-potencia.png"),
    (page(f"""<div class="tag">¿En el medio? El equilibrio</div>
<h2>Forma <span class="gold">lágrima</span></h2>
{ficha(meter(50,"Lágrima"),[("Punto dulce","Medio"),("Balance","Medio"),("Ideal para","Todo terreno")],"lagrima")}
<div class="sub" style="margin-top:30px">¿Dudas? Escribinos por WhatsApp. Guía completa en la web.</div>""", "fondo-19-desenfocado-texto.jpg", 4), "4-cierre.png"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for html, name in L:
        pg.set_content(html); pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT / name))
    b.close()
print("ok")
