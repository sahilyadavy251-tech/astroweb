/* Kundli Matching (Gun Milan) page */
/* NB: LANG is declared in i18n.js (shared) */
const $ = (s)=>document.querySelector(s);
const $$ = (s)=>document.querySelectorAll(s);
function esc(s){ return String(s==null?"":s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }

function applyLang(){
  document.documentElement.lang = LANG==="hi"?"hi":"en";
  $$("[data-i18n]").forEach(e=>{ e.textContent = t(e.dataset.i18n); });
  $$("[data-i18n-ph]").forEach(e=>{ e.placeholder = t(e.dataset.i18nPh); });
  $$(".langbtn button").forEach(b=>b.classList.toggle("on", b.dataset.lang===LANG));
}

function wireCity(inputId, suggId, latId, lonId, tzId){
  const inp=$("#"+inputId);
  inp.addEventListener("input", async ()=>{
    const q=inp.value;
    if(!q){ $("#"+suggId).innerHTML=""; return; }
    const r=await fetch("/api/cities?q="+encodeURIComponent(q));
    const list=await r.json();
    $("#"+suggId).innerHTML = list.map((c,i)=>
      `<div class="item" data-i="${i}"><b>${esc(c.name)}</b> <span>${esc(c.region)}</span></div>`).join("") ||
      `<div class="item muted">—</div>`;
    $$("#"+suggId+" .item").forEach(el=>{
      el.onclick=()=>{ const c=list[+el.dataset.i];
        inp.value=c.name+", "+c.region;
        $("#"+latId).value=c.lat; $("#"+lonId).value=c.lon; $("#"+tzId).value=c.tz;
        $("#"+suggId).innerHTML=""; };
    });
  });
}

function person(n){
  const d=$("#d"+n).value, tm=$("#t"+n).value;
  if(!d || !tm) return null;
  const [Y,M,D]=d.split("-").map(Number); const [hh,mm]=tm.split(":").map(Number);
  return { name:$("#n"+n).value||"", year:Y, month:M, day:D, hour:hh, minute:mm,
    tz_offset:parseFloat($("#tz"+n).value||"5.5"),
    lat:parseFloat($("#la"+n).value||"0"), lon:parseFloat($("#lo"+n).value||"0"),
    place:$("#p"+n).value||"" };
}

async function runMatch(){
  const a=person(1), b=person(2);
  if(!a || !b){ alert(t("errFill")); return; }
  $("#loader").classList.add("on"); $("#out").innerHTML=""; $("#errbox").style.display="none";
  try{
    const r=await fetch("/api/matching",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({person1:a, person2:b})});
    const j=await r.json();
    if(j.error) throw new Error(j.error);
    render(j);
  }catch(e){
    $("#errbox").style.display="block";
    $("#errmsg").innerHTML="<b>"+(LANG==="hi"?"त्रुटि":"Error")+":</b> "+esc(e.message||e);
  }finally{ $("#loader").classList.remove("on"); }
}

function render(j){
  const HI = LANG==="hi";
  const col = j.total>=28?"#2e7d32": j.total>=21?"#7cb342": j.total>=18?"#ef6c00":"#c62828";
  let h = `<div class="card" style="text-align:center">
    <div style="font-size:13px;color:var(--muted)">${esc(j.name_a||(HI?"व्यक्ति 1":"Person 1"))} &nbsp;❤&nbsp; ${esc(j.name_b||(HI?"व्यक्ति 2":"Person 2"))}</div>
    <div style="font-size:46px;font-weight:800;color:${col};line-height:1.1">${j.total}<span style="font-size:20px;color:var(--muted)">/36</span></div>
    <div style="font-size:16px;font-weight:700;color:${col}">${HI?j.verdict_hi:j.verdict_en} (${j.pct}%)</div>
    <div style="margin-top:10px;display:flex;gap:14px;justify-content:center;flex-wrap:wrap;font-size:12.5px;color:var(--muted)">
      <span>${HI?"चन्द्र नक्षत्र":"Moon nakshatra"}: <b>${esc(HI?j.moon_a.nakshatra_hi:j.moon_a.nakshatra)}</b> / <b>${esc(HI?j.moon_b.nakshatra_hi:j.moon_b.nakshatra)}</b></span>
    </div></div>`;

  h += `<div class="card"><h3>${HI?"अष्टकूट मिलान":"Ashtakoot breakdown"}</h3>
    <div style="overflow:auto"><table><thead><tr><th>${HI?"कूट":"Koota"}</th><th>${HI?"अंक":"Points"}</th><th>${HI?"विवरण":"Details"}</th></tr></thead><tbody>`;
  j.rows.forEach(r=>{
    const pct=r.pts/r.max;
    const c = pct>=0.75?"#2e7d32": pct>=0.4?"#ef6c00":"#c62828";
    h += `<tr><td><b>${r.k}</b></td><td style="color:${c};font-weight:700">${r.pts} / ${r.max}</td><td class="muted">${esc(r.note)}</td></tr>`;
  });
  h += `<tr><td><b>${HI?"कुल":"Total"}</b></td><td><b>${j.total} / 36</b></td><td class="muted">${j.pct}%</td></tr>`;
  h += `</tbody></table></div>`;
  if(j.doshas.length) h += `<h3>${HI?"दोष":"Doshas"}</h3><div>`+j.doshas.map(d=>`<span class="pill bad">${esc(d)}</span>`).join("")+`</div>`;
  else h += `<h3>${HI?"दोष":"Doshas"}</h3><p class="muted">${HI?"कोई बड़ा दोष नहीं":"No major dosha"}</p>`;
  h += `</div>`;

  h += `<div class="card"><h3>${HI?"मंगल दोष (मांगलिक)":"Mangal dosha (Manglik)"}</h3><div style="overflow:auto"><table>
    <thead><tr><th></th><th>${HI?"मंगल भाव":"Mars house"}</th><th>${HI?"मांगलिक":"Manglik"}</th></tr></thead><tbody>
    <tr><td><b>${esc(j.name_a||(HI?"व्यक्ति 1":"Person 1"))}</b></td><td>${j.manglik_a.house}</td>
      <td>${j.manglik_a.manglik?`<span class="pill bad">${HI?"हाँ":"Yes"}</span>`:`<span class="pill good">${HI?"नहीं":"No"}</span>`}</td></tr>
    <tr><td><b>${esc(j.name_b||(HI?"व्यक्ति 2":"Person 2"))}</b></td><td>${j.manglik_b.house}</td>
      <td>${j.manglik_b.manglik?`<span class="pill bad">${HI?"हाँ":"Yes"}</span>`:`<span class="pill good">${HI?"नहीं":"No"}</span>`}</td></tr>
    </tbody></table></div></div>`;

  h += `<div style="text-align:center;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
    <a href="/" class="btn ghost" style="text-decoration:none">← ${HI?"नई कुंडली":"New Kundli"}</a>
    <button class="btn ghost" onclick="window.print()">${HI?"प्रिंट / PDF":"Print / Save PDF"}</button></div>`;

  $("#out").innerHTML=h;
  $("#out").scrollIntoView({behavior:"smooth"});
}

window.addEventListener("DOMContentLoaded",()=>{
  $$(".langbtn button").forEach(b=>b.onclick=()=>{ LANG=b.dataset.lang; applyLang(); });
  wireCity("p1","s1","la1","lo1","tz1");
  wireCity("p2","s2","la2","lo2","tz2");
  $("#matchBtn").onclick=runMatch;
  applyLang();
});
