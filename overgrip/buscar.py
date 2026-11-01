"""Busca torneos nuevos en OverGrip y los suma al seguimiento de Sur Padel.

Una vez por día (proceso "Buscar torneos OverGrip"):
- Lee la portada de OverGrip pedida con "RSC: 1": trae todos los torneos
  (id, nombre, fechas, estado, sede, categorías) en un solo pedido.
- Los torneos próximos que todavía no están en overgrip/torneos.json se suman
  con "auto": true, un nombre corto para la franja y el Instagram del
  organizador (página de información del torneo; si no está, el del club sede).
- A los torneos automáticos les actualiza fechas y estado y los prende
  ("activo": true) desde el día anterior a la primera fecha hasta 2 días
  después de la última (o hasta que OverGrip los marque Finalizado).
  Los torneos cargados a mano (sin "auto") no se tocan.
- Avisa en el issue de avisos (llega por mail): torneos nuevos, los que
  arrancan y los que no tienen Instagram del organizador.

Uso: python3 overgrip/buscar.py [--prueba]
"""
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONF = RAIZ / "overgrip" / "torneos.json"
SITIO = "https://app.overgrip.com.ar"
ARG = timezone(timedelta(hours=-3))
CAB = {"RSC": "1", "User-Agent": "SurPadel/1.0 (+https://surpadel.com.ar)"}
NO_SON_ORGANIZADORES = {"overgripapp", "surpadelstore", "p", "reel", "explore", "stories"}
MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7,
         "ago": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dic": 12}


def bajar(ruta):
    req = urllib.request.Request(SITIO + ruta, headers=CAB)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def arreglo(texto, clave):
    """Recorta el JSON que sigue a "clave": respetando comillas y anidamiento."""
    k = texto.find(f'"{clave}":')
    if k < 0:
        raise ValueError(f"No se encontró {clave}")
    k += len(clave) + 3
    abre = texto[k]
    cierra = {"[": "]", "{": "}"}[abre]
    nivel, en_texto, j = 0, False, k
    while j < len(texto):
        c = texto[j]
        if en_texto:
            if c == "\\":
                j += 1
            elif c == '"':
                en_texto = False
        elif c == '"':
            en_texto = True
        elif c == abre:
            nivel += 1
        elif c == cierra:
            nivel -= 1
            if nivel == 0:
                break
        j += 1
    return json.loads(texto[k:j + 1])


def fechas(cuando):
    """'13 al 15 y 21 al 23 nov 2026' -> ['2026-11-13', ..., '2026-11-23'] (solo días de juego)."""
    texto = cuando.lower()
    anio = int((re.findall(r"\b(20\d\d)\b", texto) or [date.today().year])[-1])
    items, rango = [], False  # cada item: [día, mes, viene_de_rango]
    for tok in re.findall(r"\b20\d\d\b|\d{1,2}|[a-záéíóú]+", texto):
        if len(tok) == 4 and tok.isdigit():
            continue
        if tok.isdigit():
            items.append([int(tok), None, rango])
            rango = False
        elif tok == "al":
            rango = True
        elif tok in MESES:
            for it in reversed(items):
                if it[1] is not None:
                    break
                it[1] = MESES[tok]
    out = []
    for it in items:
        if it[1] is None:
            continue
        d = date(anio, it[1], it[0])
        if it[2] and out:
            x = out[-1] + timedelta(days=1)
            while x < d:
                out.append(x)
                x += timedelta(days=1)
        out.append(d)
    return [d.isoformat() for d in sorted(set(out))]


def nombre_corto(t):
    """Nombre para la franja de las historias: 'Tremendas 3° Edición' -> 'Tremendas 3°'."""
    n = re.split(r"\s+[-—–]\s+", t["nombre"])[0]
    n = re.sub(r"\b(torneo|abierto|open|edici[oó]n|20\d\d)\b", "", n, flags=re.I)
    n = re.sub(r"\s+", " ", n).strip(" -—")
    if not n or len(n) > 16:
        n = re.sub(r"\s*20\d\d\s*", " ", t.get("circuito") or t["nombre"]).strip()
    palabras = [w.capitalize() if w.isupper() and len(w) > 4 else w for w in n.split()]
    return " ".join(palabras)[:18]


def instagrams(texto):
    out = []
    for u in re.findall(r"instagram\.com/([A-Za-z0-9_.]+)", texto):
        u = u.strip(".").lower()
        if u not in NO_SON_ORGANIZADORES and u not in out:
            out.append(u)
    return out


def buscar_instagram(tid):
    """Instagram del organizador: el de la ficha del torneo; si no hay, el del club sede."""
    try:
        info = bajar(f"/torneos/{tid}/informacion")
    except Exception as e:
        print(f"{tid}: no se pudo leer la información ({e})")
        return "", []
    propios = instagrams(info)
    clubes = []
    for cu in dict.fromkeys(re.findall(r"/clubes/(CU\w+)", info)):
        try:
            clubes += [x for x in instagrams(bajar(f"/clubes/{cu}")) if x not in clubes]
        except Exception:
            pass
    if propios:
        return propios[0], [x for x in clubes if x != propios[0]]
    if clubes:
        return clubes[0], clubes[1:]
    return "", []


def torneos_overgrip():
    grupos = arreglo(bajar("/"), "grupos")
    out = {}
    for g in grupos:
        for t in g.get("torneos", []):
            t["grupo"] = g.get("estado")
            out[t["id"]] = t
    return out


def main():
    prueba = "--prueba" in sys.argv
    hoy = datetime.now(ARG).date()
    conf = json.loads(CONF.read_text()) if CONF.exists() else []
    por_id = {t["id"]: t for t in conf}
    og = torneos_overgrip()
    avisos = []

    for tid, t in og.items():
        dias = fechas(t.get("cuando") or "")
        if tid in por_id or not dias or t["grupo"] == "Finalizado":
            continue
        if date.fromisoformat(dias[0]) <= hoy:
            continue  # ya empezó: solo se suman torneos próximos
        org, sedes = buscar_instagram(tid)
        nuevo = {"id": tid, "corto": nombre_corto(t), "organiza": org, "sedes_ig": sedes,
                 "nombre": t["nombre"], "cuando": t["cuando"], "fechas": dias,
                 "sede": " · ".join(x for x in (t.get("sede"), t.get("localidad")) if x),
                 "categorias": t.get("categorias", []), "estado": t["grupo"],
                 "auto": True, "activo": False, "alta": hoy.isoformat()}
        conf.append(nuevo)
        por_id[tid] = nuevo
        ig = f"@{org}" if org else "⚠️ sin Instagram del organizador (pasámelo y lo cargo)"
        avisos.append(f"- 🆕 **{t['nombre']}** ({t['cuando']}) · franja «{nuevo['corto']}» · {ig}\n"
                      f"  {SITIO}/torneos/{tid}")

    for c in conf:
        if not c.get("auto"):
            continue
        t = og.get(c["id"])
        if t:
            c["estado"] = t["grupo"]
            dias = fechas(t.get("cuando") or "")
            if dias:
                c["fechas"], c["cuando"] = dias, t["cuando"]
        if not c.get("fechas"):
            continue
        desde = date.fromisoformat(c["fechas"][0]) - timedelta(days=1)
        hasta = date.fromisoformat(c["fechas"][-1]) + timedelta(days=2)
        activo = desde <= hoy <= hasta and c.get("estado") != "Finalizado"
        if activo and not c.get("activo"):
            avisos.append(f"- ▶️ Arranca el seguimiento de **{c['nombre']}** ({c['cuando']})"
                          + ("" if c.get("organiza") else " · ⚠️ sigue sin Instagram del organizador"))
        if not activo and c.get("activo"):
            avisos.append(f"- ⏹️ Terminó el seguimiento de **{c['nombre']}**")
        c["activo"] = activo

    if prueba:
        print(json.dumps(conf, ensure_ascii=False, indent=1))
        print("\n".join(avisos))
        return
    CONF.write_text(json.dumps(conf, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(og)} torneos en OverGrip; {sum(1 for c in conf if c.get('activo'))} activos")
    if avisos:
        sys.path.insert(0, str(Path(__file__).parent))
        from publicar import avisar
        avisar([f"**Torneos OverGrip · {hoy.strftime('%d/%m')}**"] + avisos)


if __name__ == "__main__":
    main()
