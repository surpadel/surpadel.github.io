"""Arma las piezas de Dubái del viernes 13/11 (cuartos): historia de resultados y reel."""
import pathlib, subprocess, sys
A = pathlib.Path(__file__).resolve().parent
for cmd in ([str(A / "resultados.py"), str(A / "dia4.json"), str(A / "dubai-dia4.png")],
            [str(A / "reel_dia4.py"), str(A / "reel-dubai-dia4.mp4")]):
    subprocess.run([sys.executable] + cmd, check=True)
