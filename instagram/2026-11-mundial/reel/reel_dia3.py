"""Reel 'Argentina 18 de 18' (Mundial Doha, jornada 3). Base: reel_dia2.py, con gancho en el primer segundo.

Toma de ambiente de APIMart (toma1-estadio.mp4) + gráficos animados estilo
'circuito pro' dibujados con Playwright cuadro por cuadro (fondo transparente)
y montados con ffmpeg.

Uso: FONTS_DIR=<node_modules/@fontsource> python3 reel.py <salida.mp4>
"""
import base64, os, pathlib, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
F = pathlib.Path(os.environ["FONTS_DIR"])
FPS, DUR = 24, 14.0
TOMA_A, TOMA_B, CRUCE = "toma05-focos.mp4", "toma04-publico.mp4", 6.6  # banco (duran 7,85 s): el cruce arranca antes de los 7 s
W, H = 1080, 1920


def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def ff(nombre, archivo, peso, estilo="normal"):
    return (f"@font-face{{font-family:{nombre};font-weight:{peso};font-style:{estilo};"
            f"src:url(data:font/woff2;base64,{b64(F / archivo)})}}")


FONTS = "".join([
    ff("BC", "barlow-condensed/files/barlow-condensed-latin-700-italic.woff2", 700, "italic"),
    ff("BC", "barlow-condensed/files/barlow-condensed-latin-800-italic.woff2", 800, "italic"),
    ff("B", "barlow/files/barlow-latin-600-normal.woff2", 600),
    ff("B", "barlow/files/barlow-latin-700-normal.woff2", 700),
])
LOGO = b64(RAIZ / "marca/logo-sur-padel-transparente.png")

CSS = FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;background:transparent;overflow:hidden;font-family:B;color:#fff}
.a{position:absolute;animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.8,.2,1)}
@keyframes inL{from{opacity:0;transform:translateX(-120px)}to{opacity:1;transform:none}}
@keyframes inR{from{opacity:0;transform:translateX(120px)}to{opacity:1;transform:none}}
@keyframes up{from{opacity:0;transform:translateY(60px)}to{opacity:1;transform:none}}
@keyframes pop{0%{opacity:0;transform:scale(.6)}70%{opacity:1;transform:scale(1.06)}100%{opacity:1;transform:scale(1)}}
@keyframes out{to{opacity:0;transform:translateY(-30px)}}
@keyframes fadeout{to{opacity:0}}
@keyframes dark{from{opacity:0}to{opacity:1}}
@keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}

/* capa oscura para que se lean los textos */
.v1{inset:0;background:linear-gradient(180deg,rgba(5,11,22,.75) 0%,rgba(5,11,22,.05) 22%,rgba(5,11,22,.0) 50%,rgba(5,11,22,.55) 100%)}
.v2{inset:0;background:rgba(5,11,22,.45);animation:dark .6s 2.3s both}
.v3{inset:0;background:radial-gradient(ellipse 90% 60% at 50% 45%,rgba(5,11,22,.38),rgba(5,11,22,.78));animation:dark .6s 9.1s both}

.strip{top:150px;left:50%;margin-left:-330px;width:660px;display:flex;height:66px;font-weight:700;letter-spacing:3px;
 text-transform:uppercase;font-size:24px;box-shadow:0 8px 30px rgba(0,0,0,.5);animation:wipe .6s .2s both}
.strip .x{background:#f2b21c;color:#071528;display:flex;align-items:center;padding:0 40px 0 22px;font-family:BC;font-style:italic;
 font-weight:800;font-size:36px;letter-spacing:1px;clip-path:polygon(0 0,100% 0,90% 100%,0 100%)}
.strip .y{flex:1;background:rgba(7,21,40,.92);border:1px solid rgba(255,255,255,.18);display:flex;align-items:center;
 padding:0 24px 0 30px;margin-left:-14px;clip-path:polygon(3% 0,100% 0,100% 100%,0 100%);gap:14px}
.dot{width:14px;height:14px;border-radius:50%;background:#ff3b3b;box-shadow:0 0 14px #ff3b3b;animation:blink 1s infinite}

.metal{font-family:BC;font-weight:800;font-style:italic;text-transform:uppercase;line-height:.86;text-align:center;
 background:linear-gradient(180deg,#fff 0%,#fff 45%,#c9d6e6 55%,#fff 100%);-webkit-background-clip:text;color:transparent;
 filter:drop-shadow(0 8px 24px rgba(0,0,0,.8))}
.gold{background:linear-gradient(180deg,#ffe9a8 0%,#f2b21c 45%,#b77a00 58%,#f2b21c 100%);-webkit-background-clip:text;color:transparent}
.t1{left:0;right:0;top:720px;font-size:250px;animation:pop .45s .05s both,out .4s 2.2s forwards}
.t2{left:0;right:0;top:930px;font-size:150px;animation:inR .5s .35s both,out .4s 2.25s forwards}
.kick{left:0;right:0;top:660px;text-align:center;font-weight:700;letter-spacing:10px;font-size:30px;color:#74b4e8;
 text-transform:uppercase;animation:up .4s .2s both,out .4s 2.2s forwards}

.ttl{left:70px;right:70px;top:440px;text-align:center;font-family:BC;font-style:italic;font-weight:800;font-size:92px;
 text-transform:uppercase;line-height:.9;filter:drop-shadow(0 6px 20px rgba(0,0,0,.8));animation:up .5s 2.5s both,fadeout .4s 9.0s forwards}
.sb{left:70px;right:70px;background:linear-gradient(180deg,rgba(10,22,42,.95),rgba(5,12,24,.95));border:1px solid rgba(255,255,255,.16);
 border-radius:8px;overflow:hidden;box-shadow:0 14px 40px rgba(0,0,0,.55)}
.sb .hd{display:flex;justify-content:space-between;padding:10px 22px;font-weight:700;font-size:24px;letter-spacing:4px;text-transform:uppercase}
.row{display:flex;align-items:center;height:92px;border-top:1px solid rgba(255,255,255,.08)}
.row .tri{width:0;height:0;border-left:16px solid #f2b21c;border-top:12px solid transparent;border-bottom:12px solid transparent;margin-left:22px;visibility:hidden}
.row.w .tri{visibility:visible}
.flag{width:48px;height:32px;margin-left:18px;border-radius:3px;background:linear-gradient(180deg,#74b4e8 33%,#fff 33% 66%,#74b4e8 66%);visibility:hidden}
.row.w .flag{visibility:visible}
.nm{flex:1;padding:0 20px;font-family:BC;font-style:italic;font-weight:800;font-size:54px;text-transform:uppercase;color:rgba(255,255,255,.6)}
.row.w .nm{color:#fff}
.pt{width:104px;height:100%;display:flex;align-items:center;justify-content:center;font-family:BC;font-style:italic;font-weight:800;
 font-size:64px;color:rgba(255,255,255,.55);border-left:1px solid rgba(255,255,255,.08)}
.cab .hd{background:linear-gradient(90deg,#174d94,#1d5cad)} .cab .w .pt{background:#f2b21c;color:#071528}
.dam .hd{background:linear-gradient(90deg,#8f2a5c,#b8366f)} .dam .w .pt{background:#ff6fa8;color:#16071a}
.dam .tri{border-left-color:#ff6fa8}
.s1{top:660px;animation:inL .5s 2.8s both,fadeout .4s 9.0s forwards}
.s2{top:960px;animation:inR .5s 3.2s both,fadeout .4s 9.0s forwards}
.dato{left:110px;right:110px;top:1270px;display:flex;align-items:center;gap:22px;background:rgba(7,21,40,.92);
 border-left:8px solid #f2b21c;padding:22px 28px;font-size:34px;font-weight:600;box-shadow:0 10px 30px rgba(0,0,0,.5);
 animation:up .5s 3.8s both,fadeout .4s 9.0s forwards}
.dato b{font-family:BC;font-style:italic;font-weight:800;font-size:54px;color:#f2b21c;white-space:nowrap}

.logo{left:50%;top:430px;width:330px;height:330px;margin-left:-165px;filter:drop-shadow(0 10px 40px rgba(0,0,0,.7));animation:pop .6s 9.4s both}
.c1{left:0;right:0;top:810px;font-size:132px;animation:up .5s 9.8s both}
.c2{left:0;right:0;top:1060px;text-align:center;animation:up .5s 10.2s both}
.pill{display:inline-flex;align-items:center;gap:16px;background:rgba(7,21,40,.92);border:1px solid rgba(255,255,255,.25);
 border-radius:60px;padding:20px 44px;font-weight:700;font-size:44px}
.pill span{color:#f2b21c}
.c3{left:0;right:0;top:1200px;text-align:center;font-size:28px;letter-spacing:5px;color:rgba(255,255,255,.7);animation:up .5s 10.5s both}
.cruz{left:50%;top:1300px;margin-left:-60px;width:120px;height:120px;animation:up .6s 10.7s both;opacity:.6}
"""


def sb(clase, rama, rival, pts):
    return (f'<div class="a sb {clase}"><div class=hd><span>{rama}</span><span>Final</span></div>'
            f'<div class="row w"><div class=tri></div><div class=flag></div><div class=nm>Argentina</div><div class=pt>{pts[0]}</div></div>'
            f'<div class=row><div class=tri></div><div class=flag></div><div class=nm>{rival}</div><div class=pt>{pts[1]}</div></div></div>')


def cruz():
    # Cruz del Sur sutil: cuatro estrellas celestes + una chica
    pts = [(60, 8, 9), (60, 108, 9), (18, 52, 7), (100, 60, 8), (78, 82, 4)]
    estrellas = "".join(f'<circle cx="{x}" cy="{y}" r="{r/2}" fill="#74b4e8"/>'
                        f'<path d="M{x} {y-r} L{x+r*.25} {y} L{x} {y+r} L{x-r*.25} {y}Z M{x-r} {y} L{x} {y-r*.25} L{x+r} {y} L{x} {y+r*.25}Z" fill="#74b4e8"/>'
                        for x, y, r in pts)
    return f'<svg class="a cruz" viewBox="0 0 120 120">{estrellas}</svg>'


BODY = (
    '<div class="a v1"></div><div class="a v2"></div><div class="a v3"></div>'
    '<div class="a strip"><div class=x>Mundial</div><div class=y><span class=dot></span>Doha · Fase de grupos</div></div>'
    '<div class="a kick">Argentina en el Mundial</div>'
    '<div class="a metal t1"><span class=gold>18 de 18</span></div>'
    '<div class="a metal t2">partidos ganados</div>'
    '<div class="a ttl">Jornada 3: <span class=gold>3 a 0</span></div>'
    + sb("cab s1", "Caballeros", "Francia", (3, 0))
    + sb("dam s2", "Damas", "Francia", (3, 0)) +
    '<div class="a dato"><b>6-0 6-0</b>Brea / Jensen, sin ceder un solo game</div>'
    f'<img class="a logo" src="data:image/png;base64,{LOGO}">'
    '<div class="a metal c1">El Mundial<br><span class=gold>día a día</span></div>'
    '<div class="a c2"><div class=pill>Seguí a <span>@surpadelstore</span></div></div>'
    '<div class="a c3">SURPADEL.COM.AR</div>'
    + cruz()
)


def cuadros(carpeta):
    n = int(FPS * DUR)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body>{BODY}</body></html>")
        pg.wait_for_timeout(400)
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        for i in range(n):
            ms = i * 1000 / FPS
            pg.evaluate(f"document.getAnimations().forEach(a=>a.currentTime={ms})")
            pg.screenshot(path=f"{carpeta}/{i:04d}.png", omit_background=True)
        b.close()


def montar(carpeta, salida):
    # dos tomas 1080p nativas a 24 cuadros (sin estirar ni congelar), fundidas en CRUCE
    a, b = RAIZ / 'instagram/banco-tomas' / TOMA_A, RAIZ / 'instagram/banco-tomas' / TOMA_B
    filtro = (
        "[0:v]setsar=1,format=yuv420p[a];[1:v]setsar=1,format=yuv420p[b];"
        f"[a][b]xfade=transition=fade:duration=0.8:offset={CRUCE},trim=duration={DUR},"
        "unsharp=5:5:0.35[v];"
        "[v][2:v]overlay=0:0:format=auto,format=yuv420p[out];"
        f"anullsrc=r=48000:cl=stereo,atrim=duration={DUR}[aud]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a), "-i", str(b), "-framerate", str(FPS),
                    "-i", f"{carpeta}/%04d.png", "-filter_complex", filtro, "-map", "[out]", "-map", "[aud]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-profile:v", "high", "-r", str(FPS),
                    "-maxrate", "25M", "-bufsize", "40M",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(salida)], check=True)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        cuadros(tmp)
        montar(tmp, sys.argv[1])
    print(sys.argv[1])
