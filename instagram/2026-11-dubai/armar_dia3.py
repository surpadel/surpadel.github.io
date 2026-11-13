"""Arma las piezas de Dubái del jueves 12/11 (octavos): historia de resultados, post de cuartos y reel."""
import pathlib, subprocess, sys
A = pathlib.Path(__file__).resolve().parent
for cmd in ([str(A / "resultados.py"), str(A / "dia3.json"), str(A / "dubai-dia3.png")],
            [str(A / "dubai_cuartos.py")],
            [str(A / "reel_dia3.py"), str(A / "reel-dubai-dia3.mp4")]):
    subprocess.run([sys.executable] + cmd, check=True)
