"""Reel de torneos locales (OverGrip), estilo "Torneos del Sur".

Distinto a propósito del estilo "circuito pro" de Premier (zócalo de TV, títulos
metalizados en itálica, tableros oscuros, punto rojo "en vivo", estadio):
acá es pádel de club. Fondos de club de barrio con grano, planillas de papel
pegadas con cinta, títulos rectos con contorno celeste, marcadores de chapa
(tipo flip), sello circular "Torneos del Sur" con la Cruz del Sur y golpes
secos en vez de fundidos. Mantiene escudo, colores y tipografías de Sur Padel.

Rama damas: misma pieza con rosa claro y rosa chicle en lugar de celeste.

Uso: FONTS_DIR=<node_modules/@fontsource> python3 reel_local.py spec.json salida.mp4
spec.json: ver muestra-tremendas.json en instagram/overgrip-reels/.
"""
import base64, json, os, pathlib, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
F = pathlib.Path(os.environ["FONTS_DIR"])
FPS, W, H = 24, 1080, 1920
T_CARDS, T_DATO, T_CIERRE, DUR = 2.8, 10.2, 12.6, 15.5


def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def ff(nombre, archivo, peso, estilo="normal"):
    return (f"@font-face{{font-family:{nombre};font-weight:{peso};font-style:{estilo};"
            f"src:url(data:font/woff2;base64,{b64(F / archivo)})}}")


FONTS = "".join([
    ff("BC", "barlow-condensed/files/barlow-condensed-latin-700-normal.woff2", 700),
    ff("BC", "barlow-condensed/files/barlow-condensed-latin-800-normal.woff2", 800),
    ff("BC", "barlow-condensed/files/barlow-condensed-latin-900-normal.woff2", 900),
    ff("B", "barlow/files/barlow-latin-500-normal.woff2", 500),
    ff("B", "barlow/files/barlow-latin-700-normal.woff2", 700),
    ff("B", "barlow/files/barlow-latin-800-normal.woff2", 800),
])
LOGO = b64(RAIZ / "marca/logo-sur-padel-transparente.png")

PAL = {  # acento, acento fuerte, texto sobre acento
    "cab": ("#74b4e8", "#1d5cad", "#071528"),
    "dam": ("#f4a3c4", "#ff6fa8", "#16071a"),
}


def css(rama):
    ac, ac2, tx = PAL[rama]
    return FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;background:transparent;overflow:hidden;font-family:B;color:#fff}}
.a{{position:absolute;animation-fill-mode:both}}
@keyframes slap{{0%{{opacity:0;transform:translateY(-140px) rotate(var(--r0)) scale(1.15)}}
 70%{{opacity:1;transform:translateY(8px) rotate(var(--r)) scale(.98)}}100%{{opacity:1;transform:rotate(var(--r))}}}}
@keyframes tape{{from{{opacity:0;transform:rotate(var(--r)) scaleX(0)}}to{{opacity:1;transform:rotate(var(--r)) scaleX(1)}}}}
@keyframes up{{from{{opacity:0;transform:translateY(50px)}}to{{opacity:1;transform:none}}}}
@keyframes cut{{to{{opacity:0}}}}
@keyframes away{{to{{opacity:0;transform:translateX(-160px) rotate(-6deg)}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes stamp{{0%{{opacity:0;transform:scale(1.8) rotate(-20deg)}}60%{{opacity:1;transform:scale(.92) rotate(-8deg)}}100%{{opacity:1;transform:scale(1) rotate(-8deg)}}}}
@keyframes flip{{0%{{transform:rotateX(90deg)}}100%{{transform:rotateX(0)}}}}
@keyframes bars{{0%{{opacity:1;transform:translateX(-1000px) skewX(-18deg)}}99%{{opacity:1}}100%{{opacity:0;transform:translateX(1700px) skewX(-18deg)}}}}
@keyframes mark{{from{{background-size:0% 38%}}to{{background-size:100% 38%}}}}
@keyframes dark{{from{{opacity:0}}to{{opacity:1}}}}

.v1{{inset:0;background:linear-gradient(180deg,rgba(7,21,40,.55) 0%,rgba(7,21,40,0) 30%,rgba(7,21,40,.1) 60%,rgba(7,21,40,.7) 100%)}}
.v2{{inset:0;background:rgba(7,21,40,.42);animation:dark .25s {T_CARDS-.1}s both}}
.v3{{inset:0;background:rgba(7,21,40,.25);animation:dark .25s {T_DATO}s both}}

/* barridas diagonales de transición (golpe seco, no fundido) */
.bar{{top:-200px;bottom:-200px;width:620px;left:0;opacity:0}}
.bar.b1{{background:{ac};animation:bars .45s linear}}
.bar.b2{{background:#071528;animation:bars .45s linear}}

/* sello circular */
.sello{{right:54px;top:150px;width:200px;height:200px;animation:stamp .5s .25s both}}
.sello svg{{width:200px;height:200px}}
.sello .giro{{transform-origin:100px 100px;animation:spin 14s linear infinite}}

/* cinta (masking tape) */
.cinta{{--r:-3deg;background:rgba(244,241,234,.94);color:#071528;font-family:BC;font-weight:800;text-transform:uppercase;
 letter-spacing:2px;padding:12px 34px;transform-origin:left center;
 clip-path:polygon(0 8%,2% 0,4% 10%,6% 0,96% 0,98% 12%,100% 0,100% 92%,98% 100%,96% 88%,94% 100%,4% 100%,2% 90%,0 100%);
 box-shadow:0 6px 18px rgba(0,0,0,.35)}}
.c-top{{left:64px;top:190px;font-size:40px;animation:tape .35s .45s both,cut .2s {T_CARDS}s forwards}}
.c-sub{{--r:2deg;left:96px;top:262px;font-size:28px;font-family:B;font-weight:700;letter-spacing:3px;background:{ac};
 animation:tape .35s .65s both,cut .2s {T_CARDS}s forwards}}

/* títulos rectos: uno lleno, uno en contorno */
.tit{{left:60px;right:60px;font-family:BC;font-weight:900;text-transform:uppercase;line-height:.84;
 filter:drop-shadow(0 8px 22px rgba(0,0,0,.7))}}
.tit .o{{color:rgba(7,21,40,.55);-webkit-text-stroke:5px {ac}}}
.tit .g{{color:#f2b21c}}
.h1{{top:720px;font-size:210px;animation:up .4s .55s both,away .3s {T_CARDS-.2}s forwards}}
.h2{{top:900px;font-size:210px;animation:up .4s .8s both,away .3s {T_CARDS-.15}s forwards}}

.cab{{left:60px;top:410px;font-family:BC;font-weight:900;font-size:96px;text-transform:uppercase;line-height:.9;
 animation:up .35s {T_CARDS+.05}s both,cut .2s {T_DATO}s forwards;filter:drop-shadow(0 6px 18px rgba(0,0,0,.7))}}
.cab .o{{color:transparent;-webkit-text-stroke:3px {ac}}}

/* planillas de papel */
.pl{{left:70px;right:70px;background:#f4f1ea;color:#071528;border-radius:4px;padding:56px 28px 22px 28px;
 box-shadow:0 18px 40px rgba(0,0,0,.55);
 background-image:repeating-linear-gradient(180deg,transparent 0 45px,rgba(29,92,173,.10) 45px 46px)}}
.pl .tab{{position:absolute;left:-10px;top:-18px;background:{ac};color:{tx};font-family:BC;font-weight:900;font-size:40px;
 text-transform:uppercase;padding:6px 26px 4px;letter-spacing:1px;transform:rotate(-2deg);box-shadow:0 6px 14px rgba(0,0,0,.3)}}
.pl .pin{{position:absolute;right:60px;top:-16px;width:150px;height:34px;background:rgba(244,241,234,.75);transform:rotate(4deg);
 box-shadow:0 2px 6px rgba(0,0,0,.15)}}
.fila{{display:flex;align-items:center;height:78px;position:relative}}
.fila .nm{{flex:1;font-family:BC;font-weight:800;font-size:54px;text-transform:uppercase;position:relative;white-space:nowrap}}
.fila .nm span{{background-image:linear-gradient({ac},{ac});background-repeat:no-repeat;background-position:0 82%;
 background-size:0% 38%;animation:mark .45s var(--d) both;padding:0 6px}}
.fila.l .nm span{{background:none;animation:none}}
.fila.l .nm{{color:rgba(7,21,40,.42);font-weight:700;font-size:46px}}
.est{{width:40px;color:#f2b21c;font-size:40px;text-shadow:0 2px 0 rgba(7,21,40,.35)}}
.fila.l .est{{visibility:hidden}}
.ti{{width:70px;height:70px;margin-left:10px;perspective:400px}}
.ti b{{display:flex;width:100%;height:100%;align-items:center;justify-content:center;background-color:#0b1d36;color:#fff;
 font-family:BC;font-weight:900;font-size:52px;border-radius:6px;position:relative;
 animation:flip .35s var(--d) both;transform-origin:center}}
.ti b{{background-image:linear-gradient(180deg,transparent 49%,rgba(0,0,0,.35) 49% 51%,transparent 51%)}}
.ti b.w{{background-color:{ac};color:{tx}}}
.fila.l .ti b{{background-color:#d5dbe3;color:rgba(7,21,40,.5)}}
.fila.l .ti b.w{{background-color:#0b1d36;color:#fff}}

/* dato */
.dk{{left:70px;top:520px;--r:-3deg;font-size:36px;animation:tape .3s {T_DATO+.15}s both,cut .2s {T_CIERRE}s forwards}}
.dn{{left:0;right:0;top:640px;text-align:center;font-family:BC;font-weight:900;font-size:330px;line-height:.8;
 filter:drop-shadow(0 10px 30px rgba(0,0,0,.7));animation:up .35s {T_DATO+.3}s both,cut .2s {T_CIERRE}s forwards}}
.dn .o{{color:rgba(7,21,40,.5);-webkit-text-stroke:7px {ac}}}
.dt{{left:110px;right:110px;top:1000px;text-align:center;font-size:44px;font-weight:700;line-height:1.25;
 text-shadow:0 4px 18px rgba(0,0,0,.85);animation:up .35s {T_DATO+.6}s both,cut .2s {T_CIERRE}s forwards}}
.dt em{{font-style:normal;color:{ac}}}

/* cierre */
.logo{{left:50%;top:430px;width:320px;height:320px;margin-left:-160px;filter:drop-shadow(0 10px 40px rgba(0,0,0,.7));
 animation:up .4s {T_CIERRE+.2}s both}}
.f1{{top:800px;font-size:120px;text-align:center;animation:up .4s {T_CIERRE+.45}s both}}
.f2{{left:0;right:0;top:1060px;text-align:center;animation:up .4s {T_CIERRE+.75}s both}}
.pill{{display:inline-block;background:#f4f1ea;color:#071528;border-radius:60px;padding:18px 44px;font-weight:800;font-size:44px;
 box-shadow:0 10px 28px rgba(0,0,0,.45)}}
.pill span{{color:{ac2}}}
.f3{{left:0;right:0;top:1190px;text-align:center;font-size:28px;letter-spacing:3px;color:rgba(255,255,255,.85);font-weight:700;
 animation:up .4s {T_CIERRE+1}s both;text-transform:uppercase}}
"""


def cruz(color, escala=1.0, cx=100, cy=100):
    pts = [(0, -34, 9), (0, 34, 9), (-28, 2, 7), (26, -6, 8), (12, 16, 4)]
    out = ""
    for x, y, r in pts:
        x, y, r = cx + x * escala, cy + y * escala, r * escala
        out += (f'<path d="M{x} {y-r} L{x+r*.25} {y} L{x} {y+r} L{x-r*.25} {y}Z '
                f'M{x-r} {y} L{x} {y-r*.25} L{x+r} {y} L{x} {y+r*.25}Z" fill="{color}"/>')
    return out


def sello(ac):
    txt = "TORNEOS DEL SUR · PÁDEL DE ACÁ · "
    return (f'<div class="a sello"><svg viewBox="0 0 200 200">'
            f'<circle cx="100" cy="100" r="96" fill="rgba(7,21,40,.85)" stroke="{ac}" stroke-width="4"/>'
            f'<circle cx="100" cy="100" r="64" fill="none" stroke="{ac}" stroke-width="2" stroke-dasharray="3 5"/>'
            f'<g class="giro"><defs><path id="ci" d="M100,100 m-78,0 a78,78 0 1,1 156,0 a78,78 0 1,1 -156,0"/></defs>'
            f'<text font-family="BC" font-weight="800" font-size="21" letter-spacing="3.2" fill="#fff">'
            f'<textPath href="#ci">{txt}</textPath></text></g>'
            f'{cruz(ac, 1.15)}<circle cx="100" cy="100" r="0"/></svg></div>')


def planilla(i, p, t0):
    top = 600 + i * 300
    r = (-1.6, 1.2, -0.8, 1.4)[i % 4]
    d0 = t0 + .25
    fil = ""
    for k, (pareja, sets, gana) in enumerate([(p["ganan"], p["sets"], True), (p["pierden"], p["sets"], False)]):
        tiles = ""
        for j, (a, b) in enumerate(sets):
            v = a if gana else b
            w = (a > b) if gana else (b > a)
            tiles += f'<div class=ti><b class="{"w" if w else ""}" style="--d:{d0 + .12 * j + .06 * k:.2f}s">{v}</b></div>'
        fil += (f'<div class="fila {"" if gana else "l"}"><div class=est>★</div>'
                f'<div class=nm><span style="--d:{d0 + .5:.2f}s">{pareja}</span></div>{tiles}</div>')
    return (f'<div class="a pl" style="top:{top}px;--r:{r}deg;--r0:{r*4}deg;'
            f'animation:slap .45s {t0}s both,cut .2s {T_DATO}s forwards">'
            f'<div class=tab>{p["cat"]}</div><div class=pin></div>{fil}</div>')


def body(s):
    ac = PAL[s["rama"]][0]
    cards = "".join(planilla(i, p, T_CARDS + .2 + .35 * i) for i, p in enumerate(s["partidos"][:3]))
    bars = "".join(f'<div class="a bar {c}" style="animation-delay:{t}s"></div>'
                   for t in (T_CARDS - .2, T_DATO - .2, T_CIERRE - .2) for c in ("b1",)) + \
           "".join(f'<div class="a bar b2" style="animation-delay:{t + .08}s"></div>' for t in (T_CARDS - .2, T_DATO - .2, T_CIERRE - .2))
    d = s["dato"]
    return (
        '<div class="a v1"></div><div class="a v2"></div><div class="a v3"></div>'
        + sello(ac)
        + f'<div class="a cinta c-top">{s["torneo"]}</div>'
        + f'<div class="a cinta c-sub">{s["sub"]}</div>'
        + f'<div class="a tit h1">{s["titulo"][0]}</div>'
        + f'<div class="a tit h2"><span class=o>{s["titulo"][1]}</span></div>'
        + f'<div class="a tit cab">{s["cabecera"][0]} <span class=o>{s["cabecera"][1]}</span></div>'
        + cards
        + f'<div class="a cinta dk">{d["etiqueta"]}</div>'
        + f'<div class="a dn"><span class=o>{d["numero"]}</span></div>'
        + f'<div class="a dt">{d["texto"]}</div>'
        + f'<img class="a logo" src="data:image/png;base64,{LOGO}">'
        + f'<div class="a tit f1">{s["cierre"][0]}<br><span class=o>{s["cierre"][1]}</span></div>'
        + '<div class="a f2"><div class=pill>Seguí a <span>@surpadelstore</span></div></div>'
        + f'<div class="a f3">Resultados @overgripapp · Torneo @{s["organiza"]}</div>'
        + bars
    )


def cuadros(s, carpeta):
    n = int(FPS * DUR)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{css(s['rama'])}</style></head><body>{body(s)}</body></html>")
        pg.wait_for_timeout(500)
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        for i in range(n):
            pg.evaluate(f"document.getAnimations().forEach(a=>a.currentTime={i * 1000 / FPS})")
            pg.screenshot(path=f"{carpeta}/{i:04d}.png", omit_background=True)
        b.close()


def montar(s, carpeta, salida):
    """Ambiente: el sonido de la toma, en loop y con fundido.
    Fondo: toma de club (apertura) + 2 fondos fijos con zoom lento, cortes secos, grano.
    s["fondos"] = [toma.mp4, fondo_planillas.png, fondo_dato_cierre.png] (rutas relativas a la raíz del repo)."""
    toma, f1, f2 = [str(RAIZ / x) for x in s["fondos"]]
    d1, d2 = T_DATO - T_CARDS + .0, DUR - T_DATO

    def kb(i, dur, z0, z1):
        n = int(dur * FPS)
        return (f"[{i}:v]scale=2160:-1,zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={n}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p[k{i}];")
    filtro = (
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},trim=duration={T_CARDS},"
        f"setpts=PTS-STARTPTS,fps={FPS},setsar=1,format=yuv420p[t0];"
        + kb(1, d1, 1.0, 1.08) + kb(2, d2, 1.1, 1.0)
        + "[t0][k1][k2]concat=n=3:v=1:a=0,"
        "eq=saturation=1.08:contrast=1.04,noise=alls=9:allf=t,vignette=PI/5,unsharp=5:5:0.35[bg];"
        "[bg][3:v]overlay=0:0:format=auto,format=yuv420p[out]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", toma, "-i", f1, "-i", f2,
                    "-framerate", str(FPS), "-i", f"{carpeta}/%04d.png",
                    "-stream_loop", "2", "-i", toma,
                    "-filter_complex", filtro + f";[4:a]atrim=duration={DUR},afade=t=in:d=0.4,afade=t=out:st={DUR-2}:d=2,volume=0.8[aud]",
                    "-map", "[out]", "-map", "[aud]", "-t", str(DUR),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-profile:v", "high", "-r", str(FPS), "-maxrate", "16M", "-bufsize", "32M",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(salida)], check=True)


if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    with tempfile.TemporaryDirectory() as tmp:
        cuadros(spec, tmp)
        montar(spec, tmp, pathlib.Path(sys.argv[2]).resolve())
    print(sys.argv[2])
