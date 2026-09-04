// Evaluates every {{expr}} and branch in both decks against a demo persona; exits 1 on any throw.
const fs=require('fs');
const src=fs.readFileSync(__dirname+'/../engine.js','utf8');
const Hsrc=src.slice(src.indexOf('const H = {'), src.indexOf('function tpl('));
const GOAL_LABEL={stress:'Reduce Stress',sleep:'Improve Sleep',focus:'Increase Focus',mood:'Improve Mood'};
const H=new Function('GOAL_LABEL', Hsrc+' return H;')(GOAL_LABEL);
const personas=[
 {a:{ name:'Sam', age:34, age_count:1034000, goals:['stress','sleep'], goal_1:'stress', goal_2:'sleep', goal_stress:'yes', goal_sleep:'yes', goal_mood:'no', goal_focus:'no', hdyhau:'family_and_friends', how_often_feel_stress:'sometimes', how_experience_stress:['anxious_thoughts','difficulty_sleeping'], stress_source:'work_or_school', sleep_trouble:'some', exercise:'2', schedule:'busy', future:['calm_nights','clear_head'], has_meditated_before:'none', commitment:'5', paywall:'trial' },
  L:{ name:'Sam', age_count:'1,034,000', goal_1:'Reduce Stress', goal_2:'Improve Sleep', hdyhau:'Family and friends', how_often_feel_stress:'Sometimes', how_experience_stress:'Anxious thoughts, Difficulty sleeping', stress_source:'Work or school', sleep_trouble:'Some nights', exercise:'A few times a week', schedule:'Busy most days', future:'Calm nights and deep sleep, A clearer head at work', has_meditated_before:'New to meditation' }},
 {a:{ name:'Jo', age:52, age_count:236909, goals:['mood'], goal_1:'mood', goal_mood:'yes', goal_stress:'no', goal_sleep:'no', goal_focus:'no', low_mood_freq:'unsure', happiest_around:'myself', improve_mood:'unsure', exercise:'0', schedule:'open', future:[], has_meditated_before:'a_lot' }, L:{ name:'Jo', age_count:'236,909', low_mood_freq:'Not sure', happiest_around:'By myself', improve_mood:'Not sure', exercise:'Rarely', schedule:'Pretty open', future:'', has_meditated_before:'Meditate often' }},
 {a:{ name:'Ana', age:19, age_count:542273, goals:['focus','sleep'], goal_1:'focus', goal_focus:'yes', goal_sleep:'yes', goal_stress:'no', goal_mood:'no', most_distracting:'technology', finishing_tasks:'always', procrastinate:'rarely', has_adhd_or_add:'not_shared', sleep_trouble:'most' }, L:{ name:'Ana', age_count:'542,273', most_distracting:'Technology', finishing_tasks:'Almost always', procrastinate:'Rarely', sleep_trouble:'Most nights' }},
 {a:{ name:'Lee', age:40, age_count:691213, goals:['stress'], goal_1:'stress', goal_stress:'yes', goal_sleep:'no', goal_mood:'no', goal_focus:'no', how_often_feel_stress:'unsure', how_experience_stress:['moodiness'], stress_source:'unsure', exercise:'1', schedule:'packed', future:['energy'], has_meditated_before:'once_or_twice', paywall:'declined' }, L:{ name:'Lee', age_count:'691,213', how_often_feel_stress:'Not sure', how_experience_stress:'Moodiness', stress_source:'Not sure', exercise:'Once or twice a week', schedule:'Packed, every day', future:'Energy for the things I enjoy', has_meditated_before:'Tried it once or twice' }}];
let bad=0, rendered=0;
for(const f of ['wishlist','constrained']){
  const d=JSON.parse(fs.readFileSync(__dirname+`/../decks/${f}.json`,'utf8'));
  for(const c of d.cards){
    const blob=JSON.stringify(c);
    for(const p of personas){
      let shown=true;
      if(c.branch){ try{ shown=!!new Function('a','L','return ('+c.branch+')')(p.a,p.L);}catch(err){ bad++; console.log(`${f}/${c.id} BRANCH: ${err.message}`); continue; } }
      if(!shown) continue;   // the engine never renders this card for this persona
      // evaluate only the parts the engine would render: drop list/compare items whose `when` fails
      const parts=[];
      const walk=(x)=>{ if(x==null) return; if(typeof x==='string'){ parts.push(x); return; } if(Array.isArray(x)){ x.forEach(walk); return; } if(typeof x==='object'){ if(x.when){ try{ if(!new Function('a','L','return ('+x.when+')')(p.a,p.L)) return; }catch(e){} } Object.keys(x).filter(k=>k!=='notes'&&k!=='branch'&&k!=='when').forEach(k=>walk(x[k])); } };
      walk(c);
      for(const str of parts){
        for(const m of str.matchAll(/\{\{([^}]+)\}\}/g)){
          const e=m[1];
          try{ const v=new Function('a','L','H','return ('+e+')')(p.a,p.L,H); rendered++; if(v!=null && String(v).includes('undefined')) { bad++; console.log(`${f}/${c.id}: renders "undefined" for persona ${p.a.name||'(empty)'}: ${e.slice(0,120)}`); } }
          catch(err){ bad++; console.log(`${f}/${c.id}: ${err.message} :: ${e.slice(0,140)}`); }
        }
      }
    }
  }
}
console.log(`expressions evaluated: ${rendered}, problems: ${bad}`);
process.exit(bad?1:0);
