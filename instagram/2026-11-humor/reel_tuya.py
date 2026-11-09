"""Reel de humor "Tipos de compañero" ep. 1: el que grita ¡TUYA! y se queda quieto.

Uso: python3 instagram/2026-11-humor/reel_tuya.py <version>   (version: real | ia)
Lee fuentes.json (voz y clips por versión), baja lo que falte a fuentes/, arma el reel
con ffmpeg + gráficos de Playwright y deja reel-tuya-<version>.mp4 y una tira de cuadros.
"""
import json, os, re, subprocess, sys, pathlib, urllib.request, shutil

AQUI = pathlib.Path(__file__).resolve().parent
R = AQUI.parents[1]
sys.path.insert(0, str(R / "overgrip/diseno"))
os.environ.setdefault("LOGO_PNG", str(R / "marca/logo-sur-padel-transparente.png"))
import gen  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

W, H, FPS = 1080, 1920, 30
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
FRASES = ["¡Atención, atención!", "Viene la pelota por el medio...", "¡TUYAAA!",
          "...y se queda quieto. Una estatua.", "Señoras y señores: el compañero que todos tenemos.", "¡Etiquetalo!"]


def sh(*a, salida=False):
    print("$", " ".join(map(str, a))[:300], flush=True)
    r = subprocess.run(list(map(str, a)), capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-4000:]); raise SystemExit(f"falló: {a[0]}")
    return r.stderr if salida else r.stdout


def dur(p):
    return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p).strip())


def bajar(url, dest):
    dest = pathlib.Path(dest)
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    print("bajando", url[:120], flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
        if dest.stat().st_size > 1000:
            return dest
    except Exception as e:
        print("descarga directa falló:", e)
    return None


def bajar_pexels(pagina, dest):
    """Busca el mp4 de la página de Pexels con el navegador y lo baja."""
    m = re.search(r"-(\d+)/?$", pagina)
    if m and bajar(f"https://www.pexels.com/download/video/{m.group(1)}/", dest):
        return dest
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(user_agent=UA)
        urls = []
        pg.on("response", lambda r: urls.append(r.url) if ".mp4" in r.url else None)
        pg.goto(pagina, wait_until="networkidle", timeout=90000)
        srcs = pg.eval_on_selector_all("video, video source", "els => els.map(e => e.src || e.currentSrc).filter(Boolean)")
        b.close()
    cands = [u for u in srcs + urls if ".mp4" in u]
    cands.sort(key=lambda u: ("2160" in u or "uhd" in u, "1080" in u), reverse=True)
    for u in cands:
        if bajar(u, dest):
            return dest
    raise SystemExit("no pude bajar " + pagina)


def normalizar(src, dest, maxdur=None):
    """Clip vertical 1080x1920 a 30 fps, sin audio (se guarda liviano en fuentes/)."""
    if pathlib.Path(dest).exists():
        return dest
    a = ["ffmpeg", "-y", "-i", src]
    if maxdur: a += ["-t", maxdur]
    sh(*a, "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
       "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", dest)
    return dest


def frases_tiempos(voz, total):
    """Tiempos de las frases a partir de los silencios de la locución."""
    err = sh("ffmpeg", "-i", voz, "-af", "silencedetect=noise=-32dB:d=0.22", "-f", "null", "-", salida=True)
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    segs, t = [], 0.0
    for s, e in zip(ini, fin):
        if s - t > 0.15: segs.append([t, s])
        t = e
    if total - t > 0.15: segs.append([t, total])
    print("segmentos de voz:", [(round(a, 2), round(b, 2)) for a, b in segs])
    n = len(FRASES)
    if len(segs) >= n:
        while len(segs) > n:  # unir el hueco más corto
            i = min(range(len(segs) - 1), key=lambda k: segs[k + 1][0] - segs[k][1])
            segs[i] = [segs[i][0], segs[i + 1][1]]; del segs[i + 1]
        return segs
    # respaldo: repartir por cantidad de letras
    a0, a1 = (segs[0][0], segs[-1][1]) if segs else (0, total)
    pesos = [len(f) for f in FRASES]; tot = sum(pesos); out, t = [], a0
    for p in pesos:
        d = (a1 - a0) * p / tot; out.append([t, t + d]); t += d
    return out


T = gen.THEMES["azul"]
CSS = gen.FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:B;color:#fff;background:transparent;position:relative}}
.metal{{font-family:BC;font-weight:800;font-style:italic;text-transform:uppercase;line-height:.9;text-align:center;color:#fff;
 text-shadow:0 6px 24px rgba(0,0,0,.85),0 2px 0 rgba(0,0,0,.5)}}
.gold{{color:{T['hot']}}}
.kick{{display:inline-block;background:{T['hot']};color:#071528;font-family:BC;font-style:italic;font-weight:800;font-size:40px;padding:8px 26px;letter-spacing:2px;clip-path:polygon(3% 0,100% 0,97% 100%,0 100%)}}
.top{{position:absolute;top:210px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:18px}}
.sub{{position:absolute;left:70px;right:70px;bottom:430px;text-align:center;font-weight:700;font-size:50px;line-height:1.15;
 text-shadow:0 3px 14px rgba(0,0,0,.95),0 0 3px #000}}
.sub span{{background:rgba(7,21,40,.72);padding:6px 16px;border-radius:10px;box-decoration-break:clone;-webkit-box-decoration-break:clone}}
.stamp{{position:absolute;left:50%;top:44%;transform:translate(-50%,-50%) rotate(-8deg);border:12px solid {T['hot']};color:{T['hot']};
 font-family:BC;font-style:italic;font-weight:800;font-size:190px;padding:0 40px;line-height:1.05;background:rgba(7,21,40,.55);
 text-shadow:0 6px 30px rgba(0,0,0,.7);box-shadow:0 10px 50px rgba(0,0,0,.6)}}
.card{{position:absolute;left:110px;right:110px;top:330px;background:linear-gradient(180deg,#0b1d36,#071528);border:4px solid {T['hot']};border-radius:26px;
 padding:46px 56px 50px;box-shadow:0 30px 80px rgba(0,0,0,.7)}}
.card .hd{{display:flex;justify-content:space-between;align-items:center;font-family:BC;font-style:italic;font-weight:800;font-size:44px;color:{T['acc']};letter-spacing:2px}}
.card .ovr{{font-family:BC;font-style:italic;font-weight:800;font-size:130px;color:{T['hot']};line-height:.9}}
.card .nm{{font-family:BC;font-style:italic;font-weight:800;font-size:96px;text-transform:uppercase;margin:6px 0 28px;line-height:.95}}
.st{{margin-top:22px}} .st .l{{display:flex;justify-content:space-between;font-size:38px;font-weight:700;margin-bottom:8px}}
.st .b{{height:22px;border-radius:11px;background:rgba(255,255,255,.14);overflow:hidden}} .st .b i{{display:block;height:100%;border-radius:11px}}
.cierre{{position:absolute;left:80px;right:80px;top:470px;display:flex;flex-direction:column;align-items:center;gap:36px;text-align:center}}
.logo{{width:170px;height:170px;filter:drop-shadow(0 8px 30px rgba(0,0,0,.6))}}
.brand{{font-size:30px;letter-spacing:4px;color:rgba(255,255,255,.8)}}
.arrow{{font-family:BC;font-weight:800;font-size:150px;color:{T['hot']};line-height:.6}}
"""
LOGO = f'<img class=logo src="data:image/png;base64,{gen.LOGO}">'


def stat(nombre, v, color):
    return (f'<div class=st><div class=l><span>{nombre}</span><span style="color:{color}">{v}</span></div>'
            f'<div class=b><i style="width:{max(v,2)}%;background:{color}"></i></div></div>')


def capas():
    c = {
        "hook": f'<div class=top><div class=kick>TIPOS DE COMPAÑERO · EP. 1</div>'
                f'<div class=metal style="font-size:118px">El que grita<br><span class=gold>¡tuya!</span></div></div>',
        "stamp": '<div class=stamp>¡TUYA!</div>',
        "quieto": f'<div class=top style="top:300px"><div class=metal style="font-size:130px">...y se queda<br><span class=gold>quieto</span></div>'
                  f'<div class=kick style="margin-top:20px">MODO ESTATUA ACTIVADO</div></div>',
        "ficha": ('<div class=card><div class=hd><span>FICHA DEL JUGADOR</span><span>SUR PADEL</span></div>'
                  '<div class=ovr>12</div><div class=nm>"El estatua"</div>'
                  + stat("Volumen del grito", 99, T['hot']) + stat("Reacción", 3, "#ff5a5a")
                  + stat("Cubrir el medio", 0, "#ff5a5a") + stat("Excusas después", 97, T['hot'])
                  + stat("Mirar al compañero", 100, T['acc']) + '</div>'),
        "cierre": f'<div class=cierre>{LOGO}<div class=metal style="font-size:112px">Etiquetá a tu<br><span class=gold>compañero estatua</span></div>'
                  f'<div class=arrow>↓</div><div class=brand>@SURPADELSTORE</div></div>',
    }
    for i, f in enumerate(FRASES):
        c[f"sub{i}"] = f'<div class=sub><span>{f}</span></div>'
    return c


def render_capas(out):
    out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        for k, html in capas().items():
            pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body>{html}</body></html>")
            pg.wait_for_timeout(150); pg.screenshot(path=str(out / f"{k}.png"), omit_background=True)
        b.close()


def segmento(dest, entrada, d, vf, loop_img=False, inicio=0.0):
    a = ["ffmpeg", "-y"]
    if loop_img: a += ["-loop", "1", "-framerate", FPS]
    else: a += ["-stream_loop", "-1", "-ss", inicio]
    a += ["-i", entrada, "-t", round(d, 3), "-vf", vf + f",fps={FPS},format=yuv420p",
          "-an", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-r", FPS, dest]
    sh(*a)


def ultimo_cuadro(video, png):
    sh("ffmpeg", "-y", "-sseof", "-0.1", "-i", video, "-frames:v", "1", "-update", "1", png)


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "real"
    cfg = json.load(open(AQUI / "fuentes.json"))
    F = AQUI / "fuentes"; F.mkdir(exist_ok=True)
    tmp = pathlib.Path("/tmp/reel-tuya-" + version); tmp.mkdir(exist_ok=True)

    voz = F / "voz-tuya.mp3"
    if not voz.exists() and not bajar(cfg["voz"], voz):
        raise SystemExit("no pude bajar la voz")
    clips = []
    for i, c in enumerate(cfg["versiones"][version]["clips"]):
        norm = F / f"{version}-clip{i+1}.mp4"
        if not norm.exists():
            crudo = tmp / f"crudo{i}.mp4"
            if c.get("pexels"): bajar_pexels(c["pexels"], crudo)
            elif not bajar(c["url"], crudo): raise SystemExit("no pude bajar " + c["url"])
            normalizar(crudo, norm, c.get("max"))
        clips.append((norm, c.get("inicio", 0.0)))

    dv = dur(voz)
    fr = frases_tiempos(voz, dv)
    a = fr[2][1] + 0.35                      # fin del ¡TUYA!
    b = max(fr[3][1] + 0.25, a + 1.5)        # fin de "se queda quieto"
    c = max(fr[4][1] + 0.3, b + 2.5)         # fin de "el compañero que todos tenemos"
    total = max(dv + 1.8, c + 2.6)
    print("cortes", round(a, 2), round(b, 2), round(c, 2), round(total, 2))

    capas_dir = tmp / "capas"; render_capas(capas_dir)
    esc = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    s1, s2, s3, s4 = (tmp / f"s{i}.mp4" for i in range(1, 5))
    segmento(s1, clips[0][0], a, esc, inicio=clips[0][1])
    f1 = tmp / "f1.png"; ultimo_cuadro(s1, f1)
    if len(clips) > 1:   # versión IA: toma de reacción
        segmento(s2, clips[1][0], b - a, esc, inicio=clips[1][1])
    else:                # versión real: cuadro congelado con zoom lento y desaturado
        n = int((b - a) * FPS) + 2
        segmento(s2, f1, b - a, f"scale={W*2}:{H*2},zoompan=z='1+0.18*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2.2-(ih/zoom/2.2)':d=1:s={W}x{H}:fps={FPS},eq=saturation=0.25:contrast=1.1", loop_img=True)
    f2 = tmp / "f2.png"; ultimo_cuadro(s2, f2)
    segmento(s3, f2, c - b, f"{esc},boxblur=28:3,eq=brightness=-0.18:saturation=0.6", loop_img=True)
    fondo = R / "marca/fondos/fondo-05-focos.jpg"
    n4 = int((total - c) * FPS) + 2
    segmento(s4, fondo, total - c, f"{esc},scale={W*2}:{H*2},zoompan=z='1+0.08*on/{n4}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},eq=brightness=-0.12", loop_img=True)
    lista = tmp / "lista.txt"; lista.write_text("".join(f"file '{s}'\n" for s in (s1, s2, s3, s4)))
    base = tmp / "base.mp4"; sh("ffmpeg", "-y", "-f", "concat", "-safe", 0, "-i", lista, "-c", "copy", base)

    # capas con tiempos
    capas_t = [("hook", 0.15, a), ("stamp", fr[2][0] - 0.05, a), ("quieto", a + 0.1, b), ("ficha", b + 0.15, c), ("cierre", c + 0.1, total)]
    for i, (s, e) in enumerate(fr):
        if i < 5: capas_t.append((f"sub{i}", s, min(e + 0.25, fr[i + 1][0] if i + 1 < len(fr) else e + 0.25)))
    entradas, filtros, prev = [], [], "[0:v]"
    for k, (nombre, t0, t1) in enumerate(capas_t):
        entradas += ["-loop", "1", "-framerate", FPS, "-t", round(total, 2), "-i", capas_dir / f"{nombre}.png"]
        fade = f"[{k+1}:v]format=rgba,fade=t=in:st={t0:.2f}:d=0.18:alpha=1[c{k}]"
        filtros.append(fade)
        filtros.append(f"{prev}[c{k}]overlay=0:0:enable='between(t,{t0:.2f},{t1:.2f})'[v{k}]")
        prev = f"[v{k}]"
    # audio: voz adelante + ambiente del clip (si tiene) bajo
    filtros.append(f"[{len(capas_t)+1}:a]adelay=0|0,volume=1.0,apad=whole_dur={total:.2f}[aout]")
    out = AQUI / f"reel-tuya-{version}.mp4"
    sh("ffmpeg", "-y", "-i", base, *entradas, "-i", voz, "-filter_complex", ";".join(filtros),
       "-map", prev, "-map", "[aout]", "-t", round(total, 2), "-c:v", "libx264", "-crf", "17", "-preset", "slow",
       "-pix_fmt", "yuv420p", "-r", FPS, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out)
    # tira de cuadros para revisar
    tira = AQUI / f"tira-tuya-{version}.jpg"
    ts = [0.8, fr[2][0] + 0.3, (a + b) / 2, (b + c) / 2 + 0.4, total - 0.6]
    fr_png = []
    for i, t in enumerate(ts):
        p = tmp / f"t{i}.png"; sh("ffmpeg", "-y", "-ss", round(t, 2), "-i", out, "-frames:v", 1, "-vf", "scale=360:640", p); fr_png.append(p)
    sh("ffmpeg", "-y", *sum([["-i", p] for p in fr_png], []), "-filter_complex", f"hstack=inputs={len(fr_png)}", "-q:v", 3, tira)
    print("listo", out, round(total, 2), "s")


if __name__ == "__main__":
    main()
