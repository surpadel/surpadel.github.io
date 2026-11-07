"""Reel de hype para la final del Mundial (7/11) con locución de ElevenLabs.

Tomas del banco (túnel, focos, público) + placas con código (Playwright, PNG
transparentes) + subtítulos + locución (hype-voz1.mp3, voz Uriel) con el ambiente
de las tomas a -18 dB. Uso: FONTS_DIR=... python3 reel_hype_final.py salida.mp4
"""
import base64, os, pathlib, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
F = pathlib.Path(os.environ["FONTS_DIR"])
BANCO = RAIZ / "instagram/banco-tomas"
TOMAS = [BANCO / "toma07-tunel.mp4", BANCO / "toma05-focos.mp4", BANCO / "toma04-publico.mp4"]
VOZ, VOZ_INICIO = AQUI / "hype-voz1.mp3", 0.4
DUR = 17.0


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
.kick{font-family:BC;font-weight:700;font-style:italic;font-size:46px;letter-spacing:6px;text-transform:uppercase;color:#74b4e8;
 text-shadow:0 4px 18px rgba(0,0,0,.8)}
.strip{position:absolute;top:150px;left:50%;transform:translateX(-50%);display:flex;font-family:BC;font-style:italic;font-weight:800;
 text-transform:uppercase;font-size:40px;box-shadow:0 8px 30px rgba(0,0,0,.6)}
.strip .a{background:#f2b21c;color:#071528;padding:10px 26px}.strip .b{background:#0b1d36ee;padding:10px 26px;letter-spacing:3px;font-size:34px;display:flex;align-items:center}
.flag{display:inline-block;width:150px;height:100px;border-radius:10px;box-shadow:0 0 0 3px rgba(255,255,255,.35),0 12px 30px rgba(0,0,0,.6);position:relative}
.ar{background:linear-gradient(180deg,#74acdf 33.3%,#fff 33.3% 66.6%,#74acdf 66.6%)}
.ar:after{content:"";position:absolute;left:50%;top:50%;width:22px;height:22px;margin:-11px;border-radius:50%;background:#f6b40e}
.es{background:linear-gradient(180deg,#aa151b 25%,#f1bf00 25% 75%,#aa151b 75%)}
.card{position:absolute;left:80px;right:80px;border-radius:26px;padding:36px 40px;background:rgba(7,21,40,.78);
 border:3px solid rgba(116,180,232,.5);box-shadow:0 20px 60px rgba(0,0,0,.6)}
.card.rosa{border-color:rgba(255,111,168,.7);background:rgba(22,7,26,.8)}
.card .k{font-family:BC;font-weight:700;font-style:italic;font-size:44px;letter-spacing:5px;text-transform:uppercase;color:#74b4e8}
.card.rosa .k{color:#f4a3c4}
.card .v{font-family:BC;font-weight:800;font-style:italic;font-size:118px;line-height:.95;text-transform:uppercase;margin-top:10px}
.card.rosa .v .gold{background:linear-gradient(180deg,#ffd1e3,#ff6fa8 60%,#b8366f);-webkit-background-clip:text;color:transparent}
.sub{position:absolute;left:90px;right:90px;bottom:300px;text-align:center}
.sub span{display:inline;font-size:50px;font-weight:700;line-height:1.5;padding:6px 18px;background:rgba(7,21,40,.86);
 box-decoration-break:clone;-webkit-box-decoration-break:clone;border-radius:10px}
.logo{width:420px;filter:drop-shadow(0 16px 40px rgba(0,0,0,.7))}
.handle{display:inline-block;margin-top:34px;font-family:BC;font-weight:800;font-style:italic;font-size:62px;background:#0b1d36ee;
 border:3px solid #f2b21c;border-radius:60px;padding:12px 44px}
"""

STRIP = '<div class=strip><div class=a>Mundial</div><div class=b>Doha · La final</div></div>'
PLACAS = [  # (inicio, fin, html)
    (0.3, 3.5, STRIP + '<div class="c kick" style="top:640px">Sábado 7 de noviembre</div>'
               '<div class="c metal" style="top:720px;font-size:210px">Llegó<br><span class=gold>el día</span></div>'),
    (3.7, 6.5, STRIP + '<div class=c style="top:620px"><span class="flag ar"></span>'
               '<span style="display:inline-block;width:80px"></span><span class="flag es"></span></div>'
               '<div class="c metal" style="top:780px;font-size:150px">Argentina<br><span class=gold>vs España</span></div>'
               '<div class="c kick" style="top:1110px">En las dos ramas</div>'),
    (6.7, 9.6, STRIP + '<div class=card style="top:640px"><div class=k>Caballeros</div>'
               '<div class=v>Por el <span class=gold>tercero</span><br>al hilo</div></div>'),
    (9.8, 12.9, STRIP + '<div class="card rosa" style="top:640px"><div class=k>Damas</div>'
                '<div class=v>Por la <span class=gold>revancha</span><br>de 2024</div></div>'),
    (13.0, 14.5, '<div class="c metal" style="top:700px;font-size:230px"><span class=gold>¡Vamos</span><br>Argentina!</div>'),
    (14.6, DUR, '<div class=c style="top:560px"><img class=logo src="data:image/png;base64,LOGO"><br>'
                '<span class=handle>@surpadelstore</span></div>'
                '<div class="c kick" style="top:1240px">Seguí la final con nosotros</div>'),
]
# Subtítulos: tiempos de la locución (hype-voz1.mp3) + VOZ_INICIO
SUBS = [(0.0, 1.0, "Llegó el día."), (1.29, 3.0, "Final del Mundial, en Doha."),
        (3.42, 5.94, "Argentina contra España, en las dos ramas."),
        (6.33, 8.79, "Los chicos van por el tercer título al hilo."),
        (9.23, 12.17, "Las chicas, por la revancha de la final de hace dos años."),
        (12.59, 13.74, "¡Vamos Argentina!"), (14.05, 15.7, "Seguilo con Sur Padel.")]


def render(tmp):
    logo = b64(RAIZ / "marca/logo-sur-padel-transparente.png")
    capas = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for i, (a, z, html) in enumerate(PLACAS):
            pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body>{html.replace('LOGO', logo)}</body></html>")
            pg.wait_for_timeout(200)
            f = tmp / f"placa{i}.png"; pg.screenshot(path=str(f), omit_background=True); capas.append((a, z, f, 0.25))
        for i, (a, z, t) in enumerate(SUBS):
            pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body><div class=sub><span>{t}</span></div></body></html>")
            pg.wait_for_timeout(100)
            f = tmp / f"sub{i}.png"; pg.screenshot(path=str(f), omit_background=True)
            capas.append((a + VOZ_INICIO, z + VOZ_INICIO + 0.15, f, 0.08))
        b.close()
    return capas


def main(salida):
    tmp = pathlib.Path(tempfile.mkdtemp())
    capas = render(tmp)
    # fondo: 3 tomas encadenadas con fundidos (cada una ~7,85 s)
    seg = [(0, 6.4), (6.0, 12.4), (12.0, DUR)]
    ins, fil = [], []
    for i, t in enumerate(TOMAS):
        ins += ["-i", str(t)]
    for i, (a, z) in enumerate(seg):
        d = z - a + (0.4 if i < 2 else 0)
        fil.append(f"[{i}:v]trim=0:{d:.2f},setpts=PTS-STARTPTS,fps=24,scale=1080:1920,eq=brightness=-0.06:saturation=1.1[v{i}]")
        fil.append(f"[{i}:a]atrim=0:{d:.2f},asetpts=PTS-STARTPTS[a{i}]")
    fil.append("[v0][v1]xfade=transition=fade:duration=0.4:offset=6.0[x1]")
    fil.append("[x1][v2]xfade=transition=fade:duration=0.4:offset=12.0[bg]")
    fil.append("[a0][a1]acrossfade=d=0.4[ax1];[ax1][a2]acrossfade=d=0.4,volume=-18dB[amb]")
    n = len(TOMAS)
    ins += ["-i", str(VOZ)]
    fil.append(f"[{n}:a]adelay={int(VOZ_INICIO*1000)}|{int(VOZ_INICIO*1000)},volume=1.6[voz]")
    fil.append("[amb][voz]amix=inputs=2:duration=first:dropout_transition=0,atrim=0:" + f"{DUR}" + ",afade=t=out:st=" + f"{DUR-0.8}:d=0.8[aud]")
    prev = "bg"
    for j, (a, z, f, fd) in enumerate(capas):
        k = n + 1 + j
        ins += ["-loop", "1", "-t", f"{DUR}", "-i", str(f)]
        fil.append(f"[{k}:v]format=rgba,fade=t=in:st={a}:d={fd}:alpha=1,fade=t=out:st={max(a, z-fd)}:d={fd}:alpha=1[c{j}]")
        fil.append(f"[{prev}][c{j}]overlay=0:0:enable='between(t,{a},{z})'[o{j}]")
        prev = f"o{j}"
    fil.append(f"[{prev}]unsharp=5:5:0.4,format=yuv420p[vout]")
    cmd = ["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fil), "-map", "[vout]", "-map", "[aud]",
           "-t", f"{DUR}", "-r", "24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", salida]
    subprocess.run(cmd, check=True)
    print(salida)


if __name__ == "__main__":
    main(sys.argv[1])
