"""Historia de resultados de argentinos en Dubái P1 (estilo circuito pro).

Reusa los marcadores de instagram/2026-11-mundial/formaciones.py, sin banderas
(las parejas son mixtas) y con la franja del torneo.

Uso: python3 instagram/2026-11-dubai/resultados.py datos.json salida.png
datos.json: {"franja": "Dubái P1", "bajada": "Día 1 · primera ronda", "titulo": "...",
             "bloques": [{"rama": "Damas", "tema": "rosa", "resumen": "2 de 4", "nota": "...",
                          "partidos": [{"g": "Fassio / Virseda", "p": "Collombon / Sharifova", "s": "6/2 7/5"}]}],
             "dato": "...", "cred": "..."}
"g" es la pareja con argentinos; "s" los sets desde su lado.
"""
import json, pathlib, sys
AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "instagram" / "2026-11-mundial"))
sys.path.insert(0, str(RAIZ / "overgrip" / "diseno"))
import formaciones, premier  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

formaciones.bandera = lambda cod: ""
FONDO = "../../marca/fondos/fondo-18-terraza-ciudad.jpg"


def historia(d):
    css, _ = formaciones.historia({"jornada": "", "titulo": "", "bloques": []})
    t = premier.T["azul"]
    css = css.replace(formaciones.FONDO, FONDO) + f"""
.row .nm{{padding:0 22px}}
.dato{{margin-top:34px;width:100%;background:rgba(7,21,40,.88);border:1px solid rgba(255,255,255,.16);
 border-left:8px solid {t['hot']};padding:20px 28px;font-size:31px;font-weight:600;line-height:1.3}}
.dato b{{color:{t['hot']}}}
.bh .nt{{font-family:B;font-style:normal;font-weight:600;font-size:22px;letter-spacing:1px;text-transform:none;color:#cfe0f3}}
"""
    blks = ""
    for b in d["bloques"]:
        cards = "".join(formaciones.marcador(m, m.get("et", "Primera ronda")) for m in b["partidos"])
        blks += (f'<div class="blk {b.get("tema", "azul")}"><div class=bh><span>{b["rama"]} · '
                 f'<span class=gold>{b["resumen"]}</span></span><small>{b.get("nota", "")}</small></div>'
                 f'<div class=list>{cards}</div></div>')
    dato = f'<div class=dato>{d["dato"]}</div>' if d.get("dato") else ""
    body = (f'<div class=strip><div class=a>{d["franja"]}</div><div class=b>{d["bajada"]}</div></div>'
            f'<div class=metal style="font-size:104px;margin-top:30px">{d["titulo"]}</div>'
            f'{blks}{dato}'
            f'<div class=foot><div class=cred>{d.get("cred", "")}</div>'
            '<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>')
    return css, f'{premier.deco(t)}<div class=wrap>{body}</div>'


if __name__ == "__main__":
    ent = pathlib.Path(sys.argv[1])
    d = json.load(open(ent))
    css, body = historia(d)
    sal = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ent.with_suffix(".png")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{css}</style></head><body>{body}</body></html>",
                       wait_until="load")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(sal))
        b.close()
    print(sal)
