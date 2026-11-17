"""Reel 'Táctica Sur n.º 2: El vidrio es tu aliado' (1080x1920, ~25 s, todo con código, USD 0).

Una sola idea: en la salida de pared, separate del vidrio y dejá bajar la pelota antes de pegarle.
Cancha completa desde arriba (nosotros abajo, vidrio de fondo abajo), pelota con sombra para mostrar la altura
y un medidor de altura al costado.
Escenas: gancho (le pega apurado contra el vidrio → a la red), 1 separate, 2 dejala bajar y pegale, regla, cierre.
Uso: FONTS_DIR=... LOGO_PNG=... python3 instagram/2026-11-semana4/tactica_vidrio.py [--fps 30] [--solo-tapa]
Salidas: tactica-sur-2-vidrio.mp4 y tactica-sur-2-vidrio-tapa.jpg en esta carpeta.
"""
import os, sys, pathlib, shutil, subprocess, tempfile
R = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "overgrip/diseno"))
os.environ.setdefault("LOGO_PNG", str(R / "marca/logo-sur-padel-transparente.png"))
import gen
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
NOMBRE = "tactica-sur-2-vidrio"
DUR = 25.0
t = gen.THEMES["azul"]
FONDO = gen.b64(R / "marca/fondos/fondo-07-vidrio-lluvia.jpg")

M = 56
CW, CH = 10 * M, 20 * M
CX = (1080 - CW) // 2
CY = 560

HTML = gen.FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:B;color:#fff;background:#050b16;position:relative}}
#bg{{position:absolute;inset:-40px;background:url(data:image/jpeg;base64,{FONDO}) center/cover;filter:brightness(.5) saturate(1.1)}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,11,22,.92) 0%,rgba(5,11,22,.55) 30%,rgba(5,11,22,.55) 75%,rgba(5,11,22,.95) 100%)}}
.top{{position:absolute;left:0;right:0;top:90px;display:flex;flex-direction:column;align-items:center}}
.strip{{display:flex;height:62px;font-weight:700;letter-spacing:3px;text-transform:uppercase;font-size:24px;box-shadow:0 8px 30px rgba(0,0,0,.5)}}
.strip .a{{background:{t['hot']};color:#071528;display:flex;align-items:center;padding:0 40px 0 22px;font-family:BC;font-style:italic;font-weight:800;font-size:34px;clip-path:polygon(0 0,100% 0,92% 100%,0 100%)}}
.strip .b{{background:rgba(7,21,40,.92);border:1px solid rgba(255,255,255,.18);display:flex;align-items:center;padding:0 26px 0 30px;margin-left:-14px}}
.tt{{position:absolute;left:60px;right:60px;top:180px;text-align:center;font-family:BC;font-weight:800;font-style:italic;text-transform:uppercase;line-height:.92;font-size:96px;
 color:#fff;text-shadow:0 6px 24px rgba(0,0,0,.8)}}
.tt .g{{color:{t['hot']}}} .tt .r{{color:#ff4d4d}}
.tt small{{display:block;font-family:B;font-style:normal;font-weight:600;text-transform:none;font-size:36px;line-height:1.3;margin-top:16px;color:#dfe9f5}}
.num{{display:inline-block;background:{t['hot']};color:#071528;font-family:BC;font-style:italic;font-weight:800;font-size:40px;padding:2px 22px;margin-bottom:14px;letter-spacing:2px}}
#court{{position:absolute;left:{CX}px;top:{CY}px;filter:drop-shadow(0 30px 60px rgba(0,0,0,.7))}}
#gauge{{position:absolute;left:{CX + CW + 40}px;top:{CY + 12 * M}px;width:150px;height:{7 * M}px;opacity:0}}
#gauge .bar{{position:absolute;left:60px;top:0;bottom:0;width:14px;background:rgba(255,255,255,.18);border-radius:7px}}
#gauge .lab{{position:absolute;left:0;right:0;top:-46px;text-align:center;font-size:20px;letter-spacing:3px;font-weight:700;color:rgba(255,255,255,.75)}}
#gauge .cin{{position:absolute;left:30px;width:110px;height:6px;background:{t['hot']};}}
#gauge .cint{{position:absolute;left:0;width:150px;text-align:center;font-family:BC;font-style:italic;font-weight:800;font-size:30px;color:{t['hot']}}}
#gauge .dot{{position:absolute;left:46px;width:42px;height:42px;border-radius:50%;background:#e8f25a;border:4px solid #fff;box-shadow:0 0 20px rgba(232,242,90,.6)}}
.close{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;background:rgba(5,11,22,.82);opacity:0}}
.close img{{width:220px;filter:drop-shadow(0 8px 30px rgba(0,0,0,.6))}}
.close .c1{{font-family:BC;font-style:italic;font-weight:800;font-size:86px;text-transform:uppercase;text-align:center;line-height:.95}}
.close .c1 span{{color:{t['hot']}}}
.close .c2{{font-size:38px;font-weight:600;color:#dfe9f5;text-align:center}}
.close .c3{{font-size:26px;letter-spacing:4px;color:rgba(255,255,255,.65)}}
.won{{position:absolute;left:0;right:0;top:820px;text-align:center;font-family:BC;font-style:italic;font-weight:800;font-size:118px;line-height:.9;text-transform:uppercase;opacity:0;
 color:#fff;text-shadow:0 8px 30px rgba(0,0,0,.9),0 0 40px rgba(0,0,0,.7)}}
.won span{{color:{t['hot']}}}
.rule{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;background:rgba(5,11,22,.88);opacity:0}}
.rule .h{{font-size:30px;letter-spacing:6px;font-weight:700;color:{t['acc']}}}
.rule .st{{display:flex;align-items:center;gap:22px;font-family:BC;font-style:italic;font-weight:800;font-size:92px;text-transform:uppercase}}
.rule .st b{{display:inline-flex;align-items:center;justify-content:center;width:84px;height:84px;background:{t['hot']};color:#071528;font-size:60px}}
.rule .st.last{{color:{t['hot']}}}
.rule .ft{{margin-top:18px;font-size:34px;font-weight:600;color:#dfe9f5;text-align:center}}
.brand{{position:absolute;bottom:70px;left:0;right:0;text-align:center;font-size:24px;letter-spacing:4px;color:rgba(255,255,255,.6)}}
"""

BODY = f"""<div id=bg></div><div class=shade></div>
<div class=top><div class=strip><div class=a>TÁCTICA SUR</div><div class=b>N.º 2 · El vidrio</div></div></div>
<div class=tt id=tt></div>
<svg id=court width={CW} height={CH} viewBox="0 0 {CW} {CH}">
 <rect width={CW} height={CH} fill="{t['court2']}"/>
 <rect id=zhit x=0 y={15.6*M} width={CW} height={2.0*M} fill="{t['hot']}" opacity=0 />
 <rect id=zno x=0 y={18.6*M} width={CW} height={1.4*M} fill="#ff4d4d" opacity=0 />
 <text id=thit x={CW/2} y={15.3*M} text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=46 fill="{t['hot']}" opacity=0 style="paint-order:stroke" stroke="#071528" stroke-width=8>ACÁ LE PEGÁS</text>
 <text id=tno x={CW/2} y={19.55*M} text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=40 fill="#fff" opacity=0>PEGADO AL VIDRIO, NO</text>
 <rect x=3 y=3 width={CW-6} height={CH-6} fill=none stroke="#fff" stroke-width=5 />
 <rect id=glass x=0 y={CH-14} width={CW} height=14 fill="{t['acc']}" opacity=.9 />
 <line x1=0 y1={3.05*M} x2={CW} y2={3.05*M} stroke="#fff" stroke-width=5 />
 <line x1=0 y1={16.95*M} x2={CW} y2={16.95*M} stroke="#fff" stroke-width=5 />
 <line x1={CW/2} y1={3.05*M} x2={CW/2} y2={16.95*M} stroke="#fff" stroke-width=5 />
 <line x1=-20 y1={10*M} x2={CW+20} y2={10*M} stroke="#fff" stroke-width=14 stroke-dasharray="7 7" />
 <text x={CW-10} y={10*M-14} text-anchor=end font-family=B font-weight=700 font-size=20 fill="rgba(255,255,255,.7)" style="letter-spacing:3px">RED</text>
 <text x=14 y={CH-26} font-family=B font-weight=700 font-size=22 fill="{t['acc']}" style="letter-spacing:3px">VIDRIO DE FONDO</text>
 <text x=14 y=34 font-family=B font-weight=700 font-size=22 fill="rgba(255,120,120,.95)" style="letter-spacing:3px">RIVALES</text>
 <path id=trail fill=none stroke="#fff" stroke-width=5 stroke-dasharray="14 12" opacity=0 />
 <g id=players></g>
 <g id=move></g>
 <ellipse id=shadow rx=16 ry=9 fill="rgba(0,0,0,.45)" opacity=0 />
 <circle id=ball r=15 fill="#e8f25a" stroke="#fff" stroke-width=3 opacity=0 />
 <g id=boom opacity=0><circle r=110 fill="rgba(7,21,40,.75)" stroke="#ff4d4d" stroke-width=8 /><text y=14 text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=46 fill="#ff4d4d">¡A LA RED!</text></g>
 <g id=glow opacity=0><circle r=70 fill="rgba(116,180,232,.18)" stroke="{t['acc']}" stroke-width=6 /></g>
</svg>
<div id=gauge><div class=lab>ALTURA</div><div class=bar></div>
 <div class=cin style="top:{int(7*M - 1.0/2.6*7*M)}px"></div><div class=cint style="top:{int(7*M - 1.0/2.6*7*M) + 10}px">CINTURA</div>
 <div class=dot id=gdot></div></div>
<div class=won id=won>La pared<br><span>juega para vos</span></div>
<div class=rule id=rule><div class=h>LA REGLA</div>
 <div class=st><b>1</b>Pica</div><div class=st><b>2</b>Vidrio</div><div class=st><b>3</b>Baja</div><div class="st last"><b>4</b>Pegás</div>
 <div class=ft>Separate del vidrio y esperala:<br>tenés más tiempo del que creés</div></div>
<div class=close id=close><img src="data:image/png;base64,{gen.LOGO}">
 <div class=c1>Guardalo para tu<br><span>próximo partido</span></div>
 <div class=c2>Cada semana, una Táctica Sur.<br>Seguinos para no perderte la próxima.</div>
 <div class=c3>@SURPADELSTORE</div></div>
<div class=brand id=brand>@SURPADELSTORE · SURPADEL.COM.AR</div>
"""

JS = """
const M=%(M)d, CW=%(CW)d, CH=%(CH)d, HOT='%(HOT)s', ACC='%(ACC)s', GH=%(GH)d;
const $=id=>document.getElementById(id);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const seg=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const ease=x=>x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2;
const lerp=(a,b,k)=>a+(b-a)*k;
const fade=(t,a,b,f=.35)=>Math.min(seg(t,a,a+f),1-seg(t,b-f,b));
function P(x,y){return [x*M,y*M];}
const TITLES=[
 [0,3.6,'Si le pegás apurado,<br><span class=r>la regalás</span><small>Pegado al vidrio y con la pelota subiendo</small>'],
 [3.6,11.4,'<div class=num>1 · SEPARATE</div><br>Dejá que pegue<br><span class=g>y salga del vidrio</span><small>Un paso adelante: la pelota viene hacia vos</small>'],
 [11.4,19.2,'<div class=num>2 · DEJALA BAJAR</div><br>Esperala<br><span class=g>a la cintura</span><small>Con tiempo y control, la mandás al fondo rival</small>'],
];
let lastTitle=-1;
function players(ours, rivals){
  let s='';
  for(const [x,y] of ours){const [px,py]=P(x,y);s+=`<circle cx=${px} cy=${py} r=30 fill="${HOT}" stroke="#071528" stroke-width=6 />`;}
  for(const [x,y] of rivals){const [px,py]=P(x,y);s+=`<circle cx=${px} cy=${py} r=30 fill="#ff4d4d" stroke="#2a0b0b" stroke-width=6 />`;}
  $('players').innerHTML=s;
}
let TR=[];
function ballAt(x,y,z,show){
  const [px,py]=P(x,y);
  $('shadow').setAttribute('cx',px); $('shadow').setAttribute('cy',py); $('shadow').setAttribute('opacity',show);
  $('ball').setAttribute('cx',px); $('ball').setAttribute('cy',py-z*M*0.8); $('ball').setAttribute('r',15+z*2.2); $('ball').setAttribute('opacity',show);
  return [px,py-z*M*0.8];
}
function gauge(z,show){ $('gauge').style.opacity=show; $('gdot').style.top=(GH - clamp(z/2.6,0,1)*GH - 21)+'px'; }
// recorrido de una salida de pared, k de 0 a 1 por tramo
// A: vuelo rival -> pique (7,3)->(6.4,18.3) altura 3 ; B: pique -> vidrio (6.2,20) z 0->1.6 ; C: sale del vidrio -> (5.8,16.6) z 1.6 -> 0.95
function wallBall(T,t0,t1,t2,t3){
  if(T<t0) return null;
  if(T<t1){const k=seg(T,t0,t1);return [lerp(7,6.4,k),lerp(3,18.3,k),3*4*k*(1-k)];}
  if(T<t2){const k=seg(T,t1,t2);return [lerp(6.4,6.2,k),lerp(18.3,19.75,k),1.6*Math.sin(k*Math.PI/2)];}
  const k=ease(seg(T,t2,t3));return [lerp(6.2,5.8,k),lerp(19.75,16.6,k),lerp(1.6,0.95,k)+0.35*Math.sin(k*Math.PI)];
}
function drawTrail(pts,show){ let d=''; pts.forEach((p,i)=>{d+=(i?'L':'M')+p[0]+' '+p[1];}); $('trail').setAttribute('d',d); $('trail').setAttribute('opacity',show*0.8); }
function trailUntil(T,t0,f){ const pts=[]; for(let s=t0;s<=T;s+=0.04){const b=f(s); if(b){const [px,py]=P(b[0],b[1]);pts.push([px,py-b[2]*M*0.8]);}} return pts; }
window.render=function(T){
  $('bg').style.transform=`scale(${1+T*0.004})`;
  let ti=-1; for(let i=0;i<TITLES.length;i++) if(T>=TITLES[i][0]&&T<TITLES[i][1]) ti=i;
  if(ti!==lastTitle){ $('tt').innerHTML= ti>=0?TITLES[ti][2]:''; lastTitle=ti; }
  if(ti>=0){ const [a,b]=TITLES[ti]; $('tt').style.opacity=fade(T,a,b,.3); $('tt').style.transform=`translateY(${(1-seg(T,a,a+.35))*30}px)`; }
  else $('tt').style.opacity=0;
  let ours=[[3,17.4],[6.4,18.9]], riv=[[3,7.6],[7,7.6]];
  ['zhit','thit','zno','tno'].forEach(i=>$(i).setAttribute('opacity',0));
  $('boom').setAttribute('opacity',0); $('glow').setAttribute('opacity',0); $('trail').setAttribute('opacity',0); $('move').innerHTML='';
  let bshow=0, gshow=0, gz=0;
  if(T<3.6){ // gancho: pegado al vidrio, le pega subiendo y va a la red
    const f=s=>{ if(s<0.2) return null; if(s<1.2){const k=seg(s,0.2,1.2);return [lerp(7,6.4,k),lerp(3,18.3,k),3*4*k*(1-k)];}
      if(s<1.6){const k=seg(s,1.2,1.6);return [6.4,lerp(18.3,18.75,k),1.7*k];}
      const k=seg(s,1.6,2.2);return [lerp(6.4,5,k),lerp(18.75,10,k),lerp(1.7,0.3,k)+1.0*Math.sin(k*Math.PI)*0.4]; };
    const b=f(T); if(b){ ballAt(b[0],b[1],b[2],T<2.3?1:0); bshow=T<2.3?1:0; drawTrail(trailUntil(Math.min(T,2.2),0.2,f),1); }
    $('zno').setAttribute('opacity',0.35*seg(T,0.4,0.9));
    if(T>2.2){ const [bx,by]=P(5,10); $('boom').setAttribute('transform',`translate(${bx},${by}) scale(${0.6+0.6*seg(T,2.2,2.5)})`); $('boom').setAttribute('opacity',fade(T,2.2,3.5,.2)); }
  } else if(T<11.4){ // separate: el jugador sale del vidrio, la pelota pega y sale hacia él
    $('zno').setAttribute('opacity',0.35*fade(T,3.8,6.0,.4)); $('tno').setAttribute('opacity',fade(T,4.0,6.0,.4));
    $('zhit').setAttribute('opacity',0.85*seg(T,5.6,6.2)); $('thit').setAttribute('opacity',seg(T,5.8,6.4));
    const km=ease(seg(T,4.4,5.8)); ours=[[3,17.4],[lerp(6.4,5.8,km),lerp(18.9,16.6,km)]];
    if(T>4.2&&T<6.2){ const [x1,y1]=P(6.4,18.9), [x2,y2]=P(5.8,16.4); $('move').innerHTML=`<path d="M${x1} ${y1} L ${x2} ${y2}" stroke="${ACC}" stroke-width=8 stroke-dasharray="16 10" opacity=${1-seg(T,5.6,6.2)} />`; }
    const f=s=>wallBall(s,6.4,7.6,8.3,10.4);
    const b=f(T); if(b){ ballAt(b[0],b[1],b[2],1); bshow=1; drawTrail(trailUntil(T,6.4,f),1); gshow=seg(T,6.6,7.0); gz=b[2]; }
    if(T>8.2&&T<9.2){ const [gx,gy]=P(6.2,19.75); $('glow').setAttribute('transform',`translate(${gx},${gy}) scale(${0.6+0.6*seg(T,8.2,8.6)})`); $('glow').setAttribute('opacity',fade(T,8.2,9.2,.2)); }
  } else if(T<19.2){ // dejala bajar y pegale al fondo rival
    $('zhit').setAttribute('opacity',0.5);
    ours=[[3,17.4],[5.8,16.6]];
    const f=s=>{ const w=wallBall(s,11.6,12.8,13.5,15.4); if(s<15.4) return w;
      const k=ease(seg(s,15.4,17.4)); return [lerp(5.8,2.4,k),lerp(16.6,1.6,k),0.95+6.5*4*k*(1-k)*(1-0.15*k)]; };
    const b=f(T); if(b){ ballAt(b[0],b[1],b[2],1); bshow=1; drawTrail(trailUntil(T,Math.max(11.6,T-3.2),f),1); gz=b[2]; }
    gshow=T<15.6?1:1-seg(T,15.6,16.0);
    if(T>15.1&&T<16.0){ const [gx,gy]=P(5.8,16.6); $('glow').setAttribute('transform',`translate(${gx},${gy}) scale(${0.6+0.6*seg(T,15.1,15.4)})`); $('glow').setAttribute('opacity',fade(T,15.1,16.0,.2)); }
    const kr=ease(seg(T,15.8,17.6)); riv=[[3,lerp(7.6,2.4,kr)],[7,lerp(7.6,2.8,kr)]];
    const ko=ease(seg(T,16.0,17.8)); ours=[[3,lerp(17.4,13.2,ko)],[lerp(5.8,6.8,ko),lerp(16.6,13.4,ko)]];
  }
  gauge(gz,gshow);
  if(!bshow){ $('ball').setAttribute('opacity',0); $('shadow').setAttribute('opacity',0); }
  players(ours,riv);
  $('won').style.opacity=fade(T,16.9,19.3,.3); $('won').style.transform=`scale(${0.85+0.15*ease(seg(T,16.9,17.3))})`;
  const st=fade(T,19.2,22.2,.35); $('rule').style.opacity=st; $('rule').style.transform=`scale(${0.94+0.06*seg(T,19.2,19.7)})`;
  const c=seg(T,22.0,22.5); $('close').style.opacity=c; $('brand').style.opacity=1-c;
  $('court').style.opacity=1-c*0.7;
};
""" % dict(M=M, CW=CW, CH=CH, HOT=t['hot'], ACC=t['acc'], GH=7 * M)


def main():
    fps = int(sys.argv[sys.argv.index("--fps") + 1]) if "--fps" in sys.argv else 30
    solo_tapa = "--solo-tapa" in sys.argv
    tapas = [float(x) for x in sys.argv[sys.argv.index("--cuadros") + 1].split(",")] if "--cuadros" in sys.argv else []
    tmp = pathlib.Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(f"<html><head><meta charset=utf-8><style>{HTML}</style></head><body>{BODY}<script>{JS}</script></body></html>")
        pg.wait_for_timeout(500)
        pg.evaluate("render(1.0)"); pg.screenshot(path=str(OUT / f"{NOMBRE}-tapa.jpg"), type="jpeg", quality=90)
        for c in tapas:
            pg.evaluate(f"render({c})"); pg.screenshot(path=str(pathlib.Path(os.environ.get("CUADROS_DIR", tmp.parent)) / f"{NOMBRE}-c{c}.jpg"), type="jpeg", quality=70)
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
