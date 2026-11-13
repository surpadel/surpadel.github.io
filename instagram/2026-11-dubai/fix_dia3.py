"""12/11: Campagnolo no es argentino (Nico). Corrige dia3.json y dubai_cuartos.py y rearma la historia y el post."""
import json, pathlib, subprocess, sys
A = pathlib.Path(__file__).resolve().parent
j = A / "dia3.json"
d = json.loads(j.read_text())
d["bloques"][0]["resumen"] = "5 a cuartos"
d["bloques"][0]["nota"] = "Sanyo cayó con Stupa"
j.write_text(json.dumps(d, ensure_ascii=False, indent=1))
p = A / "dubai_cuartos.py"
s = p.read_text()
s = s.replace('cruce("<em>Dal Bianco</em> / Abbate", "<em>Campagnolo</em> / Momo", duelo=True)',
              'cruce("<em>Dal Bianco</em> / Abbate", "Campagnolo / Momo")')
s = s.replace("Tres cruces entre argentinos:", "Dos cruces entre argentinos:")
p.write_text(s)
for cmd in ([str(A / "resultados.py"), str(j), str(A / "dubai-dia3-v2.png")], [str(A / "dubai_cuartos.py")]):
    subprocess.run([sys.executable] + cmd, check=True)
