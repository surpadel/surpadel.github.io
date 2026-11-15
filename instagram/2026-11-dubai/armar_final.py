"""Arma las piezas de la final de Dubái (dom 15/11): historia de campeones y reel."""
import pathlib, subprocess, sys
A = pathlib.Path(__file__).resolve().parent
for cmd in ([str(A / "resultados.py"), str(A / "final.json"), str(A / "dubai-final.png")],
            [str(A / "reel_final_dubai.py"), str(A / "reel-dubai-final.mp4")]):
    subprocess.run([sys.executable] + cmd, check=True)
