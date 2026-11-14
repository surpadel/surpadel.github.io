"""Reel Dubái P1 cuartos (13/11): Jensen/Icardo eliminan a las número 1 y Alfonso/Libaak ganan en el tie-break.
Reusa instagram/2026-11-mundial/reel/reel_final.py igual que reel_dia3.py. Uso: FONTS_DIR=... python3 reel_dia4.py salida.mp4"""
import pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reel_dia3 as D  # noqa: E402  (trae R = reel_final con CSS y sb por sets)
R, sb = D.R, D.sb

# rotación de tomas: el reel anterior usó focos y red
R.TOMA_A, R.TOMA_B, R.CRUCE = "../../banco-tomas/toma06-cancha-mojada.mp4", "../../banco-tomas/toma09-camara-tv.mp4", 6.6

R.BODY = (
    '<div class="a v1"></div><div class="a v2"></div><div class="a v3"></div>'
    '<div class="a strip"><div class=x>Dubái P1</div><div class=y><span class=dot></span>Cuartos · Viernes</div></div>'
    '<div class="a kick">Último P1 del año</div>'
    '<div class="a metal t1">Semis</div>'
    '<div class="a metal t2"><span class=gold>con acento argentino</span></div>'
    '<div class="a ttl">Golpe a las<br><span class=gold>número 1</span></div>'
    + sb("dam s1", "Damas · Cuartos", "Jensen / Icardo", "Brea / Triay", [(6, 3), (3, 6), (6, 1)])
    + sb("cab s2", "Caballeros · Cuartos", "Alfonso / Libaak", "Bautista / Bergamini", [(4, 6), (6, 3), (7, 6)]) +
    '<div class="a dato"><b>Semis</b>Augsburger/Lebrón vs. Abbate/Dal Bianco: ya hay argentino asegurado en la final</div>'
    f'<img class="a logo" src="data:image/png;base64,{R.LOGO}">'
    '<div class="a metal c1">Seguinos<br><span class=gold>en semis</span></div>'
    '<div class="a c2"><div class=pill>Seguí a <span>@surpadelstore</span></div></div>'
    '<div class="a c3">SÁBADO · SEMIS</div>'
    + R.cruz()
)

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        R.cuadros(tmp)
        R.montar(tmp, pathlib.Path(sys.argv[1]).resolve())
    print(sys.argv[1])
