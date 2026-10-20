/* Jyotish Studio front-end */
const SIGNS_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const SIGNS_HI = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुम्भ","मीन"];
const SHORT = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"];
const PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"];
const PL_HI = {Sun:"सूर्य",Moon:"चन्द्र",Mars:"मंगल",Mercury:"बुध",Jupiter:"गुरु",Venus:"शुक्र",Saturn:"शनि",Rahu:"राहु",Ketu:"केतु",Ascendant:"लग्न"};
const PL_ABBR = {Sun:"Su",Moon:"Mo",Mars:"Ma",Mercury:"Me",Jupiter:"Ju",Venus:"Ve",Saturn:"Sa",Rahu:"Ra",Ketu:"Ke",Ascendant:"Asc"};

let DATA = null, CVARGA = 1, CSTYLE = "north";

const $ = (s)=>document.querySelector(s);
const $$ = (s)=>document.querySelectorAll(s);
function signName(i){ return LANG==="hi"?SIGNS_HI[i]:SIGNS_EN[i]; }
function plName(p){ return LANG==="hi"?(PL_HI[p]||p):p; }
function fmtDeg(d){ const deg=Math.floor(d); const m=Math.round((d-deg)*60); return `${deg}\u00b0${String(m).padStart(2,"0")}'`; }
function esc(s){ return String(s==null?"":s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }

/* ---------------- language ---------------- */
function applyLang(){
  document.documentElement.lang = LANG==="hi"?"hi":"en";
  $$("[data-i18n]").forEach(e=>{ e.textContent = t(e.dataset.i18n); });
  $$("[data-i18n-ph]").forEach(e=>{ e.placeholder = t(e.dataset.i18nPh); });
  $$(".langbtn button").forEach(b=>b.classList.toggle("on", b.dataset.lang===LANG));
  const ls=$("#langSel"); if(ls) ls.value=LANG;
  if(DATA) renderAll();
}

/* ---------------- form ---------------- */
async function searchCity(q){
  if(q.length<1){ $("#sugg").innerHTML=""; return; }
  const r = await fetch("/api/cities?q="+encodeURIComponent(q));
  const list = await r.json();
  if(!list.length){ $("#sugg").innerHTML=`<div class="item muted">—</div>`; return; }
  $("#sugg").innerHTML = list.map((c,i)=>
    `<div class="item" data-i="${i}"><b>${esc(c.name)}</b> <span>${esc(c.region)}</span></div>`).join("");
  $$("#sugg .item").forEach(el=>{
    el.onclick=()=>{ const c=list[+el.dataset.i]; $("#place").value=c.name+", "+c.region;
      $("#lat").value=c.lat; $("#lon").value=c.lon; $("#tz").value=c.tz; $("#sugg").innerHTML=""; };
  });
}

async function submitForm(ev){
  ev.preventDefault();
  const d=$("#dob").value, tm=$("#tob").value;
  if(!d || !tm){ alert(t("errFill")); return; }
  const [Y,M,D]=d.split("-").map(Number); const [hh,mm]=tm.split(":").map(Number);
  const gender = (document.querySelector('input[name=gender]:checked')||{}).value || "";
  const body = { name:$("#name").value, gender, year:Y, month:M, day:D, hour:hh, minute:mm, second:0,
    tz_offset:parseFloat($("#tz").value||"5.5"),
    lat:parseFloat($("#lat").value||"0"), lon:parseFloat($("#lon").value||"0"),
    place:$("#place").value };
  $("#loader").classList.add("on"); $("#results").style.display="none";
  try{
    const r=await fetch("/api/chart",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    const j=await r.json();
    if(j.error){ alert("Error: "+j.error); return; }
    DATA=j; CVARGA=1;
    renderAll(); $("#results").style.display="block";
    $("#results").scrollIntoView({behavior:"smooth"});
  }catch(e){ alert("Failed: "+e); }
  finally{ $("#loader").classList.remove("on"); }
}

/* ---------------- tabs ---------------- */
function initTabs(){
  $$(".tabs button").forEach(b=>b.onclick=()=>{
    $$(".tabs button").forEach(x=>x.classList.remove("on")); b.classList.add("on");
    $$(".section").forEach(s=>s.classList.remove("on"));
    $("#sec-"+b.dataset.tab).classList.add("on");
    if(b.dataset.tab==="tarot" && !$("#tarotBox").dataset.loaded) loadTarot();
    if(b.dataset.tab==="transit" && !$("#transitDate").value) $("#transitDate").value=new Date().toISOString().slice(0,10);
  });
}

/* ---------------- render ---------------- */
function renderAll(){
  if(!DATA) return;
  renderOverview(); renderCharts(); renderDasha(); renderShadbala();
  renderAshtaka(); renderYogas(); renderKP(); renderJaimini();
  renderLalKitab(); renderNadi(); renderNumerology();
}
function statBox(label,val){ return `<div class="stat"><b>${esc(val)}</b><span>${esc(label)}</span></div>`; }

function renderOverview(){
  const d=DATA, m=d.meta, a=d.ascendant, p=d.planets, pan=d.panchanga;
  let h=`<h2 class="title">${t("tabOverview")}</h2><div class="stats">
    ${statBox(t("ascendant"), signName(a.sign_index)+" "+fmtDeg(a.deg_in_sign))}
    ${statBox(t("moonSign"), signName(p.Moon.sign_index)+" "+fmtDeg(p.Moon.deg_in_sign))}
    ${statBox(t("sunSign"), signName(p.Sun.sign_index)+" "+fmtDeg(p.Sun.deg_in_sign))}
    ${statBox(t("ayanamsa"), m.ayanamsa.toFixed(3)+"\u00b0")}</div>`;
  h+=`<h3>${t("panchanga")}</h3><div class="stats">
    ${statBox(t("tithi"), pan.tithi+" ("+pan.tithi_number+")")}
    ${statBox(t("paksha"), pan.paksha)}
    ${statBox(t("yoga"), pan.yoga)}
    ${statBox(t("karana"), pan.karana)}
    ${statBox(t("vara"), LANG==="hi"?pan.vara_hi:pan.vara)}
    ${statBox(t("sunrise"), (m.sunrise||"").slice(11,16)+" UTC")}
    ${statBox(t("sunset"), (m.sunset||"").slice(11,16)+" UTC")}
    ${statBox(t("nakshatra"), LANG==="hi"?p.Moon.nakshatra_hi:p.Moon.nakshatra)}</div>`;
  if(d.current_dasha && d.current_dasha.length){
    h+=`<h3>${t("currentDasha")}</h3><div>`+d.current_dasha.map(c=>
      `<span class="pill">${c.level}: ${plName(c.lord)}</span>`).join("")+`</div>`;
  }
  h+=`<h3>${t("planetaryPositions")}</h3><table><thead><tr>
    <th>${t("planet")}</th><th>${t("sign")}</th><th>${t("degree")}</th><th>${t("house")}</th>
    <th>${t("nakshatra")}</th><th>${t("pada")}</th><th>${t("nLord")}</th><th>${t("motion")}</th></tr></thead><tbody>`;
  for(const pl of PLANETS){ const x=p[pl];
    h+=`<tr><td><b>${plName(pl)}</b> <span class="muted">${PL_ABBR[pl]}</span></td>
      <td>${signName(x.sign_index)}</td><td>${fmtDeg(x.deg_in_sign)}</td><td>${x.house}</td>
      <td>${LANG==="hi"?x.nakshatra_hi:x.nakshatra}</td><td>${x.pada}</td><td>${plName(x.nakshatra_lord)}</td>
      <td class="${x.retrograde?"retro":""}">${x.retrograde?t("retrograde"):t("direct")}</td></tr>`; }
  h+=`</tbody></table>`;
  h+=`<h3>${t("houses")}</h3><table><thead><tr><th>#</th><th>${t("sign")}</th><th>${t("lord")}</th><th>${t("occupants")}</th><th>${t("cusp")}</th></tr></thead><tbody>`;
  for(let i=1;i<=12;i++){ const hs=d.houses[i];
    h+=`<tr><td>${i}</td><td>${signName(hs.sign_index)}</td><td>${plName(hs.lord)}</td>
      <td>${hs.planets.map(pl=>`<span class="pill">${plName(pl)}</span>`).join("")||'<span class="muted">—</span>'}</td>
      <td>${fmtDeg(hs.cusp%30)} ${signName(Math.floor(hs.cusp/30))}</td></tr>`; }
  h+=`</tbody></table>`;
  $("#sec-overview").innerHTML=h;
}

/* -------- North Indian chart (SVG) -------- */
const NI_ANCHOR = {1:[50,27],2:[23,12],3:[12,23],4:[27,50],5:[12,77],6:[23,88],
                   7:[50,73],8:[77,88],9:[88,77],10:[73,50],11:[88,23],12:[77,12]};
const NI_NUM = {1:[50,13],2:[31,7],3:[7,31],4:[13,50],5:[7,69],6:[31,93],
                7:[50,87],8:[69,93],9:[93,69],10:[87,50],11:[93,31],12:[69,7]};
function northChart(vargaNum){
  const v = DATA.vargas[String(vargaNum)] || DATA.vargas[vargaNum];
  const lagnaSign = v.Ascendant;
  const byHouse={}; for(let i=1;i<=12;i++) byHouse[i]=[];
  for(const pl of PLANETS){ if(v[pl]!==undefined){ const h=(((v[pl]-lagnaSign)%12)+12)%12+1; byHouse[h].push(pl);} }
  byHouse[1].unshift("Ascendant");
  let s=`<svg class="nchart" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">`;
  s+=`<rect class="box" x="0.4" y="0.4" width="99.2" height="99.2"/>`;
  s+=`<path class="ln" d="M50 0 L100 50 L50 100 L0 50 Z"/>`;
  s+=`<path class="ln" d="M0 0 L100 100 M100 0 L0 100"/>`;
  for(let h=1;h<=12;h++){
    const [nx,ny]=NI_NUM[h]; const sgn=((lagnaSign+h-1)%12)+1;
    s+=`<text x="${nx}" y="${ny}" text-anchor="middle" style="font-size:2.7px;fill:#b0888a">${sgn}</text>`;
    const list=byHouse[h]; const [x,y]=NI_ANCHOR[h];
    list.forEach((pl,i)=>{
      const cls = pl==="Ascendant" ? "asc" : "pl";
      s+=`<text class="${cls}" x="${x}" y="${y+i*4.1}" text-anchor="middle">${PL_ABBR[pl]}</text>`;
    });
  }
  s+=`</svg>`;
  return s;
}
/* -------- South Indian chart -------- */
const SI_POS={0:[1,2],1:[1,3],2:[1,4],3:[2,4],4:[3,4],5:[4,4],6:[4,3],7:[4,2],8:[4,1],9:[3,1],10:[2,1],11:[1,1]};
function southChart(vargaNum){
  const v=DATA.vargas[String(vargaNum)]||DATA.vargas[vargaNum];
  const bySign={}; for(let i=0;i<12;i++) bySign[i]=[];
  for(const pl of PLANETS) if(v[pl]!==undefined) bySign[v[pl]].push(pl);
  if(v.Ascendant!==undefined) bySign[v.Ascendant].push("Ascendant");
  let cells="";
  for(let sg=0;sg<12;sg++){ const [r,c]=SI_POS[sg];
    const list=bySign[sg].map(pl=>`<span class="pl">${PL_ABBR[pl]}</span>`).join("");
    cells+=`<div class="cell" style="grid-row:${r};grid-column:${c}"><span class="sg">${SHORT[sg]}</span>${list}</div>`; }
  const info=DATA.varga_info[String(vargaNum)];
  cells+=`<div class="cell center"><div><div class="big">D${vargaNum}</div><div>${info?info.name_en:""}</div></div></div>`;
  return `<div class="schart">${cells}</div>`;
}
function renderCharts(){
  const opts=Object.keys(DATA.vargas).map(n=>
    `<option value="${n}" ${+n===CVARGA?"selected":""}>D${n} · ${DATA.varga_info[n].name_en} (${DATA.varga_info[n].name_hi})</option>`).join("");
  let h=`<h2 class="title">${t("tabCharts")}</h2><div class="notice">${t("chartsNote")}</div>
    <div class="grid g2">
      <div><label>${t("chooseVarga")}</label><select id="vargaSel">${opts}</select></div>
      <div><label>${t("chartStyle")}</label><select id="styleSel">
        <option value="north" ${CSTYLE==="north"?"selected":""}>${t("northIndian")}</option>
        <option value="south" ${CSTYLE==="south"?"selected":""}>${t("southIndian")}</option></select></div>
    </div>
    <div style="margin-top:14px">${CSTYLE==="north"?northChart(CVARGA):southChart(CVARGA)}</div>`;
  h+=`<h3>${t("vargaAll")}</h3><div style="overflow:auto"><table><thead><tr><th>Varga</th>`;
  for(const pl of PLANETS) h+=`<th>${PL_ABBR[pl]}</th>`; h+=`<th>As</th></tr></thead><tbody>`;
  for(const n of Object.keys(DATA.vargas)){ const v=DATA.vargas[n];
    h+=`<tr><td><b>D${n}</b> <span class="muted">${DATA.varga_info[n].name_en}</span></td>`;
    for(const pl of PLANETS) h+=`<td>${SHORT[v[pl]]}</td>`;
    h+=`<td>${SHORT[v.Ascendant]}</td></tr>`; }
  h+=`</tbody></table></div>`;
  $("#sec-charts").innerHTML=h;
  $("#vargaSel").onchange=e=>{ CVARGA=+e.target.value; renderCharts(); };
  $("#styleSel").onchange=e=>{ CSTYLE=e.target.value; renderCharts(); };
}

/* -------- dasha -------- */
function dashaRow(node,depth,cur){
  const isCur = cur && cur.some(c=>c.lord===node.lord && c.start===node.start);
  const style = isCur?`style="color:#6a1b9a;font-weight:600"`:"";
  if(node.sub && node.sub.length){
    return `<details style="margin-left:${depth*14}px"><summary ${style}>${plName(node.lord)} <span class="muted">${node.years.toFixed(1)}y · ${node.start.slice(0,10)} → ${node.end.slice(0,10)}</span></summary>
      ${node.sub.map(s=>dashaRow(s,depth+1,cur)).join("")}</details>`;
  }
  return `<div style="margin-left:${depth*14}px;padding:3px 0" ${style}>${plName(node.lord)} <span class="muted">${node.years.toFixed(2)}y ${node.start.slice(0,10)} → ${node.end.slice(0,10)}</span></div>`;
}
function renderDasha(){
  const d=DATA.dasha, cur=DATA.current_dasha;
  let h=`<h2 class="title">${t("tabDasha")}</h2><div class="stats">
    ${statBox(t("startingLord"), plName(d.starting_lord))}
    ${statBox(t("balanceAtBirth"), d.balance_years_at_birth.toFixed(2)+" yrs")}
    ${statBox(t("nakshatra"), LANG==="hi"?d.moon_nakshatra_hi:d.moon_nakshatra)}</div>`;
  if(cur&&cur.length) h+=`<h3>${t("currentDasha")}</h3>`+cur.map(c=>`<span class="pill">${plName(c.lord)}</span>`).join("");
  h+=`<h3>${t("mahadasha")} / ${t("antardasha")}</h3>`+d.mahadashas.map(m=>dashaRow(m,0,cur)).join("");
  $("#sec-dasha").innerHTML=h;
}

/* -------- shadbala -------- */
function renderShadbala(){
  const s=DATA.shadbala;
  let h=`<h2 class="title">${t("tabShadbala")}</h2><div style="overflow:auto"><table><thead><tr>
    <th>${t("planet")}</th><th>${t("sthana")}</th><th>${t("dig")}</th><th>${t("kala")}</th>
    <th>${t("cheshta")}</th><th>${t("naisargika")}</th><th>${t("drik")}</th><th>${t("total")}</th><th>${t("required")}</th></tr></thead><tbody>`;
  for(const pl of PLANETS.slice(0,7)){ const x=s[pl];
    h+=`<tr><td><b>${plName(pl)}</b></td><td>${x.sthana.total.toFixed(1)}</td><td>${x.dig.toFixed(1)}</td>
      <td>${x.kala.total.toFixed(1)}</td><td>${x.cheshta.toFixed(1)}</td><td>${x.naisargika.toFixed(1)}</td>
      <td>${x.drik.toFixed(1)}</td><td><b>${x.rupa.toFixed(2)}</b></td>
      <td>${x.required_rupa} ${x.sufficient?`<span class="pill good">✓</span>`:`<span class="pill bad">✗</span>`}</td></tr>`; }
  h+=`</tbody></table></div>`;
  h+=`<h3>${t("kala")}</h3><div style="overflow:auto"><table><thead><tr><th>${t("planet")}</th><th>nathonnatha</th><th>paksha</th><th>tribhaga</th><th>varsha</th><th>masa</th><th>dina</th><th>hora</th><th>ayana</th></tr></thead><tbody>`;
  for(const pl of PLANETS.slice(0,7)){ const k=s[pl].kala;
    h+=`<tr><td>${plName(pl)}</td><td>${k.nathonnatha.toFixed(1)}</td><td>${k.paksha.toFixed(1)}</td>
      <td>${k.tribhaga.toFixed(1)}</td><td>${k.varsha.toFixed(1)}</td><td>${k.masa.toFixed(1)}</td>
      <td>${k.dina.toFixed(1)}</td><td>${k.hora.toFixed(1)}</td><td>${k.ayana.toFixed(1)}</td></tr>`; }
  h+=`</tbody></table></div>`;
  $("#sec-shadbala").innerHTML=h;
}

/* -------- ashtakavarga -------- */
function bavRow(name,arr,total){
  return `<tr><td><b>${name}</b></td>`+arr.map(v=>`<td>${v}</td>`).join("")+`<td><b>${total!=null?total:arr.reduce((a,b)=>a+b,0)}</b></td></tr>`;
}
function renderAshtaka(){
  const a=DATA.ashtakavarga;
  let head=`<tr><th>${t("planet")}</th>`+SIGNS_EN.map((s,i)=>`<th>${SHORT[i]}</th>`).join("")+`<th>${t("total337")}</th></tr>`;
  let h=`<h2 class="title">${t("tabAshtaka")}</h2><h3>${t("bav")}</h3><div style="overflow:auto"><table><thead>${head}</thead><tbody>`;
  for(const pl of PLANETS.slice(0,7)) h+=bavRow(plName(pl),a[pl].bav,a[pl].total);
  h+=bavRow("<b>"+t("sav")+"</b>",a.SAV.bav,a.SAV.total);
  h+=`</tbody></table></div>`;
  const ascSign=DATA.ascendant.sign_index;
  h+=`<h3>${t("sav")} — ${t("houses")}</h3><div style="overflow:auto"><table><thead><tr>`+[1,2,3,4,5,6,7,8,9,10,11,12].map(i=>`<th>${i}</th>`).join("")+`</tr></thead><tbody><tr>`;
  for(let hh=1;hh<=12;hh++){ h+=`<td>${a.SAV.bav[(ascSign+hh-1)%12]}</td>`; }
  h+=`</tr></tbody></table></div>`;
  h+=`<h3>${t("bav")} — after Shodhana</h3><div style="overflow:auto"><table><thead>${head}</thead><tbody>`;
  for(const pl of PLANETS.slice(0,7)) h+=bavRow(plName(pl),a[pl].after_shodhana);
  h+=`</tbody></table></div>`;
  $("#sec-ashtaka").innerHTML=h;
}

/* -------- yogas -------- */
function renderYogas(){
  const y=DATA.yogas, dz=DATA.doshas;
  function block(list,title,cls){
    if(!list.length) return `<h3>${title}</h3><p class="muted">—</p>`;
    return `<h3>${title}</h3>`+list.map(x=>`<div style="border:1px solid var(--line);border-radius:10px;padding:11px;margin:8px 0">
      <div><span class="pill ${cls}">${LANG==="hi"?x.name_hi:x.name_en}</span>
      <span class="muted">${x.planets.map(plName).join(", ")}</span></div>
      <div style="font-size:13px;margin-top:5px">${LANG==="hi"?x.description_hi:x.description_en}</div></div>`).join("");
  }
  $("#sec-yogas").innerHTML=`<h2 class="title">${t("tabYogas")}</h2>`+block(y,t("yogasFound"),"good")+block(dz,t("doshasFound"),"bad");
}

/* -------- KP -------- */
function renderKP(){
  const k=DATA.kp;
  let h=`<h2 class="title">${t("tabKP")}</h2><h3>${t("rulingPlanets")}</h3><div>`+
    k.ruling_planets.ruling_planets.map(p=>`<span class="pill">${plName(p)}</span>`).join("")+`</div>`;
  h+=`<h3>${t("cuspSubLords")}</h3><div style="overflow:auto"><table><thead><tr><th>#</th><th>${t("sign")}</th><th>${t("signLord")}</th><th>${t("starLord")}</th><th>${t("subLord")}</th><th>${t("subSub")}</th></tr></thead><tbody>`;
  for(let i=1;i<=12;i++){ const c=k.cusps[i];
    h+=`<tr><td>${i}</td><td>${signName(c.sign_index)}</td><td>${plName(c.sign_lord)}</td>
      <td>${plName(c.star_lord)}</td><td><b>${plName(c.sub_lord)}</b></td><td>${plName(c.sub_sub_lord)}</td></tr>`; }
  h+=`</tbody></table></div>`;
  h+=`<h3>${t("planetSubLords")}</h3><table><thead><tr><th>${t("planet")}</th><th>${t("signLord")}</th><th>${t("starLord")}</th><th>${t("subLord")}</th><th>${t("subSub")}</th></tr></thead><tbody>`;
  for(const pl of PLANETS){ const c=k.planets[pl];
    h+=`<tr><td><b>${plName(pl)}</b></td><td>${plName(c.sign_lord)}</td><td>${plName(c.star_lord)}</td>
      <td><b>${plName(c.sub_lord)}</b></td><td>${plName(c.sub_sub_lord)}</td></tr>`; }
  h+=`</tbody></table>`;
  h+=`<h3>${t("significators")}</h3><table><thead><tr><th>#</th><th>${t("sign")}</th><th>${t("lord")}</th><th>${t("significators")}</th></tr></thead><tbody>`;
  for(let i=1;i<=12;i++){ const s=k.significators[i];
    h+=`<tr><td>${i}</td><td>${s.sign}</td><td>${plName(s.owner)}</td>
      <td>${s.significators.map(p=>`<span class="pill">${plName(p)}</span>`).join("")}</td></tr>`; }
  h+=`</tbody></table>`;
  $("#sec-kp").innerHTML=h;
}

/* -------- Jaimini -------- */
function renderJaimini(){
  const j=DATA.jaimini;
  let h=`<h2 class="title">${t("tabJaimini")}</h2><h3>${t("charaKarakas")}</h3><table><thead><tr><th>Karaka</th><th>${t("planet")}</th><th>${t("degree")}</th></tr></thead><tbody>`;
  const KORDER=["AK","AmK","BK","MK","PiK","PK","GK","DK"];
  for(const k of KORDER){ const c=j.chara_karakas[k]; if(!c) continue;
    h+=`<tr><td><b>${k}</b> <span class="muted">${c.full_name}</span></td><td>${plName(c.planet)}</td><td>${fmtDeg(c.degree)}</td></tr>`; }
  h+=`</tbody></table>`;
  h+=`<h3>${t("karakamsa")}</h3><span class="pill">${signName(j.karakamsa.sign_index)}</span>`;
  h+=`<h3>${t("arudhaPadas")}</h3><table><thead><tr><th>Bhava</th><th>${t("sign")}</th><th>${t("lord")}</th></tr></thead><tbody>`;
  for(let i=1;i<=12;i++){ const a=j.arudha_padas[i];
    h+=`<tr><td>A${i}</td><td>${signName(a.sign_index)}</td><td>${plName(a.lord)}</td></tr>`; }
  h+=`</tbody></table>`;
  h+=`<h3>${t("charaDasha")}</h3><div>`+j.chara_dasha.map(x=>`<span class="pill">${signName(x.sign_index)} · ${x.years}y</span>`).join("")+`</div>`;
  $("#sec-jaimini").innerHTML=h;
}

/* -------- Lal Kitab -------- */
function renderLalKitab(){
  const l=DATA.lalkitab;
  let h=`<h2 class="title">${t("tabLalKitab")}</h2>`;
  if(l.blind_chart) h+=`<div class="notice">⚠ ${t("blindChart")}</div>`;
  if(l.half_blind_chart) h+=`<div class="notice">⚠ ${t("halfBlind")}</div>`;
  h+=`<h3>${t("lalChart")} & ${t("pakkaGhar")}</h3><table><thead><tr><th>${t("planet")}</th><th>${t("house")}</th><th>${t("pakkaGhar")}</th><th>${t("status")}</th></tr></thead><tbody>`;
  for(const pl of Object.keys(l.planets)){ const x=l.planets[pl];
    const tags=[]; if(x.at_home) tags.push(`<span class="pill good">${t("atHome")}</span>`);
    if(x.exalted) tags.push(`<span class="pill">${t("exalted")}</span>`);
    if(x.debilitated) tags.push(`<span class="pill bad">${t("debilitated")}</span>`);
    if(x.sleeping) tags.push(`<span class="pill bad">${t("sleeping")}</span>`);
    h+=`<tr><td><b>${plName(pl)}</b></td><td>${x.house}</td><td>${x.pakka_ghar.join(", ")}</td><td>${tags.join(" ")||"—"}</td></tr>`; }
  h+=`</tbody></table>`;
  if(l.dharmi_planets.length) h+=`<h3>${t("dharmi")}</h3><div>`+l.dharmi_planets.map(p=>`<span class="pill good">${plName(p)}</span>`).join("")+`</div>`;
  if(l.debts.length) h+=`<h3>${t("debts")}</h3><ul>`+l.debts.map(d=>`<li>${esc(d)}</li>`).join("")+`</ul>`;
  h+=`<h3>${t("remedies")}</h3>`;
  for(const pl of Object.keys(l.remedies))
    h+=`<div style="margin:8px 0"><b>${plName(pl)}</b><ul>`+l.remedies[pl].map(r=>`<li>${esc(r)}</li>`).join("")+`</ul></div>`;
  $("#sec-lalkitab").innerHTML=h;
}

/* -------- Nadi -------- */
function renderNadi(){
  const n=DATA.nadi;
  let h=`<h2 class="title">${t("tabNadi")}</h2><a href="/nadi-bnn" class="btn" style="display:inline-block;margin-bottom:12px;text-decoration:none">${t("openBnn")} &rarr;</a><div class="notice">${LANG==="hi"?
    "पारंपरिक ताड़-पत्र नाड़ी पांडुलिपि-खोज पद्धति है; यहाँ गणना-योग्य नाड़ी अंश (D150) दिया गया है।":
    "The classical palm-leaf Nadi is a manuscript-lookup system; here we compute the derivable Nadi Amsa (D150)."}</div>`;
  h+=`<h3>${t("nadiAmsa")}</h3><table><thead><tr><th>${t("planet")}</th><th>${t("sign")}</th><th>${t("nadiDivision")}</th></tr></thead><tbody>`;
  for(const pl of PLANETS.concat(["Ascendant"])){ const a=n.amsa[pl];
    h+=`<tr><td><b>${plName(pl)}</b></td><td>${signName(a.sign_index)}</td><td>${a.nadi_within_sign} / 150</td></tr>`; }
  h+=`</tbody></table>`;
  h+=`<h3>${t("nadiProgression")}</h3><table><thead><tr><th>${t("planet")}</th><th>${t("sign")}</th><th>${t("nadiDivision")}</th></tr></thead><tbody>`;
  for(const pl of PLANETS.concat(["Ascendant"])){ const a=n.progression[pl];
    h+=`<tr><td><b>${plName(pl)}</b></td><td>${signName(a.sign_index)}</td><td>${a.nadi_within_sign} / 150</td></tr>`; }
  h+=`</tbody></table>`;
  $("#sec-nadi").innerHTML=h;
}

/* -------- Numerology -------- */
function renderNumerology(){
  const n=DATA.numerology;
  const box=(k,v)=>`<div class="stat"><b>${v.number}</b><span>${k} · ${plName(String(v.ruler).split(" ")[0])}</span>
    <div style="font-size:12px;color:#5b4b66;margin-top:4px">${LANG==="hi"?v.meaning_hi:v.meaning_en}</div></div>`;
  $("#sec-numerology").innerHTML=`<h2 class="title">${t("tabNumerology")}</h2><div class="stats" style="grid-template-columns:repeat(3,1fr)">
    ${box(t("lifePath"),n.life_path)}${box(t("birthday"),n.birthday)}
    ${box(t("expression")+" ("+t("pythagorean")+")",n.expression_pythagorean)}
    ${box(t("expression")+" ("+t("chaldean")+")",n.expression_chaldean)}
    ${box(t("soulUrge"),n.soul_urge)}${box(t("personality"),n.personality)}
    ${box(t("personalYear"),n.personal_year)}</div>`;
}

/* -------- Transit -------- */
async function loadTransit(){
  const dt=$("#transitDate").value; if(!dt){ alert(t("transitDate")); return; }
  const [Y,M,D]=dt.split("-").map(Number);
  const body={year:Y,month:M,day:D,hour:12,minute:0,tz_offset:parseFloat($("#tz").value||"5.5"),
    lat:parseFloat($("#lat").value||"0"),lon:parseFloat($("#lon").value||"0"),
    natal_asc_sign:DATA.ascendant.sign_index, natal_moon_sign:DATA.planets.Moon.sign_index};
  $("#transitBox").innerHTML='<div class="loader on"><div class="spin"></div></div>';
  const r=await fetch("/api/transit",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const j=await r.json();
  if(j.error){ $("#transitBox").innerHTML='<p class="muted">'+esc(j.error)+'</p>'; return; }
  let h=`<table><thead><tr><th>${t("planet")}</th><th>${t("sign")}</th><th>${t("degree")}</th><th>${t("nakshatra")}</th><th>${t("houseFromLagna")}</th><th>${t("houseFromMoon")}</th></tr></thead><tbody>`;
  for(const pl of PLANETS){ const x=j.planets[pl];
    h+=`<tr><td><b>${plName(pl)}</b></td><td>${signName(x.sign_index)}</td><td>${fmtDeg(x.deg_in_sign)}</td>
      <td>${LANG==="hi"?x.nakshatra_hi:x.nakshatra}</td><td>${x.house_from_lagna}</td><td>${x.house_from_moon}</td></tr>`; }
  h+=`</tbody></table>`;
  $("#transitBox").innerHTML=h;
}

/* -------- Tarot -------- */
async function loadTarot(){
  const spread=$("#tarotSpread").value;
  const r=await fetch("/api/tarot?spread="+spread);
  const j=await r.json();
  $("#tarotBox").innerHTML=j.cards.map(c=>`<div style="border:1px solid var(--line);border-radius:10px;padding:12px;margin:8px 0">
    <div class="muted" style="font-size:12px">${LANG==="hi"?c.position_hi:c.position_en}</div>
    <div style="font-size:16px;color:#4a148c;margin:3px 0"><b>${esc(c.card)}</b> <span class="muted">${esc(c.card_hi)}</span>
      <span class="pill ${c.reversed?"bad":"good"}">${c.reversed?t("reversed"):t("upright")}</span></div>
    <div style="font-size:13px">${esc(c.meaning_en)}</div></div>`).join("");
  $("#tarotBox").dataset.loaded="1";
}

/* ---------------- init ---------------- */
window.addEventListener("DOMContentLoaded",()=>{
  $$(".langbtn button").forEach(b=>b.onclick=()=>{ LANG=b.dataset.lang; applyLang(); });
  $("#langSel").addEventListener("change",e=>{ LANG=e.target.value; applyLang(); });
  $("#form").addEventListener("submit", submitForm);
  $("#place").addEventListener("input", e=>searchCity(e.target.value));
  $("#printBtn").onclick=()=>window.print();
  $("#tarotSpread").addEventListener("change", ()=>{ $("#tarotBox").dataset.loaded=""; loadTarot(); });
  $("#tarotBtn").onclick=()=>{ $("#tarotBox").dataset.loaded=""; loadTarot(); };
  $("#transitBtn").onclick=loadTransit;
  applyLang(); initTabs();
});
