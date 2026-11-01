"""Historias "especiales" de la cobertura de torneos OverGrip (además de los resultados de cruces).

- "Hoy se juega" (tipo hoy): una por día de torneo, desde las 9:00. Junta todos
  los torneos que juegan ese día e invita a seguir @surpadelstore para tener los
  resultados al día.
- "Lo mejor de las zonas" (tipo zona): una por rama y por día de zonas, desde las
  22:45 (o a la mañana siguiente si quedó pendiente). Muestra los partidos más
  peleados del día (3 sets, tie-breaks, diferencia corta), uno por categoría.
- "Ya están las llaves" (tipo llaves): una por torneo, cuando OverGrip ya armó la
  mayoría de los cruces y todavía no se jugó ninguno.

historias.py llama a trabajos() para saber qué falta y a dibujar() para armarlas.
Cada historia lleva una "clave" única en historias.json, así nunca se repite.
"""
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "overgrip" / "datos"
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
ORDEN_CRUCES = ["16avos", "Octavos de Final", "Cuartos de Final", "Semifinal", "Final"]
MARCADOR = re.compile(r"^\d{1,2}/\d{1,2}( \d{1,2}/\d{1,2}){1,2}$")
ZONA_DESDE = (22, 45)
HOY_DESDE = 9
MAX_ZONA = {"azul": 5, "rosa": 4}


def franja(nombre):
    """Estilo de la franja para que el nombre literal del torneo entre siempre."""
    n = len(nombre)
    fs = 34 if n <= 16 else 28 if n <= 26 else 22 if n <= 40 else 18
    return f' style="font-size:{fs}px;max-width:720px;white-space:normal;line-height:1.05"'


def tamano_nombre(nombre):
    n = len(nombre)
    return 66 if n <= 16 else 54 if n <= 26 else 44 if n <= 40 else 36


def leer(p, vacio):
    return json.loads(p.read_text()) if p.exists() else vacio


def corto(pareja):
    out = []
    for j in pareja.split(" / "):
        ap, _, nom = j.partition(", ")
        out.append(f"{ap} {nom[:1]}." if nom else ap)
    return " / ".join(out)


def dia_texto(iso):
    d = date.fromisoformat(iso)
    return f"{DIAS[d.weekday()]} {d.day}/{d.month}"


def peleado(p):
    """Cuanto más chico, más peleado: 3 sets primero, después tie-breaks y diferencia de games."""
    sets = [tuple(map(int, s.split("/"))) for s in p["res"].split()]
    dif = abs(sum(a for a, _ in sets) - sum(b for _, b in sets))
    tb = sum(1 for a, b in sets if {a, b} == {6, 7})
    return (-len(sets), -tb, dif)


def datos_torneo(tid):
    return leer(DATOS / f"{tid}.json", {})


def ya_hecho(hist, clave):
    return any(h.get("clave") == clave for h in hist)


def trabajos(conf, hist, ahora):
    """Historias especiales que corresponde armar ahora."""
    hoy = ahora.date()
    minutos = ahora.hour * 60 + ahora.minute
    activos = [c for c in conf if c.get("activo")]
    out = []

    # 1) Hoy se juega (solo torneos con fechas conocidas)
    jugando = [c for c in activos if hoy.isoformat() in c.get("fechas", [])]
    clave = f"hoy-{hoy.isoformat()}"
    if jugando and HOY_DESDE <= ahora.hour < 22 and not ya_hecho(hist, clave):
        items = []
        for c in jugando:
            d = datos_torneo(c["id"])
            hay_zona = any(z["dia"] == hoy.isoformat() for z in d.get("zonas", {}).values())
            hay_cruce = any(x["dia"] == hoy.isoformat() for x in d.get("cruces", {}).values())
            fase = "Fase de zonas" if hay_zona else ("Se definen las llaves" if hay_cruce else "")
            items.append({"corto": c.get("corto", "Torneo"), "sede": c.get("sede", ""),
                          "organiza": c.get("organiza", ""), "fase": fase})
        solo_damas = all(cat.startswith("Damas") for c in jugando for cat in c.get("categorias", ["x"]))
        etiquetas = [c["organiza"] for c in jugando if c.get("organiza")][:4]
        out.append({"tipo": "hoy", "clave": clave, "torneo": jugando[0]["id"], "inst": "Hoy",
                    "tema": "rosa" if solo_damas else "azul", "items": items,
                    "dia": dia_texto(hoy.isoformat()), "etiquetas": etiquetas,
                    "archivo": f"especiales/hoy-{hoy.isoformat()}.png",
                    "alt": "Hoy se juega: " + "; ".join(f"{i['corto']} {i['sede']}".strip() for i in items)
                           + ". Seguí @surpadelstore para tener todos los resultados al día."})

    for c in activos:
        d = datos_torneo(c["id"])
        zonas = d.get("zonas", {})
        cruces = d.get("cruces", {})

        # 2) Lo mejor de las zonas
        dias_zona = sorted({z["dia"] for z in zonas.values() if z.get("dia")})
        for dia in dias_zona:
            dd = date.fromisoformat(dia)
            toca = (dd == hoy and minutos >= ZONA_DESDE[0] * 60 + ZONA_DESDE[1]) or \
                   (dd == hoy - timedelta(days=1) and ahora.hour < 12)
            if not toca:
                continue
            jugados = [dict(codigo=k, **z) for k, z in zonas.items()
                       if z["dia"] == dia and z["estado"] == "Finalizado" and MARCADOR.match(z["res"] or "")
                       and z["p1"].strip() and z["p2"].strip() and z["gan"] in (1, 2)]
            for rama in ("azul", "rosa"):
                clave = f"zona-{c['id']}-{dia}-{rama}"
                if ya_hecho(hist, clave):
                    continue
                ps = sorted((p for p in jugados if p["cat"].startswith("Damas") == (rama == "rosa")),
                            key=peleado)
                elegidos, cats = [], set()
                for p in ps:  # primero uno por categoría, después completa
                    if p["cat"] not in cats and len(elegidos) < MAX_ZONA[rama]:
                        elegidos.append(p)
                        cats.add(p["cat"])
                for p in ps:
                    if len(elegidos) >= MAX_ZONA[rama]:
                        break
                    if p not in elegidos:
                        elegidos.append(p)
                if len(elegidos) < 2:
                    continue
                elegidos.sort(key=lambda p: p["cat"])
                out.append({
                    "tipo": "zona", "clave": clave, "torneo": c["id"], "inst": "Zonas", "tema": rama,
                    "corto": c.get("corto", "Torneo"), "organiza": c.get("organiza", ""),
                    "strip": f"Zonas · {DIAS[dd.weekday()]}" + (" · Damas" if rama == "rosa" else ""),
                    "partidos": [{"tag": f"{p['cat']} · Zona {p.get('zona', '')}".strip(" ·"),
                                  "g": corto(p["p1"] if p["gan"] == 1 else p["p2"]),
                                  "p": corto(p["p2"] if p["gan"] == 1 else p["p1"]), "s": p["res"]}
                                 for p in elegidos],
                    "codigos": {p["codigo"]: p["res"] for p in elegidos},
                    "archivo": f"{c['id']}/zonas-{dia}-{rama}.png",
                    "alt": f"Lo mejor de las zonas del {dia_texto(dia)}: " + "; ".join(
                        f"{p['cat']}, ganaron {corto(p['p1'] if p['gan'] == 1 else p['p2'])} {p['res']}"
                        for p in elegidos),
                })

        # 3) Ya están las llaves
        clave = f"llaves-{c['id']}"
        if cruces and not ya_hecho(hist, clave) and 9 <= ahora.hour < 23 \
                and not any(x["estado"] in ("Finalizado", "WO", "En curso") for x in cruces.values()):
            por_cat = {}
            for x in cruces.values():
                por_cat.setdefault(x["cat"], []).append(x)
            listas = []
            for cat, xs in por_cat.items():
                primera = min(ORDEN_CRUCES.index(x["inst"]) for x in xs if x["inst"] in ORDEN_CRUCES)
                ronda = [x for x in xs if x["inst"] == ORDEN_CRUCES[primera]]
                armados = sum(1 for x in ronda if x["p1"].strip() and x["p2"].strip())
                if armados * 2 >= len(ronda):
                    listas.append(cat)
            if por_cat and len(listas) * 10 >= len(por_cat) * 6:
                desde = min((x["dia"] for x in cruces.values() if x.get("dia")), default="")
                cab = [k.replace("Caballeros ", "") for k in sorted(por_cat) if k.startswith("Caballeros")]
                dam = [k.replace("Damas ", "") for k in sorted(por_cat) if k.startswith("Damas")]
                out.append({
                    "tipo": "llaves", "clave": clave, "torneo": c["id"], "inst": "Llaves", "tema": "azul",
                    "corto": c.get("corto", "Torneo"), "organiza": c.get("organiza", ""),
                    "caballeros": cab, "damas": dam, "desde": dia_texto(desde) if desde else "",
                    "archivo": f"{c['id']}/llaves.png",
                    "alt": f"Ya están las llaves de {c.get('corto', 'el torneo')}"
                           + (f": se juegan desde el {dia_texto(desde)}" if desde else "")
                           + ". Mirá tu cruce en app.overgrip.com.ar.",
                })
    return out


# ---------- dibujo ----------

def _html(d, gen, premier):
    t = gen.THEMES[d["tema"]]
    fondos = {("hoy", "azul"): "fondo-09-publico.jpg", ("hoy", "rosa"): "fondo-15-rosa-arena.jpg",
              ("zona", "azul"): "fondo-12-club-canchas.jpg", ("zona", "rosa"): "fondo-17-rosa-cesped.jpg",
              ("llaves", "azul"): "fondo-10-tunel.jpg"}
    fondo = "../../marca/fondos/" + fondos[(d["tipo"], d["tema"])]
    css = premier.base_css(t, 1080, 1920, fondo) + f"""
.wrap{{padding:150px 70px 230px}}
.list{{width:100%;flex:1;display:flex;flex-direction:column;justify-content:center;gap:18px;padding:36px 0 50px}}
.tc{{background:linear-gradient(90deg,rgba(7,21,40,.95),rgba(7,21,40,.7));border-left:8px solid {t['hot']};border-radius:6px;padding:22px 30px;box-shadow:0 10px 30px rgba(0,0,0,.45)}}
.tc .n{{font-family:BC;font-weight:800;font-style:italic;font-size:66px;line-height:1;text-transform:uppercase}}
.tc .s{{font-size:28px;color:rgba(255,255,255,.75);margin-top:6px}}
.tc .f{{display:inline-block;margin-top:12px;font-size:22px;font-weight:700;letter-spacing:3px;text-transform:uppercase;background:{t['court']};padding:6px 14px;border-radius:4px}}
.tc .o{{font-size:26px;color:{t['acc']};font-weight:700;margin-top:8px}}
.cta{{width:100%;text-align:center;background:rgba(7,21,40,.88);border:3px solid {t['hot']};border-radius:14px;padding:30px 30px 34px;box-shadow:0 10px 30px rgba(0,0,0,.5)}}
.cta .k{{font-weight:700;letter-spacing:6px;font-size:24px;color:{t['acc']};text-transform:uppercase}}
.cta .h{{font-family:BC;font-weight:800;font-style:italic;font-size:76px;line-height:1;text-transform:uppercase;margin-top:8px}}
.cta .h b{{color:{t['hot']}}}
.cta .p{{font-size:30px;color:rgba(255,255,255,.85);margin-top:10px;line-height:1.3}}
.lead{{font-size:34px;text-align:center;color:rgba(255,255,255,.9);margin-top:22px;line-height:1.3;text-shadow:0 3px 14px rgba(0,0,0,.8)}}
.cats{{display:flex;flex-wrap:wrap;gap:12px;padding:16px 18px}}
.cats span{{font-family:BC;font-weight:800;font-style:italic;font-size:44px;text-transform:uppercase;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);border-radius:6px;padding:4px 18px}}
.sb.rosa .hd{{background:linear-gradient(90deg,#8f2a5c,#b8366f)}}
"""
    if d["tema"] == "rosa":
        css += ".gold{background:linear-gradient(180deg,#ffe0ee 0%,#ff6fa8 45%,#c23a78 58%,#ff8fbd 100%);-webkit-background-clip:text}"
    org = f'Torneo <b>@{d["organiza"]}</b> · ' if d.get("organiza") else ""
    seguinos = '<div class=brand>SEGUÍ @SURPADELSTORE · TODOS LOS TORNEOS AL DÍA</div>'
    logo = f'<img class=logo style="margin-top:46px" src="data:image/png;base64,{gen.LOGO}">'

    if d["tipo"] == "hoy":
        cards = "".join(
            f'<div class=tc><div class=n style="font-size:{tamano_nombre(i["corto"])}px">{i["corto"]}</div>'
            + (f'<div class=s>{i["sede"]}</div>' if i["sede"] else "")
            + (f'<div class=o>@{i["organiza"]}</div>' if i["organiza"] else "")
            + (f'<div class=f>{i["fase"]}</div>' if i["fase"] else "") + "</div>"
            for i in d["items"])
        body = (f'<div class=strip><div class=a>Hoy</div><div class=b>{d["dia"]}</div></div>{logo}'
                f'<div class=metal style="font-size:132px;margin-top:22px">Hoy se<br><span class=gold>juega</span></div>'
                f'<div class=list>{cards}</div>'
                '<div class=cta><div class=k>Resultados al día</div>'
                '<div class=h>Seguí a <b>@surpadelstore</b></div>'
                '<div class=p>Te contamos cada cruce, cada final y los campeones de los torneos de la zona.</div></div>'
                '<div class=foot style="margin-top:34px"><div class=live><span class=dot></span>En vivo en app.overgrip.com.ar</div>'
                '<div class=cred>Resultados <b>@overgripapp</b></div>'
                '<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>')
    elif d["tipo"] == "zona":
        cards = "".join(premier.scoreboard(m, m["tag"]) for m in d["partidos"])
        body = (f'<div class=strip><div class=a{franja(d["corto"])}>{d["corto"]}</div><div class=b>{d["strip"]}</div></div>{logo}'
                f'<div class=metal style="font-size:112px;margin-top:22px">Lo mejor de<br>las <span class=gold>zonas</span></div>'
                f'<div class=list>{cards}</div>'
                '<div class=foot><div class=live><span class=dot></span>Todas las zonas en app.overgrip.com.ar</div>'
                f'<div class=cred>{org}Resultados <b>@overgripapp</b></div>{seguinos}</div>')
    else:  # llaves
        blk = ""
        for rama, cats, cls in (("Caballeros", d["caballeros"], ""), ("Damas", d["damas"], " rosa")):
            if cats:
                blk += (f'<div class="sb{cls}"><div class=hd><span>{rama}</span><span>Llaves listas</span></div>'
                        '<div class=cats>' + "".join(f"<span>{x}</span>" for x in cats) + "</div></div>")
        desde = f'<div class=lead>Se juegan desde el <b>{d["desde"]}</b>.<br>Mirá tu cruce y tu horario en OverGrip.</div>' if d["desde"] else \
            '<div class=lead>Mirá tu cruce y tu horario en OverGrip.</div>'
        body = (f'<div class=strip><div class=a{franja(d["corto"])}>{d["corto"]}</div><div class=b>Llaves</div></div>{logo}'
                f'<div class=metal style="font-size:124px;margin-top:22px">Ya están<br>las <span class=gold>llaves</span></div>'
                f'{desde}<div class=list>{blk}</div>'
                '<div class=foot><div class=live><span class=dot></span>Cruces y horarios en app.overgrip.com.ar</div>'
                f'<div class=cred>{org}Resultados <b>@overgripapp</b></div>{seguinos}</div>')
    return (f"<html><head><meta charset=utf-8><style>{css}</style></head>"
            f"<body>{premier.deco(t)}<div class=wrap>{body}</div></body></html>")


def dibujar(lista, salida):
    if not lista:
        return
    sys.path.insert(0, str(RAIZ / "instagram" / "2026-11-jpq"))
    import gen, premier
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for d in lista:
            destino = Path(salida) / d["archivo"]
            destino.parent.mkdir(parents=True, exist_ok=True)
            pg = b.new_page(viewport={"width": 1080, "height": 1920})
            # base_css resuelve el fondo relativo a la carpeta del generador
            pg.set_content(_html(d, gen, premier))
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(destino))
            pg.close()
            print(destino)
        b.close()
