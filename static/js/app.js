/* Home page: birth-details form -> navigates to the dedicated /kundli page */
let LANG = "en";
const $ = (s)=>document.querySelector(s);
const $$ = (s)=>document.querySelectorAll(s);
function esc(s){ return String(s==null?"":s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }

function applyLang(){
  document.documentElement.lang = LANG==="hi"?"hi":"en";
  $$("[data-i18n]").forEach(e=>{ e.textContent = t(e.dataset.i18n); });
  $$("[data-i18n-ph]").forEach(e=>{ e.placeholder = t(e.dataset.i18nPh); });
  $$(".langbtn button").forEach(b=>b.classList.toggle("on", b.dataset.lang===LANG));
  const ls=$("#langSel"); if(ls) ls.value=LANG;
}

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

function submitForm(ev){
  ev.preventDefault();
  const d=$("#dob").value, tm=$("#tob").value;
  if(!d || !tm){ alert(t("errFill")); return; }
  const [Y,M,D]=d.split("-").map(Number); const [hh,mm]=tm.split(":").map(Number);
  const gender = (document.querySelector('input[name=gender]:checked')||{}).value || "";
  const p = new URLSearchParams({
    name:$("#name").value||"", gender,
    year:Y, month:M, day:D, hour:hh, minute:mm,
    tz_offset:$("#tz").value||"5.5", lat:$("#lat").value||"0",
    lon:$("#lon").value||"0", place:$("#place").value||"", lang:LANG
  });
  window.location.href = "/kundli?" + p.toString();   /* open the separate result page */
}

window.addEventListener("DOMContentLoaded",()=>{
  $$(".langbtn button").forEach(b=>b.onclick=()=>{ LANG=b.dataset.lang; applyLang(); });
  const ls=$("#langSel"); if(ls) ls.addEventListener("change",e=>{ LANG=e.target.value; applyLang(); });
  $("#form").addEventListener("submit", submitForm);
  $("#place").addEventListener("input", e=>searchCity(e.target.value));
  applyLang();
});
