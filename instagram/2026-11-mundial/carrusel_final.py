"""Carrusel de feed (1080x1350) 'Así forma Argentina en la final' del Mundial.

Portada + cruces de damas + cruces de caballeros + camino a la final.
Uso: FONTS_DIR=... python3 instagram/2026-11-mundial/carrusel_final.py datos.json carpeta_salida
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import formaciones as F  # noqa: E402
from formaciones import premier  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

W, H = 1080, 1350
t, r = premier.T["azul"], premier.T["rosa"]
CSS = premier.base_css(t, W, H, F.FONDO) + f"""
.wrap{{padding:70px 70px 56px}}
.flag{{position:relative;flex:none;width:54px;height:36px;border-radius:4px;box-shadow:0 0 0 1px rgba(255,255,255,.3)}}
.big .flag{{width:150px;height:100px;border-radius:10px;box-shadow:0 0 0 3px rgba(255,255,255,.35),0 12px 30px rgba(0,0,0,.6)}}
.big{{display:flex;align-items:center;gap:60px;margin-top:50px}}
.big .x{{font-family:BC;font-style:italic;font-weight:800;font-size:70px;color:{t['acc']}}}
.sub{{margin-top:26px;font-size:34px;color:#dfe9f5;text-align:center}}
.swipe{{margin-top:40px;font-family:BC;font-style:italic;font-weight:800;font-size:40px;letter-spacing:3px;text-transform:uppercase;color:{t['hot']}}}
.list{{width:100%;display:flex;flex-direction:column;gap:22px;margin-top:40px}}
.m{{background:rgba(11,29,54,.86);border:2px solid {t['acc']}55;border-radius:18px;overflow:hidden}}
.rosa .m{{border-color:{r['acc']}77;background:rgba(22,7,26,.84)}}
.m .hd{{padding:10px 24px;font-weight:700;letter-spacing:4px;font-size:22px;text-transform:uppercase;
 background:linear-gradient(90deg,{t['court2']},{t['court']})}}
.rosa .m .hd{{background:linear-gradient(90deg,{r['court2']},{r['court']})}}
.p{{display:flex;align-items:center;gap:20px;padding:24px 26px;font-family:BC;font-style:italic;font-weight:800;font-size:50px;text-transform:uppercase}}
.p.rv{{color:rgba(255,255,255,.72)}}
.vsl{{display:flex;align-items:center;gap:16px;padding:0 26px;font-family:BC;font-style:italic;font-weight:800;font-size:28px;color:{t['acc']}}}
.rosa .vsl{{color:{r['acc']}}}
.vsl:before,.vsl:after{{content:"";flex:1;height:1px;background:rgba(255,255,255,.18)}}
.tbl{{width:100%;margin-top:40px;border-radius:18px;overflow:hidden;background:rgba(11,29,54,.86);border:2px solid {t['acc']}55}}
.tr{{display:grid;grid-template-columns:190px 1fr 1fr;align-items:center;border-top:1px solid rgba(255,255,255,.1);padding:16px 24px;font-size:30px;font-weight:700}}
.tr.h{{border-top:0;background:linear-gradient(90deg,{t['court2']},{t['court']});font-size:22px;letter-spacing:4px;text-transform:uppercase;padding:12px 24px}}
.tr .f{{font-family:BC;font-style:italic;font-weight:800;font-size:36px;text-transform:uppercase;color:{t['acc']}}}
.cell{{display:flex;align-items:center;gap:14px}} .cell .flag{{width:42px;height:28px}}
.cell b{{font-family:BC;font-style:italic;font-weight:800;font-size:36px;color:{t['hot']}}} .cell i{{font-style:normal;font-size:26px;width:150px}}
.dato{{margin-top:34px;font-size:32px;color:#dfe9f5;text-align:center}} .dato b{{color:{t['hot']}}}
"""


def strip(d): return f'<div class=strip><div class=a>Mundial</div><div class=b>Doha · {d}</div></div>'


FOOT = ('<div class=foot><div class=cred>Selección <b>@padel_apa</b> · Mundial <b>@padelfip</b></div>'
        '<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>')


def portada(d):
    return (strip("La final") + f'<div class=metal style="font-size:150px;margin-top:70px">{d["titulo"]}</div>'
            f'<div class=big>{F.bandera("ar")}<span class=x>vs</span>{F.bandera(d["fp"])}</div>'
            f'<div class=sub>{d["sub"]}</div><div class=swipe>Deslizá →</div>' + FOOT)


def rama(b, d):
    ms = ""
    for i, m in enumerate(b["partidos"]):
        ms += (f'<div class=m><div class=hd>Partido {i + 1}</div>'
               f'<div class=p>{F.bandera("ar")}{m["g"]}</div><div class=vsl>vs</div>'
               f'<div class="p rv">{F.bandera(d["fp"])}{m["p"]}</div></div>')
    return (strip("La final") + f'<div class=metal style="font-size:120px;margin-top:40px">{b["titulo"]}</div>'
            f'<div class="list {b["tema"]}">{ms}</div>' + FOOT)


def camino(c):
    rows = '<div class="tr h"><span>Ronda</span><span>Caballeros</span><span>Damas</span></div>'
    for f in c["filas"]:
        rows += (f'<div class=tr><span class=f>{f[0]}</span>'
                 f'<span class=cell>{F.bandera(f[1])}<i>{f[5]}</i><b>{f[2]}</b></span>'
                 f'<span class=cell>{F.bandera(f[3])}<i>{f[6]}</i><b>{f[4]}</b></span></div>')
    return (strip("Camino a la final") + f'<div class=metal style="font-size:120px;margin-top:40px">{c["titulo"]}</div>'
            f'<div class=tbl>{rows}</div><div class=dato>{c["dato"]}</div>' + FOOT)


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    slides = [portada(d)] + [rama(b, d) for b in d["ramas"]] + [camino(d["camino"])]
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": W, "height": H})
        for i, s in enumerate(slides, 1):
            pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head>"
                           f"<body>{premier.deco(t)}<div class=wrap>{s}</div></body></html>")
            pg.wait_for_timeout(300)
            f = out / f"final-formaciones-{i}.png"; pg.screenshot(path=str(f)); print(f)
        br.close()
