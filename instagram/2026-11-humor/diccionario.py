"""Carrusel de humor "Diccionario del pádel amateur" vol. 1 (1080x1350).
Uso: python3 instagram/2026-11-humor/diccionario.py <vol>  -> dic-v<vol>-1-portada.png ... dic-v<vol>-5-cierre.png (3 palabras por volumen)"""
import os, sys, pathlib
AQUI = pathlib.Path(__file__).resolve().parent
R = AQUI.parents[1]
sys.path.insert(0, str(R / "overgrip/diseno"))
os.environ.setdefault("LOGO_PNG", str(R / "marca/logo-sur-padel-transparente.png"))
import gen  # noqa
from playwright.sync_api import sync_playwright  # noqa

T = gen.THEMES["azul"]; HOT, ACC = T["hot"], T["acc"]
W, H = 1080, 1350

ENTRADAS = [
    ("¡Tuya!", "interj.", "Palabra que se grita con total seguridad un segundo antes de no moverse.",
     "—¡Tuya! <i>(La pelota pasa por el medio. Nadie se mueve.)</i>", "Ver también: <b>¡Vos!</b>, <b>¡Dale!</b>, <b>“pensé que ibas”</b>."),
    ("Último game", "loc. sust.", "Unidad de tiempo indeterminada, de entre 40 minutos y una hora y media.",
     "—Último game y nos vamos. <i>(21:30. Se fueron a las 23:10.)</i>", "Ver también: <b>“el que gana, gana”</b>, <b>“uno más”</b>."),
    ("Fue afuera", "fr. hecha", "Fallo inapelable que dicta el que estaba más lejos de la pelota.",
     "—Fue afuera. Clarito. <i>(Estaba de espaldas, atándose la zapatilla.)</i>", "Ver también: <b>“picó en la línea”</b>, <b>“repetimos”</b>."),
    ("Paleta", "s. f.", "Responsable directa de todas las derrotas. Nunca del que la usa.",
     "—Con esta no le pego a nada. <i>(Tiene tres meses.)</i>", "Ver también: <b>“es la goma”</b>, <b>“está muy dura”</b>, <b>“me compro otra”</b>."),
    ("El vidrio", "s. m.", "Rival invisible que solo juega para el equipo de enfrente.",
     "—Tocó el vidrio y me cambió todo. <i>(No tocó el vidrio.)</i>", "Ver también: <b>el sol</b>, <b>el viento</b>, <b>la pelota pinchada</b>."),
    ("Tercer tiempo", "s. m.", "Única parte del partido en la que nadie pierde y todos jugaron bárbaro.",
     "—¿Viste esa bandeja que metí? <i>(Nadie la vio.)</i>", "Ver también: <b>“la próxima los liquidamos”</b>."),
]

CSS = gen.FONTS + f"""*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:B;color:#fff;position:relative;
 background:radial-gradient(ellipse 900px 520px at 50% -60px,rgba(116,180,232,.22),transparent 70%),linear-gradient(180deg,#071528 0%,#0b1d36 60%,#071528 100%)}}
.lineas{{position:absolute;inset:0;opacity:.07;background:repeating-linear-gradient(180deg,transparent 0 58px,#fff 58px 60px)}}
.marg{{position:absolute;top:0;bottom:0;left:118px;width:3px;background:rgba(242,178,28,.35)}}
.stars{{position:absolute;right:80px;top:90px;opacity:.45}} .stars i{{position:absolute;color:{ACC};font-style:normal;font-size:22px}}
.head{{position:absolute;top:70px;left:160px;right:80px;display:flex;justify-content:space-between;font-family:BC;font-style:italic;font-weight:800;font-size:34px;letter-spacing:3px;color:{ACC}}}
.wrap{{position:absolute;left:160px;right:90px;top:200px;bottom:150px;display:flex;flex-direction:column;justify-content:center}}
.pal{{font-family:BC;font-style:italic;font-weight:800;font-size:150px;line-height:.9;text-transform:uppercase;color:#fff;text-shadow:0 8px 30px rgba(0,0,0,.6)}}
.cat{{margin-top:18px;font-size:40px;font-style:italic;color:{HOT};font-weight:600}}
.sep{{margin:34px 0 30px;height:6px;width:160px;background:{HOT};border-radius:3px}}
.def{{font-size:62px;line-height:1.25;font-weight:600}}
.ej{{margin-top:46px;background:rgba(19,41,74,.85);border-left:10px solid {ACC};border-radius:0 22px 22px 0;padding:34px 40px;font-size:48px;line-height:1.3}}
.ej i{{color:rgba(255,255,255,.65)}} .ej small{{display:block;font-family:BC;font-style:italic;font-weight:800;font-size:30px;letter-spacing:3px;color:{ACC};margin-bottom:10px}}
.ver{{margin-top:40px;font-size:40px;color:rgba(255,255,255,.75);line-height:1.35}} .ver b{{color:#fff}}
.pie{{position:absolute;bottom:56px;left:160px;right:80px;display:flex;justify-content:space-between;align-items:center;font-size:26px;letter-spacing:3px;color:rgba(255,255,255,.55)}}
.num{{font-family:BC;font-style:italic;font-weight:800;font-size:34px;color:{HOT};letter-spacing:2px}}
.logo{{width:120px;height:120px}}
"""
STARS = '<div class=stars><i style="left:0;top:0">✦</i><i style="left:42px;top:62px">✦</i><i style="left:-30px;top:112px">✦</i><i style="left:22px;top:166px">✦</i></div>'
LOGO = f'<img class=logo src="data:image/png;base64,{gen.LOGO}">'
BASE = '<div class=lineas></div><div class=marg></div>' + STARS


def portada():
    return BASE + f"""
<div class=head><span>VOL. {VOL}</span><span>EDICIÓN AMATEUR</span></div>
<div class=wrap>
 <div style="font-size:44px;font-weight:600;color:{ACC};letter-spacing:6px;text-transform:uppercase">Diccionario del</div>
 <div class=pal style="font-size:210px;margin-top:10px">Pádel<br><span style="color:{HOT}">amateur</span></div>
 <div class=sep></div>
 <div class=def style="font-size:50px">Las palabras que todos decimos en la cancha y lo que <b style="color:{HOT}">en realidad</b> significan.</div>
</div>
<div class=pie><span>@SURPADELSTORE</span><span class=num>DESLIZÁ →</span></div>"""


def entrada(i, e):
    pal, cat, d, ej, ver = e
    tam = 150 if len(pal) <= 9 else 128
    return BASE + f"""
<div class=head><span>DICCIONARIO DEL PÁDEL AMATEUR</span><span class=num style="color:{HOT}">{i}/3</span></div>
<div class=wrap>
 <div class=pal style="font-size:{tam}px">{pal}</div>
 <div class=cat>{cat}</div>
 <div class=sep></div>
 <div class=def>{d}</div>
 <div class=ej><small>EJEMPLO DE USO</small>{ej}</div>
 <div class=ver>{ver}</div>
</div>
<div class=pie><span>@SURPADELSTORE</span><span>SURPADEL.COM.AR</span></div>"""


def cierre():
    return BASE + f"""
<div class=head><span>DICCIONARIO DEL PÁDEL AMATEUR</span><span>VOL. {VOL}</span></div>
<div class=wrap style="align-items:flex-start">
 <div class=pal style="font-size:140px">¿Cuál<br><span style="color:{HOT}">nos faltó?</span></div>
 <div class=sep></div>
 <div class=def style="font-size:52px">Dejala en los comentarios: las mejores van al <b style="color:{HOT}">volumen {VOL+1}</b>.</div>
 <div class=ej style="margin-top:50px;font-size:46px"><small>Y AHORA</small>Mandáselo a tu compañero.<br><i>Él sabe cuál es la suya.</i></div>
 <div style="margin-top:60px;display:flex;align-items:center;gap:26px">{LOGO}<div style="font-size:30px;letter-spacing:4px;color:rgba(255,255,255,.75)">SEGUÍ A<br><b style="color:#fff;font-size:40px">@SURPADELSTORE</b></div></div>
</div>"""


VOL = int(sys.argv[1]) if len(sys.argv) > 1 else 1

if __name__ == "__main__":
    import unicodedata
    def slug(t): return unicodedata.normalize("NFKD", t.strip("¡!")).encode("ascii", "ignore").decode().lower().replace(" ", "-")
    tanda = ENTRADAS[(VOL - 1) * 3:(VOL - 1) * 3 + 3]
    piezas = ([(f"dic-v{VOL}-1-portada.png", portada())] + [(f"dic-v{VOL}-{i+2}-{slug(e[0])}.png", entrada(i + 1, e)) for i, e in enumerate(tanda)]
              + [(f"dic-v{VOL}-5-cierre.png", cierre())])
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        for nombre, body in piezas:
            pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>")
            pg.wait_for_timeout(250); pg.screenshot(path=str(AQUI / nombre)); print(AQUI / nombre)
        b.close()
