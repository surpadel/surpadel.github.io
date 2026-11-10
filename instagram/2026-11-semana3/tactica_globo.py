"""Reel 'Táctica Sur n.º 1: El globo no es para respirar' (1080x1920, ~25 s, todo con código, USD 0).

Cancha completa vista desde arriba (nosotros abajo, rivales arriba), pelota con sombra para mostrar la altura.
Escenas: gancho (globo corto → remate), 1 cuándo, 2 adónde, 3 después (subir a la red), cierre.
Uso: FONTS_DIR=... LOGO_PNG=... python3 instagram/2026-11-semana3/tactica_globo.py [--fps 30] [--solo-tapa]
Salidas: tactica-sur-1-globo.mp4 y tactica-sur-1-globo-tapa.jpg en esta carpeta.
"""
import os, sys, pathlib, shutil, subprocess, tempfile
R = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "overgrip/diseno"))
os.environ.setdefault("LOGO_PNG", str(R / "marca/logo-sur-padel-transparente.png"))
import gen
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
NOMBRE = "tactica-sur-1-globo"
DUR = 25.0
t = gen.THEMES["azul"]
FONDO = gen.b64(R / "marca/fondos/fondo-05-focos.jpg")

# cancha: 10 x 20 m, 56 px por metro
M = 56
CW, CH = 10 * M, 20 * M

HTML = gen.FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:B;color:#fff;background:#050b16;position:relative}}
#bg{{position:absolute;inset:-40px;background:url(data:image/jpeg;base64,{FONDO}) center/cover;filter:brightness(.55) saturate(1.1)}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,11,22,.92) 0%,rgba(5,11,22,.55) 30%,rgba(5,11,22,.55) 75%,rgba(5,11,22,.95) 100%)}}
.top{{position:absolute;left:0;right:0;top:90px;display:flex;flex-direction:column;align-items:center}}
.strip{{display:flex;height:62px;font-weight:700;letter-spacing:3px;text-transform:uppercase;font-size:24px;box-shadow:0 8px 30px rgba(0,0,0,.5)}}
.strip .a{{background:{t['hot']};color:#071528;display:flex;align-items:center;padding:0 40px 0 22px;font-family:BC;font-style:italic;font-weight:800;font-size:34px;clip-path:polygon(0 0,100% 0,92% 100%,0 100%)}}
.strip .b{{background:rgba(7,21,40,.92);border:1px solid rgba(255,255,255,.18);display:flex;align-items:center;padding:0 26px 0 30px;margin-left:-14px}}
.tt{{position:absolute;left:60px;right:60px;top:180px;text-align:center;font-family:BC;font-weight:800;font-style:italic;text-transform:uppercase;line-height:.92;font-size:96px;
 color:#fff;text-shadow:0 6px 24px rgba(0,0,0,.8);transition:none}}
.tt .g{{color:{t['hot']}}} .tt .r{{color:#ff4d4d}}
.tt small{{display:block;font-family:B;font-style:normal;font-weight:600;text-transform:none;font-size:36px;line-height:1.3;margin-top:16px;color:#dfe9f5}}
.num{{display:inline-block;background:{t['hot']};color:#071528;font-family:BC;font-style:italic;font-weight:800;font-size:40px;padding:2px 22px;margin-bottom:14px;letter-spacing:2px}}
#court{{position:absolute;left:{(1080-CW)//2}px;top:560px;filter:drop-shadow(0 30px 60px rgba(0,0,0,.7))}}
.close{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;background:rgba(5,11,22,.82);opacity:0}}
.close img{{width:220px;filter:drop-shadow(0 8px 30px rgba(0,0,0,.6))}}
.close .c1{{font-family:BC;font-style:italic;font-weight:800;font-size:86px;text-transform:uppercase;text-align:center;line-height:.95}}
.close .c1 span{{color:{t['hot']}}}
.close .c2{{font-size:38px;font-weight:600;color:#dfe9f5;text-align:center}}
.close .c3{{font-size:26px;letter-spacing:4px;color:rgba(255,255,255,.65)}}
.won{{position:absolute;left:0;right:0;top:790px;text-align:center;font-family:BC;font-style:italic;font-weight:800;font-size:118px;line-height:.9;text-transform:uppercase;opacity:0;
 color:#fff;text-shadow:0 8px 30px rgba(0,0,0,.9),0 0 40px rgba(0,0,0,.7)}}
.won span{{color:{t['hot']}}}
.stat{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(5,11,22,.86);opacity:0}}
.stat .big{{font-family:BC;font-style:italic;font-weight:800;font-size:250px;line-height:.85;color:{t['hot']};text-shadow:0 10px 40px rgba(0,0,0,.7)}}
.stat .mid{{font-family:BC;font-style:italic;font-weight:800;font-size:84px;text-transform:uppercase;text-align:center;line-height:.95;margin-top:10px}}
.stat .mid span{{color:{t['acc']}}}
.stat .src{{margin-top:34px;font-size:26px;color:rgba(255,255,255,.6);text-align:center}}
.brand{{position:absolute;bottom:70px;left:0;right:0;text-align:center;font-size:24px;letter-spacing:4px;color:rgba(255,255,255,.6)}}
"""

BODY = f"""<div id=bg></div><div class=shade></div>
<div class=top><div class=strip><div class=a>TÁCTICA SUR</div><div class=b>N.º 1 · El globo</div></div></div>
<div class=tt id=tt></div>
<svg id=court width={CW} height={CH} viewBox="0 0 {CW} {CH}">
 <defs>
  <linearGradient id=deep x1=0 y1=0 x2=0 y2=1><stop offset=0 stop-color="{t['hot']}" stop-opacity=.65 /><stop offset=1 stop-color="{t['hot']}" stop-opacity=.15 /></linearGradient>
 </defs>
 <rect width={CW} height={CH} fill="{t['court2']}"/>
 <rect id=zdeep x=0 y=0 width={CW} height={2.6*M} fill="url(#deep)" opacity=0 />
 <rect id=zno x=0 y={4.5*M} width={CW} height={4.2*M} fill="#ff4d4d" opacity=0 />
 <text id=tdeep x={CW/2} y={1.6*M} text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=46 fill="#071528" opacity=0>ACÁ, AL FONDO</text>
 <text id=tno x={CW/2} y={6.9*M} text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=50 fill="#fff" opacity=0>CORTO = REMATE</text>
 <rect x=3 y=3 width={CW-6} height={CH-6} fill=none stroke="#fff" stroke-width=5 />
 <line x1=0 y1={3.05*M} x2={CW} y2={3.05*M} stroke="#fff" stroke-width=5 />
 <line x1=0 y1={16.95*M} x2={CW} y2={16.95*M} stroke="#fff" stroke-width=5 />
 <line x1={CW/2} y1={3.05*M} x2={CW/2} y2={16.95*M} stroke="#fff" stroke-width=5 />
 <line x1=-20 y1={10*M} x2={CW+20} y2={10*M} stroke="#fff" stroke-width=14 stroke-dasharray="7 7" />
 <text x={CW-10} y={10*M-14} text-anchor=end font-family=B font-weight=700 font-size=20 fill="rgba(255,255,255,.7)" style="letter-spacing:3px">RED</text>
 <text x=14 y={CH-16} font-family=B font-weight=700 font-size=22 fill="{t['acc']}" style="letter-spacing:3px">VOS Y TU COMPAÑERO</text>
 <text x=14 y=34 font-family=B font-weight=700 font-size=22 fill="rgba(255,120,120,.95)" style="letter-spacing:3px">RIVALES</text>
 <path id=trail fill=none stroke="#fff" stroke-width=5 stroke-dasharray="14 12" opacity=0 />
 <g id=players></g>
 <ellipse id=shadow rx=16 ry=9 fill="rgba(0,0,0,.45)" opacity=0 />
 <circle id=ball r=15 fill="#e8f25a" stroke="#fff" stroke-width=3 opacity=0 />
 <g id=boom opacity=0><circle r=88 fill="rgba(255,77,77,.15)" stroke="#ff4d4d" stroke-width=8 /><text y=14 text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=42 fill="#ff4d4d">¡PUM!</text></g>
 <g id=up opacity=0></g>
</svg>
<div class=won id=won>¡Y ya ganaste<br><span>la red!</span></div>
<div class=stat id=stat><div class=big>8 de 10</div><div class=mid>puntos se ganan<br><span>desde la red</span></div><div class=src>Estudios de pádel profesional</div></div>
<div class=close id=close><img src="data:image/png;base64,{gen.LOGO}">
 <div class=c1>Guardalo para tu<br><span>próximo partido</span></div>
 <div class=c2>Cada semana, una Táctica Sur.<br>Seguinos para no perderte la próxima.</div>
 <div class=c3>@SURPADELSTORE</div></div>
<div class=brand id=brand>@SURPADELSTORE · SURPADEL.COM.AR</div>
"""

JS = """
const M=%(M)d, CW=%(CW)d, CH=%(CH)d, HOT='%(HOT)s', ACC='%(ACC)s';
const $=id=>document.getElementById(id);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const seg=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const ease=x=>x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2;
const lerp=(a,b,k)=>a+(b-a)*k;
const fade=(t,a,b,f=.35)=>Math.min(seg(t,a,a+f),1-seg(t,b-f,b));
function P(x,y){return [x*M,y*M];}
const TITLES=[
 [0,3.6,'Si el globo queda corto,<br><span class=r>te lo comen</span><small>El rival remata desde la red</small>'],
 [3.6,11.4,'<div class=num>1 · PROFUNDO</div><br>Que pique<br><span class=g>al fondo</span><small>Cerca de la pared, lejos de la red rival</small>'],
 [11.4,19.2,'<div class=num>2 · Y SUBÍ</div><br>Mientras vuela,<br><span class=g>subí a la red</span><small>Con tu compañero, juntos: el globo es para recuperar la red</small>'],
];
let lastTitle=-1;
function players(ours, rivals, hlR){
  let s='';
  for(const [x,y] of ours){const [px,py]=P(x,y);s+=`<circle cx=${px} cy=${py} r=30 fill="${HOT}" stroke="#071528" stroke-width=6 />`;}
  for(const [x,y] of rivals){const [px,py]=P(x,y);
    if(hlR>0) s+=`<circle cx=${px} cy=${py} r=${44+10*hlR} fill=none stroke="#ff4d4d" stroke-width=5 opacity=${hlR} />`;
    s+=`<circle cx=${px} cy=${py} r=30 fill="#ff4d4d" stroke="#2a0b0b" stroke-width=6 />`;}
  $('players').innerHTML=s;
}
function ball(a,b,h,k,show){ // de a a b, altura máxima h (m), avance k
  const x=lerp(a[0],b[0],k), y=lerp(a[1],b[1],k), z=h*4*k*(1-k);
  const [px,py]=P(x,y);
  $('shadow').setAttribute('cx',px); $('shadow').setAttribute('cy',py); $('shadow').setAttribute('opacity',show);
  $('ball').setAttribute('cx',px); $('ball').setAttribute('cy',py-z*M*0.8); $('ball').setAttribute('r',15+z*2.2); $('ball').setAttribute('opacity',show);
}
function trail(a,b,h,k,show){
  let d='';const n=30;
  for(let i=0;i<=n;i++){const q=i/n*k;const x=lerp(a[0],b[0],q),y=lerp(a[1],b[1],q),z=h*4*q*(1-q);const [px,py]=P(x,y);d+=(i?'L':'M')+px+' '+(py-z*M*0.8);}
  $('trail').setAttribute('d',d); $('trail').setAttribute('opacity',show*0.8);
}
window.render=function(T){
  // fondo con zoom lento
  $('bg').style.transform=`scale(${1+T*0.004})`;
  // títulos
  let ti=-1; for(let i=0;i<TITLES.length;i++) if(T>=TITLES[i][0]&&T<TITLES[i][1]) ti=i;
  if(ti!==lastTitle){ $('tt').innerHTML= ti>=0?TITLES[ti][2]:''; lastTitle=ti; }
  if(ti>=0){ const [a,b]=TITLES[ti]; const o=fade(T,a,b,.3); $('tt').style.opacity=o; $('tt').style.transform=`translateY(${(1-seg(T,a,a+.35))*30}px)`; }
  else $('tt').style.opacity=0;
  // posiciones base
  let ours=[[3,16.6],[7,17]], riv=[[3,7.8],[7,7.8]], hl=0;
  ['zdeep','tdeep','zno','tno'].forEach(i=>$(i).setAttribute('opacity',0));
  $('boom').setAttribute('opacity',0); $('trail').setAttribute('opacity',0);
  let bshow=0;
  if(T<3.6){ // gancho: globo corto y remate
    const A=[3,16.4], B=[4,7.2], C=[6.5,17.5];
    if(T<1.6){ const k=ease(seg(T,0.1,1.6)); ball(A,B,3.2,k,1); trail(A,B,3.2,k,1); }
    else { const k=seg(T,1.6,2.2); ball(B,C,0.6,k,1); trail(A,B,3.2,1,1);
      const [bx,by]=P(4,7.2); $('boom').setAttribute('transform',`translate(${bx},${by}) scale(${0.6+0.6*seg(T,1.6,1.9)})`);
      $('boom').setAttribute('opacity',fade(T,1.6,3.5,.2)); }
    bshow=1;
  } else if(T<11.4){ // profundo sí, corto no
    $('zdeep').setAttribute('opacity',0.9*seg(T,3.8,4.4)); $('tdeep').setAttribute('opacity',seg(T,4.0,4.6));
    $('zno').setAttribute('opacity',0.35*seg(T,4.8,5.4)); $('tno').setAttribute('opacity',seg(T,5.0,5.6));
    const A=[3,16.4], B=[2.2,1.3]; const k=ease(seg(T,6.2,9.6));
    if(T>6.0){ ball(A,B,7.5,k,1); trail(A,B,7.5,k,1); bshow=1; }
    const kr=ease(seg(T,7.0,10.0)); riv=[[3,lerp(7.8,2.6,kr)],[7,lerp(7.8,3.2,kr)]];
  } else if(T<21.8){ // y subí: globo + subir juntos
    const A=[7,17], B=[7.8,1.3]; const kb=ease(seg(T,12.2,15.6));
    if(T>12.0){ ball(A,B,7.5,kb,1); trail(A,B,7.5,kb,1); bshow=1; }
    const k=ease(seg(T,12.6,16.4));
    ours=[[3,lerp(16.6,12.6,k)],[7,lerp(17,12.8,k)]];
    riv=[[3,lerp(7.8,1.6,k)],[7,lerp(7.8,1.9,k)]];
    $('zdeep').setAttribute('opacity',0.5*seg(T,11.6,12.2));
    let s=''; if(k<1&&T>12.4){ for(const x of [3,7]){ const [px,py]=P(x,16.0); s+=`<path d="M${px} ${py} L ${px} ${py-3.2*M}" stroke="${ACC}" stroke-width=8 stroke-dasharray="16 10" opacity=${1-k} />`; } }
    $('up').innerHTML=s; $('up').setAttribute('opacity',1);
  }
  if(T>=11.4) {} else $('up').setAttribute('opacity',0);
  if(!bshow){ $('ball').setAttribute('opacity',0); $('shadow').setAttribute('opacity',0); }
  players(ours,riv,hl);
  // cierre
  $('won').style.opacity=fade(T,16.6,19.3,.3); $('won').style.transform=`scale(${0.85+0.15*ease(seg(T,16.6,17.0))})`;
  const st=fade(T,19.2,22.0,.35); $('stat').style.opacity=st; $('stat').style.transform=`scale(${0.94+0.06*seg(T,19.2,19.7)})`;
  const c=seg(T,21.8,22.3); $('close').style.opacity=c; $('brand').style.opacity=1-c;
  $('court').style.opacity=1-c*0.7;
};
""" % dict(M=M, CW=CW, CH=CH, HOT=t['hot'], ACC=t['acc'])


def main():
    fps = int(sys.argv[sys.argv.index("--fps") + 1]) if "--fps" in sys.argv else 30
    solo_tapa = "--solo-tapa" in sys.argv
    tmp = pathlib.Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{HTML}</style></head><body>{BODY}<script>{JS}</script></body></html>")
        pg.wait_for_timeout(500)
        pg.evaluate("render(1.0)"); pg.screenshot(path=str(OUT / f"{NOMBRE}-tapa.jpg"), type="jpeg", quality=90)
        if not solo_tapa:
            n = int(DUR * fps)
            for i in range(n):
                pg.evaluate(f"render({i / fps:.4f})")
                pg.screenshot(path=str(tmp / f"f{i:05d}.jpg"), type="jpeg", quality=92)
        b.close()
    if not solo_tapa:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(tmp / "f%05d.jpg"),
                        "-f", "lavfi", "-t", str(DUR), "-i", "anullsrc=r=44100:cl=stereo",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
                        "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(OUT / f"{NOMBRE}.mp4")], check=True)
    shutil.rmtree(tmp)
    print(OUT / f"{NOMBRE}.mp4")


if __name__ == "__main__":
    main()
