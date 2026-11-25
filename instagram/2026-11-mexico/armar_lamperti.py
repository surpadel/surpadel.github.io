"""Arma reel_lamperti.py (homenaje a Lamperti) a partir de reel_previa.py y lo corre."""
import pathlib, re, runpy, sys
AQUI = pathlib.Path(__file__).resolve().parent
src = (AQUI / "reel_previa.py").read_text()


def rep(a, b):
    global src
    assert src.count(a) == 1, a[:60]
    src = src.replace(a, b)


rep('"""Reel previa del Mexico Major (vie 20/11): "¿Repite Augsburger?".', '"""Reel homenaje a Miguel Lamperti (mié 25/11 20:00): "Gracias, Miguelito".')
rep('TOMAS = [BANCO / "toma05-focos.mp4", BANCO / "toma09-camara-tv.mp4", RAIZ / "instagram/2026-11-mundial/reel/toma2-estadio-hq.mp4"]',
    'TOMAS = [BANCO / "toma04-publico.mp4", BANCO / "toma06-cancha-mojada.mp4", BANCO / "toma07-tunel.mp4"]')
rep('VOZ = AQUI / "previa-voz-agustin.mp3"', 'VOZ = AQUI / "lamperti-voz-agustin.mp3"')
URL = ("https://elevenlabsusercontent.com/database/workspace/616874bc8ff04f49a33e0fd2b53295f7/content_generation/"
       "rVcUQlHaUKuG3RkGHEjt/X8LEIY3u3PG22LtK9MQF/content.mp3?Expires=1795582800&KeyName=assets-cdn-key-1&Signature=aTbxXkaPNa9P9lgwbGN6XRDR5yM=")
src = re.sub(r'VOZ_URL = os.environ.get\("VOZ_URL", "[^"]*"\)', lambda m: 'VOZ_URL = os.environ.get("VOZ_URL", "' + URL + '")', src)
rep('SALIDA = AQUI / "reel-previa-mexico.mp4"', 'SALIDA = AQUI / "reel-lamperti.mp4"')
a = src.index('UNIDADES = ['); b = src.index(']', a) + 1
src = src[:a] + '''UNIDADES = ["Bahía Blanca. Empezó a los doce años, pegándole a la pared.",
            "En 2006 ya era el número uno de Argentina.",
            "Siete títulos y más de treinta finales en el circuito,",
            "contra las leyendas de cada época.",
            "En 2016 le dio a Argentina el punto del título mundial.",
            "Jugó tres eras del pádel: Pro Tour, World Padel Tour y Premier.",
            "Acapulco es su último Premier.",
            "Gracias por tanto, Miguelito."]''' + src[b:]
a = src.index("STRIP = '"); b = src.index("]\n", src.index("HTML = [")) + 2
src = src[:a] + '''STRIP = '<div class=strip><div class=a>Leyenda</div><div class=b><span class=dot></span>Último baile · Acapulco</div></div>'
HTML = [
    STRIP + '<div class="c kick" style="top:600px">Bahía Blanca · desde los 12</div>'
            '<div class="c metal" style="top:680px;font-size:210px">Gracias,<br><span class=gold>Miguelito</span></div>',
    STRIP + '<div class=card style="top:560px"><div class=k>N.º 1 de Argentina en 2006</div>'
            '<div class=v><span class=gold>7 títulos</span></div>'
            '<div class=n>y más de 30 finales en el circuito,<br>contra las leyendas de cada época</div></div>',
    STRIP + '<div class=card style="top:600px"><div class=k>Mundial 2016</div>'
            '<div class=v>El punto<br><span class=gold>del título</span></div>'
            '<div class=n>para Argentina</div></div>',
    STRIP + '<div class=card style="top:560px"><div class=k>Pro Tour · WPT · Premier</div>'
            '<div class=v><span class=gold>3 eras</span></div>'
            '<div class=n>Acapulco, su último Premier</div></div>',
    '<div class="c metal" style="top:330px;font-size:120px">Gracias por<br><span class=gold>tanto, maestro</span></div>'
    '<div class=c style="top:700px"><img class=logo src="data:image/png;base64,LOGO"><br>'
    '<span class=handle>@surpadelstore</span></div>'
    '<div class="c kick" style="top:1340px">Seguinos: el Major, al día</div>',
]
''' + src[b:]
rep("""    placas = [(0.3, U[1][1] + v), (U[2][0] + v - 0.1, U[3][1] + v), (U[4][0] + v - 0.1, U[5][1] + v),
              (U[6][0] + v - 0.1, U[7][0] + v + 0.2), (U[7][0] + v + 0.3, DUR)]""",
    """    placas = [(0.3, U[0][1] + v), (U[1][0] + v - 0.1, U[3][1] + v), (U[4][0] + v - 0.1, U[4][1] + v),
              (U[5][0] + v - 0.1, U[6][1] + v), (U[7][0] + v - 0.1, DUR)]""")
dest = AQUI / "reel_lamperti.py"
dest.write_text(src)
sys.argv = [str(dest)] + sys.argv[1:]
runpy.run_path(str(dest), run_name="__main__")
