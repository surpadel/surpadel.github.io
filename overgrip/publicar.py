"""Publica en Instagram (por Buffer) las historias de OverGrip pendientes.

Lee overgrip/datos/historias.json (lo escribe historias.py) y, para cada
historia con "publicada": false:

- Controles antes de publicar: la imagen existe, los partidos siguen
  terminados en OverGrip con el MISMO resultado (si lo corrigieron, no sale),
  las dos parejas están completas y el marcador tiene formato válido.
  Si algo no cierra, queda como BORRADOR en Buffer para que Nico la revise.
- Octavos, cuartos (y 16avos): se publican solas, con etiquetas en la imagen.
- Semifinales ("A la final") y finales ("Los campeones"): van como
  RECORDATORIO de Buffer: llega el aviso al celu y Nico publica desde
  Instagram agregando el sticker de mención.
- Tope de historias automáticas por corrida y horario de silencio
  (00:30 a 8:00): en silencio no publica nada, queda para la mañana.
- Siempre al canal de Instagram de Sur Padel y solo como historia:
  el código no puede publicar en otro canal ni en el feed.
- Avisa a Nico en un issue del repositorio (llega por mail).

Necesita el secreto BUFFER_API_KEY. Sin él no hace nada.

Uso:
  python3 overgrip/publicar.py            -> publica lo pendiente
  python3 overgrip/publicar.py --prueba   -> muestra qué haría, sin publicar
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "overgrip" / "datos"
HIST = DATOS / "historias.json"
SALIDA = RAIZ / "instagram" / "overgrip"
ARG = timezone(timedelta(hours=-3))

API = "https://api.buffer.com"
CANAL_INSTAGRAM = "6ae29db22f1f5ed648070dca"  # @surpadelstore, fijo a propósito
OVERGRIP = "overgripapp"
TOPE_POR_CORRIDA = 4
SILENCIO = ((0, 30), (8, 0))  # de 00:30 a 08:00 no se publica
CON_STICKER = {"Semifinal", "Final"}  # van como recordatorio
MARCADOR = re.compile(r"^\d{1,2}/\d{1,2}( \d{1,2}/\d{1,2}){1,2}$")


def leer(p, vacio):
    return json.loads(p.read_text()) if p.exists() else vacio


def en_silencio(ahora):
    (h1, m1), (h2, m2) = SILENCIO
    t = (ahora.hour, ahora.minute)
    return (h1, m1) <= t < (h2, m2)


def problemas(h):
    """Lista de motivos para NO publicar sola esta historia (vacía = todo bien)."""
    out = []
    if not (SALIDA / h["archivo"]).exists():
        out.append("no está la imagen")
    codigos = h.get("codigos") or {}
    if not codigos:
        out.append("historia sin datos de partidos (formato viejo)")
    datos = leer(DATOS / f"{h['torneo']}.json", {}).get("cruces", {})
    for cod, res in codigos.items():
        p = datos.get(cod)
        if not p:
            out.append(f"{cod}: no figura en OverGrip")
            continue
        if p["estado"] != "Finalizado":
            out.append(f"{cod}: ahora figura '{p['estado']}'")
        if p["res"] != res:
            out.append(f"{cod}: el resultado cambió ({res} → {p['res']})")
        if not MARCADOR.match(p["res"] or ""):
            out.append(f"{cod}: marcador raro '{p['res']}'")
        if not p["p1"].strip() or not p["p2"].strip() or p["gan"] not in (1, 2):
            out.append(f"{cod}: falta una pareja o el ganador")
    return out


def entrada(h, modo):
    """Arma el input de createPost. modo: auto | recordatorio | borrador."""
    etiquetas = [{"handle": OVERGRIP, "x": 0.5, "y": 0.93}]
    if h.get("organiza"):
        etiquetas.insert(0, {"handle": h["organiza"], "x": 0.5, "y": 0.9})
    imagen = {"url": h["url"], "metadata": {"altText": h.get("alt") or "Resultados del torneo",
                                            "userTags": etiquetas}}
    inp = {
        "channelId": CANAL_INSTAGRAM,
        "schedulingType": "notification" if modo == "recordatorio" else "automatic",
        "mode": "shareNow",
        "assets": [{"image": imagen}],
        "metadata": {"instagram": {"type": "story", "shouldShareToFeed": False}},
    }
    if modo == "recordatorio":
        inp["mode"] = "customScheduled"
        inp["dueAt"] = (datetime.now(timezone.utc) + timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    if modo == "borrador":
        inp["saveToDraft"] = True
        inp["mode"] = "addToQueue"
    # Candado: solo Instagram de Sur Padel y solo historias.
    assert inp["channelId"] == CANAL_INSTAGRAM and inp["metadata"]["instagram"]["type"] == "story"
    return inp


ENUMS = {"schedulingType", "mode", "type"}


def gql(v, clave=None):
    """Convierte un dict de Python en literal GraphQL (enums sin comillas)."""
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k}: {gql(x, k)}" for k, x in v.items()) + "}"
    if isinstance(v, list):
        return "[" + ", ".join(gql(x, clave) for x in v) + "]"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if clave in ENUMS:
        return v
    return json.dumps(v, ensure_ascii=False)


def crear(inp, clave):
    q = ("mutation { createPost(input: " + gql(inp) + ") { "
         "... on PostActionSuccess { post { id status } } "
         "... on MutationError { message } } }")
    req = urllib.request.Request(API, data=json.dumps({"query": q}).encode(),
                                 headers={"Authorization": f"Bearer {clave}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read().decode())
    if resp.get("errors"):
        raise RuntimeError(resp["errors"][0].get("message", "error de Buffer"))
    res = resp["data"]["createPost"]
    if "post" not in res:
        raise RuntimeError(res.get("message", "Buffer no creó la historia"))
    return res["post"]


def avisar(lineas):
    """Comentario en el issue de avisos (GitHub manda mail). Sin token, solo imprime."""
    texto = "\n".join(lineas)
    print(texto)
    tok, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not tok or not repo:
        return
    base = f"https://api.github.com/repos/{repo}/issues"
    cab = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}

    def pedir(url, datos=None, metodo="GET"):
        r = urllib.request.Request(url, data=json.dumps(datos).encode() if datos else None,
                                   headers=cab, method=metodo)
        with urllib.request.urlopen(r, timeout=30) as x:
            return json.loads(x.read().decode())

    try:
        abiertos = pedir(base + "?labels=avisos-instagram&state=open")
        if abiertos:
            pedir(abiertos[0]["comments_url"], {"body": texto}, "POST")
        else:
            pedir(base, {"title": "Avisos de historias de Instagram",
                         "body": "Acá se avisa cada historia que sale o queda para revisar.\n\n" + texto,
                         "labels": ["avisos-instagram"]}, "POST")
    except Exception as e:  # el aviso nunca frena la publicación
        print("No se pudo avisar:", e)


def main():
    prueba = "--prueba" in sys.argv
    clave = os.environ.get("BUFFER_API_KEY", "")
    if not clave and not prueba:
        print("Sin BUFFER_API_KEY: no se publica nada.")
        return
    hist = leer(HIST, [])
    pend = [h for h in hist if not h.get("publicada")]
    if not pend:
        print("Nada pendiente")
        return
    ahora = datetime.now(ARG)
    if en_silencio(ahora) and not prueba:
        print("Horario de silencio: queda para la mañana")
        return
    autos, lineas = 0, []
    for h in pend:
        motivos = problemas(h)
        if motivos:
            modo = "borrador"
        elif h.get("inst") in CON_STICKER:
            modo = "recordatorio"
        elif autos < TOPE_POR_CORRIDA:
            modo = "auto"
        else:
            continue  # pasa a la próxima corrida
        inp = entrada(h, modo)
        if prueba:
            print(f"[prueba] {h['archivo']} -> {modo} {motivos or ''}")
            print("   " + gql(inp)[:300])
            continue
        try:
            post = crear(inp, clave)
        except Exception as e:
            lineas.append(f"- ⚠️ No salió {h['archivo']}: {e}")
            continue
        h["en_buffer"] = post["id"]
        h["modo"] = modo
        h["publicada"] = True  # ya está en Buffer (sale sola, recordatorio o borrador): no se repite
        if modo == "auto":
            autos += 1
        cartel = {"auto": "✅ Publicada", "recordatorio": "🔔 Lista para publicar con sticker (aviso de Buffer)",
                  "borrador": "📝 Quedó como borrador para revisar"}[modo]
        extra = f" — {'; '.join(motivos)}" if motivos else ""
        lineas.append(f"- {cartel}: {h.get('alt', h['archivo'])[:140]}{extra}\n\n  ![]({h['url']})")
    if prueba:
        return
    HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=1))
    if lineas:
        avisar([f"**{ahora.strftime('%d/%m %H:%M')}**"] + lineas)


if __name__ == "__main__":
    main()
