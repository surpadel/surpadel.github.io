"""Reel previa del Mexico Major (vie 20/11): "¿Repite Augsburger?".

Tomas del banco (focos, cámara de TV, estadio) + placas con código + subtítulos +
locución de ElevenLabs (voz Agustín energético, eleven_v4). Si la voz no está en el
repo, la baja de VOZ_URL (en Actions sí hay red). Los tiempos de placas y
subtítulos salen solos de los silencios de la locución.
Uso: FONTS_DIR=... LOGO_PNG=... python3 reel_previa.py [salida.mp4]
"""
import base64, os, pathlib, re, subprocess, sys, tempfile, urllib.request
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
F = pathlib.Path(os.environ["FONTS_DIR"])
LOGO = pathlib.Path(os.environ.get("LOGO_PNG", RAIZ / "marca/logo-sur-padel-transparente.png"))
BANCO = RAIZ / "instagram/banco-tomas"
TOMAS = [BANCO / "toma05-focos.mp4", BANCO / "toma09-camara-tv.mp4", RAIZ / "instagram/2026-11-mundial/reel/toma2-estadio-hq.mp4"]
VOZ = AQUI / "previa-voz-agustin.mp3"
VOZ_URL = os.environ.get("VOZ_URL", "https://elevenlabsusercontent.com/database/workspace/616874bc8ff04f49a33e0fd2b53295f7/content_generation/nJEuqHL69uFi76JZZRbt/1axKsvaatiK2oqcexDbV/content.mp3?Expires=1795143600&KeyName=assets-cdn-key-1&Signature=4jD8ofzX9dwCeIvVk7shKb5S44M=")
VOZ_INICIO = 0.4
SALIDA = AQUI / "reel-previa-mexico.mp4"

UNIDADES = ["Leo Augsburger viene de ganar en Dubái.", "¿Repite en Acapulco?",
            "Enfrente están Tapia y Coello:", "ganaron los tres Majors del año y van por el cuarto.",
            "Y ojo: el año pasado,", "Augsburger y Lebrón jugaron la final en México.",
            "Del 23 al 29,", "seguilo con Sur Padel."]


def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def font(fam, path, w, st):
    return f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,{b64(F/path)});font-weight:{w};font-style:{st}}}"


CSS = "".join([
    font("BC", "barlow-condensed/files/barlow-condensed-latin-800-italic.woff2", 800, "italic"),
    font("BC", "barlow-condensed/files/barlow-condensed-latin-700-italic.woff2", 700, "italic"),
    font("B", "barlow/files/barlow-latin-700-normal.woff2", 700, "normal"),
]) + """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;background:transparent;overflow:hidden;color:#fff;font-family:B}
.c{position:absolute;left:0;right:0;text-align:center}
.metal{font-family:BC;font-weight:800;font-style:italic;text-transform:uppercase;line-height:.9;
 background:linear-gradient(180deg,#fff 0%,#dfe9f5 55%,#9fb4cc 100%);-webkit-background-clip:text;color:transparent;
 filter:drop-shadow(0 10px 30px rgba(0,0,0,.75))}
.gold{background:linear-gradient(180deg,#ffe28a,#f2b21c 55%,#a8730b);-webkit-background-clip:text;color:transparent}
.kick{font-family:BC;font-weight:700;font-style:italic;font-size:48px;letter-spacing:6px;text-transform:uppercase;color:#74b4e8;
 text-shadow:0 0 14px #000,0 0 28px #000,0 4px 18px rgba(0,0,0,.9)}
.strip{position:absolute;top:150px;left:50%;transform:translateX(-50%);display:flex;font-family:BC;font-style:italic;font-weight:800;
 text-transform:uppercase;font-size:40px;box-shadow:0 8px 30px rgba(0,0,0,.6);white-space:nowrap}
.strip .a{background:#f2b21c;color:#071528;padding:10px 26px}.strip .b{background:#0b1d36ee;padding:10px 26px;letter-spacing:3px;font-size:34px;display:flex;align-items:center}
.dot{display:inline-block;width:16px;height:16px;border-radius:50%;background:#e53935;margin-right:12px}
.card{position:absolute;left:80px;right:80px;border-radius:26px;padding:36px 40px;background:rgba(7,21,40,.78);
 border:3px solid rgba(116,180,232,.5);box-shadow:0 20px 60px rgba(0,0,0,.6)}
.card .k{font-family:BC;font-weight:700;font-style:italic;font-size:46px;letter-spacing:5px;text-transform:uppercase;color:#74b4e8}
.card .v{font-family:BC;font-weight:800;font-style:italic;font-size:120px;line-height:.95;text-transform:uppercase;margin-top:10px}
.card .n{font-size:44px;font-weight:700;margin-top:18px;color:#dfe9f5}
.sub{position:absolute;left:90px;right:90px;bottom:300px;text-align:center}
.sub span{display:inline;font-size:50px;font-weight:700;line-height:1.5;padding:6px 18px;background:rgba(7,21,40,.86);
 box-decoration-break:clone;-webkit-box-decoration-break:clone;border-radius:10px}
.logo{width:420px;filter:drop-shadow(0 16px 40px rgba(0,0,0,.7))}
.handle{display:inline-block;margin-top:34px;font-family:BC;font-weight:800;font-style:italic;font-size:62px;background:#0b1d36ee;
 border:3px solid #f2b21c;border-radius:60px;padding:12px 44px}
"""

STRIP = '<div class=strip><div class=a>Circuito pro</div><div class=b><span class=dot></span>Acapulco · 23 al 29/11</div></div>'
HTML = [
    STRIP + '<div class="c kick" style="top:600px">Campeón en Dubái</div>'
            '<div class="c metal" style="top:680px;font-size:200px">¿Repite<br><span class=gold>Augsburger?</span></div>',
    STRIP + '<div class=card style="top:600px"><div class=k>Enfrente: Tapia y Coello</div>'
            '<div class=v><span class=gold>3 de 3</span><br>Majors en 2026</div>'
            '<div class=n>Van por el cuarto en México</div></div>',
    STRIP + '<div class=card style="top:600px"><div class=k>Acapulco 2025</div>'
            '<div class=v>Augsburger y Lebrón,<br><span class=gold>finalistas</span></div></div>',
    STRIP + '<div class="c kick" style="top:640px">Mexico Major</div>'
            '<div class="c metal" style="top:720px;font-size:230px">Del 23<br><span class=gold>al 29/11</span></div>',
    '<div class=c style="top:560px"><img class=logo src="data:image/png;base64,LOGO"><br>'
    '<span class=handle>@surpadelstore</span></div>'
    '<div class="c kick" style="top:1240px">Seguinos: resultados al día</div>',
]


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout.strip())


def tiempos(voz):
    """Inicio y fin de cada unidad: reparte por largo de texto y ajusta al silencio más cercano."""
    d = dur(voz)
    log = subprocess.run(["ffmpeg", "-i", str(voz), "-af", "silencedetect=n=-35dB:d=0.18", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    sil = list(zip(ini, fin + [d] * (len(ini) - len(fin))))
    s0 = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    e = sil[-1][0] if sil and sil[-1][1] >= d - 0.05 else d
    medios = [(a + b) / 2 for a, b in sil if a > s0 + 0.1 and b < e - 0.1]
    largos = [len(u) for u in UNIDADES]
    tot, acc, cortes = sum(largos), 0, []
    for l in largos[:-1]:
        acc += l
        t = s0 + (e - s0) * acc / tot
        cerca = [m for m in medios if abs(m - t) < 1.0 and (not cortes or m > cortes[-1] + 0.3)]
        cortes.append(min(cerca, key=lambda m: abs(m - t)) if cerca else t)
    bordes = [s0] + cortes + [e]
    print("silencios", sil, "\nbordes", bordes, "\nduracion voz", d)
    return [(bordes[i], bordes[i + 1]) for i in range(len(UNIDADES))], d


def render(tmp, U, DUR):
    logo = b64(LOGO)
    v = VOZ_INICIO
    placas = [(0.3, U[1][1] + v), (U[2][0] + v - 0.1, U[3][1] + v), (U[4][0] + v - 0.1, U[5][1] + v),
              (U[6][0] + v - 0.1, U[7][0] + v + 0.2), (U[7][0] + v + 0.3, DUR)]
    capas = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for i, ((a, z), html) in enumerate(zip(placas, HTML)):
            pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body>{html.replace('LOGO', logo)}</body></html>")
            pg.wait_for_timeout(200)
            f = tmp / f"placa{i}.png"; pg.screenshot(path=str(f), omit_background=True); capas.append((a, z, f, 0.25))
        for i, ((a, z), t) in enumerate(zip(U, UNIDADES)):
            pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body><div class=sub><span>{t}</span></div></body></html>")
            pg.wait_for_timeout(100)
            f = tmp / f"sub{i}.png"; pg.screenshot(path=str(f), omit_background=True)
            capas.append((a + v, z + v + 0.1, f, 0.08))
        if os.environ.get("MUESTRA"):
            for i, (a, z, f, _) in enumerate(capas[:5]):
                (AQUI / f"muestra-placa{i}.png").write_bytes(f.read_bytes())
        b.close()
    return capas


def main(salida):
    if not VOZ.exists():
        req = urllib.request.Request(VOZ_URL, headers={"User-Agent": "Mozilla/5.0"})
        VOZ.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    U, dv = tiempos(VOZ)
    DUR = round(dv + VOZ_INICIO + 1.2, 2)
    tmp = pathlib.Path(tempfile.mkdtemp())
    capas = render(tmp, U, DUR)
    c1, c2 = round(DUR / 3, 2), round(2 * DUR / 3, 2)
    seg = [(0, c1), (c1, c2), (c2, DUR)]
    ins, fil = [], []
    for t in TOMAS:
        ins += ["-stream_loop", "-1", "-i", str(t)]
    for i, (a, z) in enumerate(seg):
        d = z - a + (0.4 if i < 2 else 0)
        fil.append(f"[{i}:v]trim=0:{d:.2f},setpts=PTS-STARTPTS,fps=24,scale=1080:1920,eq=brightness=-0.08:saturation=1.1[v{i}]")
        fil.append(f"[{i}:a]atrim=0:{d:.2f},asetpts=PTS-STARTPTS[a{i}]")
    fil.append(f"[v0][v1]xfade=transition=fade:duration=0.4:offset={c1}[x1]")
    fil.append(f"[x1][v2]xfade=transition=fade:duration=0.4:offset={c2}[bg]")
    fil.append("[a0][a1]acrossfade=d=0.4[ax1];[ax1][a2]acrossfade=d=0.4,volume=-18dB[amb]")
    n = len(TOMAS)
    ins += ["-i", str(VOZ)]
    fil.append(f"[{n}:a]adelay={int(VOZ_INICIO*1000)}|{int(VOZ_INICIO*1000)},volume=1.6[voz]")
    fil.append(f"[amb][voz]amix=inputs=2:duration=longest:dropout_transition=0,atrim=0:{DUR},afade=t=out:st={DUR-0.8}:d=0.8[aud]")
    prev = "bg"
    for j, (a, z, f, fd) in enumerate(capas):
        k = n + 1 + j
        ins += ["-loop", "1", "-t", f"{DUR}", "-i", str(f)]
        fil.append(f"[{k}:v]format=rgba,fade=t=in:st={a:.2f}:d={fd}:alpha=1,fade=t=out:st={max(a, z-fd):.2f}:d={fd}:alpha=1[c{j}]")
        fil.append(f"[{prev}][c{j}]overlay=0:0:enable='between(t,{a:.2f},{z:.2f})'[o{j}]")
        prev = f"o{j}"
    fil.append(f"[{prev}]unsharp=5:5:0.4,format=yuv420p[vout]")
    cmd = ["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fil), "-map", "[vout]", "-map", "[aud]",
           "-t", f"{DUR}", "-r", "24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(salida)]
    subprocess.run(cmd, check=True)
    print(salida, DUR)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else SALIDA)
