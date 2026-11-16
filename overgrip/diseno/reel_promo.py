"""Reel promo semanal "Este finde se juega en el sur" (estilo Torneos del Sur).

Invita a seguir @surpadelstore para ver los resultados de los torneos de la
semana. Reusa el estilo de reel_local.py (cinta, sello, planillas de papel,
casilleros de chapa, barridas) y suma locución + subtítulos.

Uso: FONTS_DIR=<node_modules/@fontsource> python3 reel_promo.py spec.json salida.mp4
spec: ver instagram/overgrip-reels/promo-semana-1/spec.json
  torneos: [{nombre, dias: [[letra, num], ...], linea, organiza}]  (hasta 3)
  subs: [[desde, hasta, texto], ...]   (segundos, sobre el reel)
  voz: ruta del mp3 (relativa al repo), voz_desde: segundos
  fondos: [toma.mp4, fondo_planillas, fondo_cierre]
"""
import json, pathlib, subprocess, sys, tempfile
import reel_local as rl
from playwright.sync_api import sync_playwright

T_CARDS, T_DATO, T_CIERRE, DUR = 3.4, 7.4, 9.4, 14.0
rl.T_CARDS, rl.T_DATO, rl.T_CIERRE, rl.DUR = T_CARDS, T_DATO, T_CIERRE, DUR
FPS, W, H = rl.FPS, rl.W, rl.H


def css_extra(ac):
    return f"""
.h1,.h2{{font-size:190px}}
.h1{{top:740px}}.h2{{top:900px}}
.pl{{padding:60px 30px 26px 30px}}
.pl .tab{{font-size:46px}}
.dias{{display:flex;gap:12px;align-items:flex-end;margin-top:4px}}
.dia{{display:flex;flex-direction:column;align-items:center;gap:4px}}
.dia i{{font-style:normal;font-family:BC;font-weight:800;font-size:28px;letter-spacing:2px;color:rgba(7,21,40,.6)}}
.dia .ti{{width:92px;height:92px;margin:0}}
.dia .ti b{{font-size:66px}}
.mes{{font-family:BC;font-weight:800;font-size:40px;color:rgba(7,21,40,.55);margin-left:10px;padding-bottom:16px;text-transform:uppercase}}
.lin{{margin-top:16px;display:flex;justify-content:space-between;align-items:center;font-family:BC;font-weight:800;font-size:40px;text-transform:uppercase}}
.lin .org span{{background-image:linear-gradient({ac},{ac});background-repeat:no-repeat;background-position:0 82%;
 background-size:0% 38%;animation:mark .45s var(--d) both;padding:0 6px;text-transform:none;font-family:B;font-weight:800;font-size:38px}}
.lin .sd{{color:rgba(7,21,40,.6);font-size:34px}}
.dn{{font-size:250px;top:660px}}
.sub{{left:70px;right:70px;top:1500px;text-align:center}}
.sub span{{display:inline-block;background:rgba(7,21,40,.82);border:2px solid {ac};border-radius:14px;padding:12px 26px;
 font-weight:800;font-size:44px;line-height:1.2;box-shadow:0 8px 24px rgba(0,0,0,.4)}}
@keyframes sub{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
"""


def planilla(i, t, t0):
    top = 560 + i * 300
    r = (-1.6, 1.2, -0.8)[i % 3]
    d0 = t0 + .25
    dias = "".join(f'<div class=dia><i>{l}</i><div class=ti><b class="{"w" if j == 0 else ""}" '
                   f'style="--d:{d0 + .1 * j:.2f}s">{n}</b></div></div>' for j, (l, n) in enumerate(t["dias"]))
    return (f'<div class="a pl" style="top:{top}px;--r:{r}deg;--r0:{r*4}deg;'
            f'animation:slap .45s {t0}s both,cut .2s {T_DATO}s forwards">'
            f'<div class=tab>{t["nombre"]}</div><div class=pin></div>'
            f'<div class=dias>{dias}<div class=mes>{t.get("mes", "nov")}</div></div>'
            f'<div class=lin><div class=org><span style="--d:{d0 + .5:.2f}s">@{t["organiza"]}</span></div>'
            f'<div class=sd>{t.get("linea", "")}</div></div></div>')


def body(s):
    ac = rl.PAL["cab"][0]
    cards = "".join(planilla(i, t, T_CARDS + .25 + .4 * i) for i, t in enumerate(s["torneos"][:3]))
    ts = (T_CARDS - .2, T_DATO - .2, T_CIERRE - .2)
    bars = "".join(f'<div class="a bar b1" style="animation-delay:{t}s"></div>'
                   f'<div class="a bar b2" style="animation-delay:{t + .08}s"></div>' for t in ts)
    subs = "".join(f'<div class="a sub" style="animation:sub .2s {a}s both,cut .15s {b}s forwards"><span>{x}</span></div>'
                   for a, b, x in s["subs"])
    d = s["dato"]
    return (
        '<div class="a v1"></div><div class="a v2"></div><div class="a v3"></div>'
        + rl.sello(ac)
        + f'<div class="a cinta c-top">{s["cinta"][0]}</div>'
        + f'<div class="a cinta c-sub">{s["cinta"][1]}</div>'
        + f'<div class="a tit h1">{s["titulo"][0]}</div>'
        + f'<div class="a tit h2"><span class=o>{s["titulo"][1]}</span></div>'
        + f'<div class="a tit cab">{s["cabecera"][0]} <span class=o>{s["cabecera"][1]}</span></div>'
        + cards
        + f'<div class="a cinta dk">{d["etiqueta"]}</div>'
        + f'<div class="a dn"><span class=o>{d["numero"]}</span></div>'
        + f'<div class="a dt">{d["texto"]}</div>'
        + f'<img class="a logo" src="data:image/png;base64,{rl.LOGO}">'
        + f'<div class="a tit f1">{s["cierre"][0]}<br><span class=o>{s["cierre"][1]}</span></div>'
        + '<div class="a f2"><div class=pill>Seguí a <span>@surpadelstore</span></div></div>'
        + '<div class="a f3">Resultados @overgripapp</div>'
        + subs + bars
    )


def cuadros(s, carpeta):
    ac = rl.PAL["cab"][0]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{rl.css('cab')}{css_extra(ac)}</style></head>"
                       f"<body>{body(s)}</body></html>")
        pg.wait_for_timeout(500)
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        for i in range(int(FPS * DUR)):
            pg.evaluate(f"document.getAnimations().forEach(a=>a.currentTime={i * 1000 / FPS})")
            pg.screenshot(path=f"{carpeta}/{i:04d}.png", omit_background=True)
        b.close()


def montar(s, carpeta, salida):
    toma, f1, f2 = [str(rl.RAIZ / x) for x in s["fondos"]]
    voz = str(rl.RAIZ / s["voz"])
    d1, d2 = T_DATO - T_CARDS, DUR - T_DATO

    def kb(i, dur, z0, z1):
        n = int(dur * FPS)
        return (f"[{i}:v]scale=2160:-1,zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={n}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p[k{i}];")
    ms = int(s.get("voz_desde", .4) * 1000)
    filtro = (
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},trim=duration={T_CARDS},"
        f"setpts=PTS-STARTPTS,fps={FPS},setsar=1,format=yuv420p[t0];"
        + kb(1, d1, 1.0, 1.08) + kb(2, d2, 1.1, 1.0)
        + "[t0][k1][k2]concat=n=3:v=1:a=0,"
        "eq=saturation=1.08:contrast=1.04,noise=alls=9:allf=t,vignette=PI/5,unsharp=5:5:0.35[bg];"
        "[bg][3:v]overlay=0:0:format=auto,format=yuv420p[out];"
        f"[4:a]atrim=duration={DUR},afade=t=in:d=0.4,afade=t=out:st={DUR-2}:d=2,volume=0.13[amb];"
        f"[5:a]adelay={ms}|{ms},volume=1.0[vz];"
        f"[amb][vz]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[aud]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", toma, "-i", f1, "-i", f2,
                    "-framerate", str(FPS), "-i", f"{carpeta}/%04d.png",
                    "-stream_loop", "2", "-i", toma, "-i", voz,
                    "-filter_complex", filtro, "-map", "[out]", "-map", "[aud]", "-t", str(DUR),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-profile:v", "high", "-r", str(FPS),
                    "-maxrate", "16M", "-bufsize", "32M",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(salida)], check=True)


if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    with tempfile.TemporaryDirectory() as tmp:
        cuadros(spec, tmp)
        montar(spec, tmp, pathlib.Path(sys.argv[2]).resolve())
    print(sys.argv[2])
