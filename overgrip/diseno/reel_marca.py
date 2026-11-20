"""Reel de marca de Sur Padel, ritmo pausado (pedido de Nico, 20/11/2026).

Los reels anteriores iban muy rápido y casi no se llegaba a leer. Acá cada pantalla tiene
una sola idea, pocas palabras y letra grande, y queda quieta al menos 4 s. La voz dice lo
mismo que el texto. Cada pantalla tiene su toma del banco, unidas con fundidos suaves.

Uso: FONTS_DIR=<node_modules/@fontsource> python3 reel_marca.py spec.json salida.mp4

spec.json:
  pantallas: [{toma, dur, l1, l2}] (l1/l2 admiten <g>palabra en dorado</g>); la última es el cierre
  cierre: {l1, l2, pill}
  voz (opcional): mp3 relativo a la raíz del repo; voz_frases: [[inicio_en_el_mp3, fin], ...]
    una frase por pantalla: cada una arranca 0,5 s después de que entra su pantalla.
"""
import base64, json, os, pathlib, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
F = pathlib.Path(os.environ["FONTS_DIR"])
FPS, W, H, XF = 24, 1080, 1920, 0.6  # XF: duración del fundido entre tomas


def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def ff(nombre, archivo, peso, estilo="normal"):
    return (f"@font-face{{font-family:{nombre};font-weight:{peso};font-style:{estilo};"
            f"src:url(data:font/woff2;base64,{b64(F / archivo)})}}")


FONTS = "".join([
    ff("BC", "barlow-condensed/files/barlow-condensed-latin-800-italic.woff2", 800, "italic"),
    ff("BC", "barlow-condensed/files/barlow-condensed-latin-900-italic.woff2", 900, "italic"),
    ff("B", "barlow/files/barlow-latin-700-normal.woff2", 700),
    ff("B", "barlow/files/barlow-latin-800-normal.woff2", 800),
])
LOGO = b64(RAIZ / "marca/logo-sur-padel-transparente.png")


def inicios(s):
    """Momento en que entra cada pantalla (las tomas se pisan XF segundos)."""
    t, out = 0.0, []
    for p in s["pantallas"]:
        out.append(t)
        t += p["dur"] - XF
    return out, t + XF


def css(s):
    t0, dur = inicios(s)
    reglas = ""
    for i, p in enumerate(s["pantallas"]):
        a, b = t0[i] + 0.35, t0[i] + p["dur"] - XF - 0.1
        ultima = i == len(s["pantallas"]) - 1
        salida = "" if ultima else f",out .45s {b:.2f}s forwards"
        reglas += f".p{i}{{animation:in .7s {a:.2f}s both{salida}}}\n"
        reglas += f".p{i} .l2{{animation:in .7s {a+.35:.2f}s both}}\n"
    return FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;background:transparent;overflow:hidden;font-family:B;color:#fff}
.a{position:absolute;animation-fill-mode:both}
@keyframes in{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
@keyframes out{to{opacity:0}}
.vel{inset:0;background:linear-gradient(180deg,rgba(7,21,40,.55) 0%,rgba(7,21,40,.15) 30%,rgba(7,21,40,.35) 55%,rgba(7,21,40,.8) 100%)}
.franja{left:0;right:0;top:0;height:10px;background:linear-gradient(90deg,#74b4e8 0 33%,#fff 33% 66%,#74b4e8 66%)}
.esc{left:50%;top:150px;width:150px;margin-left:-75px;filter:drop-shadow(0 6px 22px rgba(0,0,0,.6))}
.pan{left:70px;right:70px;top:760px;text-align:center}
.l1,.l2{font-family:BC;font-weight:900;font-style:italic;text-transform:uppercase;line-height:.95;
 font-size:150px;text-shadow:0 8px 30px rgba(0,0,0,.75)}
.l2{display:block}
g,.g{color:#f2b21c}
.pie{left:0;right:0;bottom:150px;text-align:center;font-weight:700;font-size:34px;letter-spacing:4px;
 color:rgba(255,255,255,.8);text-transform:uppercase}
.pie b{color:#74b4e8}
.cruz{right:80px;bottom:260px;width:110px;opacity:.55}
.cie{left:70px;right:70px;top:430px;text-align:center}
.cie img{width:400px;filter:drop-shadow(0 10px 40px rgba(0,0,0,.7))}
.cie .l1{font-size:120px;margin-top:40px}
.pill{display:inline-block;margin-top:56px;background:#f2b21c;color:#071528;border-radius:70px;padding:22px 54px;
 font-weight:800;font-size:56px;box-shadow:0 10px 28px rgba(0,0,0,.45)}
""" + reglas


def cruz():
    pts = [(0, -34, 9), (0, 34, 9), (-28, 2, 7), (26, -6, 8), (12, 16, 4)]
    out = ""
    for x, y, r in pts:
        x, y = 50 + x, 50 + y
        out += (f'<path d="M{x} {y-r} L{x+r*.25} {y} L{x} {y+r} L{x-r*.25} {y}Z '
                f'M{x-r} {y} L{x} {y-r*.25} L{x+r} {y} L{x} {y+r*.25}Z" fill="#74b4e8"/>')
    return f'<svg class="a cruz" viewBox="0 0 100 100">{out}</svg>'


def body(s):
    n = len(s["pantallas"])
    html = '<div class="a vel"></div><div class="a franja"></div>'
    for i, p in enumerate(s["pantallas"][:-1]):
        html += (f'<div class="a pan p{i}"><span class=l1>{p["l1"]}</span>'
                 f'<span class="l2 a" style="position:static">{p["l2"]}</span></div>')
    c = s["cierre"]
    html += (f'<div class="a cie p{n-1}"><img src="data:image/png;base64,{LOGO}">'
             f'<div class=l1>{c["l1"]}<br><span class=g>{c["l2"]}</span></div>'
             f'<div class="pill l2" style="display:inline-block">{c["pill"]}</div></div>')
    # escudo chico y pie fijos en las pantallas de texto (se van al cierre)
    fin_txt = inicios(s)[0][-1]
    html += (f'<img class="a esc" style="animation:in .7s .2s both,out .4s {fin_txt-.3:.2f}s forwards" '
             f'src="data:image/png;base64,{LOGO}">')
    html += (f'<div class="a pie" style="animation:in .7s .5s both,out .4s {fin_txt-.3:.2f}s forwards">'
             f'Pádel de acá · <b>@surpadelstore</b></div>')
    html += cruz()
    return html


def cuadros(s, carpeta):
    _, dur = inicios(s)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{css(s)}</style></head><body>{body(s)}</body></html>")
        pg.wait_for_timeout(500)
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        for i in range(int(FPS * dur)):
            pg.evaluate(f"document.getAnimations().forEach(a=>a.currentTime={i * 1000 / FPS})")
            pg.screenshot(path=f"{carpeta}/{i:04d}.png", omit_background=True)
        b.close()


def montar(s, carpeta, salida):
    t0, dur = inicios(s)
    ps = s["pantallas"]
    ins, filtro = [], ""
    for i, p in enumerate(ps):
        ins += ["-i", str(RAIZ / p["toma"])]
        # toma lenta (70 %) para que no se sienta acelerada; zoom suave
        filtro += (f"[{i}:v]setpts=PTS/0.7,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                   f"trim=duration={p['dur']},setpts=PTS-STARTPTS,fps={FPS},setsar=1,format=yuv420p[v{i}];")
    prev = "v0"
    for i in range(1, len(ps)):
        filtro += f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={t0[i]:.3f}[x{i}];"
        prev = f"x{i}"
    k = len(ps)
    filtro += (f"[{prev}]eq=saturation=1.06:contrast=1.03,vignette=PI/5[bg];"
               f"[bg][{k}:v]overlay=0:0:format=auto,format=yuv420p[out];")
    ins += ["-framerate", str(FPS), "-i", f"{carpeta}/%04d.png"]
    # ambiente de las tomas, bajo
    ins += ["-stream_loop", "4", "-i", str(RAIZ / ps[0]["toma"])]
    filtro += f"[{k+1}:a]atrim=duration={dur},volume=0.25"
    if s.get("voz"):
        filtro += "[amb]"
        ins += ["-i", str(RAIZ / s["voz"])]
        partes = ""
        for j, (a, b) in enumerate(s["voz_frases"]):
            d = int((t0[j] + 0.5) * 1000)
            partes += f";[{k+2}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,adelay={d}|{d}[f{j}]"
        n = len(s["voz_frases"])
        filtro += partes + ";" + "".join(f"[f{j}]" for j in range(n)) + \
            f"amix=inputs={n}:normalize=0[vz];[amb][vz]amix=inputs=2:normalize=0"
    filtro += f",afade=t=in:d=0.5,afade=t=out:st={dur-1.5:.2f}:d=1.5[aud]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", filtro,
                    "-map", "[out]", "-map", "[aud]", "-t", f"{dur:.2f}",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-profile:v", "high", "-r", str(FPS),
                    "-maxrate", "16M", "-bufsize", "32M", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(salida)], check=True)


if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    with tempfile.TemporaryDirectory() as tmp:
        cuadros(spec, tmp)
        montar(spec, tmp, pathlib.Path(sys.argv[2]).resolve())
    print(sys.argv[2], inicios(spec)[1])
