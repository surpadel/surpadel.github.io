"""Reel 'Táctica Sur n.º 3: Ante la duda, más alto' (1080x1920, ~25 s, todo con código, USD 0).

Una sola idea: si estás incómodo, pasala con altura y margen sobre la red.
Dato: el 51,4% (hombres) y el 45,3% (mujeres) de los errores en profesionales van a la red
(Ramírez Ortega, Sánchez Pay y Sánchez-Alcaraz, Padel Scientific Journal, 2025; 1068 golpes, WPT Valencia 2021).
Reusa el estilo y el armado de tactica_medio.py (misma carpeta).
Uso: FONTS_DIR=... LOGO_PNG=... python3 instagram/2026-11-semana5/tactica_alto.py [--fps 30] [--solo-tapa] [--cuadros 1,8,13]
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tactica_medio as base
from tactica_medio import gen, t, M, CW, CH, R

FONDO = gen.b64(R / "marca/fondos/fondo-05-focos.jpg")
HTML = base.HTML.replace(base.FONDO, FONDO).replace(".rule .ft{", ".rule .src{margin-top:6px;font-size:22px;color:rgba(255,255,255,.6);text-align:center;line-height:1.4}\n.rule .ft{")

BODY = f"""<div id=bg></div><div class=shade></div>
<div class=top><div class=strip><div class=a>TÁCTICA SUR</div><div class=b>N.º 3 · Más alto</div></div></div>
<div class=tt id=tt></div>
<svg id=court width={CW} height={CH} viewBox="0 0 {CW} {CH}">
 <rect width={CW} height={CH} fill="{t['court2']}"/>
 <rect x=3 y=3 width={CW-6} height={CH-6} fill=none stroke="#fff" stroke-width=5 />
 <line x1=0 y1={3.05*M} x2={CW} y2={3.05*M} stroke="#fff" stroke-width=5 />
 <line x1=0 y1={16.95*M} x2={CW} y2={16.95*M} stroke="#fff" stroke-width=5 />
 <line x1={CW/2} y1={3.05*M} x2={CW/2} y2={16.95*M} stroke="#fff" stroke-width=5 />
 <line x1=-20 y1={10*M} x2={CW+20} y2={10*M} stroke="#fff" stroke-width=14 stroke-dasharray="7 7" />
 <text x={CW-10} y={10*M-14} text-anchor=end font-family=B font-weight=700 font-size=20 fill="rgba(255,255,255,.7)" style="letter-spacing:3px">RED</text>
 <text x=14 y=34 font-family=B font-weight=700 font-size=22 fill="rgba(255,120,120,.95)" style="letter-spacing:3px">RIVALES</text>
 <text x=14 y={CH-26} font-family=B font-weight=700 font-size=22 fill="{t['acc']}" style="letter-spacing:3px">NOSOTROS</text>
 <path id=ghost fill=none stroke="#ff4d4d" stroke-width=8 stroke-dasharray="12 10" opacity=0 />
 <path id=trail fill=none stroke="#fff" stroke-width=5 stroke-dasharray="14 12" opacity=0 />
 <g id=marg opacity=0><rect x={0.4*M} y={8.6*M} width={CW-0.8*M} height={1.4*M} fill="{t['hot']}" opacity=.22 />
  <text x={CW/2} y={8.35*M} text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=40 fill="{t['hot']}" style="paint-order:stroke" stroke="#071528" stroke-width=7>MARGEN</text></g>
 <g id=players></g>
 <ellipse id=shadow rx=16 ry=9 fill="rgba(0,0,0,.45)" opacity=0 />
 <circle id=ball r=15 fill="#e8f25a" stroke="#fff" stroke-width=3 opacity=0 />
 <g id=boom opacity=0><circle r=120 fill="rgba(7,21,40,.8)" stroke="#ff4d4d" stroke-width=8 /><text id=boomt y=16 text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=46 fill="#ff4d4d">¡A LA RED!</text></g>
 <g id=okb opacity=0><circle r=130 fill="rgba(7,21,40,.8)" stroke="{t['hot']}" stroke-width=8 /><text y=-6 text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=42 fill="{t['hot']}">ERROR</text><text y=38 text-anchor=middle font-family=BC font-style=italic font-weight=800 font-size=42 fill="{t['hot']}">DEL RIVAL</text></g>
</svg>
<div class=won id=won>Ante la duda<br><span>más alto</span></div>
<div class=rule id=rule><div class=h>EL DATO</div>
 <div class=st><b>½</b>de los errores</div><div class="st last">va a la red</div>
 <div class=ft>Hombres 51,4% · Mujeres 45,3%<br>en partidos de profesionales</div>
 <div class=src>Ramírez Ortega, Sánchez Pay y Sánchez-Alcaraz (2025)<br>Padel Scientific Journal · 1.068 golpes, WPT Valencia 2021</div></div>
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
 [0,3.6,'La mitad de los errores<br><span class=r>van a la red</span><small>En partidos de profesionales</small>'],
 [3.6,11.4,'<div class=num>1 · MÁS ALTURA</div><br>Si estás incómodo,<br><span class=g>pasala alta</span><small>Con margen sobre la red, no rozándola</small>'],
 [11.4,19.2,'<div class=num>2 · QUE JUEGUEN OTRA</div><br>Una pelota más<br><span class=g>es una chance más</span><small>Si la pasás, el rival también puede fallar</small>'],
];
let lastTitle=-1;
function circ(px,py,r,fill,stroke){ return '<circle cx='+px+' cy='+py+' r='+r+' fill="'+fill+'" stroke="'+stroke+'" stroke-width=6 />'; }
function players(ours,rivals){
  let s='';
  for(const [x,y] of ours){const [px,py]=P(x,y); s+=circ(px,py,30,HOT,'#071528');}
  for(const [x,y] of rivals){const [px,py]=P(x,y); s+=circ(px,py,30,'#ff4d4d','#2a0b0b');}
  $('players').innerHTML=s;
}
function ballAt(x,y,z,show){
  const [px,py]=P(x,y);
  $('shadow').setAttribute('cx',px); $('shadow').setAttribute('cy',py); $('shadow').setAttribute('opacity',show);
  $('ball').setAttribute('cx',px); $('ball').setAttribute('cy',py-z*M*0.8); $('ball').setAttribute('r',15+z*2.2); $('ball').setAttribute('opacity',show);
}
function pathOf(pts){ let d=''; pts.forEach(function(p,i){ d+=(i?'L':'M')+p[0]+' '+p[1]; }); return d; }
function pts(t0,t1,f){ const r=[]; for(let s=t0;s<=t1;s+=0.04){const b=f(s); if(b){const q=P(b[0],b[1]); r.push([q[0],q[1]-b[2]*M*0.8]);}} return r; }
// tiro chato: de (2.6,18.4) hacia la red, se queda en (1.7,10)
function flat(s,a,b){ const k=seg(s,a,b); return [lerp(2.6,1.7,k),lerp(18.4,10.05,k),lerp(0.9,0.35,k)]; }
// tiro con altura: de (2.6,18.4) a (6.6,4.2), pasa la red alto
function high(s,a,b){ const k=seg(s,a,b); return [lerp(2.6,6.6,k),lerp(18.4,4.2,k),0.9+2.6*4*k*(1-k)]; }
window.render=function(T){
  $('bg').style.transform='scale('+(1+T*0.004)+')';
  let ti=-1; for(let i=0;i<TITLES.length;i++) if(T>=TITLES[i][0]&&T<TITLES[i][1]) ti=i;
  if(ti!==lastTitle){ $('tt').innerHTML= ti>=0?TITLES[ti][2]:''; lastTitle=ti; }
  if(ti>=0){ const a=TITLES[ti][0], b=TITLES[ti][1]; $('tt').style.opacity=fade(T,a,b,.3); $('tt').style.transform='translateY('+((1-seg(T,a,a+.35))*30)+'px)'; }
  else $('tt').style.opacity=0;
  let ours=[[2.6,18.4],[7.2,15.6]], riv=[[3,6.6],[7,6.6]], bshow=0;
  ['boom','okb','marg','ghost','trail'].forEach(function(i){ $(i).setAttribute('opacity',0); });
  if(T<3.6){ // gancho: tiro chato e incómodo, a la red
    const f=function(s){ return s<0.4?null:flat(s,0.4,1.6); };
    const b=f(Math.min(T,1.6)); if(b){ bshow=T<2.6?1:0; ballAt(b[0],b[1],b[2],bshow); $('trail').setAttribute('d',pathOf(pts(0.4,Math.min(T,1.6),f))); $('trail').setAttribute('opacity',0.8); }
    if(T>1.6){ const q=P(3.4,12.8); $('boom').setAttribute('transform','translate('+q[0]+','+q[1]+') scale('+(0.6+0.6*seg(T,1.6,1.9))+')'); $('boom').setAttribute('opacity',fade(T,1.6,3.5,.2)); }
  } else if(T<11.4){ // más altura: el chato fantasma vs el alto
    $('ghost').setAttribute('d',pathOf(pts(0.4,1.6,function(s){return flat(s,0.4,1.6);}))); $('ghost').setAttribute('opacity',0.95*fade(T,3.8,11.2,.4));
    $('marg').setAttribute('opacity',seg(T,6.4,7.0)*(1-seg(T,10.8,11.3)));
    const f=function(s){ return s<5.2?null:high(s,5.2,7.6); };
    const b=f(Math.min(T,7.6)); if(b){ bshow=1; ballAt(b[0],b[1],b[2],1); $('trail').setAttribute('d',pathOf(pts(5.2,Math.min(T,7.6),f))); $('trail').setAttribute('opacity',0.8); }
    const kr=ease(seg(T,6.8,8.0)); riv=[[3,6.6],[lerp(7,6.8,kr),lerp(6.6,3.6,kr)]];
    if(T>7.6) bshow=1;
  } else if(T<19.2){ // que jueguen otra: pasa, el rival la juega y falla a la red
    const f=function(s){ if(s<11.8) return null; if(s<13.8) return high(s,11.8,13.8);
      const k=seg(s,14.2,15.4); return [lerp(6.6,5.4,k),lerp(4.2,9.95,k),lerp(0.9,0.3,k)]; };
    const b=f(Math.min(T,15.4)); if(b){ bshow=T<16.4?1:0; ballAt(b[0],b[1],b[2],bshow); $('trail').setAttribute('d',pathOf(pts(Math.max(11.8,T-2.6),Math.min(T,15.4),f))); $('trail').setAttribute('opacity',0.8); }
    const kr=ease(seg(T,12.6,13.8)); riv=[[3,6.6],[lerp(7,6.8,kr),lerp(6.6,3.6,kr)]];
    if(T>15.4){ const q=P(5.4,7.4); $('okb').setAttribute('transform','translate('+q[0]+','+q[1]+') scale('+(0.6+0.6*seg(T,15.4,15.7))+')'); $('okb').setAttribute('opacity',fade(T,15.4,16.8,.2)); }
  }
  if(!bshow){ $('ball').setAttribute('opacity',0); $('shadow').setAttribute('opacity',0); }
  players(ours,riv);
  $('won').style.opacity=fade(T,16.6,19.3,.3); $('won').style.transform='scale('+(0.85+0.15*ease(seg(T,16.6,17.0)))+')';
  const st=fade(T,19.2,22.2,.35); $('rule').style.opacity=st; $('rule').style.transform='scale('+(0.94+0.06*seg(T,19.2,19.7))+')';
  const c=seg(T,22.0,22.5); $('close').style.opacity=c; $('brand').style.opacity=1-c;
  $('court').style.opacity=1-c*0.7;
};
""" % dict(M=M, CW=CW, CH=CH, HOT=t['hot'], ACC=t['acc'])


if __name__ == "__main__":
    base.NOMBRE = "tactica-sur-3-alto"
    base.HTML, base.BODY, base.JS = HTML, BODY, JS
    base.main()
