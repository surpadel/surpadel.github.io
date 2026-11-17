"""Arma las piezas de la semana 16-22/11 aprobadas por Nico: agenda (mié 18) y Táctica Sur n.º 2 (mar 17)."""
import subprocess, sys, pathlib
D = pathlib.Path(__file__).parent
for s in ["agenda.py", "tactica_vidrio.py"]:
    subprocess.run([sys.executable, str(D / s)], check=True)
