#!/usr/bin/env python3
"""Shared deck-building library for the Balance onboarding prototypes.
One builder per competitor base (build_decks.py = Calmer, build_decks_it.py = Insight Timer) authors its wish list and derives its
constrained deck; everything they share lives here: the note helper, sourced proof constants, the principles glossary, the lint,
the copy/edits.json applier and the write + check + cache-stamp step.
Tags: existing | unused | copy | swift | superwall | new | cut.  Copy in [brackets] is a placeholder to verify."""
import json, copy, re, sys, os, subprocess, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def N(template, tag, why, calmer=None, evidence=None, fills=None, loss=None, ref=None):
    d = {"template": template, "tag": tag, "why": why}
    if calmer: d["calmer"] = calmer
    if evidence: d["evidence"] = evidence
    if fills: d["fills"] = fills
    if loss: d["loss"] = loss
    if ref: d["ref"] = ref
    return d


MEDEXP = [
  {"id":"none","text":"New to meditation","color":"misty_peach","icon":"icon-new"},
  {"id":"once_or_twice","text":"Tried it once or twice","color":"mint_green","icon":"icon-tried"},
  {"id":"a_little","text":"Meditate occasionally","color":"papaya_whip","icon":"icon-occasionally"},
  {"id":"a_lot","text":"Meditate often","color":"polar_blue","icon":"icon-often"}]
BADGES = [{"l":"Google Play's Best App of 2021"},{"l":"Apple's App of the Day"},{"stars":True,"l":"4.9","s":"120,000+ App Store ratings"}]
REVIEWS = [
  {"text":"My therapist recommended this for me to work on during off session. I was skeptical at first but I had this for over a year now and it's helped me calm down during panic attacks or when I'm overwhelmed.","who":"Steffanosaur, App Store review"},
  {"text":"It helps me fall asleep, helps me relax when my anxiety is high, and just works SO well as an app.","who":"Maya P., App Store review"},
  {"text":"This app has changed how I view myself and the world. Taught me how to meditate, the benefits of mindfulness and meditation. Love that they use real voices and not AI. It's worth paying for.","who":"Sgomz, App Store review"}]
FREQ4 = [{"id":"not_at_all","text":"Not at all","color":"mint_green"},{"id":"some","text":"Some days","color":"papaya_whip"},{"id":"most","text":"Most days","color":"apricot"},{"id":"nearly_every","text":"Nearly every day","color":"misty_peach"}]


PRINCIPLES = {
 "arrival": {"name":"Meet the arrival","text":"Most new users come from a Meta ad about stress or anxiety and have never used a meditation app. Orient them before asking anything personal, and speak to the reason they tapped.","source":"HDYHAU Sep 4: Meta is 40% of respondents at 6.6% trial start vs 13.9% overall; round 2 A2 (newcomers reached a paywall not knowing what the app does)"},
 "proof-early": {"name":"Proof before the ask","text":"Trust is built before the commitment moment, not at it. Awards, ratings and member counts go where the user is still deciding whether to invest 3 minutes.","source":"March A3 (the store listing was the strongest pre-app trust signal); Calmer #1; Insight Timer's 5 proof placements"},
 "payoff": {"name":"Every ask has a payoff","text":"A question earns its place by changing something the user can see: a reason line for why we ask, and the answer used within 2 screens.","source":"Growth Gems principle 2; 23-app benchmark rule 2 (reason in the header); rule 3 (result points back to what you said)"},
 "echo": {"name":"Say it back","text":"Read the user's own words back to them. Personalization the user cannot see is not personalization to them.","source":"Synthesis #1 (answer echo, the biggest gap vs the field); round 2 A4 (a named result is where 'it understood me' landed); Alex 5:00 ('a major need')"},
 "rhythm": {"name":"Ask, echo, teach, preview","text":"Never run 2 question blocks back to back. After 1 or 2 questions, pay the user back with a validation, a piece of evidence or a look at the product.","source":"Calmer's spine (15 questions, ~20 interstitials); synthesis #2; round 2: 3 of 4 Calmer testers named the explanations unprompted"},
 "sourced": {"name":"Sourced, dated evidence","text":"Every number carries a source and a date. Claims are stated plainly with a disclaimer where results vary. No 'clinically proven', no unsourced stats.","source":"March B4/B5 (age-specific stats were the strongest confidence builder; ours were dated and unsourced); Anna's citation set; Balance whitepaper 2025"},
 "felt-value": {"name":"Show the product before the paywall","text":"The paywall arriving before any sense of the product was the abandonment trigger in March. Previews of real sections and a named first session stand in for felt value.","source":"March D1 (12 of 18) and F1 (5 of 6 newcomers); round 2 A5 (content access resolved the try-first objection); synthesis #10"},
 "humans": {"name":"Made by humans, shown not said","text":"Faces, voices and the handcrafted mechanism answer the 'is this AI' worry without using the word, which plants the thought.","source":"Cindy (Sep 2024); coaches prior art; App Store review 'Love that they use real voices and not AI'; 3 competitors sell teacher credibility"},
 "reassure": {"name":"Specific reassurance beside sensitive asks","text":"A concrete, checkable line next to the field it protects ('never shown to anyone') builds more trust than any general promise.","source":"23-app benchmark rule 4 (Strava, Gentler Streak: highest trust ratings in the set); the deck had zero reassurance copy"},
 "no-deficit": {"name":"Compassion, never agitation","text":"No scare copy, no presupposed diagnosis, always a 'Not sure'. Validate what the user said, then teach. The structure of Calmer's agitate-then-absolve arc is used; its claims are not.","source":"Balance voice (compassionate, grounded); synthesis #9; Calmer's dark patterns documented-not-copied"},
 "commit": {"name":"A small commitment before the big one","text":"A realistic practice goal and a reminder time right before the paywall turn intent into a plan, and make the trial feel like a decision already half made.","source":"Synthesis #4 (Insight Timer's praise ladder, cheapest high-leverage steal); Calmer #41; CYTR +24.7% trial starts"},
 "honest-result": {"name":"A result built only from real answers","text":"The profile reflects what the user actually said. No invented sub-scores, no manufactured headroom, no clinical framing.","source":"Round 2 P18 (Calmer scored his healthy diet as Fair and he thanked it); A4; 'not a clinical assessment' line"},
 "keep-what-works": {"name":"Keep what already tests well","text":"The goal screens, the reminder flow, the trial-reminder chooser and the live paywall stay as they are. The redesign is the connective tissue around them.","source":"Alex 4:35 ('keep our goal screens as they exist'); prior-art census (wins came from reordering and framing, not new content); CYTR and ReciMe are baseline wins"},
 "voice": {"name":"Balance voice","text":"Accessible, grounded, compassionate, realistic. Digits, full sentences, contractions, no first person except 'Let's', no exclamation points, no 'mindfulness' unless we teach it.","source":"Balance content style guide"},
 "trial-anxiety": {"name":"Name the trial mechanics","text":"Forgetting to cancel is the objection behind the objection. Say when the reminder comes and what happens on day 7 before asking for the trial.","source":"Round 2 A3 (the trial-reminder paywall was the only element praised unprompted for the objection it targets); Insight Timer and Calmer timelines"}
}

# ---------------- lint ----------------
def lint(deck, constrained=False, allowed=None, name_ok=None):
    errs=[]; ids=set()
    for c in deck["cards"]:
        if c["id"] in ids: errs.append(f"dup id {c['id']}")
        ids.add(c["id"])
        if "notes" not in c: errs.append(f"{c['id']}: no notes")
        if c["type"]!="end" and not c.get("principles"): errs.append(f"{c['id']}: no principles (why mode)")
        blob=json.dumps({k:v for k,v in c.items() if k not in ("notes","branch")})
        if constrained:
            if c["type"] not in allowed: errs.append(f"{c['id']}: type {c['type']} not allowed in constrained")
            toks=re.findall(r"\{\{([^}]+)\}\}", blob)
            bad=[t for t in toks if not (t.strip()=="a.name" and c["type"] in name_ok) and not (t.strip()=="L.age_count" and c["type"]=="ageMetrics")]
            if bad: errs.append(f"{c['id']}: interpolation in constrained deck: {bad[:2]}")
            if c["type"]=="question" and len(c.get("options",[]))>6: errs.append(f"{c['id']}: >6 options on a standard select")
            if c["notes"].get("tag")=="new": errs.append(f"{c['id']}: tagged new in constrained deck")
        if c["type"] in ("question","scrollableQuestion","multiselect","keyboard","slider","commitment") and not c.get("noReason") and not (c.get("subtitle") or c.get("kicker")):
            errs.append(f"{c['id']}: question without a reason line")
        if c["id"] in ("age","focus_adhd","gender") and not c.get("reassure"):
            errs.append(f"{c['id']}: sensitive ask without a reassurance line")
        t=c.get("title")
        if isinstance(t,list) and not c.get("longTitleOK"):
            if len(t)>2: errs.append(f"{c['id']}: headline has {len(t)} lines (max 2)")
            for ln in t:
                plain=re.sub(r"<[^>]+>","",re.sub(r"\{\{[^}]+\}\}","Samuel",ln))
                if len(plain)>24: errs.append(f"{c['id']}: headline line too long ({len(plain)}): {plain}")
        for k in ("title","subtitle","body"):
            v=c.get(k); s=" ".join(v) if isinstance(v,list) else (v or "")
            if "—" in s or "–" in s: errs.append(f"{c['id']}: dash in {k}")
            if re.search(r"\bAI\b", s): errs.append(f"{c['id']}: 'AI' in {k}")
    return errs


# ---------------- copy/edits.json: Alex's in-place edits, applied last so they win ----------------
def apply_edits(deck):
    path=os.path.join(ROOT,"copy","edits.json")
    if not os.path.exists(path): return 0
    data=json.load(open(path)); edits=data.get("edits",data if isinstance(data,list) else [])
    by_id={c["id"]:c for c in deck["cards"]}; applied=0; dyn=[]
    for e in edits:
        if e.get("deck") not in (None,"both",deck["id"]): continue
        field=e.get("field",""); val=e.get("edited","")
        cid=e.get("card")
        # deck-level pseudo cards
        if cid=="_principles":
            _,k,f=field.split(":",2)
            if k in deck.get("principles",{}) and f in ("name","text","source"): deck["principles"][k][f]=val; applied+=1
            continue
        if cid=="_deck":
            if field=="deck:name": deck["name"]=val; applied+=1
            elif field=="deck:description": deck["description"]=val; applied+=1
            elif field.startswith("phase:") and deck.get("phases"): deck["phases"][int(field.split(":")[1])]=val; applied+=1
            continue
        c=by_id.get(cid)
        if not c: continue
        key,_,idx=field.partition(":")
        try:
            if key=="why": c["how"]=val
            elif key=="note":
                sub,_,i=idx.partition(":"); n=c.setdefault("notes",{})
                if sub=="fill": n.setdefault("fills",[])
                if sub=="fill" and i!="": 
                    while len(n["fills"])<=int(i): n["fills"].append("")
                    n["fills"][int(i)]=val
                elif sub in ("why","loss","evidence","calmer","ref"): n[sub]=val
                else: continue
            elif key=="pw":
                sub,_,i=idx.partition(":")
                if sub in ("review","who"):
                    revs=c.setdefault("reviews",[{"t":"I use it daily and I'm finally sleeping better.. Premium is so worth it!","w":"Tracy"},{"t":"It helps me fall asleep, helps me relax when my anxiety is high, and just works SO well as an app.","w":"Maya P."},{"t":"It's helped me calm down during panic attacks or when I'm overwhelmed.","w":"Steffanosaur"}])
                    revs[int(i)]["t" if sub=="review" else "w"]=val
                else: c.setdefault("copy",{})[sub]=val
            elif key=="cta": c["cta"]=val
            elif key=="tap": c["tapLabel"]=val
            elif key=="session": c["sessions"][idx.split(":")[1]]["title"]=val
            elif key=="title":
                if c["type"]=="cytr": c["titleTpl"]=val
                else: c["title"]=val.split("\n")
            elif key in ("kicker","subtitle","reassure","cite","foot","note"): c[key]=val
            elif key=="body": c["body"]=val.split("\n") if "\n" in val else val
            elif key=="disclaimer": c["disclaimer"]=val.split("\n")
            elif key=="insight": c["profiles"][idx]["insight"]=val
            elif key=="opt": c["options"][int(idx)]["text"]=val
            elif key=="item":
                it=c["items"][int(idx)]
                if isinstance(it,str): c["items"][int(idx)]=val
                elif "text" in it: it["text"]=val
                else: it["title"]=val
            elif key=="bio": c["bios"][int(idx)]["text"]=val
            elif key=="review": c["reviews"][int(idx)]["text"]=val
            elif key=="badge":
                t,_,sub=val.partition(" / "); c["laurels"][int(idx)]["l"]=t.strip(); c["laurels"][int(idx)]["s"]=sub.strip()
            elif key=="mockrow":
                t,_,sub=val.partition(" / "); c["mock"]["rows"][int(idx)]["t"]=t.strip(); c["mock"]["rows"][int(idx)]["s"]=sub.strip()
            else: continue
            applied+=1
            if e.get("dynamic") and "{{" not in val: dyn.append(f"{c['id']}.{field}")
        except Exception as ex:
            print(f"  ! could not apply edit {e.get('card')}.{field}: {ex}")
    if dyn: print(f"  ! {deck['id']}: {len(dyn)} personalized line(s) replaced with fixed text: {', '.join(dyn[:6])}")
    return applied


# ---------------- write + check + stamp ----------------
def finish(decks, allowed, name_ok, check=True):
    """decks: [(deck_dict, constrained_bool), ...]. Applies edits, lints, writes decks/<id>.json, runs check_exprs.js, stamps index.html."""
    ok=True
    for deck, cons in decks:
        n=apply_edits(deck)
        if n: print(f"{deck['id']}: applied {n} copy edit(s) from copy/edits.json")
        for c in deck["cards"]:
            if "with_" in c: c["with"] = c.pop("with_")
        e = lint(deck, cons, allowed, name_ok)
        print(f"{deck['id']}: {len(deck['cards'])} cards, lint {'OK' if not e else 'FAIL'}")
        for x in e: print("   -", x)
        ok = ok and not e
        json.dump(deck, open(os.path.join(ROOT,"decks",deck["id"]+".json"),"w"), indent=1, ensure_ascii=False)
    if ok and check:
        r = subprocess.run(["node", os.path.join(ROOT,"tools","check_exprs.js")], capture_output=True, text=True); print(r.stdout.strip())
        if r.returncode: print(r.stderr); ok=False
    # stamp index.html so browsers pick up new engine/styles immediately (GitHub Pages caches aggressively)
    if ok:
        ip=os.path.join(ROOT,"index.html"); html=open(ip).read(); stamp=str(int(time.time()))
        html=re.sub(r'styles\.css(\?v=\d+)?', f'styles.css?v={stamp}', html); html=re.sub(r'engine\.js(\?v=\d+)?', f'engine.js?v={stamp}', html)
        open(ip,"w").write(html)
    return ok
