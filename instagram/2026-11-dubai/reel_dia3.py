"""Reel Dubái P1 día 3 (octavos, 12/11): remontada de Tello/Arce y el cruce Brea vs Jensen en cuartos.
Reusa el reel de la final del Mundial (instagram/2026-11-mundial/reel/reel_final.py) y cambia textos,
marcadores (por sets) y tomas. Uso: FONTS_DIR=... python3 reel_dia3.py salida.mp4"""
import pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "2026-11-mundial" / "reel"))
import reel_final as R  # noqa: E402

# rotación de tomas: el reel anterior usó público y estadio
R.TOMA_A, R.TOMA_B, R.CRUCE = "../../banco-tomas/toma05-focos.mp4", "toma3-red-hq.mp4", 6.6
R.CSS = R.CSS.replace(".cab .w .pt{background:#f2b21c;color:#071528}", "").replace(".dam .w .pt{background:#ff6fa8;color:#16071a}", "") + (
    ".sb .nm{font-size:46px}.sb .pt{width:92px}.cab .pt.ws{background:#f2b21c;color:#071528}"
    ".dam .pt.ws{background:#ff6fa8;color:#16071a}")


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
    '<div class="a strip"><div class=x>Dubái P1</div><div class=y><span class=dot></span>Octavos · Jueves</div></div>'
    '<div class="a kick">Último P1 del año</div>'
    '<div class="a metal t1">Cuartos</div>'
    '<div class="a metal t2"><span class=gold>a la vista</span></div>'
    '<div class="a ttl">Remontada<br><span class=gold>y duelo argentino</span></div>'
    + sb("cab s1", "Caballeros · Octavos", "Tello / Arce", "Alonso / Goñi", [(3, 6), (6, 3), (6, 2)])
    + sb("dam s2", "Damas · Octavos", "Brea / Triay", "Talaván / Saiz", [(6, 3), (6, 1)]) +
    '<div class="a dato"><b>6 días</b>Brea y Jensen jugaron juntas la final del Mundial… y el viernes se cruzan en cuartos</div>'
    f'<img class="a logo" src="data:image/png;base64,{R.LOGO}">'
    '<div class="a metal c1">Seguinos<br><span class=gold>en cuartos</span></div>'
    '<div class="a c2"><div class=pill>Seguí a <span>@surpadelstore</span></div></div>'
    '<div class="a c3">VIERNES · CUARTOS</div>'
    + R.cruz()
)

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        R.cuadros(tmp)
        R.montar(tmp, pathlib.Path(sys.argv[1]).resolve())
    print(sys.argv[1])
