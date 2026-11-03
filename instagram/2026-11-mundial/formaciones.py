"""Historia 'Así formó Argentina' del Mundial (estilo circuito pro).

Una historia por jornada con las 3 parejas de caballeros y las 3 de damas
y sus marcadores. Se publica junto con el reel de la jornada (pedido de Nico, 3/11).

Uso: FONTS_DIR=... LOGO_PNG=marca/logo-sur-padel-transparente.png \
     python3 instagram/2026-11-mundial/formaciones.py datos.json salida.png
datos.json: {"jornada": "Jornada 2", "titulo": "Así formó <span class=gold>Argentina</span>",
             "bloques": [{"rama": "Caballeros", "tema": "azul", "rival": "Países Bajos", "serie": "3-0",
                          "partidos": [{"g": "Tapia / Libaak", "p": "Países Bajos", "s": "6/4 6/2"}, ...]}, ...]}
"""
import json, pathlib, sys
RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "overgrip" / "diseno"))
import gen, premier  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

FONDO = "../../marca/fondos/fondo-01-arena-tribuna.jpg"

# Banderas dibujadas con CSS (códigos en el JSON: "fg" ganador, "fp" rival)
BANDERAS = {
    "ar": "linear-gradient(180deg,#74acdf 33.3%,#fff 33.3% 66.6%,#74acdf 66.6%)",
    "nl": "linear-gradient(180deg,#ae1c28 33.3%,#fff 33.3% 66.6%,#21468b 66.6%)",
    "be": "linear-gradient(90deg,#000 33.3%,#fdda24 33.3% 66.6%,#ef3340 66.6%)",
    "fr": "linear-gradient(90deg,#0055a4 33.3%,#fff 33.3% 66.6%,#ef4135 66.6%)",
    "es": "linear-gradient(180deg,#aa151b 25%,#f1bf00 25% 75%,#aa151b 75%)",
    "it": "linear-gradient(90deg,#009246 33.3%,#fff 33.3% 66.6%,#ce2b37 66.6%)",
    "pt": "linear-gradient(90deg,#006600 40%,#ff0000 40%)",
    "de": "linear-gradient(180deg,#000 33.3%,#dd0000 33.3% 66.6%,#ffce00 66.6%)",
    "br": "radial-gradient(circle at 50% 50%,#002776 18%,transparent 19%),linear-gradient(135deg,transparent 30%,#ffdf00 30% 70%,transparent 70%),#009c3b",
    "cl": "linear-gradient(180deg,transparent 50%,#d52b1e 50%),linear-gradient(90deg,#0039a6 35%,#fff 35%)",
    "us": "linear-gradient(90deg,#3c3b6e 40%,transparent 40%) 0 0/100% 54% no-repeat,repeating-linear-gradient(180deg,#b22234 0 7.7%,#fff 7.7% 15.4%)",
    "gb": "linear-gradient(90deg,transparent 42%,#c8102e 42% 58%,transparent 58%),linear-gradient(180deg,transparent 38%,#c8102e 38% 62%,transparent 62%),#012169",
}


def bandera(cod):
    sol = ('<i style="position:absolute;left:50%;top:50%;width:9px;height:9px;margin:-4.5px;border-radius:50%;'
           'background:#f6b40e"></i>') if cod == "ar" else ""
    return (f'<span class=flag style="background:{BANDERAS.get(cod, "#555")}">{sol}</span>')


def marcador(m, label):
    def sets(mine):
        out = ""
        for st in m["s"].split():
            a, b = st.split("/")
            v, o = (a, b) if mine else (b, a)
            out += f'<div class="set{" won" if int(v) > int(o) else ""}">{v}</div>'
        return out
    return (f'<div class=sb><div class=hd><span>{label}</span><span>Final</span></div>'
            f'<div class="row w"><div class=tri></div>{bandera(m.get("fg", "ar"))}<div class=nm>{m["g"]}</div>{sets(True)}</div>'
            f'<div class=row><div class=tri></div>{bandera(m.get("fp", ""))}<div class=nm>{m["p"]}</div>{sets(False)}</div></div>')


def historia(d):
    t = premier.T["azul"]
    r = premier.T["rosa"]
    css = premier.base_css(t, 1080, 1920, FONDO) + f"""
.wrap{{padding:120px 70px 120px}}
.blk{{width:100%;margin-top:30px}}
.bh{{display:flex;justify-content:space-between;align-items:baseline;font-family:BC;font-style:italic;font-weight:800;
 text-transform:uppercase;font-size:46px;margin-bottom:10px}}
.bh small{{font-family:B;font-style:normal;font-weight:700;font-size:24px;letter-spacing:3px;color:{t['acc']}}}
.list{{display:flex;flex-direction:column;gap:10px}}
.row{{height:56px}} .row .nm{{font-size:29px}} .set{{width:58px;font-size:36px}}
.sb .hd{{padding:4px 16px;font-size:18px}}
.rosa .sb .hd{{background:linear-gradient(90deg,{r['court2']},{r['court']})}}
.rosa .set.won{{background:{r['hot']};color:#16071a}} .rosa .row .tri{{border-left-color:{r['hot']}}}
.rosa .bh small{{color:{r['acc']}}}
.foot{{gap:10px}}
.flag{{position:relative;flex:none;width:44px;height:30px;margin-left:14px;border-radius:3px;box-shadow:0 0 0 1px rgba(255,255,255,.25)}}
.row .nm{{padding:0 14px}}
"""
    blks = ""
    for b in d["bloques"]:
        cards = "".join(marcador(m, f"Partido {i + 1}") for i, m in enumerate(b["partidos"]))
        blks += (f'<div class="blk {b.get("tema", "azul")}"><div class=bh><span>{b["rama"]} · '
                 f'<span class=gold>{b["serie"]}</span></span><small>vs {b["rival"]}</small></div>'
                 f'<div class=list>{cards}</div></div>')
    body = (f'<div class=strip><div class=a>Mundial</div><div class=b>Doha · {d["jornada"]}</div></div>'
            f'<div class=metal style="font-size:110px;margin-top:34px">{d["titulo"]}</div>'
            f'{blks}'
            '<div class=foot><div class=cred>Selección <b>@padel_apa</b> · Mundial <b>@padelfip</b></div>'
            '<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>')
    return css, f'{premier.deco(t)}<div class=wrap>{body}</div>'


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    css, body = historia(d)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{css}</style></head><body>{body}</body></html>")
        pg.wait_for_timeout(300)
        pg.screenshot(path=sys.argv[2])
        b.close()
    print(sys.argv[2])
