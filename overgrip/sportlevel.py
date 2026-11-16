"""Torneos de SportLevel (sportlevel.ar) para el seguimiento de Sur Padel.

Algunos clubes de La Plata (Distrito Padel Center, ALPHA Padel) no usan OverGrip
sino SportLevel. Este módulo los lleva al mismo formato que OverGrip, así
historias.py, especiales.py y publicar.py funcionan igual.

- partidos(slug): un solo pedido público por torneo (el cronograma del evento)
  con todos los partidos de todas las categorías. Devuelve (cruces, zonas) en el
  formato compacto de seguir.py. El resultado va del lado del ganador, como en
  OverGrip.
- buscar(conf, hoy): lee el buscador público de torneos de pádel y suma a
  torneos.json los de la zona (La Plata, Berazategui, Quilmes y alrededores),
  con el Instagram de la comunidad organizadora. Les actualiza fechas y estado.

En torneos.json cada torneo de SportLevel lleva "fuente": "sportlevel" y
"slug": "<comunidad>/<evento>". El id empieza con "SL-".
"""
import json
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta

API = "https://api.sportlevel.ar/api"
SITIO = "https://sportlevel.ar"
CAB = {"User-Agent": "SurPadel/1.0 (+https://surpadel.com.ar)", "Accept": "application/json"}

# Zona que cubre Sur Padel: zona sur del conurbano y La Plata (sin CABA).
ZONA = {"lat": (-35.25, -34.68), "lon": (-58.55, -57.70)}

CATEGORIAS = {"PRIMERA": "1ra", "SEGUNDA": "2da", "TERCERA": "3ra", "CUARTA": "4ta",
              "QUINTA": "5ta", "SEXTA": "6ta", "SEPTIMA": "7ma", "OCTAVA": "8va"}
RONDAS = ["Final", "Semifinal", "Cuartos de Final", "Octavos de Final", "16avos"]
ESTADOS_FIN = {"COMPLETED", "FINISHED", "PLAYED"}


def pedir(ruta):
    req = urllib.request.Request(API + ruta, headers=CAB)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


# ---------- partidos ----------

def categoria(m):
    """'Caballeros 6ta', 'Damas 2da', 'Caballeros 5ta +35'."""
    rama = "Damas" if (m.get("gender") or "").upper().startswith("DAM") else "Caballeros"
    nivel = CATEGORIAS.get((m.get("category") or "").upper())
    if not nivel:  # nombre libre: "<Evento> 2da CABALLEROS" -> busca "2da"
        nombre = (m.get("categoryName") or "").split()
        nivel = next((x for x in nombre if x[:1].isdigit()), m.get("categoryCode") or "")
    extra = (m.get("division") or m.get("categoryLabel") or "").strip()
    return f"{rama} {nivel}" + (f" {extra}" if extra else "")


def titulo(palabra):
    if palabra.isupper() or palabra.islower():
        return "-".join(p[:1].upper() + p[1:].lower() for p in palabra.split("-"))
    return palabra


# Segundos nombres comunes: con 3 palabras deciden si la del medio es nombre o apellido
# ("Juan Manuel Nardelli" -> Nardelli; "Vanesa Perez Serrano" -> Perez Serrano).
NOMBRES = set("""agustin agustina alejandro andres angel ariel belen candela carlos cruz daniel david diego
emilia emiliano esteban ezequiel facundo federico felipe fernando florencia francisco gabriel gaston
guadalupe ignacio ines jose josefina juan julian julieta lautaro lucas lucia luis luz manuel maria
mariano martin martina matias maximo mercedes miguel nicolas pablo paula pedro rafael ramiro ramon
rocio rodrigo santiago sebastian simon sofia sol tomas valentin valentina victoria""".split())


def jugador(nombre):
    """'Juan Ignacio Moreno Lezana' -> 'Moreno Lezana, Juan Ignacio' (formato OverGrip).

    Con 4 palabras o más el apellido son las dos últimas; con 3, la última salvo
    que la del medio no sea un nombre conocido (entonces van las dos últimas)."""
    ps = [titulo(p) for p in nombre.split()]
    if len(ps) < 2:
        return " ".join(ps)
    if len(ps) >= 4:
        n = 2
    elif len(ps) == 3:
        n = 1 if sin_tildes(ps[1]).lower() in NOMBRES else 2
    else:
        n = 1
    return f"{' '.join(ps[-n:])}, {' '.join(ps[:-n])}"


def pareja(label):
    if not label:
        return ""
    return " / ".join(jugador(j) for j in label.split(" - ") if j.strip())


def marcador(score, gano_a):
    """'{"sets":[{"side1":6,"side2":2},...]}' -> '6/2 4/6 6/0' visto desde el ganador."""
    try:
        sets = json.loads(score)["sets"] if isinstance(score, str) else (score or {}).get("sets", [])
    except (ValueError, TypeError, KeyError):
        return ""
    out = []
    for s in sets:
        a, b = s.get("side1"), s.get("side2")
        if a is None or b is None:
            continue
        out.append(f"{a}/{b}" if gano_a else f"{b}/{a}")
    return " ".join(out)


def partidos(slug):
    """Devuelve (cruces, zonas) con el formato de seguir.compactar()."""
    comunidad, evento = slug.split("/")
    datos = pedir(f"/community-events/by-slug/{comunidad}/{evento}/schedule/default")
    ms = [m for m in datos.get("matches", []) if not m.get("bye")]
    ultima = {}
    for m in ms:
        if (m.get("stageKey") or "").startswith("KNOCKOUT"):
            clave = m.get("categoryCode") or m.get("categoryName")
            ultima[clave] = max(ultima.get(clave, 0), m.get("bracketRound") or 0)
    cruces, zonas = {}, {}
    for m in ms:
        cuando = m.get("scheduledAt") or ""
        w = m.get("winnerTeamId")
        gan = 1 if w and w == m.get("sideATeamId") else 2 if w and w == m.get("sideBTeamId") else None
        terminado = (m.get("status") or "").upper() in ESTADOS_FIN
        res = marcador(m.get("score"), gan == 1) if terminado and gan else ""
        estado = ("Finalizado" if res else "WO") if terminado and gan else (
            "En curso" if (m.get("status") or "").upper() in ("IN_PROGRESS", "LIVE", "PLAYING") else "Pendiente")
        d = {
            "cat": categoria(m),
            "dia": cuando[:10] or None,
            "hora": cuando[11:16] or None,
            "sede": "",
            "estado": estado,
            "p1": pareja(m.get("sideALabel")),
            "p2": pareja(m.get("sideBLabel")),
            "res": res,
            "gan": gan,
        }
        cod = f"SL{datos.get('eventId', '')}-{m.get('categoryCode') or ''}-{m.get('id')}"
        if (m.get("stageKey") or "").startswith("KNOCKOUT"):
            atras = ultima.get(m.get("categoryCode") or m.get("categoryName"), 0) - (m.get("bracketRound") or 0)
            d["inst"] = RONDAS[atras] if 0 <= atras < len(RONDAS) else f"Ronda {m.get('bracketRound')}"
            cruces[cod] = d
        else:
            d["inst"] = "Zona"
            d["zona"] = (m.get("groupName") or "").replace("Zona", "").replace("Grupo", "").strip()
            zonas[cod] = d
    return cruces, zonas


def fechas_de_juego(slug):
    """Días con partidos programados (los cronogramas tienen días por franja)."""
    comunidad, evento = slug.split("/")
    datos = pedir(f"/community-events/by-slug/{comunidad}/{evento}/schedule/default")
    dias = {c["date"] for c in datos.get("capacity", []) if c.get("date")}
    dias |= {m["scheduledAt"][:10] for m in datos.get("matches", []) if m.get("scheduledAt")}
    return sorted(dias)


# ---------- búsqueda de torneos ----------

def en_zona(club):
    lat, lon = club.get("latitude"), club.get("longitude")
    return (lat is not None and lon is not None and ZONA["lat"][0] <= lat <= ZONA["lat"][1]
            and ZONA["lon"][0] <= lon <= ZONA["lon"][1])


def instagram(comunidad):
    try:
        c = pedir(f"/communities/by-slug/{comunidad}")
    except Exception:
        return ""
    url = ((c.get("socials") or {}).get("instagramUrl") or "").strip().rstrip("/")
    return url.rsplit("/", 1)[-1].lstrip("@") if "instagram.com" in url else ""


def nombre_corto(nombre):
    """'Distrito Padel Center Open 3' -> 'Distrito Open 3'; 'Grand Master ALPHA Padel 2026' -> 'Grand Master ALPHA'."""
    sacar = {"padel", "pádel", "center", "2026", "2027", "club"}
    ps = [p for p in nombre.split() if p.lower() not in sacar]
    corto = " ".join(ps)
    return corto if len(corto) <= 22 else " ".join(ps[:3])


def rango(desde, hasta):
    a, b = date.fromisoformat(desde[:10]), date.fromisoformat(hasta[:10])
    return [(a + timedelta(days=i)).isoformat() for i in range((b - a).days + 1)] if b >= a else [desde[:10]]


def cuando_texto(dias):
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"]
    if not dias:
        return ""
    ds = [date.fromisoformat(d) for d in dias]
    return ", ".join(str(d.day) for d in ds[:-1]) + (" y " if len(ds) > 1 else "") + \
        f"{ds[-1].day} {meses[ds[-1].month - 1]} {ds[-1].year}"


def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def buscar(conf, hoy):
    """Suma torneos nuevos de la zona y actualiza fechas/estado de los de SportLevel.

    Devuelve la lista de avisos. Modifica conf en el lugar."""
    avisos = []
    lista = pedir("/events/finder?sportId=6")
    por_slug = {c.get("slug"): c for c in conf if c.get("fuente") == "sportlevel"}
    for e in lista:
        slug = f"{e.get('communitySlug')}/{e.get('slug')}"
        if not any(en_zona(cl) for cl in e.get("clubs", [])):
            continue
        estado = {"ONGOING": "En Curso", "OPEN": "Inscripción abierta", "UPCOMING": "Próximo",
                  "FINISHED": "Finalizado", "CLOSED": "Finalizado"}.get(e.get("finderStatus"), e.get("finderStatus"))
        try:
            dias = fechas_de_juego(slug)
        except Exception:
            dias = []
        dias = dias or rango(e["startsAt"], e["endsAt"])
        c = por_slug.get(slug)
        if not c:
            org = instagram(e.get("communitySlug"))
            c = {"id": "SL-" + e.get("slug"), "fuente": "sportlevel", "slug": slug,
                 "corto": nombre_corto(e.get("name", "Torneo")), "organiza": org, "sedes_ig": [],
                 "nombre": e.get("name"), "cuando": cuando_texto(dias), "fechas": dias,
                 "sede": " · ".join(sorted({cl.get("clubName", "") for cl in e.get("clubs", [])})),
                 "categorias": sorted({f"{'Damas' if x.get('gender') == 'DAMAS' else 'Caballeros'} "
                                       f"{CATEGORIAS.get(x.get('category'), x.get('category'))}"
                                       for x in e.get("categories", [])}),
                 "estado": estado, "auto": True, "activo": False, "alta": hoy.isoformat()}
            conf.append(c)
            por_slug[slug] = c
            ig = f"@{org}" if org else "⚠️ sin Instagram del organizador (pasámelo y lo cargo)"
            avisos.append(f"- 🆕 **{c['nombre']}** (SportLevel, {c['cuando']}) · franja «{c['corto']}» · {ig}\n"
                          f"  {SITIO}/c/{slug.replace('/', '/eventos/')}")
            continue
        c["estado"] = estado
        if dias and c.get("auto"):
            c["fechas"], c["cuando"] = dias, cuando_texto(dias)
        if not c.get("organiza"):
            org = instagram(e.get("communitySlug"))
            if org:
                c["organiza"] = org
                avisos.append(f"- 📸 Instagram encontrado para **{c['nombre']}**: @{org}")
    return avisos


if __name__ == "__main__":
    import sys
    for s in sys.argv[1:]:
        cr, zo = partidos(s)
        print(s, len(cr), "cruces,", len(zo), "zonas")
        for k, v in list(cr.items())[-5:]:
            print(k, v)
