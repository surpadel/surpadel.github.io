"""Reel homenaje a Miguel Lamperti, versión larga con fotos reales (pasadas por Nico el 24/11).

Locución nueva (~40 s, voz Agustín). Cada tramo: foto enmarcada sobre su versión desenfocada
con zoom lento, o placa tipográfica sobre fondo desenfocado. Cierre: foto de estudio que pasa
de blanco y negro a color. Ambiente: público de toma04.
Uso: FONTS_DIR=... LOGO_PNG=... python3 reel_lamperti_v3.py [salida.mp4]
"""
import os, pathlib, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import reel_lamperti as R  # noqa: E402

FOTOS = AQUI / "lamperti"
VOZ = AQUI / "lamperti-voz-v3.mp3"
SALIDA = AQUI / "reel-lamperti-v3.mp4"
AMB = R.BANCO / "toma04-publico.mp4"

R.UNIDADES = [
    "Bahía Blanca. Empezó a los doce años, pegándole a la pared.",
    "En 2006 ya era el número uno de Argentina.",
    "Siete títulos y más de treinta finales en el circuito,",
    "contra las leyendas de cada época.",
    "En 2016 le dio a Argentina el punto del título mundial.",
    "En 2021 eligió de compañero a un pibe de diecinueve años: Arturo Coello.",
    "Jugó tres eras del pádel: Pro Tour, World Padel Tour y Premier.",
    "En Acapulco, su último Premier, quedó afuera en la previa...",
    "y entró como lucky loser para jugar una vez más.",
    "Quiere que lo recuerden como un loco lindo que lo dio todo por el pádel.",
    "Gracias por tanto, Miguelito.",
]

CSS2 = R.CSS + """
.bg{position:absolute;inset:-60px;width:1200px;height:2040px;object-fit:cover;filter:blur(30px) brightness(.42) saturate(.85)}
.bg.full{filter:blur(18px) brightness(.32) saturate(.8)}
.tint{position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,21,40,.55) 0%,rgba(7,21,40,.15) 35%,rgba(7,21,40,.7) 62%,rgba(7,21,40,.95) 100%)}
.fr{position:absolute;left:50%;transform:translateX(-50%);object-fit:cover;border-radius:30px;border:6px solid rgba(116,180,232,.85);
 box-shadow:0 0 0 3px rgba(242,178,28,.55),0 30px 80px rgba(0,0,0,.75)}
.bw{filter:grayscale(1) contrast(1.05)}
.bg.bw{filter:blur(18px) brightness(.32) grayscale(1)}
.quote{position:absolute;left:90px;right:90px;top:560px;text-align:center}
.quote .q{font-family:BC;font-weight:800;font-style:italic;font-size:260px;line-height:.6;color:#f2b21c}
.quote .t{font-family:BC;font-weight:800;font-style:italic;font-size:112px;line-height:.98;text-transform:uppercase;margin-top:30px;
 filter:drop-shadow(0 10px 30px rgba(0,0,0,.75))}
.quote .a{font-family:BC;font-weight:700;font-style:italic;font-size:44px;letter-spacing:5px;text-transform:uppercase;color:#74b4e8;margin-top:40px}
"""


def fondo(foto, marco=None, bw=False):
    src = "data:image/jpeg;base64," + R.b64(FOTOS / foto)
    c = " bw" if bw else ""
    if marco is None:
        return f'<img class="bg full{c}" src="{src}"><div class=tint></div>'
    w, h, top, pos = marco
    return (f'<img class="bg{c}" src="{src}"><div class=tint></div>'
            f'<img class="fr{c}" src="{src}" style="top:{top}px;width:{w}px;height:{h}px;object-position:{pos}">')


P = (700, 860, 250)
S = R.STRIP


def tit(kick, big, size=170, top=1150):
    return (S + f'<div class="c kick" style="top:{top}px">{kick}</div>'
            f'<div class="c metal" style="top:{top+65}px;font-size:{size}px">{big}</div>')


# (unidades, foto, marco o None, texto)
TRAMOS = [
    ([0], "lamperti-foto3.jpg", P + ("50% 35%",), tit("Bahía Blanca · desde los 12", "Gracias, <span class=gold>Miguelito</span>", 150)),
    ([1], "lamperti-foto2.jpg", P + ("50% 20%",), tit("Número 1 de Argentina", "En <span class=gold>2006</span>")),
    ([2, 3], "lamperti-foto4.jpg", P + ("50% 25%",), tit("Más de 30 finales en el circuito", "<span class=gold>7</span> títulos")),
    ([4], "lamperti-foto6.jpg", P + ("50% 30%",), tit("Mundial 2016 · para Argentina", "El punto <span class=gold>del título</span>", 128)),
    ([5], "lamperti-foto5.jpg", None,
     S + '<div class="c kick" style="top:560px">2021 · su compañero</div>'
         '<div class="c metal" style="top:640px;font-size:520px"><span class=gold>19</span></div>'
         '<div class="c metal" style="top:1100px;font-size:96px">años: Arturo Coello</div>'),
    ([6], "lamperti-foto5.jpg", (960, 640, 380, "55% 40%"), tit("Pro Tour · WPT · Premier", "<span class=gold>3</span> eras", 170, 1080)),
    ([7, 8], "lamperti-foto3.jpg", None,
     S + '<div class="c kick" style="top:600px">Acapulco · su último Premier</div>'
         '<div class="c metal" style="top:690px;font-size:230px">Lucky<br><span class=gold>loser</span></div>'
         '<div class="c kick" style="top:1170px;color:#fff">Para jugar una vez más</div>'),
    ([9], "lamperti-foto1.jpg", None,
     '<div class=quote><div class=q>“</div><div class="t metal">Un loco lindo que<br><span class=gold>lo dio todo</span><br>por el pádel</div>'
     '<div class=a>Miguel Lamperti</div></div>'),
    ([10], "lamperti-foto1.jpg", (620, 760, 470, "50% 25%"),
     '<div class="c metal" style="top:150px;font-size:120px">Gracias por<br><span class=gold>tanto, maestro</span></div>'
     '<div class="c kick" style="top:1270px">@lamperti.ml10</div>'
     '<div class=c style="top:1340px"><span class=handle style="font-size:52px;margin-top:0">Seguinos · @surpadelstore</span></div>'),
]
BW = {7}          # tramos en blanco y negro
FADE_BW = 8       # tramo que pasa de blanco y negro a color


def run(*a):
    subprocess.run([str(x) for x in a], check=True)


def main(salida):
    R.VOZ = VOZ
    U, dv = R.tiempos(VOZ)
    v = R.VOZ_INICIO
    DUR = round(dv + v + 1.6, 2)
    lim = [0.0] + [U[t[0][-1]][1] + v + 0.15 for t in TRAMOS[:-1]] + [DUR]
    tmp = pathlib.Path(tempfile.mkdtemp())
    X = 0.4
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})

        def shot(html, f, transp):
            pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS2}</style></head><body>{html}</body></html>")
            pg.wait_for_timeout(250)
            pg.screenshot(path=str(f), omit_background=transp)

        fondos, capas = [], []
        for i, (_, foto, marco, texto) in enumerate(TRAMOS):
            f = tmp / f"fondo{i}.png"; shot(fondo(foto, marco, bw=i in BW), f, False); fondos.append(f)
            t = tmp / f"texto{i}.png"; shot(texto, t, True)
            capas.append((lim[i] + 0.25, lim[i + 1] + (0 if i == len(TRAMOS) - 1 else 0.1), t, 0.3))
        fbw = tmp / "fondo-bw.png"; shot(fondo(TRAMOS[FADE_BW][1], TRAMOS[FADE_BW][2], bw=True), fbw, False)
        for i, ((a, z), t) in enumerate(zip(U, R.UNIDADES)):
            f = tmp / f"sub{i}.png"; shot(f"<div class=sub><span>{t}</span></div>", f, True)
            capas.append((a + v, z + v - 0.02, f, 0.08))
        if os.environ.get("MUESTRA"):
            for i, (f, (_, _, t, _)) in enumerate(zip(fondos, capas)):
                (pathlib.Path(os.environ["MUESTRA"]) / f"m{i}.png").write_bytes(f.read_bytes())
        b.close()
    clips = []
    for i, f in enumerate(fondos):
        d = lim[i + 1] - lim[i] + (X if i < len(fondos) - 1 else 0)
        n = int(d * 24) + 1
        c = tmp / f"clip{i}.mp4"
        z = f"scale=2160:3840,zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=24"
        if i != FADE_BW:
            run("ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", f, "-vf", f"{z},trim=0:{d:.2f},format=yuv420p", "-t", f"{d:.2f}",
                "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", c)
        else:
            fil = f"[0:v]{z}[bw];[1:v]{z}[co];[bw][co]xfade=transition=fade:duration=1.6:offset=0.9,trim=0:{d:.2f},format=yuv420p[o]"
            run("ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", f"{d+2:.2f}", "-i", fbw, "-loop", "1", "-t", f"{d+2:.2f}", "-i", f,
                "-filter_complex", fil, "-map", "[o]", "-t", f"{d:.2f}", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", c)
        clips.append(c)
    ins, fil = [], []
    for c in clips:
        ins += ["-i", str(c)]
    prev = "0:v"
    for i in range(1, len(clips)):
        fil.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={X}:offset={lim[i]:.2f}[x{i}]")
        prev = f"x{i}"
    nc = len(clips)
    ins += ["-stream_loop", "-1", "-i", str(AMB), "-i", str(VOZ)]
    fil.append(f"[{nc}:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,volume=-20dB[amb]")
    fil.append(f"[{nc+1}:a]adelay={int(v*1000)}|{int(v*1000)},volume=1.6[voz]")
    fil.append(f"[amb][voz]amix=inputs=2:duration=longest:dropout_transition=0,atrim=0:{DUR},afade=t=out:st={DUR-0.8}:d=0.8[aud]")
    for j, (a, z, f, fd) in enumerate(capas):
        k = nc + 2 + j
        ins += ["-loop", "1", "-t", f"{DUR}", "-i", str(f)]
        fil.append(f"[{k}:v]format=rgba,fade=t=in:st={a:.2f}:d={fd}:alpha=1,fade=t=out:st={max(a, z-fd):.2f}:d={fd}:alpha=1[c{j}]")
        fil.append(f"[{prev}][c{j}]overlay=0:0:enable='between(t,{a:.2f},{z:.2f})'[o{j}]")
        prev = f"o{j}"
    fil.append(f"[{prev}]format=yuv420p[vout]")
    run("ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fil), "-map", "[vout]", "-map", "[aud]",
        "-t", f"{DUR}", "-r", "24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", salida)
    print(salida, DUR, [round(x, 2) for x in lim])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else SALIDA)
