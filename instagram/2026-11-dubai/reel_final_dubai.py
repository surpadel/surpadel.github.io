"""Reel Dubái P1 final (15/11): Augsburger/Lebrón campeones 7/6 5/7 6/3 ante Alfonso/Libaak.
Reusa reel_dia3.py (reel_final.py). Uso: FONTS_DIR=... python3 reel_final_dubai.py salida.mp4"""
import pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reel_dia3 as D  # noqa: E402
R, sb = D.R, D.sb

# rotación de tomas: el reel anterior usó túnel y estadio; confeti para campeones
R.TOMA_A, R.TOMA_B, R.CRUCE = "../../banco-tomas/toma08-confeti.mp4", "toma3-red-hq.mp4", 6.6

R.BODY = (
    '<div class="a v1"></div><div class="a v2"></div><div class="a v3"></div>'
    '<div class="a strip"><div class=x>Dubái P1</div><div class=y><span class=dot></span>Final · Domingo</div></div>'
    '<div class="a kick">Último P1 del año</div>'
    '<div class="a metal t1">Augsburger</div>'
    '<div class="a metal t2"><span class=gold>campeón en Dubái</span></div>'
    '<div class="a ttl">Final de<br><span class=gold>tres sets</span></div>'
    + sb("cab s1", "Caballeros · Final", "Augsburger / Lebrón", "Alfonso / Libaak", [(7, 6), (5, 7), (6, 3)])
    + sb("dam s2", "Damas · Final", "Fernández / Calvo", "Josemaría / González", [(7, 5), (6, 1)]) +
    '<div class="a dato"><b>2.º título</b>del año para Augsburger y Lebrón. Alfonso y Libaak, primera final juntos</div>'
    f'<img class="a logo" src="data:image/png;base64,{R.LOGO}">'
    '<div class="a metal c1">Seguinos<br><span class=gold>en México</span></div>'
    '<div class="a c2"><div class=pill>Seguí a <span>@surpadelstore</span></div></div>'
    '<div class="a c3">MEXICO MAJOR · DESDE EL 23/11</div>'
    + R.cruz()
)

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        R.cuadros(tmp)
        R.montar(tmp, pathlib.Path(sys.argv[1]).resolve())
    print(sys.argv[1])
