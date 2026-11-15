"""Reel Dubái P1 semis (14/11): final con tres argentinos (Alfonso/Libaak vs Augsburger/Lebrón).
Reusa reel_dia3.py (reel_final.py). Uso: FONTS_DIR=... python3 reel_dia5.py salida.mp4"""
import pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reel_dia3 as D  # noqa: E402
R, sb = D.R, D.sb

# rotación de tomas: el reel anterior usó cancha mojada y cámara de TV
R.TOMA_A, R.TOMA_B, R.CRUCE = "../../banco-tomas/toma07-tunel.mp4", "toma2-estadio-hq.mp4", 6.6

R.BODY = (
    '<div class="a v1"></div><div class="a v2"></div><div class="a v3"></div>'
    '<div class="a strip"><div class=x>Dubái P1</div><div class=y><span class=dot></span>Semis · Sábado</div></div>'
    '<div class="a kick">Último P1 del año</div>'
    '<div class="a metal t1">Final</div>'
    '<div class="a metal t2"><span class=gold>con tres argentinos</span></div>'
    '<div class="a ttl">Domingo de<br><span class=gold>revancha</span></div>'
    + sb("cab s1", "Caballeros · Semis", "Alfonso / Libaak", "De Pascual / Garrido", [(6, 1), (6, 4)])
    + sb("cab s2", "Caballeros · Semis", "Augsburger / Lebrón", "Abbate / Dal Bianco", [(6, 4), (6, 2)]) +
    '<div class="a dato"><b>2 de 2</b>Alfonso/Libaak les ganaron los dos últimos cruces: Madrid y Kuwait</div>'
    f'<img class="a logo" src="data:image/png;base64,{R.LOGO}">'
    '<div class="a metal c1">Seguinos<br><span class=gold>en la final</span></div>'
    '<div class="a c2"><div class=pill>Seguí a <span>@surpadelstore</span></div></div>'
    '<div class="a c3">DOMINGO · FINAL</div>'
    + R.cruz()
)

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        R.cuadros(tmp)
        R.montar(tmp, pathlib.Path(sys.argv[1]).resolve())
    print(sys.argv[1])
