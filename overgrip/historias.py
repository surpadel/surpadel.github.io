"""Arma las historias de Instagram con los resultados nuevos de OverGrip.

Lee overgrip/datos/novedades.json (lo escribe seguir.py) y junta los partidos
terminados que todavía no tienen imagen en grupos: mismo torneo, misma
instancia, misma rama (caballeros azul, damas rosa) y mismo día. Nunca mezcla
torneos ni instancias.

Un grupo se dibuja recién cuando terminaron todos sus partidos (pedido de Nico,
15/11/2026: no tirar un resultado suelto y después otros tres). Excepción: si lo
único que falta son partidos "aparte" (demorados: pasaron 2h30 de su hora sin
resultado; o lejanos: programados 2 horas o más después de los ya terminados),
sale lo terminado. Los lejanos forman su propia tanda más tarde (prioridad
normal); los demorados, cuando aparecen, van en una historia "suelta" que va
última en la cola y solo sale si queda lugar en el tope del día.
Las deja en instagram/overgrip/<torneo>/ y las anota en overgrip/datos/historias.json
como pendientes de publicar.

Uso:
  python3 overgrip/historias.py --hay   -> imprime "true" o "false"
  python3 overgrip/historias.py         -> dibuja lo que corresponda
  python3 overgrip/historias.py --ya    -> dibuja todo lo pendiente sin esperar

Además arma las historias especiales de especiales.py (Hoy se juega,
Lo mejor de las zonas, Ya están las llaves) cuando corresponde.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "overgrip" / "datos"
NOV = DATOS / "novedades.json"
HIST = DATOS / "historias.json"
CONF = RAIZ / "overgrip" / "torneos.json"
SALIDA = RAIZ / "instagram" / "overgrip"
RAW = "https://raw.githubusercontent.com/surpadel/surpadel.github.io/main/"
ARG = timezone(timedelta(hours=-3))
MAX_POR_HISTORIA = 6  # entran 6 marcadores cómodos (probado 15/11)
DEMORA = timedelta(hours=4)  # pasó su hora + 4 h sin resultado: demorado
# (OverGrip suele cargar los resultados entre 1 y 3,5 horas después de la hora del partido)
LEJOS = timedelta(minutes=120)  # programado 2 h o más después de los ya terminados: va aparte
ESPERA_MAX = timedelta(hours=6)  # red de seguridad: ningún resultado espera más que esto
TERMINADOS = {"Finalizado", "WO"}

# instancia -> (rótulo de la franja, título, fondo azul, fondo rosa)
INSTANCIAS = {
    "16avos": ("16avos", "A <span class=gold>octavos</span>", "fondo-05-focos.jpg", "fondo-17-rosa-cesped.jpg"),
    "Octavos de Final": ("Octavos", "A <span class=gold>cuartos</span>", "fondo-02-red-arena.jpg", "fondo-16-rosa-red.jpg"),
    "Cuartos de Final": ("Cuartos", "A <span class=gold>semis</span>", "fondo-01-arena-tribuna.jpg", "fondo-15-rosa-arena.jpg"),
    "Semifinal": ("Semifinales", "A la <span class=gold>final</span>", "fondo-06-final-spot.jpg", "fondo-16-rosa-red.jpg"),
    "Final": ("Finales", "Los <span class=gold>campeones</span>", "fondo-14-campeones-confeti.jpg", "fondo-15-rosa-arena.jpg"),
}
ORDEN = list(INSTANCIAS)


def leer(p, vacio):
    return json.loads(p.read_text()) if p.exists() else vacio


def corto(pareja):
    """'González, Bruno / Stubbe, Nazareno' -> 'González B. / Stubbe N.'"""
    out = []
    for j in pareja.split(" / "):
        ap, _, nom = j.partition(", ")
        out.append(f"{ap} {nom[:1]}." if nom else ap)
    return " / ".join(out)


def dibujable(p):
    return p["estado"] == "Finalizado" and p["res"] and p["inst"] in INSTANCIAS


def pendientes(nov):
    """Partidos terminados sin imagen (no WO), con la tanda en que se detectaron."""
    out = []
    for tanda in nov:
        if tanda.get("dibujada"):
            continue
        hechos = set(tanda.get("hechos", []))
        for p in tanda["partidos"]:
            if dibujable(p) and p.get("codigo") not in hechos:
                out.append((tanda, p))
    return out


def rama(p):
    return "rosa" if (p.get("cat") or "").startswith("Damas") else "azul"


def inicio(p):
    try:
        return datetime.strptime(f'{p["dia"]} {p["hora"]}', "%Y-%m-%d %H:%M").replace(tzinfo=ARG)
    except (KeyError, TypeError, ValueError):
        return None


def grupos_listos(lista, ahora, forzar=False):
    """Agrupa por (torneo, instancia, rama, día) y devuelve solo los grupos listos.

    Devuelve {clave: (partidos, códigos de los demorados que quedan afuera)}.
    Listo = no queda ningún partido del grupo sin terminar en OverGrip, o los
    que quedan están "aparte" (demorados o lejanos), o el resultado más viejo
    ya esperó ESPERA_MAX, o se pidió --ya."""
    grupos = {}
    for tanda, p in lista:
        clave = (tanda["torneo"], p["inst"], rama(p), p.get("dia") or "")
        grupos.setdefault(clave, []).append((tanda, p))
    cruces_de = {}
    listos = {}
    for clave, items in grupos.items():
        torneo, inst, ram, dia = clave
        if torneo not in cruces_de:
            cruces_de[torneo] = leer(DATOS / f"{torneo}.json", {}).get("cruces", {})
        ya = {p.get("codigo") for _, p in items}
        faltan_cod = [(cod, c) for cod, c in cruces_de[torneo].items()
                      if cod not in ya and c.get("inst") == inst and rama(c) == ram
                      and (c.get("dia") or "") == dia and c.get("estado") not in TERMINADOS]
        faltan = [c for _, c in faltan_cod]
        horas = [h for h in (inicio(p) for _, p in items) if h]
        ultima = max(horas) if horas else None

        def demorado(c):
            h = inicio(c)
            return h is not None and ahora >= h + DEMORA

        def lejano(c):
            h = inicio(c)
            return h is not None and ultima is not None and h >= ultima + LEJOS

        viejo = min(datetime.strptime(t["hora"], "%Y-%m-%d %H:%M").replace(tzinfo=ARG) for t, _ in items)
        if forzar or all(demorado(c) or lejano(c) for c in faltan) or ahora - viejo >= ESPERA_MAX:
            listos[clave] = ([p for _, p in items], sorted(cod for cod, c in faltan_cod if demorado(c)))
        else:
            print(f"Espera {torneo} {inst} {ram} {dia}: {len(items)} listos, faltan {len(faltan)}",
                  file=sys.stderr)  # a stderr: --hay solo debe imprimir true/false
    return listos


def armar_trabajos(listos, conf, hist):
    demorados = {c for h in hist for c in h.get("demorados", [])}
    sello = datetime.now(ARG).strftime("%m%d-%H%M")
    trabajos = []
    for (torneo, inst, rama, dia), (ps, afuera) in sorted(listos.items(), key=lambda g: (ORDEN.index(g[0][1]), g[0][2])):
        grupo = f"{torneo}|{inst}|{rama}|{dia}"
        ps.sort(key=lambda p: p["cat"])
        rot, titulo, f_azul, f_rosa = INSTANCIAS[inst]
        if inst == "Final" and rama == "rosa":
            titulo = "Las <span class=gold>campeonas</span>"
        info = conf.get(torneo, {})
        partes = -(-len(ps) // MAX_POR_HISTORIA)
        tam = -(-len(ps) // partes)  # reparte parejo: 6 -> 3 + 3, no 5 + 1
        for n in range(0, len(ps), tam):
            tramo = ps[n:n + tam]
            slug = f"{inst.split()[0].lower()}-{rama}-{sello}-{n // tam + 1}"
            trabajos.append({
                "torneo": torneo,
                "corto": info.get("corto", "Torneo"),
                "organiza": info.get("organiza", ""),
                "tema": rama,
                "fondo": f"../../marca/fondos/{f_rosa if rama == 'rosa' else f_azul}",
                "strip": rot + (" · Damas" if rama == "rosa" else ""),
                "titulo": titulo,
                "partidos": [
                    {"tag": p["cat"], "g": corto(p["p1"] if p["gan"] == 1 else p["p2"]),
                     "p": corto(p["p2"] if p["gan"] == 1 else p["p1"]), "s": p["res"]}
                    for p in tramo
                ],
                "inst": inst,
                "grupo": grupo,
                "demorados": afuera if n == 0 else [],  # quedaron afuera por demorados
                # trae un partido que quedó afuera por demorado: va última en la cola
                "suelta": any(p.get("codigo") in demorados for p in tramo),
                "codigos": {p["codigo"]: p["res"] for p in tramo if p.get("codigo")},
                "archivo": f"{torneo}/{slug}.png",
                "alt": f"{rot}: " + "; ".join(f"{p['cat']}, ganaron {corto(p['p1'] if p['gan'] == 1 else p['p2'])} {p['res']}" for p in tramo),
            })
    return trabajos


def dibujar(trabajos):
    sys.path.insert(0, str(RAIZ / "overgrip" / "diseno"))
    sys.path.insert(0, str(RAIZ / "overgrip"))
    import gen, premier, especiales
    from playwright.sync_api import sync_playwright

    def html(d):
        t = gen.THEMES[d["tema"]]
        css = premier.base_css(t, 1080, 1920, d["fondo"]) + (
            ".wrap{padding:150px 70px 230px}"
            ".list{width:100%;flex:1;display:flex;flex-direction:column;justify-content:center;gap:18px;padding:40px 0 60px}")
        if d["tema"] == "rosa":
            css += ".gold{background:linear-gradient(180deg,#ffe0ee 0%,#ff6fa8 45%,#c23a78 58%,#ff8fbd 100%);-webkit-background-clip:text}"
        org = f'Torneo <b>@{d["organiza"]}</b> · ' if d["organiza"] else ""
        foot = ('<div class=foot><div class=live><span class=dot></span>Seguilo en vivo en app.overgrip.com.ar</div>'
                f'<div class=cred>{org}Resultados <b>@overgripapp</b></div>'
                '<div class=brand>@SURPADELSTORE · SURPADEL.COM.AR</div></div>')
        cards = "".join(premier.scoreboard(m, m["tag"]) for m in d["partidos"])
        body = (f'<div class=strip><div class=a{especiales.franja(d["corto"])}>{d["corto"]}</div><div class=b>{d["strip"]}</div></div>'
                f'<img class=logo style="margin-top:46px" src="data:image/png;base64,{gen.LOGO}">'
                f'<div class=metal style="font-size:124px;margin-top:22px">{d["titulo"]}</div>'
                f'<div class=list>{cards}</div>{foot}')
        return (f"<html><head><meta charset=utf-8><style>{css}</style></head>"
                f"<body>{premier.deco(t)}<div class=wrap>{body}</div></body></html>")

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for d in trabajos:
            destino = SALIDA / d["archivo"]
            destino.parent.mkdir(parents=True, exist_ok=True)
            pg = b.new_page(viewport={"width": 1080, "height": 1920})
            pg.set_content(html(d))
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(destino))
            pg.close()
            print(destino)
        b.close()


def main():
    sys.path.insert(0, str(Path(__file__).parent))
    import especiales
    nov = leer(NOV, [])
    hist = leer(HIST, [])
    conf_lista = leer(CONF, [])
    lista = pendientes(nov)
    forzar = "--ya" in sys.argv
    ahora = datetime.now(ARG)
    extra = especiales.trabajos(conf_lista, hist, ahora)
    listos = grupos_listos(lista, ahora, forzar)
    hay = bool(listos)
    if "--hay" in sys.argv:
        print("true" if hay or extra else "false")
        return
    if not hay and not extra:
        print("Nada para dibujar todavía")
        return
    conf = {t["id"]: t for t in conf_lista}
    trabajos = armar_trabajos(listos, conf, hist) if hay else []
    dibujar(trabajos)
    especiales.dibujar(extra, SALIDA)
    sello = ahora.strftime("%Y-%m-%d %H:%M")
    for d in trabajos:
        hist.append({"creada": sello, "torneo": d["torneo"], "inst": d["inst"],
                     "organiza": d["organiza"], "codigos": d["codigos"], "archivo": d["archivo"],
                     "grupo": d["grupo"], **({"suelta": True} if d["suelta"] else {}),
                     **({"demorados": d["demorados"]} if d["demorados"] else {}),
                     "url": RAW + "instagram/overgrip/" + d["archivo"], "alt": d["alt"][:1000],
                     "publicada": False})
    for d in extra:
        hist.append({"creada": sello, "torneo": d["torneo"], "inst": d["inst"], "tipo": d["tipo"],
                     "clave": d["clave"], "organiza": d.get("organiza", ""),
                     "etiquetas": d.get("etiquetas") or ([d["organiza"]] if d.get("organiza") else []),
                     "codigos": d.get("codigos", {}), "archivo": d["archivo"],
                     "url": RAW + "instagram/overgrip/" + d["archivo"], "alt": d["alt"][:1000],
                     "publicada": False})
    HIST.write_text(json.dumps(hist[-300:], ensure_ascii=False, indent=1))
    if hay:
        hechos = {p["codigo"] for ps, _ in listos.values() for p in ps if p.get("codigo")}
        for tanda in nov:
            if tanda.get("dibujada"):
                continue
            marcados = set(tanda.get("hechos", [])) | {p["codigo"] for p in tanda["partidos"] if p.get("codigo") in hechos}
            if marcados:
                tanda["hechos"] = sorted(marcados)
            if all(p.get("codigo") in marcados or not dibujable(p) for p in tanda["partidos"]):
                tanda["dibujada"] = True
                tanda.pop("hechos", None)
        NOV.write_text(json.dumps(nov, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
