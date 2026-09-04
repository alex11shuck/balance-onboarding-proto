/* Balance onboarding prototype engine.
   Decks are JSON card arrays with optional `branch` predicates, mirroring hoth's session.json + Lua card engine.
   Routes: #/            landing
           #/<deck>      start deck fresh
           #/<deck>/<id> jump to a card (missing answers filled from a demo persona)
           #/map/<deck>  flow map (spec view)
   ?notes=1 shows build notes (template, feasibility, sources) beside / inside the frame. */
(function(){
const $ = s => document.querySelector(s);
const app = $('#app');
const DECKS = {};
const S = { deckId:null, deck:null, idx:-1, a:{}, L:{}, hist:[], notes:false, sheet:false };
const qs = new URLSearchParams(location.search);
S.notes = qs.get('notes') === '1';

const PERSONA = { name:'Sam', age:34, age_count:1034000, age_range:'25-44', gender:'prefer_not', hdyhau:'facebook_or_instagram',
  goals:['stress','sleep'], goal_1:'stress', goal_2:'sleep', goal_stress:'yes', goal_sleep:'yes', goal_mood:'no', goal_focus:'no',
  how_often_feel_stress:'sometimes', how_experience_stress:['anxious_thoughts','difficulty_sleeping'], stress_source:'work_or_school',
  ready_to_sleep:'no', sleep_trouble:'sometimes', keep_awake:'stress', exercise:'2', schedule:'busy', future:['calm_nights','clear_head','present'],
  has_meditated_before:'none', commitment:'5', when_to_meditate:'evening', reminder_time:'6:00 pm', bedtime:'10:00 pm' };
const PERSONA_L = { name:'Sam', age_count:'1,034,000', goal_1:'Reduce Stress', goal_2:'Improve Sleep', hdyhau:'Facebook or Instagram', how_often_feel_stress:'Sometimes',
  how_experience_stress:'Anxious thoughts, Difficulty sleeping', stress_source:'Work or school', sleep_trouble:'Sometimes', keep_awake:'Stress',
  exercise:'A couple of times a week', schedule:'Busy most days', future:'Calm nights, A clearer head, Feeling present', has_meditated_before:'New to meditation', commitment:'5 days a week', when_to_meditate:'Evening' };

const GOAL_LABEL = { stress:'Reduce Stress', sleep:'Improve Sleep', focus:'Increase Focus', mood:'Improve Mood' };
const GOAL_COLOR = { stress:'purple_haze', sleep:'polar_blue', focus:'apricot', mood:'misty_peach' };
const TAG_LABEL = { existing:'Existing template', unused:'Built, unused', copy:'Copy change', swift:'Swift bookend', superwall:'Superwall dashboard', new:'New template (eng)', cut:'Cut in this version' };

/* ---------- helpers ---------- */
const esc = s => String(s==null?'':s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const lines = t => Array.isArray(t) ? t.join('<br>') : (t||'');
const H = { lower:x=>String(x||'').toLowerCase(), first:x=>Array.isArray(x)?x[0]:x,
  list:(x)=>{ const arr = Array.isArray(x)? x : String(x||'').split(', ').filter(Boolean); if(arr.length<=1) return arr[0]||''; return arr.slice(0,-1).join(', ')+' and '+arr[arr.length-1]; },
  goal:(g)=>GOAL_LABEL[g]||g, n:(x)=>Number(x||0).toLocaleString() };
function tpl(str){ if(!str) return ''; return String(str).replace(/\{\{([^}]+)\}\}/g, (_,e)=>{ try{ const v = new Function('a','L','H','return ('+e+')')(S.a,S.L,H); return v==null?'':String(v);}catch(err){ return '['+e+']'; } }); }
function tl(t){ return tpl(lines(t)); }
function branchOK(card){ if(!card.branch) return true; try{ return !!new Function('a','L','return ('+card.branch+')')(S.a,S.L);}catch(e){ console.warn('branch error',card.id,e); return true; } }
function ageCount(age){ const a=Number(age)||34; return Math.round(1350000 * Math.exp(-Math.pow((a-27)/16,2)) + 180000); }
function setA(q,id,label){ S.a[q]=id; S.L[q]=label; if(q==='age'){ S.a.age_count=ageCount(id); S.L.age_count=S.a.age_count.toLocaleString(); } }
function visibleCards(){ return S.deck.cards.filter(c=>branchOK(c)); }
function colorVar(c){ return c ? `var(--${c})` : 'var(--purple_haze)'; }
function iconImg(name){ if(!name) return ''; if(name.length<=3) return `<span class="ico" style="font-size:30px;display:flex;align-items:center;justify-content:center">${name}</span>`; return `<img src="assets/icons/${name}.png" alt="" onerror="this.style.visibility='hidden'">`; }

/* ---------- routing ---------- */
window.addEventListener('hashchange', route);
async function loadDeck(id){ if(DECKS[id]) return DECKS[id]; const r = await fetch(`decks/${id}.json?v=${Date.now()%100000}`); const d = await r.json(); DECKS[id]=d; return d; }
async function route(){
  const h = location.hash.replace(/^#\/?/,'');
  const parts = h.split('/').filter(Boolean);
  if(!parts.length){ renderLanding(); return; }
  if(parts[0]==='map'){ const d = await loadDeck(parts[1]||'wishlist'); renderMap(d); return; }
  const deck = await loadDeck(parts[0]);
  if(S.deckId!==parts[0] || S.idx<0){ S.deckId=parts[0]; S.deck=deck; S.a={}; S.L={}; S.hist=[]; S.idx=-1; }
  if(parts[1]){ const i = deck.cards.findIndex(c=>c.id===parts[1]); if(i>=0){ if(!Object.keys(S.a).length){ Object.assign(S.a, PERSONA); Object.assign(S.L, PERSONA_L); } S.idx=i; S.hist=[]; renderCard(); return; } }
  if(S.idx<0){ S.idx = deck.cards.findIndex(c=>branchOK(c)); }
  renderCard();
}
function go(delta){
  const cards = S.deck.cards;
  if(delta<0){ if(S.hist.length){ S.idx = S.hist.pop(); renderCard(); } return; }
  let i = S.idx+1; while(i<cards.length && !branchOK(cards[i])) i++;
  if(i>=cards.length){ return; }
  S.hist.push(S.idx); S.idx=i; renderCard();
}
function setHash(){ const id = S.deck.cards[S.idx]?.id; history.replaceState(null,'',`${location.pathname}${location.search}#/${S.deckId}/${id}`); }

/* ---------- landing ---------- */
async function renderLanding(){
  const w = await loadDeck('wishlist'); const c = await loadDeck('constrained');
  const stat = d => { const q = d.cards.filter(x=>['question','scrollableQuestion','multiselect','keyboard','slider','commitment','goalRanking'].includes(x.type)).length; return `<div class="stats"><span><b>${d.cards.length}</b> screens</span><span><b>${q}</b> asks</span><span><b>${d.cards.filter(x=>x.notes&&x.notes.tag==='new').length}</b> new templates</span></div>`; };
  const notesQ = S.notes ? '?notes=1' : '';
  app.innerHTML = `<div class="landing">
    <h1>Balance onboarding prototype</h1>
    <p class="sub">Two clickable versions of a Calmer-style flow in Balance's skin, from welcome to today's paywall. Built Sep 4, 2026 for the Balance top-of-funnel bet. Tap through on a phone, or open the flow map for the screen-by-screen spec. Copy in <b>[brackets]</b> is a placeholder to verify.</p>
    <div class="versions">
      <div class="vcard"><h2>${esc(w.name)}</h2><p>${esc(w.description)}</p>${stat(w)}<div class="row"><a class="btn" href="${location.pathname}${notesQ}#/wishlist">Start</a><a class="btn secondary small" href="${location.pathname}${notesQ}#/map/wishlist">Flow map</a></div></div>
      <div class="vcard"><h2>${esc(c.name)}</h2><p>${esc(c.description)}</p>${stat(c)}<div class="row"><a class="btn" href="${location.pathname}${notesQ}#/constrained">Start</a><a class="btn secondary small" href="${location.pathname}${notesQ}#/map/constrained">Flow map</a></div></div>
    </div>
    <div class="legend"><h3>Reading the build notes</h3>
      Build notes show each screen's template and what it costs to ship. Turn them on with <a href="${location.pathname}?notes=${S.notes?'0':'1'}#/">${S.notes?'notes off':'notes on'}</a>. Tags:
      <div class="row" style="margin-top:8px">${Object.keys(TAG_LABEL).map(t=>`<span class="tag tag-${t}">${TAG_LABEL[t]}</span>`).join('')}</div>
      <p style="margin:12px 0 0">The real onboarding is a JSON card array read by a Lua card engine, so every screen tagged <i>existing</i> or <i>built, unused</i> is a content change in <code>session.json</code>, not engineering. <i>Copy change</i> means new words on a card that already ships. <i>Swift bookend</i> and <i>Superwall dashboard</i> live outside the deck. <i>New template</i> is Lua engine work that ships to Android too.</p>
    </div>
  </div>`;
}

/* ---------- flow map ---------- */
function renderMap(d){
  const notesQ = S.notes ? '?notes=1' : '';
  const asks = d.cards.filter(x=>['question','scrollableQuestion','multiselect','keyboard','slider','commitment','goalRanking'].includes(x.type));
  const tags = {}; d.cards.forEach(c=>{ const t=(c.notes&&c.notes.tag)||'existing'; tags[t]=(tags[t]||0)+1; });
  app.innerHTML = `<div class="map">
    <p><a href="${location.pathname}${notesQ}#/">← All versions</a></p>
    <h1>${esc(d.name)}: flow map</h1>
    <p style="color:var(--dark);max-width:760px">${esc(d.description)} Core questions are counted the way the 23-app Health &amp; Fitness benchmark counts them (field median 6, ceiling 12; Balance today 8 on the stress + sleep path).</p>
    <div class="summary"><div class="stat"><b>${d.cards.length}</b>screens in the deck</div><div class="stat"><b>${asks.length}</b>asks (questions, pickers, entries)</div>${Object.keys(tags).map(t=>`<div class="stat"><b>${tags[t]}</b><span class="tag tag-${t}">${TAG_LABEL[t]||t}</span></div>`).join('')}</div>
    <div style="overflow-x:auto"><table><thead><tr><th>#</th><th>Screen</th><th>Type / template</th><th>Shown when</th><th>Tag</th><th>Source</th><th>Notes</th></tr></thead><tbody>
    ${d.cards.map((c,i)=>{ const n=c.notes||{}; return `<tr><td class="n">${i+1}</td><td><a href="${location.pathname}${notesQ}#/${d.id}/${c.id}"><b>${esc((Array.isArray(c.title)?c.title.join(' '):(c.title||c.id)).replace(/<[^>]+>/g,''))}</b></a><br><code>${esc(c.id)}</code></td><td>${esc(c.type)}${n.template&&n.template!==c.type?`<br><code>${esc(n.template)}</code>`:''}</td><td>${c.branch?`<code>${esc(c.branch)}</code>`:'everyone'}</td><td><span class="tag tag-${n.tag||'existing'}">${TAG_LABEL[n.tag]||n.tag||'Existing template'}</span></td><td>${n.calmer?`Calmer ${esc(n.calmer)}<br>`:''}${esc(n.evidence||'')}</td><td>${esc(n.why||'')}${n.loss?`<br><b>Lost vs wish list:</b> ${esc(n.loss)}`:''}${n.fills&&n.fills.length?`<br><b>Verify:</b> ${n.fills.map(esc).join('; ')}`:''}</td></tr>`; }).join('')}
    </tbody></table></div></div>`;
}

/* ---------- card rendering ---------- */
function renderCard(){
  const card = S.deck.cards[S.idx]; if(!card){ return; }
  setHash();
  const vis = visibleCards(); const pos = Math.max(0, vis.indexOf(card)); const pct = Math.round(((pos+1)/vis.length)*100);
  const phase = S.deck.phases && card.phase ? `<div class="steps">Part ${card.phase} of ${S.deck.phases.length} · ${esc(S.deck.phases[card.phase-1])}</div>` : '';
  const back = S.hist.length ? `<button class="back" aria-label="Back">‹</button>` : '';
  const notesBtn = S.notes ? `<button class="notesbtn" aria-label="Build notes">i</button>` : '';
  const hideProgress = ['paywall','end','welcome'].includes(card.type);
  app.innerHTML = `<div class="stage">
    <div class="frame"><div class="screen">
      <div class="topbar"></div>
      ${hideProgress?'':`<div class="progress"><i style="width:${pct}%"></i></div>${phase}`}
      ${back}${notesBtn}
      <div id="cardbody" class="card ${card.layout||'center'}"></div>
    </div></div>
    ${S.notes ? sidePanel(card) : ''}
  </div>`;
  const body = $('#cardbody');
  const r = RENDER[card.type] || RENDER.text;
  r(card, body);
  $('.back')?.addEventListener('click', ()=>go(-1));
  $('.notesbtn')?.addEventListener('click', ()=>toggleSheet(card));
  if(window.innerWidth<=820 && S.notes && S.sheet) toggleSheet(card, true);
}
function notesHTML(card){ const n = card.notes||{}; return `<h4>Build notes · ${esc(card.id)}</h4>
  <span class="tag tag-${n.tag||'existing'}">${TAG_LABEL[n.tag]||n.tag||'Existing template'}</span>
  <div class="kv"><div>Template</div><div><code>${esc(n.template||card.type)}</code></div>
  ${n.calmer?`<div>Calmer</div><div>${esc(n.calmer)}</div>`:''}
  ${n.evidence?`<div>Evidence</div><div>${esc(n.evidence)}</div>`:''}
  ${n.why?`<div>Why</div><div>${esc(n.why)}</div>`:''}
  ${n.loss?`<div>Lost</div><div>${esc(n.loss)}</div>`:''}
  ${card.branch?`<div>Shown when</div><div><code>${esc(card.branch)}</code></div>`:''}</div>
  ${n.fills&&n.fills.length?`<h4 style="margin-top:12px">Verify before shipping</h4><ul class="fills">${n.fills.map(f=>`<li>${esc(f)}</li>`).join('')}</ul>`:''}`; }
function sidePanel(card){ const vis = visibleCards(); return `<div class="side"><div class="panel">${notesHTML(card)}</div><div class="panel"><h4>Where you are</h4>${esc(S.deck.name)} · screen ${vis.indexOf(card)+1} of ${vis.length} on this path<br><a href="${location.pathname}?notes=1#/map/${S.deckId}">Flow map</a> · <a href="${location.pathname}?notes=1#/">All versions</a><br><span style="color:var(--grey)">Answers so far: ${esc(Object.keys(S.L).filter(k=>S.L[k]).map(k=>k+': '+S.L[k]).join(' · ')||'none')}</span></div></div>`; }
function toggleSheet(card, force){ const ex = $('.sheet'); if(ex && !force){ ex.remove(); S.sheet=false; return; } if(ex) ex.remove(); S.sheet=true; const d = document.createElement('div'); d.className='sheet'; d.innerHTML = `<button class="close" aria-label="Close">×</button>${notesHTML(card)}`; $('.screen').appendChild(d); d.querySelector('.close').onclick=()=>{ d.remove(); S.sheet=false; }; }

/* ---------- shared fragments ---------- */
const CHECK = `<svg class="check" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="10" fill="#30C5CA"/><path d="M6.5 11.5l3 3 6-6.5" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const LOCK = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#878888" stroke-width="2"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 018 0v3"/></svg>`;
function head(card, opts={}){ return `${card.kicker?`<div class="kicker">${tpl(card.kicker)}</div>`:''}<h1 class="title ${opts.sm?'sm':''}">${tl(card.title)}</h1>${card.subtitle?`<p class="subtitle">${tl(card.subtitle)}</p>`:''}`; }
function reassure(card){ return card.reassure ? `<div class="reassure">${LOCK}<span>${tpl(card.reassure)}</span></div>` : ''; }
function cta(label, extra=''){ return `<div class="bottom">${extra}<button class="cta" id="cta">${esc(label||'Continue')}</button></div>`; }
function tapToContinue(){ return `<div class="bottom" style="align-items:center"><button class="ghost tap" id="cta">Tap to continue</button></div>`; }
function bindNext(sel='#cta'){ const b = $(sel); if(b) b.onclick = ()=>go(1); }
function laurelsHTML(ls){ if(!ls||!ls.length) return ''; return `<div class="badges">${ls.map(l=>`<span class="badge">${l.stars?'<span class="star">★</span>':''}<b>${tpl(l.l)}</b>${l.s?`<span>${tpl(l.s)}</span>`:''}</span>`).join('')}</div>`; }

/* ---------- renderers ---------- */
const RENDER = {};
RENDER.welcome = (c, el)=>{
  el.innerHTML = `<div class="hero"><img src="assets/welcome.svg" alt=""></div>${head(c)}${c.authority?`<div class="authority">${c.authority.avatars?`<span class="avatars"><img src="assets/coaches/ofosu.png" alt=""><img src="assets/coaches/leah.png" alt=""></span>`:''}<span>${tpl(c.authority.text)}</span></div>`:''}${laurelsHTML(c.laurels)}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta||'Continue', '') );
  if(c.sub) el.insertAdjacentHTML('beforeend', `<div style="text-align:center;color:var(--grey);font-size:16px;margin:-26px 0 34px">${tpl(c.sub)}</div>`);
  bindNext();
};
RENDER.text = (c, el)=>{
  el.innerHTML = `${c.image?`<div style="font-size:56px;margin-bottom:22px">${c.image.length<=3?c.image:`<img src="assets/icons/${c.image}.png" style="width:96px;height:96px" alt="">`}</div>`:''}${head(c)}${(c.body && !c.items)?`<p class="body ${c.bodyInk?'ink':''}">${tl(c.body)}</p>`:''}${c.items?`<div class="vlist">${c.items.filter(it=>{ if(typeof it==='string'||!it.when) return true; try{ return !!new Function('a','L','return ('+it.when+')')(S.a,S.L);}catch(e){ return true; } }).map(it=>`<div class="vitem">${CHECK}<div><div class="t">${tpl(it.title||it.text||it)}</div>${it.subtitle?`<div class="s">${tpl(it.subtitle)}</div>`:''}</div></div>`).join('')}</div>`:''}${(c.body && c.items)?`<p class="body">${tl(c.body)}</p>`:''}${reassure(c)}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', c.tap ? tapToContinue() : cta(c.cta)); bindNext();
};
RENDER.textImage = (c, el)=>{
  const m = c.mock;
  const mock = m ? `<div class="mock">${m.header?`<div class="mh">${tpl(m.header)}</div>`:''}${m.pill?`<div class="pill">${tpl(m.pill)}</div>`:''}${(m.rows||[]).map(r=>`<div class="mrow ${r.hl?'hl':''}"><span class="dot" style="background:${colorVar(r.color)}"></span><span>${tpl(r.t)}${r.s?`<small>${tpl(r.s)}</small>`:''}</span></div>`).join('')}</div>` : (c.image?`<img src="${c.image}" alt="" style="width:220px;margin-top:18px">`:'');
  el.innerHTML = `${head(c,{sm:true})}${mock}${c.body?`<p class="body">${tl(c.body)}</p>`:''}${reassure(c)}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', c.tap ? tapToContinue() : cta(c.cta)); bindNext();
};
RENDER.list = (c, el)=>{
  el.innerHTML = `${head(c,{sm:true})}<div class="vlist">${c.items.map(it=>`<div class="vitem"><div class="ico" style="background:${colorVar(it.color)}">${it.icon||'✓'}</div><div><div class="t">${tpl(it.title)}</div>${it.subtitle?`<div class="s">${tpl(it.subtitle)}</div>`:''}</div></div>`).join('')}</div>${c.body?`<p class="body">${tl(c.body)}</p>`:''}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.question = (c, el)=>{
  const style = c.style || (c.options.length>4 ? 'compact' : '');
  el.innerHTML = `${head(c,{sm:c.options.length>4})}<div class="opts ${style}">${c.options.map(o=>`<button class="opt" data-id="${esc(o.id)}" style="background:${style==='teal'?'':colorVar(o.color)}"><span class="txt">${tpl(o.text)}${o.sub?`<small>${tpl(o.sub)}</small>`:''}</span>${style==='teal'?'':iconImg(o.icon)}</button>`).join('')}</div>${c.subAnswer?`<button class="ghost sub-answer" data-id="${esc(c.subAnswer.id)}">${esc(c.subAnswer.text)}</button>`:''}${reassure(c)}<div class="spacer"></div>`;
  el.querySelectorAll('.opt,.sub-answer').forEach(b=>b.onclick=()=>{ const o = c.options.find(x=>x.id===b.dataset.id) || c.subAnswer; setA(c.questionId, b.dataset.id, o.text.replace(/<[^>]+>/g,'')); if(c.derive) deriveFrom(c, b.dataset.id); b.classList.add('sel'); setTimeout(()=>go(1), 220); });
};
RENDER.scrollableQuestion = (c, el)=>{ RENDER.question(Object.assign({style:'teal'}, c), el); };
RENDER.multiselect = (c, el)=>{
  const sel = new Set();
  el.innerHTML = `${head(c,{sm:c.options.length>5})}<div class="opts compact">${c.options.map(o=>`<button class="opt" data-id="${esc(o.id)}" style="background:${colorVar(o.color)}"><span class="txt">${tpl(o.text)}</span><span class="chk">${'<svg width="14" height="14" viewBox="0 0 22 22" fill="none"><path d="M6.5 11.5l3 3 6-6.5" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'}</span></button>`).join('')}</div>${reassure(c)}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta||'Continue', c.skip?`<button class="ghost" id="skip">Skip</button>`:''));
  const btn = $('#cta'); btn.disabled = true;
  el.querySelectorAll('.opt').forEach(b=>b.onclick=()=>{ const id=b.dataset.id; if(sel.has(id)){ sel.delete(id); b.classList.remove('sel'); } else { if(c.max && sel.size>=c.max) return; sel.add(id); b.classList.add('sel'); } btn.disabled = sel.size===0; });
  btn.onclick = ()=>{ const ids=[...sel]; setA(c.questionId, ids, ids.map(i=>c.options.find(o=>o.id===i).text.replace(/<[^>]+>/g,'')).join(', ')); go(1); };
  $('#skip')?.addEventListener('click', ()=>{ setA(c.questionId, [], ''); go(1); });
};
RENDER.goalRanking = (c, el)=>{
  const goals = ['stress','sleep','focus','mood']; const sel = [];
  const tiles = ()=>`<div class="opts tiles">${goals.map(g=>`<button class="tile" data-g="${g}" style="background:${colorVar(GOAL_COLOR[g])}"><img src="assets/goals/${g}.png" alt="">${GOAL_LABEL[g]}</button>`).join('')}</div>`;
  const phase1 = ()=>{ el.innerHTML = `<h1 class="title">${tl(c.title||['Select the goals that','matter to you.'])}</h1>${tiles()}<div class="spacer"></div>${tapToContinue()}`;
    el.querySelectorAll('.tile').forEach(t=>t.onclick=()=>{ const g=t.dataset.g; const i=sel.indexOf(g); if(i>=0) sel.splice(i,1); else sel.push(g); t.classList.toggle('sel'); });
    $('#cta').onclick=()=>{ if(!sel.length) return; if(sel.length===1){ finish([sel[0]]); } else phase2(); }; };
  const phase2 = ()=>{ const order=[]; el.innerHTML = `<h1 class="title">${tl(c.rankTitle||['Now select each goal','in order of importance.'])}</h1><div class="opts tiles">${sel.map(g=>`<button class="tile" data-g="${g}" style="background:${colorVar(GOAL_COLOR[g])}"><img src="assets/goals/${g}.png" alt="">${GOAL_LABEL[g]}</button>`).join('')}</div><div class="spacer"></div>${tapToContinue()}`;
    el.querySelectorAll('.tile').forEach(t=>t.onclick=()=>{ const g=t.dataset.g; if(order.includes(g)) return; order.push(g); t.classList.add('sel'); t.insertAdjacentHTML('afterbegin',`<span class="rank">${order.length}</span>`); if(order.length===sel.length) setTimeout(()=>finish(order),350); });
    $('#cta').onclick=()=>{ if(order.length===sel.length) finish(order); }; };
  const finish = (order)=>{ S.a.goals=order; order.forEach((g,i)=>{ S.a['goal_'+(i+1)]=g; S.L['goal_'+(i+1)]=GOAL_LABEL[g]; }); for(let i=order.length+1;i<=4;i++){ delete S.a['goal_'+i]; delete S.L['goal_'+i]; } goals.forEach(g=>S.a['goal_'+g]= order.includes(g)?'yes':'no'); S.L.goals = order.map(g=>GOAL_LABEL[g]).join(', '); go(1); };
  phase1();
};
RENDER.goalsMetrics = (c, el)=>{
  const order = S.a.goals || ['stress','sleep']; const rows = order.map(g=>c.metrics.find(m=>m.goal===g)).filter(Boolean);
  el.innerHTML = `${head(c)}<div class="metrics">${rows.map(m=>{ const [n,...rest]=m.text.split(' '); return `<div class="metric" style="background:${colorVar(GOAL_COLOR[m.goal])}"><span class="n">${n}</span><span>${rest.join(' ')}</span></div>`; }).join('')}</div>${c.disclaimer?`<div class="disclaimer">${tl(c.disclaimer)}</div>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', c.tap===false ? cta('Continue') : tapToContinue()); bindNext();
};
RENDER.ageMetrics = (c, el)=>{
  const n = ageCount(S.a.age); S.a.age_count = n; S.L.age_count = n.toLocaleString();
  el.innerHTML = `${head(c)}${c.body?`<p class="body ink">${tl(c.body)}</p>`:''}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>${tapToContinue()}`; bindNext();
};
RENDER.keyboard = (c, el)=>{
  el.innerHTML = `${head(c)}<input class="field" id="fld" ${c.numpad?'inputmode="numeric" pattern="[0-9]*"':'autocapitalize="words"'} placeholder="${esc(c.placeholder||'')}" maxlength="${c.numpad?3:24}">${reassure(c)}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta||'Continue'));
  const f = $('#fld'), b = $('#cta'); b.disabled = true; setTimeout(()=>f.focus(), 50);
  const valid = v => c.numpad ? (Number(v)>=13 && Number(v)<200) : v.trim().length>=1;
  f.oninput = ()=>{ b.disabled = !valid(f.value); };
  const submit = ()=>{ if(!valid(f.value)) return; const v = c.numpad ? Number(f.value) : f.value.trim(); setA(c.questionId, v, String(v)); if(c.numpad){ S.a.age_range = v<18?'13-17':v<25?'18-24':v<45?'25-44':'45+'; } go(1); };
  b.onclick = submit; f.onkeydown = e=>{ if(e.key==='Enter') submit(); };
};
RENDER.slider = (c, el)=>{
  const stops = c.stops; let v = c.default||1;
  el.innerHTML = `${head(c)}<div class="slider"><div class="cap" id="cap">${esc(stops[v].caption||stops[v].label)}</div><input type="range" min="0" max="${stops.length-1}" step="1" value="${v}" id="rng"><div class="poles"><span>${esc(c.poles?.[0]||stops[0].label)}</span><span>${esc(c.poles?.[1]||stops[stops.length-1].label)}</span></div></div>${reassure(c)}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta||'Continue'));
  $('#rng').oninput = e=>{ v=Number(e.target.value); $('#cap').textContent = stops[v].caption||stops[v].label; };
  $('#cta').onclick = ()=>{ setA(c.questionId, stops[v].id, stops[v].label); go(1); };
};
RENDER.commitment = (c, el)=>{
  let pick=null;
  el.innerHTML = `${head(c,{sm:true})}<div class="opts compact">${c.options.map(o=>`<button class="opt" data-id="${esc(o.id)}" style="background:${colorVar(o.color)}"><span class="txt">${tpl(o.text)}${o.sub?`<small>${tpl(o.sub)}</small>`:''}</span>${o.badge?`<span class="tag tag-existing">${esc(o.badge)}</span>`:''}</button>`).join('')}</div><div class="praise" id="praise"></div>${c.foot?`<div class="foot">${tpl(c.foot)}</div>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta||'Continue')); const b=$('#cta'); b.disabled=true;
  el.querySelectorAll('.opt').forEach(x=>x.onclick=()=>{ el.querySelectorAll('.opt').forEach(y=>y.classList.remove('sel')); x.classList.add('sel'); pick=c.options.find(o=>o.id===x.dataset.id); $('#praise').textContent = pick.praise||''; b.disabled=false; });
  b.onclick=()=>{ setA(c.questionId, pick.id, pick.text.replace(/<[^>]+>/g,'')); go(1); };
};
RENDER.setReminderTime = (c, el)=>{
  const times = c.times || ['6:00 am','7:00 am','8:00 am','12:00 pm','6:00 pm','8:00 pm','9:30 pm','10:00 pm','11:00 pm'];
  let pick = tpl(c.default||times[0]); if(!times.includes(pick)) pick = times[0];
  el.innerHTML = `${head(c)}<div class="times">${times.map(t=>`<button class="time ${t===pick?'sel':''}" data-t="${t}">${t}</button>`).join('')}</div>${c.foot?`<div class="foot">${tpl(c.foot)}</div>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta||'Continue'));
  el.querySelectorAll('.time').forEach(t=>t.onclick=()=>{ el.querySelectorAll('.time').forEach(y=>y.classList.remove('sel')); t.classList.add('sel'); pick=t.dataset.t; });
  $('#cta').onclick=()=>{ setA(c.questionId||'reminder_time', pick, pick); go(1); };
};
RENDER.pushOptIn = (c, el)=>{
  el.innerHTML = `<div style="font-size:64px;margin-bottom:18px">🔔</div>${head(c)}${c.body?`<p class="body">${tl(c.body)}</p>`:''}${c.foot?`<div class="foot" style="max-width:300px">${tpl(c.foot)}</div>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta||'Continue'));
  $('#cta').onclick=()=>{ const p=document.createElement('div'); p.className='osprompt'; p.innerHTML=`<div class="osbox"><div class="t">“Balance” Would Like to Send You Notifications</div><div class="m">Notifications may include alerts, sounds, and icon badges. These can be configured in Settings.</div><div class="b"><button id="dontallow">Don't Allow</button><button id="allow">Allow</button></div></div>`; $('.screen').appendChild(p); p.querySelectorAll('button').forEach(b=>b.onclick=()=>{ setA(c.questionId||'push', b.id==='allow'?'yes':'no', b.id==='allow'?'Allowed':'Declined'); p.remove(); go(1); }); };
};
RENDER.userReview = (c, el)=>{
  el.innerHTML = `${head(c,{sm:true})}${laurelsHTML(c.laurels)}<div class="reviews">${c.reviews.map(r=>`<div class="review"><div class="stars">★★★★★</div><p>“${tpl(r.text)}”</p><div class="who">${esc(r.who)}</div></div>`).join('')}</div>${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.primer = (c, el)=>{ RENDER.text(Object.assign({kicker:'Did you know?', tap:true}, c), el); };
RENDER.loading = (c, el)=>{
  const bars = c.bars.map(b=>tpl(b));
  el.innerHTML = `<img src="assets/loading-art.png" alt="" style="width:150px;height:150px;margin-bottom:10px">${head(c)}<div class="bars">${bars.map((b,i)=>`<div class="bar"><div class="lbl"><span>${b}</span><span class="ok" id="ok${i}"></span></div><div class="trk"><i id="b${i}"></i></div></div>`).join('')}</div><div class="spacer"></div>`;
  bars.forEach((b,i)=>{ setTimeout(()=>{ const e=$('#b'+i); if(e) e.style.width='100%'; }, 200+i*900); setTimeout(()=>{ const o=$('#ok'+i); if(o) o.textContent='✓'; }, 1100+i*900); });
  setTimeout(()=>{ if(S.deck.cards[S.idx]===c) go(1); }, 1500+bars.length*900);
};
RENDER.profile = (c, el)=>{
  // sub-scores derived only from answers actually given; unanswered dimensions are omitted rather than invented
  const rows = (c.scores||[]).map(s=>{ const v = S.a[s.from]; if(v==null || (Array.isArray(v)&&!v.length)) return null; const key = Array.isArray(v)? (v.length>=3?'many':v.length===2?'some':'one') : v; const lvl = (s.map&&s.map[key]) || s.default || 'mid'; return {label:s.label, lvl, text:(s.text&&s.text[lvl])||{good:'Steady',mid:'Room to grow',low:'Needs care'}[lvl]}; }).filter(Boolean);
  const pts = {good:3,mid:2,low:1}; const score = rows.length ? Math.round((rows.reduce((t,r)=>t+pts[r.lvl],0)/(rows.length*3))*100) : 50;
  const g1 = S.a.goal_1||'stress'; const prof = (c.profiles&&(c.profiles[g1]||c.profiles.default))||{name:'The Steady Starter',insight:''};
  S.L.profile_name = prof.name; S.a.profile_score = score;
  const arc = (p)=>{ const a = Math.PI*(1-Math.max(0.02,p)); return {x:120+90*Math.cos(a), y:100-90*Math.sin(a)}; }; const e = arc(score/100);
  el.innerHTML = `${head(c,{sm:true})}<div class="gauge"><svg viewBox="0 0 240 130"><path d="M30 100 A90 90 0 0 1 210 100" stroke="#E3E6E8" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M30 100 A90 90 0 0 1 ${e.x.toFixed(1)} ${e.y.toFixed(1)}" stroke="#30C5CA" stroke-width="14" fill="none" stroke-linecap="round"/><text x="120" y="92" text-anchor="middle" font-size="30" font-weight="300" fill="#0A0A0B" font-family="Work Sans, sans-serif">${score}</text></svg><div class="val">${prof.name}<small>${tpl(c.scoreLabel||'Your starting point')} · out of 100</small></div></div>
    <div class="scores">${rows.map(r=>`<div class="score ${r.lvl}">${esc(r.label)}<b>${esc(r.text)}</b></div>`).join('')}</div>
    ${prof.insight?`<div class="insight">${tpl(prof.insight)}</div>`:''}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.quizResult = (c, el)=>{
  const g1 = S.a.goal_1||'stress'; const prof = (c.profiles&&(c.profiles[g1]||c.profiles.default))||{}; S.L.profile_name = prof.name||'';
  el.innerHTML = `${head(c,{sm:true})}<div class="gauge"><svg viewBox="0 0 240 130"><path d="M30 100 A90 90 0 0 1 210 100" stroke="#E3E6E8" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M30 100 A90 90 0 0 1 183 37" stroke="#30C5CA" stroke-width="14" fill="none" stroke-linecap="round"/></svg><div class="val">${esc(prof.name||'')}<small>${tpl(c.scoreLabel||'Your starting point')}</small></div></div>${prof.body?`<p class="body">${tpl(prof.body)}</p>`:''}${prof.insight?`<div class="insight">${tpl(prof.insight)}</div>`:''}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.chart = (c, el)=>{
  const w=320,h=170; const px = i=>28+i*(w-48)/3; const withY=[132,96,62,38], aloneY=[132,124,118,114];
  const path = ys => ys.map((y,i)=>`${i?'L':'M'}${px(i)} ${y}`).join(' ');
  const labels = c.weeks||['Today','Week 1','Week 3','Week 6'];
  el.innerHTML = `${head(c,{sm:true})}<div class="chart"><svg viewBox="0 0 ${w} ${h}"><line x1="22" y1="140" x2="${w-8}" y2="140" stroke="#E3E6E8"/><path d="${path(aloneY)}" stroke="#C6CBCE" stroke-width="3" fill="none" stroke-dasharray="6 6" stroke-linecap="round"/><path d="${path(withY)}" stroke="#30C5CA" stroke-width="4" fill="none" stroke-linecap="round"/>${withY.map((y,i)=>`<circle cx="${px(i)}" cy="${y}" r="5" fill="#fff" stroke="#30C5CA" stroke-width="3"/>`).join('')}${labels.map((l,i)=>`<text x="${px(i)}" y="160" font-size="11" text-anchor="middle" fill="#878888" font-family="Work Sans, sans-serif">${esc(l)}</text>`).join('')}</svg><div class="leg"><span><i style="background:#30C5CA"></i>${tpl(c.withLabel||'With Balance')}</span><span><i style="background:#C6CBCE"></i>${tpl(c.aloneLabel||'On your own')}</span></div></div>${c.body?`<p class="body">${tl(c.body)}</p>`:''}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.comparison = (c, el)=>{
  const pick = (arr)=> arr.flatMap(x=>{ if(typeof x==='string') return [tpl(x)]; if(x.from){ return String(S.L[x.from]||'').split(', ').filter(Boolean).map(t=>x.prefix?tpl(x.prefix)+t.charAt(0).toLowerCase()+t.slice(1):t); } if(x.when){ try{ if(!new Function('a','L','return ('+x.when+')')(S.a,S.L)) return []; }catch(e){} } return [tpl(x.text)]; }).filter(Boolean).slice(0,5);
  el.innerHTML = `${head(c,{sm:true})}<div class="compare"><div class="col"><h5>${tpl(c.withoutTitle||'On your own')}</h5><ul>${pick(c.without).map(t=>`<li>${t}</li>`).join('')}</ul></div><div class="col with"><h5>${tpl(c.withTitle||'With Balance')}</h5><ul>${pick(c.with).map(t=>`<li>${t}</li>`).join('')}</ul></div></div>${c.body?`<p class="body">${tl(c.body)}</p>`:''}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.benefits = (c, el)=>{
  el.innerHTML = `${head(c,{sm:true})}${laurelsHTML(c.laurels)}<div class="vlist">${c.items.map(it=>`<div class="vitem">${CHECK}<div><div class="t">${tpl(it.title||it)}</div>${it.subtitle?`<div class="s">${tpl(it.subtitle)}</div>`:''}</div></div>`).join('')}</div>${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.signup = (c, el)=>{
  el.innerHTML = `${head(c)}${c.body?`<p class="body">${tl(c.body)}</p>`:''}<div class="spacer"></div><div class="bottom"><button class="cta" style="background:#000" id="cta"> Continue with Apple</button><button class="cta outline" id="g">Continue with Google</button><button class="cta outline" id="e">Continue with email</button>${c.sub?`<div style="text-align:center;color:var(--grey);font-size:14px">${tpl(c.sub)}</div>`:''}</div>`;
  ['#cta','#g','#e'].forEach(s=>{ const b=$(s); if(b) b.onclick=()=>go(1); });
};
RENDER.paywall = (c, el)=>{
  const screen = $('.screen');
  el.innerHTML = '';
  const pw = document.createElement('div'); pw.className='pw';
  const headline = (c.headlines && (c.headlines[S.a.goal_1]||c.headlines.default)) || 'Reduce daily stress and anxiety';
  if(c.design==='recime'){
    const items = c.benefits || ['400+ meditations for stress, sleep, focus and mood','Sleep stories, music and soundscapes','A new session built for you every day','Ad-free, on every device'];
    pw.innerHTML = `<button class="x" aria-label="Close">×</button>
      <div class="pw-top"><img src="assets/paywall-art.png" alt=""><div class="pw-badge">7-day free trial</div><h2>Try Balance for free</h2></div>
      <div class="pw-list">${items.map(t=>`<div class="pw-item">${CHECK}<span>${tpl(t)}</span></div>`).join('')}</div>
      <div class="plans"><div class="plan on"><span class="r"></span><div class="a">Annual</div><div class="p">$69.99/year</div><div class="d">$5.83 a month. 7 days free.</div></div><div class="plan"><span class="r"></span><div class="a">Monthly</div><div class="p">$9.99/month</div><div class="d">No free trial</div></div></div>
      <div class="bottom" style="padding-bottom:0"><button class="cta" id="cta">Try for $0.00</button></div><div class="fine">7 days free, then $69.99 per year. Cancel anytime.</div><div class="fine" style="margin-top:6px"><span class="link">Restore Purchase</span></div>`;
  } else {
    pw.innerHTML = `<button class="x" aria-label="Close">×</button><div class="art"><img src="assets/paywall-art.png" alt="" style="width:250px;height:250px;object-fit:contain"></div><h2>${tpl(headline)}</h2><div class="dots"><i class="on"></i><i></i><i></i><i></i></div>
      <div class="plans"><div class="plan on"><span class="r"></span><div class="a">Annual</div><div class="p">$5.83/month</div><div class="d">$69.99 for 12 months</div></div><div class="plan"><span class="r"></span><div class="a">Monthly</div><div class="p">$9.99/month</div><div class="d">No free trial included</div></div></div>
      <div class="bottom" style="padding-bottom:0"><button class="cta" id="cta">Start your FREE week</button></div><div class="fine">7 days free, then $5.83 per month ($69.99 per year)</div>`;
  }
  screen.appendChild(pw);
  pw.querySelector('.x').onclick=()=>{ setA('paywall','declined','Declined'); pw.remove(); go(1); };
  pw.querySelector('#cta').onclick=()=>{ setA('paywall','trial','Started trial'); pw.remove(); go(1); };
};
RENDER.end = (c, el)=>{
  const other = S.deckId==='wishlist'?'constrained':'wishlist';
  el.innerHTML = `${head(c,{sm:true})}${c.body?`<p class="body">${tl(c.body)}</p>`:''}${c.items?`<div class="vlist">${c.items.map(it=>`<div class="vitem">${CHECK}<div><div class="t">${tpl(it.title||it)}</div>${it.subtitle?`<div class="s">${tpl(it.subtitle)}</div>`:''}</div></div>`).join('')}</div>`:''}<div class="endnote">${tpl(c.note||'')}</div><div class="spacer"></div><div class="bottom"><button class="cta" id="cta">Start over</button><a class="cta outline" style="display:flex;align-items:center;justify-content:center;text-decoration:none" href="${location.pathname}${S.notes?'?notes=1':''}#/${other}">Try the ${other==='wishlist'?'wish list':'constrained'} version</a><a class="ghost" style="text-align:center;text-decoration:none" href="${location.pathname}${S.notes?'?notes=1':''}#/map/${S.deckId}">Flow map</a></div>`;
  $('#cta').onclick=()=>{ S.idx=-1; location.hash = `#/${S.deckId}`; route(); };
};
function deriveFrom(c,id){
  if(c.derive==='ageBand'){ const mid={'13-17':16,'18-24':21,'25-34':29,'35-44':39,'45-54':49,'55+':60}[id]||34; S.a.age=mid; S.L.age=String(mid); S.a.age_count=ageCount(mid); S.L.age_count=S.a.age_count.toLocaleString(); S.a.age_range = mid<18?'13-17':mid<25?'18-24':mid<45?'25-44':'45+'; }
}
RENDER.coaches = (c, el)=>{
  el.innerHTML = `<div class="coaches"><div class="coach"><img src="assets/coaches/ofosu.png" alt="Ofosu"><div class="n">Ofosu</div></div><div class="coach"><img src="assets/coaches/leah.png" alt="Leah"><div class="n">Leah</div></div></div>${head(c)}<div class="bios">${(c.bios||[]).map(b=>`<div class="bio"><b>${esc(b.name)}</b><span>${tpl(b.text)}</span></div>`).join('')}</div>${c.body?`<p class="body">${tl(c.body)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};

route();
})();
