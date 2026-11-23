"""Reel 'Táctica Sur n.º 3: El medio tiene dueño' (1080x1920, ~25 s, todo con código, USD 0).

Una sola idea: la pelota al medio la toma el que la tiene de derecha (con dos diestros, el del revés),
grita "¡mía!" y el compañero cubre el hueco.
Escenas: gancho (nadie va y se regala el punto), 1 mirá la derecha, 2 avisá y cubrí, regla, cierre.
Uso: FONTS_DIR=... LOGO_PNG=... python3 instagram/2026-11-semana5/tactica_medio.py [--fps 30] [--solo-tapa] [--cuadros 1,8,13]
Salidas: tactica-sur-3-medio.mp4 y tactica-sur-3-medio-tapa.jpg en esta carpeta.
"""
import os, sys, pathlib, shutil, subprocess, tempfile
R = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "overgrip/diseno"))
os.environ.setdefault("LOGO_PNG", str(R / "marca/logo-sur-padel-transparente.png"))
import gen
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
NOMBRE = "tactica-sur-3-medio"
DUR = 25.0
t = gen.THEMES["azul"]
FONDO = gen.b64(R / "marca/fondos/fondo-02-red-arena.jpg")

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
<div class=top><div class=strip><div class=a>TÁCTICA SUR</div><div class=b>N.º 3 · El medio</div></div></div>
<div class=tt id=tt></div>
<svg id=court width={CW} height={CH} viewBox="0 0 {CW} {CH}">
 <rect width={CW} height={CH} fill="{t['court2']}"/>
 <rect id=zmid x={4.2*M} y={13.4*M} width={1.6*M} height={6.4*M} fill="#ff4d4d" opacity=0 />
 <rect id=zder1 x={3*M} y={13.4*M} width={2.6*M} height={6.4*M} fill="{t['hot']}" opacity=0 />
 <rect id=zder2 x={7*M} y={13.4*M} width={2.9*M} height={6.4*M} fill="{t['acc']}" opacity=0 />
 <text id=tmid x={5*M} y={13.1*M} text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=44 fill="#ff4d4d" opacity=0 style="paint-order:stroke" stroke="#071528" stroke-width=8>¿DE QUIÉN?</text>
 <text id=tder1 x={4.3*M} y={14.1*M} text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=34 fill="#fff" style="paint-order:stroke" stroke="#071528" stroke-width=6 opacity=0>SU DERECHA</text>
 <text id=tder2 x={8.45*M} y={14.1*M} text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=34 fill="#fff" style="paint-order:stroke" stroke="#071528" stroke-width=6 opacity=0>SU DERECHA</text>
 <rect x=3 y=3 width={CW-6} height={CH-6} fill=none stroke="#fff" stroke-width=5 />
 <line x1=0 y1={3.05*M} x2={CW} y2={3.05*M} stroke="#fff" stroke-width=5 />
 <line x1=0 y1={16.95*M} x2={CW} y2={16.95*M} stroke="#fff" stroke-width=5 />
 <line x1={CW/2} y1={3.05*M} x2={CW/2} y2={16.95*M} stroke="#fff" stroke-width=5 />
 <line x1=-20 y1={10*M} x2={CW+20} y2={10*M} stroke="#fff" stroke-width=14 stroke-dasharray="7 7" />
 <text x={CW-10} y={10*M-14} text-anchor=end font-family=B font-weight=700 font-size=20 fill="rgba(255,255,255,.7)" style="letter-spacing:3px">RED</text>
 <text x=14 y=34 font-family=B font-weight=700 font-size=22 fill="rgba(255,120,120,.95)" style="letter-spacing:3px">RIVALES</text>
 <text id=trev x={2.6*M} y={CH-26} text-anchor=middle font-family=B font-weight=700 font-size=22 fill="{t['acc']}" style="letter-spacing:3px">REVÉS</text>
 <text id=tdri x={7.4*M} y={CH-26} text-anchor=middle font-family=B font-weight=700 font-size=22 fill="{t['acc']}" style="letter-spacing:3px">DRIVE</text>
 <path id=trail fill=none stroke="#fff" stroke-width=5 stroke-dasharray="14 12" opacity=0 />
 <g id=move></g>
 <g id=players></g>
 <g id=bubbles></g>
 <ellipse id=shadow rx=16 ry=9 fill="rgba(0,0,0,.45)" opacity=0 />
 <circle id=ball r=15 fill="#e8f25a" stroke="#fff" stroke-width=3 opacity=0 />
 <g id=boom opacity=0><circle r=120 fill="rgba(7,21,40,.8)" stroke="#ff4d4d" stroke-width=8 /><text y=-4 text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=44 fill="#ff4d4d">PUNTO</text><text y=40 text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=44 fill="#ff4d4d">REGALADO</text></g>
 <g id=glow opacity=0><circle r=70 fill="rgba(242,178,28,.18)" stroke="{t['hot']}" stroke-width=6 /></g>
</svg>
<div class=won id=won>El medio<br><span>ya tiene dueño</span></div>
<div class=rule id=rule><div class=h>LA REGLA</div>
 <div class=st><b>1</b>Medio</div><div class=st><b>2</b>Derecha</div><div class=st><b>3</b>¡Mía!</div><div class="st last"><b>4</b>Cubrí</div>
 <div class=ft>Con dos diestros, el medio es del revés.<br>Hablenlo antes de arrancar el partido</div></div>
<div class=close id=close><img src="data:image/png;base64,{gen.LOGO}">
 <div class=c1>Mandáselo a<br><span>tu compañero</span></div>
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
 [0,3.6,'Pelota al medio<br>y <span class=r>nadie va</span><small>El punto más fácil de regalar</small>'],
 [3.6,11.4,'<div class=num>1 · MIRÁ LA DERECHA</div><br>Va el que la tiene<br><span class=g>de derecha</span><small>Con dos diestros: el que juega de revés</small>'],
 [11.4,19.2,'<div class=num>2 · AVISÁ Y CUBRÍ</div><br>El que va<br><span class=g>grita ¡mía!</span><small>Y el compañero cubre el hueco que queda</small>'],
];
let lastTitle=-1;
function players(ours, rivals, hi){
  let s='';
  ours.forEach(([x,y],i)=>{const [px,py]=P(x,y);
    if(hi===i) s+=`<circle cx=${px} cy=${py} r=48 fill=none stroke="${HOT}" stroke-width=6 opacity=.9 />`;
    s+=`<circle cx=${px} cy=${py} r=30 fill="${HOT}" stroke="#071528" stroke-width=6 />`;
    // raqueta del lado derecho (diestro mirando a la red: derecha = pantalla a la derecha)
    s+=`<line x1=${px+26} y1=${py-6} x2=${px+52} y2=${py-30} stroke="#fff" stroke-width=6 stroke-linecap=round />`;});
  for(const [x,y] of rivals){const [px,py]=P(x,y);s+=`<circle cx=${px} cy=${py} r=30 fill="#ff4d4d" stroke="#2a0b0b" stroke-width=6 />`;}
  $('players').innerHTML=s;
}
function bubble(x,y,txt,op,col){ if(op<=0) return ''; const [px,py]=P(x,y);
  return `<g opacity=${op} transform="translate(${px},${py-78})"><rect x=-78 y=-34 width=156 height=56 rx=14 fill="${col}" /><text y=8 text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=38 fill="#071528">${txt}</text></g>`; }
function ballAt(x,y,z,show){
  const [px,py]=P(x,y);
  $('shadow').setAttribute('cx',px); $('shadow').setAttribute('cy',py); $('shadow').setAttribute('opacity',show);
  $('ball').setAttribute('cx',px); $('ball').setAttribute('cy',py-z*M*0.8); $('ball').setAttribute('r',15+z*2.2); $('ball').setAttribute('opacity',show);
}
function drawTrail(pts,show){ let d=''; pts.forEach((p,i)=>{d+=(i?'L':'M')+p[0]+' '+p[1];}); $('trail').setAttribute('d',d); $('trail').setAttribute('opacity',show*0.8); }
function trailUntil(T,t0,f){ const pts=[]; for(let s=t0;s<=T;s+=0.04){const b=f(s); if(b){const [px,py]=P(b[0],b[1]);pts.push([px,py-b[2]*M*0.8]);}} return pts; }
// pelota del rival al medio: (7,6) -> (5,16.6), altura en arco
function toMid(s,a,b){ const k=seg(s,a,b); return [lerp(7,5,k),lerp(6,16.6,k),0.6+2.6*4*k*(1-k)]; }
window.render=function(T){
  $('bg').style.transform=`scale(${1+T*0.004})`;
  let ti=-1; for(let i=0;i<TITLES.length;i++) if(T>=TITLES[i][0]&&T<TITLES[i][1]) ti=i;
  if(ti!==lastTitle){ $('tt').innerHTML= ti>=0?TITLES[ti][2]:''; lastTitle=ti; }
  if(ti>=0){ const [a,b]=TITLES[ti]; $('tt').style.opacity=fade(T,a,b,.3); $('tt').style.transform=`translateY(${(1-seg(T,a,a+.35))*30}px)`; }
  else $('tt').style.opacity=0;
  let ours=[[2.6,17.2],[7.4,17.2]], riv=[[3,6.2],[7,6.2]], hi=-1, bub='';
  ['zmid','tmid','zder1','zder2','tder1','tder2'].forEach(i=>$(i).setAttribute('opacity',0));
  $('boom').setAttribute('opacity',0); $('glow').setAttribute('opacity',0); $('trail').setAttribute('opacity',0); $('move').innerHTML='';
  let bshow=0;
  if(T<3.6){ // gancho: los dos dudan y la pelota pasa por el medio
    const f=s=>{ if(s<0.2) return null; if(s<1.5) return toMid(s,0.2,1.5);
      const k=seg(s,1.5,2.2); return [5,lerp(16.6,19.8,k),lerp(0.6,0.2,k)]; };
    const b=f(T); if(b){ bshow=T<2.3?1:0; ballAt(b[0],b[1],b[2],bshow); drawTrail(trailUntil(Math.min(T,2.2),0.2,f),1); }
    $('zmid').setAttribute('opacity',0.35*seg(T,0.4,0.9)); $('tmid').setAttribute('opacity',seg(T,0.5,0.9)*(1-seg(T,3.2,3.6)));
    const d=Math.sin(seg(T,0.9,1.9)*Math.PI)*0.5; ours=[[2.6+d,17.2],[7.4-d,17.2]];
    bub+=bubble(2.6+d,17.2,'¿TUYA?',fade(T,0.9,2.4,.2),'#fff')+bubble(7.4-d,17.2,'¿TUYA?',fade(T,1.1,2.6,.2),'#fff');
    if(T>2.2){ const [bx,by]=P(5,13.6); $('boom').setAttribute('transform',`translate(${bx},${by}) scale(${0.6+0.6*seg(T,2.2,2.5)})`); $('boom').setAttribute('opacity',fade(T,2.2,3.5,.2)); }
  } else if(T<11.4){ // mirá la derecha: zonas de derecha, el medio cae en la del revés
    $('zder1').setAttribute('opacity',0.55*seg(T,4.0,4.6)); $('tder1').setAttribute('opacity',seg(T,4.2,4.8));
    $('zder2').setAttribute('opacity',0.35*seg(T,4.6,5.2)); $('tder2').setAttribute('opacity',seg(T,4.8,5.4));
    $('zmid').setAttribute('opacity',0.0);
    hi = T>6.0?0:-1;
    const f=s=>{ if(s<7.0) return null; if(s<8.6) return toMid(s,7.0,8.6);
      const k=ease(seg(s,9.0,10.8)); return [lerp(4.6,8.2,k),lerp(16.8,2.2,k),0.9+5*4*k*(1-k)]; };
    const km=ease(seg(T,7.2,8.6)); ours=[[lerp(2.6,4.4,km),lerp(17.2,17.0,km)],[7.4,17.2]];
    if(T>7.0&&T<8.8){ const [x1,y1]=P(2.6,17.2), [x2,y2]=P(4.3,17.0); $('move').innerHTML=`<path d="M${x1} ${y1} L ${x2} ${y2}" stroke="${HOT}" stroke-width=8 stroke-dasharray="16 10" opacity=${1-seg(T,8.4,8.8)} />`; }
    const b=f(T); if(b){ ballAt(b[0],b[1],b[2],1); bshow=1; drawTrail(trailUntil(T,Math.max(7.0,T-2.6),f),1); }
    if(T>8.5&&T<9.4){ const [gx,gy]=P(4.6,16.8); $('glow').setAttribute('transform',`translate(${gx},${gy}) scale(${0.6+0.6*seg(T,8.5,8.8)})`); $('glow').setAttribute('opacity',fade(T,8.5,9.4,.2)); }
  } else if(T<19.2){ // avisá y cubrí
    $('zder1').setAttribute('opacity',0.3); $('tder1').setAttribute('opacity',0.6);
    const km=ease(seg(T,12.2,13.6)); const kc=ease(seg(T,12.6,14.2));
    ours=[[lerp(2.6,4.4,km),lerp(17.2,16.9,km)],[lerp(7.4,6.4,kc),lerp(17.2,17.8,kc)]]; hi=0;
    bub+=bubble(ours[0][0],ours[0][1],'¡MÍA!',fade(T,12.0,14.4,.2),HOT);
    bub+=bubble(ours[1][0],ours[1][1],'CUBRO',fade(T,13.0,15.0,.2),ACC);
    if(T>12.6&&T<14.6){ const [x1,y1]=P(7.4,17.2), [x2,y2]=P(6.3,17.9); $('move').innerHTML=`<path d="M${x1} ${y1} L ${x2} ${y2}" stroke="${ACC}" stroke-width=8 stroke-dasharray="16 10" opacity=${1-seg(T,14.2,14.6)} />`; }
    const f=s=>{ if(s<11.8) return null; if(s<13.6) return toMid(s,11.8,13.6);
      const k=ease(seg(s,13.9,15.8)); return [lerp(4.6,2.2,k),lerp(16.8,1.8,k),0.9+6*4*k*(1-k)]; };
    const b=f(T); if(b){ ballAt(b[0],b[1],b[2],1); bshow=1; drawTrail(trailUntil(T,Math.max(11.8,T-2.8),f),1); }
    const kr=ease(seg(T,14.4,16.2)); riv=[[3,lerp(6.2,2.4,kr)],[7,lerp(6.2,2.8,kr)]];
  }
  $('bubbles').innerHTML=bub;
  if(!bshow){ $('ball').setAttribute('opacity',0); $('shadow').setAttribute('opacity',0); }
  players(ours,riv,hi);
  $('won').style.opacity=fade(T,16.6,19.3,.3); $('won').style.transform=`scale(${0.85+0.15*ease(seg(T,16.6,17.0))})`;
  const st=fade(T,19.2,22.2,.35); $('rule').style.opacity=st; $('rule').style.transform=`scale(${0.94+0.06*seg(T,19.2,19.7)})`;
  const c=seg(T,22.0,22.5); $('close').style.opacity=c; $('brand').style.opacity=1-c;
  $('court').style.opacity=1-c*0.7;
};
""" % dict(M=M, CW=CW, CH=CH, HOT=t['hot'], ACC=t['acc'])


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
