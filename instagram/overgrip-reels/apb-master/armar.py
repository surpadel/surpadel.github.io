"""Arma el reel de campeones del APB Master con overgrip/diseno/reel_local.py (el workflow solo corre scripts de instagram/)."""
import pathlib, subprocess, sys
R = pathlib.Path(__file__).resolve().parents[3]
d = pathlib.Path(__file__).resolve().parent
subprocess.run([sys.executable, str(R / "overgrip/diseno/reel_local.py"), str(d / "spec.json"), str(d / "reel-apb-master.mp4")], check=True, cwd=str(R))
