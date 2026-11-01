"""Arma las historias de Instagram con los resultados nuevos de OverGrip.

Lee overgrip/datos/novedades.json (lo escribe seguir.py), junta los partidos
terminados que todavía no tienen imagen y, cuando conviene (4 o más partidos,
o el más viejo espera hace más de 60 minutos), dibuja historias estilo
"circuito pro" agrupadas por instancia y por rama (caballeros azul, damas rosa).
Las deja en instagram/overgrip/<torneo>/ y las anota en overgrip/datos/historias.json
como pendientes de publicar.

Uso:
  python3 overgrip/historias.py --hay   -> imprime "true" o "false"
  python3 overgrip/historias.py         -> dibuja lo que corresponda
  python3 overgrip/historias.py --ya    -> dibuja todo lo pendiente sin esperar
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
MAX_POR_HISTORIA = 5
MINIMO = 4
ESPERA = timedelta(minutes=60)

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


def pendientes(nov):
    """Partidos terminados sin imagen (no WO), con la hora en que se detectaron."""
    out = []
    for tanda in nov:
        if tanda.get("dibujada"):
            continue
        for p in tanda["partidos"]:
            if p["estado"] == "Finalizado" and p["res"] and p["inst"] in INSTANCIAS:
                out.append((tanda, p))
    return out


def conviene(lista, forzar=False):
    if not lista:
        return False
    if forzar or len(lista) >= MINIMO:
        return True
    viejo = min(datetime.strptime(t["hora"], "%Y-%m-%d %H:%M").replace(tzinfo=ARG) for t, _ in lista)
    return datetime.now(ARG) - viejo >= ESPERA


def armar_trabajos(lista, conf):
    grupos = {}
    for tanda, p in lista:
        rama = "rosa" if p["cat"].startswith("Damas") else "azul"
        grupos.setdefault((tanda["torneo"], p["inst"], rama), []).append(p)
    sello = datetime.now(ARG).strftime("%m%d-%H%M")
    trabajos = []
    for (torneo, inst, rama), ps in sorted(grupos.items(), key=lambda g: (ORDEN.index(g[0][1]), g[0][2])):
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
                "archivo": f"{torneo}/{slug}.png",
                "alt": f"{rot}: " + "; ".join(f"{p['cat']}, ganaron {corto(p['p1'] if p['gan'] == 1 else p['p2'])} {p['res']}" for p in tramo),
            })
    return trabajos


def dibujar(trabajos):
    sys.path.insert(0, str(RAIZ / "instagram" / "2026-11-jpq"))
    import gen, premier
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
        body = (f'<div class=strip><div class=a>{d["corto"]}</div><div class=b>{d["strip"]}</div></div>'
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
    nov = leer(NOV, [])
    lista = pendientes(nov)
    forzar = "--ya" in sys.argv
    if "--hay" in sys.argv:
        print("true" if conviene(lista, forzar) else "false")
        return
    if not conviene(lista, forzar):
        print("Nada para dibujar todavía")
        return
    conf = {t["id"]: t for t in leer(CONF, [])}
    trabajos = armar_trabajos(lista, conf)
    dibujar(trabajos)
    hist = leer(HIST, [])
    ahora = datetime.now(ARG).strftime("%Y-%m-%d %H:%M")
    for d in trabajos:
        hist.append({"creada": ahora, "torneo": d["torneo"], "archivo": d["archivo"],
                     "url": RAW + "instagram/overgrip/" + d["archivo"], "alt": d["alt"][:1000],
                     "publicada": False})
    HIST.write_text(json.dumps(hist[-200:], ensure_ascii=False, indent=1))
    for tanda in nov:
        tanda["dibujada"] = True
    NOV.write_text(json.dumps(nov, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
