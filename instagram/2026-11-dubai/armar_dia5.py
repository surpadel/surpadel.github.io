"""Arma las piezas de Dubái del sábado 14/11 (semis): historia de resultados y reel."""
import pathlib, subprocess, sys
A = pathlib.Path(__file__).resolve().parent
for cmd in ([str(A / "resultados.py"), str(A / "dia5.json"), str(A / "dubai-dia5.png")],
            [str(A / "reel_dia5.py"), str(A / "reel-dubai-dia5.mp4")]):
    subprocess.run([sys.executable] + cmd, check=True)
