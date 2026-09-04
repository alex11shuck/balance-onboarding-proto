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
S.why = qs.get('why') === '1';
S.edit = qs.get('edit') === '1';
function modeQ(){ const p=[]; if(S.notes) p.push('notes=1'); if(S.why) p.push('why=1'); if(S.edit) p.push('edit=1'); return p.length?('?'+p.join('&')):''; }

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
  goal:(g)=>GOAL_LABEL[g]||g, n:(x)=>Number(x||0).toLocaleString(),
  pick:(c,a,b)=>c?a:b,
  exp:(a)=>({none:"You're new to this", once_or_twice:"You've tried meditation before", a_little:"You already meditate now and then", a_lot:"You already meditate often"})[a.has_meditated_before]||"You're new to this",
  days:(a)=>({packed:"your days are packed", busy:"you're busy most days", some:"you have some room to breathe", open:"your schedule is pretty open"})[a.schedule]||"your days are busy",
  Days:(a)=>{ const d=H.days(a); return d.charAt(0).toUpperCase()+d.slice(1); },
  happy:(a)=>({myself:"You recharge on your own, so your sessions will protect that time.", family:"You feel happiest around family, so your sessions will help you show up for them.", friends:"You feel happiest around friends, so your sessions will help you show up for them."})[a.happiest_around]||"Your sessions start with what already lifts you.",
  pulls:(a)=>({thoughts:"your thoughts pull you away most", surroundings:"your surroundings pull you away most", technology:"technology pulls you away most", people:"other people pull you away most"})[a.most_distracting]||"attention slips more than you'd like",
  goalsPhrase:(a)=>{ const m={stress:"less stress", sleep:"better sleep", focus:"sharper focus", mood:"a steadier mood"}; const g=(a.goals||[a.goal_1||'stress']).map(x=>m[x]).filter(Boolean); return H.list(g); },
  firstFuture:(a,L)=>{ const f=String(L.future||'').split(', ').filter(Boolean)[0]; return f? f.charAt(0).toLowerCase()+f.slice(1) : ''; } };
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
  if(S.idx<0){ if(S.edit && !Object.keys(S.a).length){ Object.assign(S.a, PERSONA); Object.assign(S.L, PERSONA_L); } S.idx = deck.cards.findIndex(c=>branchOK(c)); }
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
  const notesQ = modeQ();
  const tq=(n,w)=>{ const p=[]; if(n) p.push('notes=1'); if(w) p.push('why=1'); return p.length?('?'+p.join('&')):''; };
  app.innerHTML = `<div class="landing">
    <h1>Balance onboarding prototype</h1>
    <p class="sub">Two clickable versions of a Calmer-style flow in Balance's skin, from welcome to today's paywall. Built Sep 4, 2026 for the Balance top-of-funnel bet. Tap through on a phone, or open the flow map for the screen-by-screen spec. Copy in <b>[brackets]</b> is a placeholder to verify.</p>
    <div class="versions">
      <div class="vcard"><h2 ${S.edit?'contenteditable data-deck="wishlist" data-ek="deck:name" class="ed"':''}>${esc(w.name)}</h2><p ${S.edit?'contenteditable data-deck="wishlist" data-ek="deck:description" class="ed"':''}>${esc(w.description)}</p>${stat(w)}<div class="row"><a class="btn" href="${location.pathname}${notesQ}#/wishlist">Start</a><a class="btn secondary small" href="${location.pathname}${notesQ}#/map/wishlist">Flow map</a></div></div>
      <div class="vcard"><h2 ${S.edit?'contenteditable data-deck="constrained" data-ek="deck:name" class="ed"':''}>${esc(c.name)}</h2><p ${S.edit?'contenteditable data-deck="constrained" data-ek="deck:description" class="ed"':''}>${esc(c.description)}</p>${stat(c)}<div class="row"><a class="btn" href="${location.pathname}${notesQ}#/constrained">Start</a><a class="btn secondary small" href="${location.pathname}${notesQ}#/map/constrained">Flow map</a></div></div>
    </div>
    <div class="legend" style="margin-bottom:16px"><h3>Two review modes</h3>
      <div class="row" style="margin:8px 0 12px"><a class="btn small ${S.why?'':'secondary'}" href="${location.pathname}${tq(S.notes,!S.why)}#/">${S.why?'✓ ':''}Why mode</a><a class="btn small ${S.notes?'':'secondary'}" href="${location.pathname}${tq(!S.notes,S.why)}#/">${S.notes?'✓ ':''}Build notes</a></div>
      <a class="btn small ${S.edit?'':'secondary'}" href="${location.pathname}${(()=>{const p=[]; if(S.notes)p.push('notes=1'); if(S.why)p.push('why=1'); if(!S.edit)p.push('edit=1'); return p.length?'?'+p.join('&'):'';})()}#/" style="margin-left:-4px">${S.edit?'✓ ':''}Edit copy</a>
      <b>Why mode</b> (for content design and marketing) shows the principles behind each screen: what it is doing for the user, and the research or competitor evidence it rests on. <b>Build notes</b> (for product and engineering) show each screen's template and what it costs to ship. Either mode adds a small button at the top of the phone; on a desktop the panel sits beside the frame. <b>Edit copy</b> lets you tap any line of text on a screen and rewrite it in place; taps stop navigating and a small bar moves you through the flow. Your edits stay on this device until you export them, and the export is a file the build applies on the next publish.</div>
    <div class="legend"><h3>Reading the build notes</h3>
      Tags:
      <div class="row" style="margin-top:8px">${Object.keys(TAG_LABEL).map(t=>`<span class="tag tag-${t}">${TAG_LABEL[t]}</span>`).join('')}</div>
      <p style="margin:12px 0 0">The real onboarding is a JSON card array read by a Lua card engine, so every screen tagged <i>existing</i> or <i>built, unused</i> is a content change in <code>session.json</code>, not engineering. <i>Copy change</i> means new words on a card that already ships. <i>Swift bookend</i> and <i>Superwall dashboard</i> live outside the deck. <i>New template</i> is Lua engine work that ships to Android too.</p>
    </div>
  </div>`;
  if(S.edit){ app.querySelectorAll('[data-deck]').forEach(el=>{ const dk=el.dataset.deck, key=el.dataset.ek; el.addEventListener('focus',()=>el.dataset.before=el.innerText); el.addEventListener('blur',()=>{ const now=el.innerText.trim(); if(now===(el.dataset.before||'').trim()) return; const st=edStore(); st[dk]=st[dk]||{}; st[dk]['_deck']=st[dk]['_deck']||{}; st[dk]['_deck'][key]={source:key==='deck:name'?(dk==='wishlist'?w.name:c.name):(dk==='wishlist'?w.description:c.description), rendered:el.dataset.before, edited:now, dynamic:false}; edSave(st); el.classList.add('ed-changed'); }); }); }
}

/* ---------- flow map ---------- */
function renderMap(d){
  const notesQ = modeQ();
  const g = d.principles||{};
  const asks = d.cards.filter(x=>['question','scrollableQuestion','multiselect','keyboard','slider','commitment','goalRanking'].includes(x.type));
  const tags = {}; d.cards.forEach(c=>{ const t=(c.notes&&c.notes.tag)||'existing'; tags[t]=(tags[t]||0)+1; });
  app.innerHTML = `<div class="map">
    <p><a href="${location.pathname}${notesQ}#/">← All versions</a></p>
    <h1>${esc(d.name)}: flow map</h1>
    <p style="color:var(--dark);max-width:760px">${esc(d.description)} Core questions are counted the way the 23-app Health &amp; Fitness benchmark counts them (field median 6, ceiling 12; Balance today 8 on the stress + sleep path).</p>
    <div class="summary"><div class="stat"><b>${d.cards.length}</b>screens in the deck</div><div class="stat"><b>${asks.length}</b>asks (questions, pickers, entries)</div>${Object.keys(tags).map(t=>`<div class="stat"><b>${tags[t]}</b><span class="tag tag-${t}">${TAG_LABEL[t]||t}</span></div>`).join('')}</div>
    <div style="overflow-x:auto"><table><thead><tr><th>#</th><th>Screen</th><th>Type / template</th><th>Shown when</th><th>Tag</th><th>Source</th><th>Notes</th>${S.why?'<th>Principles</th>':''}</tr></thead><tbody>
    ${d.cards.map((c,i)=>{ const n=c.notes||{}; return `<tr><td class="n">${i+1}</td><td><a href="${location.pathname}${notesQ}#/${d.id}/${c.id}"><b>${esc((Array.isArray(c.title)?c.title.join(' '):(c.title||c.id)).replace(/<[^>]+>/g,''))}</b></a><br><code>${esc(c.id)}</code></td><td>${esc(c.type)}${n.template&&n.template!==c.type?`<br><code>${esc(n.template)}</code>`:''}</td><td>${c.branch?`<code>${esc(c.branch)}</code>`:'everyone'}</td><td><span class="tag tag-${n.tag||'existing'}">${TAG_LABEL[n.tag]||n.tag||'Existing template'}</span></td><td>${n.calmer?`Calmer ${esc(n.calmer)}<br>`:''}${esc(n.evidence||'')}</td><td>${esc(n.why||'')}${n.loss?`<br><b>Lost vs wish list:</b> ${esc(n.loss)}`:''}${n.fills&&n.fills.length?`<br><b>Verify:</b> ${n.fills.map(esc).join('; ')}`:''}</td>${S.why?`<td>${(c.principles||[]).map(k=>`<span class="tag tag-why">${esc((g[k]||{}).name||k)}</span>`).join(' ')}${c.how?`<br><span style="color:var(--dark)">${esc(c.how)}</span>`:''}</td>`:''}</tr>`; }).join('')}
    </tbody></table></div>${S.why?`<h2 style="font-weight:300;margin:36px 0 10px">The principles</h2><div class="gloss">${Object.keys(g).map(k=>`<div class="princ"><b>${esc(g[k].name)}</b><div>${esc(g[k].text)}</div>${g[k].source?`<div class="src">${esc(g[k].source)}</div>`:''}</div>`).join('')}</div>`:''}</div>`;
}

/* ---------- card rendering ---------- */
function renderCard(){
  const card = S.deck.cards[S.idx]; if(!card){ return; }
  setHash();
  const vis = visibleCards(); const pos = Math.max(0, vis.indexOf(card)); const pct = Math.round(((pos+1)/vis.length)*100);
  const phase = S.deck.phases && card.phase ? `<div class="steps">Part ${card.phase} of ${S.deck.phases.length} · ${esc(S.deck.phases[card.phase-1])}</div>` : '';
  const back = S.hist.length ? `<button class="back" aria-label="Back">‹</button>` : '';
  const notesBtn = (S.notes ? `<button class="notesbtn" aria-label="Build notes">i</button>` : '') + (S.why ? `<button class="notesbtn why" style="right:${S.notes?50:14}px" aria-label="Why this screen">?</button>` : '');
  const hideProgress = ['paywall','end','welcome'].includes(card.type);
  app.innerHTML = `<div class="stage">
    <div class="frame"><div class="screen">
      <div class="topbar"></div>
      ${hideProgress?'':`<div class="progress"><i style="width:${pct}%"></i></div>${phase}`}
      ${back}${notesBtn}
      <div id="cardbody" class="card ${card.layout||'center'}"></div>
    </div></div>
    ${(S.notes||S.why) ? sidePanel(card) : ''}
  </div>`;
  const body = $('#cardbody');
  const r = RENDER[card.type] || RENDER.text;
  r(card, body);
  requestAnimationFrame(()=>{ if(body.scrollHeight > body.clientHeight + 4) body.classList.replace('center','top'); });
  if(S.edit){ setupEdit(card, body); const side=$('.side'); if(side) makeEditable(side, card); }
  $('.back')?.addEventListener('click', ()=>go(-1));
  $('.notesbtn:not(.why)')?.addEventListener('click', ()=>toggleSheet(card,false,'notes'));
  $('.notesbtn.why')?.addEventListener('click', ()=>toggleSheet(card,false,'why'));

}
function notesHTML(card){ const n = card.notes||{}; return `<h4>Build notes · ${esc(card.id)}</h4>
  <span class="tag tag-${n.tag||'existing'}">${TAG_LABEL[n.tag]||n.tag||'Existing template'}</span>
  <div class="kv"><div>Template</div><div><code>${esc(n.template||card.type)}</code></div>
  ${n.calmer?`<div>Calmer</div><div data-ek="note:calmer">${esc(n.calmer)}</div>`:''}
  ${n.evidence?`<div>Evidence</div><div data-ek="note:evidence">${esc(n.evidence)}</div>`:''}
  ${n.why?`<div>Why</div><div data-ek="note:why">${esc(n.why)}</div>`:''}
  ${n.loss?`<div>Lost</div><div data-ek="note:loss">${esc(n.loss)}</div>`:''}
  ${card.branch?`<div>Shown when</div><div><code>${esc(card.branch)}</code></div>`:''}</div>
  ${n.fills&&n.fills.length?`<h4 style="margin-top:12px">Verify before shipping</h4><ul class="fills">${n.fills.map((f,i)=>`<li data-ek="note:fill:${i}">${esc(f)}</li>`).join('')}</ul>`:''}`; }
function whyHTML(card){ const g = S.deck.principles||{}; const keys = card.principles||[]; if(!keys.length) return `<h4>Why this screen</h4><span style="color:var(--grey)">No principle recorded for this card.</span>`; return `<h4>Why this screen</h4><p class="how" data-ek="why:how" style="margin:0 0 12px;color:var(--ink)">${card.how?tpl(card.how):(S.edit?'(add a line about how this screen uses the principles)':'')}</p>${keys.map(k=>{ const p=g[k]||{name:k,text:''}; return `<div class="princ" data-pk="${esc(k)}"><b data-ek="principle:${esc(k)}:name">${esc(p.name)}</b><div class="ptext" data-ek="principle:${esc(k)}:text">${esc(p.text)}</div><div class="src" data-ek="principle:${esc(k)}:source">${esc(p.source||'')}</div></div>`; }).join('')}`; }
function sidePanel(card){ const vis = visibleCards(); return `<div class="side">${S.why?`<div class="panel why">${whyHTML(card)}</div>`:''}${S.notes?`<div class="panel">${notesHTML(card)}</div>`:''}<div class="panel"><h4>Where you are</h4>${esc(S.deck.name)} · screen ${vis.indexOf(card)+1} of ${vis.length} on this path<br><a href="${location.pathname}${modeQ()}#/map/${S.deckId}">Flow map</a> · <a href="${location.pathname}${modeQ()}#/">All versions</a><br><span style="color:var(--grey)">Answers so far: ${esc(Object.keys(S.L).filter(k=>S.L[k]).map(k=>k+': '+S.L[k]).join(' · ')||'none')}</span></div></div>`; }
function toggleSheet(card, force, kind){ const ex = $('.sheet'); if(ex && !force && ex.dataset.kind===kind){ ex.remove(); S.sheet=false; return; } if(ex) ex.remove(); S.sheet=true; const d = document.createElement('div'); d.className='sheet'; d.dataset.kind=kind||'notes'; d.innerHTML = `<button class="close" aria-label="Close">×</button>${kind==='why'?whyHTML(card):notesHTML(card)}`; if(S.edit) setTimeout(()=>makeEditable(d, card), 0); $('.screen').appendChild(d); d.querySelector('.close').onclick=()=>{ d.remove(); S.sheet=false; }; }

/* ---------- shared fragments ---------- */
const CHECK = `<svg class="check" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="10" fill="#30C5CA"/><path d="M6.5 11.5l3 3 6-6.5" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const LOCK = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#878888" stroke-width="2"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 018 0v3"/></svg>`;
function head(card, opts={}){ return `${card.kicker?`<div class="kicker">${tpl(card.kicker)}</div>`:''}<h1 class="title ${opts.sm?'sm':''}">${tl(card.title)}</h1>${card.subtitle?`<p class="subtitle">${tl(card.subtitle)}</p>`:''}`; }
function reassure(card){ return card.reassure ? `<div class="reassure">${LOCK}<span>${tpl(card.reassure)}</span></div>` : ''; }
function cta(label, extra=''){ return S.edit ? `<div class="bottom">${extra}<div class="cta" id="cta" role="button">${esc(label||'Continue')}</div></div>` : `<div class="bottom">${extra}<button class="cta" id="cta">${esc(label||'Continue')}</button></div>`; }
function tapToContinue(){ const c=S.deck.cards[S.idx]||{}; const l=c.tapLabel||'Tap to continue'; return S.edit ? `<div class="bottom" style="align-items:center"><div class="ghost tap" id="cta" role="button">${esc(l)}</div></div>` : `<div class="bottom" style="align-items:center"><button class="ghost tap" id="cta">${esc(l)}</button></div>`; }
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
  const wrap=el.querySelector('.opts'); el.querySelectorAll('.opt').forEach(b=>b.onclick=()=>{ const id=b.dataset.id; if(sel.has(id)){ sel.delete(id); b.classList.remove('sel'); } else { if(c.max && sel.size>=c.max){ wrap.classList.add('shake'); setTimeout(()=>wrap.classList.remove('shake'),350); return; } sel.add(id); b.classList.add('sel'); } wrap.classList.toggle('maxed', !!c.max && sel.size>=c.max); btn.disabled = sel.size===0; });
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
RENDER.assembly = (c, el)=>{
  const chips = [S.L.goal_1, S.L.goal_2, S.L.how_experience_stress && S.L.how_experience_stress.split(', ')[0], S.L.keep_awake && S.L.keep_awake.split(', ')[0], S.L.has_meditated_before, S.L.schedule].filter(Boolean).slice(0,5);
  const colors=['purple_haze','polar_blue','mint_green','papaya_whip','misty_peach'];
  const sess = (c.sessions&&(c.sessions[S.a.goal_1]||c.sessions.default))||{title:'Settling a busy mind',coach:'Ofosu'};
  el.innerHTML = `<div class="coaches small"><div class="coach"><img src="assets/coaches/ofosu.png" alt="Ofosu"><div class="n">Ofosu</div></div><div class="coach"><img src="assets/coaches/leah.png" alt="Leah"><div class="n">Leah</div></div></div>${head(c,{sm:true})}
    <div class="chips" id="chips">${chips.map((t,i)=>`<span class="chip" style="background:var(--${colors[i%colors.length]})">${esc(t)}</span>`).join('')}</div>
    <svg class="arrow" width="24" height="26" viewBox="0 0 24 28" fill="none"><path d="M12 2v22M5 17l7 7 7-7" stroke="#878888" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
    <div class="sesscard" id="sess"><img src="assets/coaches/${sess.coach==='Leah'?'leah':'ofosu'}.png" alt=""><div><div class="mh">Your first session</div><div class="st">${esc(sess.title)}</div><div class="ss">10 min · with ${esc(sess.coach)}</div></div></div>
    ${c.body?`<p class="body" id="abody">${tl(c.body)}</p>`:''}${c.foot?`<div class="foot" id="afoot">${tpl(c.foot)}</div>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta||'Continue'));
  const b=$('#cta'); b.style.visibility='hidden';
  el.querySelectorAll('.chip').forEach((ch,i)=>setTimeout(()=>ch.classList.add('in'), 300+i*350));
  setTimeout(()=>{ $('#sess')?.classList.add('in'); }, 500+chips.length*350);
  setTimeout(()=>{ $('#abody')?.classList.add('in'); $('#afoot')?.classList.add('in'); b.style.visibility='visible'; }, 1100+chips.length*350);
  bindNext();
};
RENDER.legacyLoading = (c, el)=>{
  const texts = c.texts || ['your goals…','your experience…','your preferences…','your age…'];
  el.innerHTML = `<img src="assets/loading-art.png" alt="" style="width:190px;height:190px">${'<p class="body ink" style="margin-top:6px">Creating program based on<br><span class="link" id="lt">'+esc(texts[0])+'</span></p>'}<div class="spacer"></div>`;
  texts.forEach((t,i)=>setTimeout(()=>{ const e=$('#lt'); if(e) e.textContent=t; }, 900*i));
  setTimeout(()=>{ if(S.deck.cards[S.idx]===c) go(1); }, 900*texts.length+400);
};
RENDER.profile = (c, el)=>{
  // sub-scores derived only from answers actually given; unanswered dimensions are omitted rather than invented
  const rows = (c.scores||[]).map(s=>{ const v = S.a[s.from]; if(v==null || (Array.isArray(v)&&!v.length)) return null; const key = Array.isArray(v)? (v.length>=3?'many':v.length===2?'some':'one') : v; const lvl = (s.map&&s.map[key]) || s.default || 'mid'; return {label:s.label, lvl, text:(s.text&&s.text[lvl])||{good:'Steady',mid:'Room to grow',low:'Needs care'}[lvl]}; }).filter(Boolean);
  const pts = {good:3,mid:2,low:1}; const score = rows.length ? Math.round((rows.reduce((t,r)=>t+pts[r.lvl],0)/(rows.length*3))*100) : 50;
  const g1 = S.a.goal_1||'stress'; const prof = (c.profiles&&(c.profiles[g1]||c.profiles.default))||{name:'The Steady Starter',insight:''};
  S.L.profile_name = prof.name; S.a.profile_score = score;
  const arc = (p)=>{ const a = Math.PI*(1-Math.max(0.02,p)); return {x:120+90*Math.cos(a), y:100-90*Math.sin(a)}; }; const e = arc(score/100);
  el.innerHTML = `${head(c,{sm:true})}<div class="gauge"><svg viewBox="0 0 240 110"><path d="M30 100 A90 90 0 0 1 210 100" stroke="#E3E6E8" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M30 100 A90 90 0 0 1 ${e.x.toFixed(1)} ${e.y.toFixed(1)}" stroke="#30C5CA" stroke-width="14" fill="none" stroke-linecap="round"/><text x="120" y="88" text-anchor="middle" font-size="34" font-weight="300" fill="#0A0A0B" font-family="Work Sans, sans-serif">${score}</text><text x="120" y="104" text-anchor="middle" font-size="10" letter-spacing="1" fill="#878888" font-family="Work Sans, sans-serif">OUT OF 100</text></svg></div>
    <div class="profname">${esc(prof.name)}<small>${tpl(c.scoreLabel||'Your starting point')}</small></div>
    <div class="scores">${rows.map(r=>`<div class="score ${r.lvl}">${esc(r.label)}<b>${esc(r.text)}</b></div>`).join('')}</div>
    ${prof.insight?`<div class="insight">${tpl(prof.insight)}</div>`:''}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.quizResult = (c, el)=>{
  const g1 = S.a.goal_1||'stress'; const prof = (c.profiles&&(c.profiles[g1]||c.profiles.default))||{}; S.L.profile_name = prof.name||'';
  el.innerHTML = `${head(c,{sm:true})}<div class="profname" style="margin-top:22px">${esc(prof.name||'')}<small>${tpl(c.scoreLabel||'Your starting point')}</small></div>${prof.body?`<p class="body">${tpl(prof.body)}</p>`:''}${prof.insight?`<div class="insight">${tpl(prof.insight)}</div>`:''}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
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
  const wo = pick(c.without||[]); el.innerHTML = `${head(c,{sm:true})}<div class="compare ${wo.length?'':'single'}">${wo.length?`<div class="col"><h5>${tpl(c.withoutTitle||'On your own')}</h5><ul>${wo.map(t=>`<li>${t}</li>`).join('')}</ul></div>`:''}<div class="col with"><h5>${tpl(c.withTitle||'With Balance')}</h5><ul>${pick(c.with).map(t=>`<li>${t}</li>`).join('')}</ul></div></div>${c.body?`<p class="body">${tl(c.body)}</p>`:''}${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.benefits = (c, el)=>{
  el.innerHTML = `${head(c,{sm:true})}${laurelsHTML(c.laurels)}<div class="vlist">${c.items.map(it=>`<div class="vitem">${CHECK}<div><div class="t">${tpl(it.title||it)}</div>${it.subtitle?`<div class="s">${tpl(it.subtitle)}</div>`:''}</div></div>`).join('')}</div>${c.cite?`<p class="cite">${tpl(c.cite)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};
RENDER.cytr = (c, el)=>{
  let days = 2; const fmt = d => { const t=new Date(); t.setDate(t.getDate()+7-d); return t.toLocaleDateString('en-US',{month:'short',day:'numeric'}); };
  const draw = ()=>{ el.innerHTML = `<svg width="200" height="150" viewBox="0 0 200 150" fill="none" style="margin-bottom:22px"><rect x="62" y="6" width="76" height="138" rx="14" stroke="#B7B1D9" stroke-width="3" fill="#fff"/><rect x="50" y="34" width="100" height="26" rx="6" fill="#D7EDF0"/><circle cx="62" cy="47" r="6" fill="#30C5CA"/><rect x="74" y="41" width="60" height="4" rx="2" fill="#fff"/><rect x="74" y="50" width="44" height="4" rx="2" fill="#fff"/><circle cx="28" cy="76" r="14" stroke="#0A0A0B" stroke-width="1.5"/><circle cx="20" cy="84" r="12" fill="#FDF1EB"/><rect x="146" y="10" width="20" height="20" rx="3" transform="rotate(20 156 20)" stroke="#0A0A0B" stroke-width="1.5" fill="#FDF1EB"/><path d="M158 96c0 14 12 14 12 26" stroke="#0A0A0B" stroke-width="1.5"/><circle cx="170" cy="124" r="4" stroke="#0A0A0B" stroke-width="1.5" fill="#fff"/><line x1="56" y1="144" x2="144" y2="144" stroke="#0A0A0B" stroke-width="1.5"/></svg><h1 class="title sm" data-ek="title">${esc((c.titleTpl||"We'll remind you {days} days\nbefore your trial ends").replace('{days}',days)).replace(/\n/g,'<br>')}</h1><div class="opts compact" style="margin-top:34px">${[2,3].map(d=>`<button class="opt cytr-opt ${d===days?'sel':''}" data-d="${d}" style="background:#fff;border:2px solid ${d===days?'var(--deep)':'#E3E6E8'};min-height:64px;justify-content:space-between"><span class="txt" style="color:${d===days?'var(--ink)':'var(--grey)'}">${d} days before</span><span style="font-weight:400;font-size:14px;color:${d===days?'var(--ink)':'var(--grey)'}">${fmt(d)}</span></button>`).join('')}</div><div class="spacer"></div>`;
    el.insertAdjacentHTML('beforeend', cta('Continue'));
    el.querySelectorAll('.cytr-opt').forEach(b=>b.onclick=()=>{ days=Number(b.dataset.d); draw(); });
    $('#cta').onclick=()=>{ setA('trial_reminder', String(days), days+' days before'); go(1); }; };
  draw();
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
  if(c.design==='live'){
    const reviews = c.reviews || [{"t":"I use it daily and I'm finally sleeping better.. Premium is so worth it!","w":"Tracy"},{"t":"It helps me fall asleep, helps me relax when my anxiety is high, and just works SO well as an app.","w":"Maya P."},{"t":"It's helped me calm down during panic attacks or when I'm overwhelmed.","w":"Steffanosaur"}];
    const K = Object.assign({title:'7 days for free', sub:'then $5.83 / month\n($69.99 billed yearly after trial)', laurel1:'10M+ / happy users', laurel2:'4.9 star rating', nopay:'No payment due now', cta:'Start your FREE week', plans:'View all plans'}, c.copy||{});
    const [l1a,l1b]=K.laurel1.split(' / ');
    pw.innerHTML = `<button class="x" style="left:14px;right:auto" aria-label="Close">×</button>
      <div class="pw-live"><h2 data-ek="pw:title">${esc(K.title)}</h2><div class="pw-sub" data-ek="pw:sub">${esc(K.sub).replace(/\n/g,'<br>')}</div>
      <div class="pw-laurels"><div class="wreath"><svg class="wr" viewBox="0 0 140 64" fill="none" xmlns="http://www.w3.org/2000/svg"><g stroke="#30C5CA" stroke-width="2" stroke-linecap="round"><path d="M28 60 C10 50 6 30 14 8"/><path d="M112 60 C130 50 134 30 126 8"/></g><g fill="#30C5CA">${[[14,12,-40],[11,22,-30],[10,33,-15],[12,44,0],[17,53,15]].map(([x,y,r])=>`<ellipse cx="${x}" cy="${y}" rx="6" ry="3" transform="rotate(${r} ${x} ${y})"/><ellipse cx="${140-x}" cy="${y}" rx="6" ry="3" transform="rotate(${-r} ${140-x} ${y})"/>`).join('')}</g></svg><div class="w-in" data-ek="pw:laurel1"><b>${esc(l1a||'')}</b><span>${esc(l1b||'')}</span></div></div><div class="pw-stars"><b data-ek="pw:laurel2">${esc(K.laurel2)}</b><span>★★★★★</span></div></div>
      <div class="reviews pw-reviews">${reviews.map((r,i)=>`<div class="review pw-review"><div class="stars">★★★★★</div><p data-ek="pw:review:${i}">${esc(r.t)}</p><div class="who" data-ek="pw:who:${i}">${esc(r.w)}</div></div>`).join('')}</div>
      <div class="spacer"></div><div class="pw-nopay">✓ &nbsp;<span data-ek="pw:nopay">${esc(K.nopay)}</span></div>
      <div class="bottom" style="padding-bottom:0">${S.edit?`<div class="cta" id="cta" role="button" data-ek="pw:cta">${esc(K.cta)}</div>`:`<button class="cta" id="cta">${esc(K.cta)}</button>`}</div><div class="fine"><span style="text-decoration:underline;color:var(--ink)" data-ek="pw:plans">${esc(K.plans)}</span></div></div>`;
  } else if(c.design==='recime'){
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
  pw.querySelector('#cta').onclick=()=>{ if(S.edit) return; setA('paywall','trial','Started trial'); pw.remove(); go(1); };
  if(S.edit) makeEditable(pw, c);
};
RENDER.end = (c, el)=>{
  const other = S.deckId==='wishlist'?'constrained':'wishlist';
  el.innerHTML = `${head(c,{sm:true})}${c.body?`<p class="body">${tl(c.body)}</p>`:''}${c.items?`<div class="vlist">${c.items.map(it=>`<div class="vitem">${CHECK}<div><div class="t">${tpl(it.title||it)}</div>${it.subtitle?`<div class="s">${tpl(it.subtitle)}</div>`:''}</div></div>`).join('')}</div>`:''}<div class="endnote">${tpl(c.note||'')}</div><div class="spacer"></div><div class="bottom"><button class="cta" id="cta">Start over</button><a class="cta outline" style="display:flex;align-items:center;justify-content:center;text-decoration:none" href="${location.pathname}${modeQ()}#/${other}">Try the ${other==='wishlist'?'wish list':'constrained'} version</a><a class="ghost" style="text-align:center;text-decoration:none" href="${location.pathname}${modeQ()}#/map/${S.deckId}">Flow map</a></div>`;
  $('#cta').onclick=()=>{ S.idx=-1; location.hash = `#/${S.deckId}`; route(); };
};
/* ---------- edit-in-place mode ---------- */
const EDITABLE = [
  {sel:'h1.title', key:'title', src:c=>c.type==='cytr'?(c.titleTpl||"We'll remind you {days} days\nbefore your trial ends"):(Array.isArray(c.title)?c.title.join('\n'):(c.title||''))},
  {sel:'.kicker', key:'kicker', src:c=>c.kicker||''},
  {sel:'p.subtitle', key:'subtitle', src:c=>c.subtitle||''},
  {sel:'p.body', key:'body', src:c=>Array.isArray(c.body)?c.body.join('\n'):(c.body||'')},
  {sel:'.reassure span', key:'reassure', src:c=>c.reassure||''},
  {sel:'p.cite', key:'cite', src:c=>c.cite||''},
  {sel:'.foot', key:'foot', src:c=>c.foot||''},
  {sel:'.disclaimer', key:'disclaimer', src:c=>Array.isArray(c.disclaimer)?c.disclaimer.join('\n'):(c.disclaimer||'')},
  {sel:'.insight', key:'insight', src:c=>{ const g=S.a.goal_1||'stress'; return (c.profiles&&c.profiles[g]&&c.profiles[g].insight)||''; }, suffix:()=>':'+(S.a.goal_1||'stress')},
  {sel:'#cardbody .cta', key:'cta', src:c=>c.cta||'Continue'},
  {sel:'#cardbody .tap', key:'tap', src:c=>c.tapLabel||'Tap to continue'},
  {sel:'.opt .txt', key:'opt', indexed:true, src:(c,i)=>(c.options&&c.options[i]&&c.options[i].text)||''},
  {sel:'.vitem .t', key:'item', indexed:true, src:(c,i)=>{ const it=c.items&&c.items[i]; return it? (typeof it==='string'? it : (it.text||it.title||'')) : ''; }},
  {sel:'.bio span', key:'bio', indexed:true, src:(c,i)=>(c.bios&&c.bios[i]&&c.bios[i].text)||''},
  {sel:'#cardbody .review p', key:'review', indexed:true, src:(c,i)=>(c.reviews&&c.reviews[i]&&c.reviews[i].text)||''},
  {sel:'.metric span:last-child', key:'metric', indexed:true, src:(c,i)=>(c.metrics&&c.metrics[i]&&c.metrics[i].text)||''},
  {sel:'.mock .mrow > span:last-child', key:'mockrow', indexed:true, src:(c,i)=>(c.mock&&c.mock.rows&&c.mock.rows[i])?[c.mock.rows[i].t,c.mock.rows[i].s].filter(Boolean).join(' / '):''},
  {sel:'.col.with li, .col:not(.with) li', key:'compare', indexed:true, src:()=>''},
  {sel:'.badge', key:'badge', indexed:true, src:(c,i)=>(c.laurels&&c.laurels[i])?[c.laurels[i].l,c.laurels[i].s].filter(Boolean).join(' / '):''},
  {sel:'.endnote', key:'note', src:c=>c.note||''},
  {sel:'.steps', key:'phase', src:c=>(S.deck.phases&&c.phase)?S.deck.phases[c.phase-1]:'', pseudo:'_deck', suffix:c=>':'+((c.phase||1)-1)},
  {sel:'.sesscard .st', key:'session:title', src:c=>{ const g=S.a.goal_1||'stress'; return (c.sessions&&(c.sessions[g]||c.sessions.default)||{}).title||''; }, suffix:()=>':'+(S.a.goal_1||'stress')},
];
function makeEditable(root, card){
  const store = edStore();
  const mineFor = (pseudo)=> (store[S.deckId]||{})[pseudo||card.id]||{};
  const wire = (el, key, raw, pseudo)=>{
    if(el.dataset.edwired) return; el.dataset.edwired='1';
    const mine = mineFor(pseudo);
    el.setAttribute('contenteditable','true'); el.classList.add('ed'); el.dataset.edkey=key; el.spellcheck=false;
    if(raw && raw.includes('{{')) el.classList.add('ed-dyn');
    if(mine[key] && mine[key].edited!=null){ el.innerHTML = esc(mine[key].edited).replace(/\n/g,'<br>'); el.classList.add('ed-changed'); }
    const rendered0 = el.innerText;
    el.addEventListener('focus', ()=>{ el.dataset.before = el.innerText; });
    el.addEventListener('blur', ()=>{
      const now = el.innerText.replace(/ /g,' ').trim(); const before = (el.dataset.before||'').trim();
      if(now===before) return;
      const st = edStore(); const cid = pseudo||card.id; st[S.deckId]=st[S.deckId]||{}; st[S.deckId][cid]=st[S.deckId][cid]||{};
      st[S.deckId][cid][key] = {source: raw, rendered: (mine[key]?mine[key].rendered:rendered0), edited: now, dynamic: !!(raw && raw.includes('{{'))};
      edSave(st); el.classList.add('ed-changed'); refreshEditBar();
    });
    el.addEventListener('keydown', e=>{ if(e.key==='Enter' && !e.shiftKey && !/title|body|disclaimer|principle|note|why|sub/.test(key)){ e.preventDefault(); el.blur(); } });
  };
  EDITABLE.forEach(def=>{
    root.querySelectorAll(def.sel).forEach((el,i)=>{
      const key = def.key + (def.indexed? ':'+i : '') + (def.suffix? def.suffix(card) : '');
      wire(el, key, def.src(card, i), def.pseudo);
    });
  });
  // anything tagged data-ek (why panel, notes, paywall, cytr)
  root.querySelectorAll('[data-ek]').forEach(el=>{
    const key = el.dataset.ek; let raw='', pseudo=null;
    if(key.startsWith('principle:')){ const [,k,f]=key.split(':'); raw=((S.deck.principles||{})[k]||{})[f]||''; pseudo='_principles'; }
    else if(key==='why:how') raw=card.how||'';
    else if(key.startsWith('note:')){ const parts=key.split(':'); const n=card.notes||{}; raw = parts[1]==='fill' ? ((n.fills||[])[Number(parts[2])]||'') : (n[parts[1]]||''); }
    else if(key.startsWith('pw:')){ raw=(card.copy||{})[key.slice(3)]||''; }
    else if(key==='title'){ raw=EDITABLE[0].src(card); }
    wire(el, key, raw, pseudo);
  });
}
function setupEdit(card, body){
  body.addEventListener('click', e=>{ if(e.target.closest('.opt,.tile,.tap,#cta,.ghost,.time,.cytr-opt,.x,.plan')) { e.stopPropagation(); e.preventDefault(); } }, true);
  makeEditable(body, card);
  const bar = document.createElement('div'); bar.className='editbar'; bar.id='editbar'; $('.screen').appendChild(bar); refreshEditBar();
}
function edStore(){ try{ return JSON.parse(localStorage.getItem('balance-proto-edits')||'{}'); }catch(e){ return {}; } }
function edSave(o){ try{ localStorage.setItem('balance-proto-edits', JSON.stringify(o)); }catch(e){} }
function edCount(){ const o=edStore(); let n=0; for(const d in o) for(const c in o[d]) n+=Object.keys(o[d][c]).length; return n; }
function setupEdit(card, body){
  const store = edStore(); const mine = (store[S.deckId]||{})[card.id]||{};
  // neutralize navigation taps inside the card; the toolbar moves the flow
  body.addEventListener('click', e=>{ if(e.target.closest('.opt,.tile,.tap,#cta,.ghost,.time,.cytr-opt,.x,.plan')) { e.stopPropagation(); e.preventDefault(); } }, true);
  EDITABLE.forEach(def=>{
    body.querySelectorAll(def.sel).forEach((el,i)=>{
      const key = def.key + (def.indexed? ':'+i : '') + (def.suffix? def.suffix() : '');
      const raw = def.src(card, i);
      el.setAttribute('contenteditable','true'); el.classList.add('ed'); el.dataset.edkey=key; el.spellcheck=false;
      if(raw && raw.includes('{{')) el.classList.add('ed-dyn');
      if(mine[key] && mine[key].edited!=null){ el.innerHTML = esc(mine[key].edited).replace(/\n/g,'<br>'); el.classList.add('ed-changed'); }
      const rendered0 = el.innerText;
      el.addEventListener('focus', ()=>{ el.dataset.before = el.innerText; });
      el.addEventListener('blur', ()=>{
        const now = el.innerText.replace(/ /g,' ').trim(); const before = (el.dataset.before||'').trim();
        if(now===before) return;
        const st = edStore(); st[S.deckId]=st[S.deckId]||{}; st[S.deckId][card.id]=st[S.deckId][card.id]||{};
        st[S.deckId][card.id][key] = {source: raw, rendered: mine[key]?mine[key].rendered:rendered0, edited: now, dynamic: !!(raw && raw.includes('{{'))};
        edSave(st); el.classList.add('ed-changed'); refreshEditBar();
      });
      el.addEventListener('keydown', e=>{ if(e.key==='Enter' && !e.shiftKey && !def.key.match(/title|body|disclaimer/)){ e.preventDefault(); el.blur(); } });
    });
  });
  // paywall lives outside #cardbody
  const bar = document.createElement('div'); bar.className='editbar'; bar.id='editbar'; $('.screen').appendChild(bar); refreshEditBar();
}
function refreshEditBar(){ const bar=$('#editbar'); if(!bar) return; const n=edCount(); bar.innerHTML = `<button id="ed-back">‹</button><span>Edit mode · <b>${n}</b> edit${n===1?'':'s'}</span><button id="ed-export" ${n?'':'disabled'}>Export</button><button id="ed-next">›</button>`;
  $('#ed-back').onclick=()=>go(-1); $('#ed-next').onclick=()=>go(1); $('#ed-export').onclick=exportEdits; }
function exportEdits(){
  const st = edStore(); const out = {exported: new Date().toISOString(), deck: S.deckId, edits: []};
  for(const d in st) for(const c in st[d]) for(const k in st[d][c]) out.edits.push(Object.assign({deck:d, card:c, field:k}, st[d][c][k]));
  const json = JSON.stringify(out, null, 1);
  const m = document.createElement('div'); m.className='sheet'; m.dataset.kind='export';
  m.innerHTML = `<button class="close" aria-label="Close">×</button><h4>Your edits (${out.edits.length})</h4><p style="margin:0 0 8px">Copy this and send it to Alex, or save it as <code>copy/edits.json</code> in the repo. The build applies it last, so these edits win. Lines marked <i>personalized</i> replace a live expression with fixed text unless the tokens are kept.</p><textarea id="ed-json" readonly>${esc(json)}</textarea><div class="row" style="margin-top:10px"><button class="btn small" id="ed-copy">Copy</button><a class="btn small secondary" id="ed-dl" download="edits.json" href="data:application/json;charset=utf-8,${encodeURIComponent(json)}">Download</a><button class="btn small secondary" id="ed-clear">Clear all edits</button></div>`;
  $('.screen').appendChild(m);
  m.querySelector('.close').onclick=()=>m.remove();
  $('#ed-copy').onclick=async()=>{ try{ await navigator.clipboard.writeText(json); $('#ed-copy').textContent='Copied'; }catch(e){ $('#ed-json').select(); document.execCommand('copy'); $('#ed-copy').textContent='Copied'; } };
  $('#ed-clear').onclick=()=>{ if(confirm('Remove all saved edits on this device?')){ edSave({}); m.remove(); renderCard(); } };
}
function deriveFrom(c,id){
  if(c.derive==='ageBand'){ const mid={'13-17':16,'18-24':21,'25-34':29,'35-44':39,'45-54':49,'55+':60}[id]||34; S.a.age=mid; S.L.age=String(mid); S.a.age_count=ageCount(mid); S.L.age_count=S.a.age_count.toLocaleString(); S.a.age_range = mid<18?'13-17':mid<25?'18-24':mid<45?'25-44':'45+'; }
}
RENDER.coaches = (c, el)=>{
  el.innerHTML = `<div class="coaches"><div class="coach"><img src="assets/coaches/ofosu.png" alt="Ofosu"><div class="n">Ofosu</div></div><div class="coach"><img src="assets/coaches/leah.png" alt="Leah"><div class="n">Leah</div></div></div>${head(c)}<div class="bios">${(c.bios||[]).map(b=>`<div class="bio"><b>${esc(b.name)}</b><span>${tpl(b.text)}</span></div>`).join('')}</div>${c.body?`<p class="body">${tl(c.body)}</p>`:''}<div class="spacer"></div>`;
  el.insertAdjacentHTML('beforeend', cta(c.cta)); bindNext();
};

route();
})();
