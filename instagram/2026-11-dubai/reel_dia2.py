"""Reel Dubái P1 día 2 (16avos, 11/11): remontada de Augsburger/Lebrón y caída de Di Nenno/Navarro.
Reusa el reel de la final del Mundial (instagram/2026-11-mundial/reel/reel_final.py) y cambia textos,
marcadores (por sets) y tomas. Uso: FONTS_DIR=... python3 reel_dia2.py salida.mp4"""
import pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "2026-11-mundial" / "reel"))
import reel_final as R  # noqa: E402

# rotación de tomas: el reel anterior usó cámara de TV y cancha mojada
R.TOMA_A, R.TOMA_B, R.CRUCE = "../../banco-tomas/toma04-publico.mp4", "toma2-estadio-hq.mp4", 6.6
R.CSS = R.CSS.replace(".cab .w .pt{background:#f2b21c;color:#071528}", "") + (
    ".sb .nm{font-size:46px}.sb .pt{width:92px}.cab .pt.ws{background:#f2b21c;color:#071528}")


def sb(clase, rama, g, p, sets):
    ga = sum(a > b for a, b in sets)
    wa, wb = ("row w", "row") if ga * 2 > len(sets) else ("row", "row w")
    pa = "".join(f'<div class="pt{" ws" if a > b else ""}">{a}</div>' for a, b in sets)
    pb = "".join(f'<div class="pt{" ws" if b > a else ""}">{b}</div>' for a, b in sets)
    return (f'<div class="a sb {clase}"><div class=hd><span>{rama}</span><span>Final</span></div>'
            f'<div class="{wa}"><div class=tri></div><div class=nm>{g}</div>{pa}</div>'
            f'<div class="{wb}"><div class=tri></div><div class=nm>{p}</div>{pb}</div></div>')


R.BODY = (
    '<div class="a v1"></div><div class="a v2"></div><div class="a v3"></div>'
    '<div class="a strip"><div class=x>Dubái P1</div><div class=y><span class=dot></span>16avos · Miércoles</div></div>'
    '<div class="a kick">Último P1 del año</div>'
    '<div class="a metal t1">Golpe</div>'
    '<div class="a metal t2"><span class=gold>en Dubái</span></div>'
    '<div class="a ttl">Una remontada<br><span class=gold>y una sorpresa</span></div>'
    + sb("cab s1", "Caballeros · 16avos", "Augsburger / Lebrón", "Castaño / Hernández", [(4, 6), (6, 3), (6, 3)])
    + sb("cab s2", "Caballeros · 16avos", "Di Nenno / Navarro", "Aragón / Roglán", [(6, 0), (4, 6), (2, 6)]) +
    '<div class="a dato"><b>6-0</b>Di Nenno y Paquito ganaron el primer set… y perdieron con una pareja de la previa</div>'
    f'<img class="a logo" src="data:image/png;base64,{R.LOGO}">'
    '<div class="a metal c1">Seguinos<br><span class=gold>para la próxima</span></div>'
    '<div class="a c2"><div class=pill>Seguí a <span>@surpadelstore</span></div></div>'
    '<div class="a c3">JUEVES · OCTAVOS</div>'
    + R.cruz()
)

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        R.cuadros(tmp)
        R.montar(tmp, pathlib.Path(sys.argv[1]).resolve())
    print(sys.argv[1])
