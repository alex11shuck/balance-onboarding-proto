#!/usr/bin/env python3
"""Regenerates the spec doc in the context directory from the two deck JSONs."""
import json, os, sys
R=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'decks')
OUT='/Users/alexshuck/Desktop/context-directory/projects/balance-onboarding-prototypes/prototype-calmer-package-v1.md'
W=json.load(open(R+'/wishlist.json')); C=json.load(open(R+'/constrained.json'))
cw={c['id']:c for c in W['cards']}; cc={c['id']:c for c in C['cards']}
TAG={'existing':'existing template','unused':'built, unused','copy':'copy change','swift':'Swift bookend','superwall':'Superwall','new':'new template','cut':'cut'}
def title(c):
    t=c.get('title') or c['id']; t=' '.join(t) if isinstance(t,list) else t
    import re
    t=re.sub(r'<[^>]+>','',t)
    return re.sub(r'\{\{[^}]+\}\}','[…]',t)
def br(c):
    b=c.get('branch')
    if not b: return 'everyone'
    return (b.replace("a.goal_1==='stress'","stress #1").replace("a.goal_1==='sleep'","sleep #1").replace("a.goal_1==='mood'","mood #1").replace("a.goal_1==='focus'","focus #1")
             .replace("a.goal_sleep==='yes' && a.goal_1!=='sleep'","sleep selected, not #1").replace("a.goal_sleep!=='yes'","no sleep goal").replace("a.goal_sleep==='yes'","sleep selected").replace("a.paywall==='trial'","trial started"))
asks={'question','scrollableQuestion','multiselect','keyboard','slider','commitment','goalRanking'}
def flow_table(d):
    out=["| # | Screen | Type | Shown when | Cost | Calmer | Why it's here |","|---|---|---|---|---|---|---|"]
    for i,c in enumerate(d['cards'],1):
        n=c.get('notes',{})
        out.append(f"| {i} | **{title(c)}** (`{c['id']}`) | {c['type']} | {br(c)} | {TAG.get(n.get('tag'),n.get('tag',''))} | {n.get('calmer','')} | {n.get('why','')} |")
    return '\n'.join(out)
m=["| Wish-list screen | In the constrained version | Production template | Cost | What we lose |","|---|---|---|---|---|"]
kept=adapted=cut=0
for c0 in W['cards']:
    cid=c0['id']; c=cc.get(cid)
    if c is None:
        cut+=1; m.append(f"| `{cid}` | **Cut** | | cut | {c0.get('notes',{}).get('why','')[:140]} |"); continue
    n=c.get('notes',{})
    changed = json.dumps({k:v for k,v in c0.items() if k!='notes'},sort_keys=True)!=json.dumps({k:v for k,v in c.items() if k!='notes'},sort_keys=True)
    if changed: adapted+=1
    else: kept+=1
    m.append(f"| `{cid}` | {('Adapted: '+n.get('why','')) if changed else 'Kept as is'} | `{n.get('template',c['type'])}` | {TAG.get(n.get('tag'),n.get('tag',''))} | {n.get('loss','')} |")
added=[c for c in C['cards'] if c['id'] not in cw]
for c in added: m.append(f"| (new in constrained) `{c['id']}` | {c['notes'].get('why','')} | `{c['notes'].get('template',c['type'])}` | {TAG.get(c['notes'].get('tag'))} | |")
fills=[]
for d in (W,C):
    for c in d['cards']:
        for f in c.get('notes',{}).get('fills',[]):
            line=f"- `{c['id']}`: {f}"
            if line not in fills: fills.append(line)
def tags(d):
    t={}
    for c in d['cards']: k=c.get('notes',{}).get('tag','existing'); t[k]=t.get(k,0)+1
    return ', '.join(f"{v} {TAG[k]}" for k,v in sorted(t.items()))
wa=sum(1 for c in W['cards'] if c['type'] in asks); ca=sum(1 for c in C['cards'] if c['type'] in asks)
doc=f"""# Balance onboarding prototype v1: Calmer's package, two versions

_Built Sep 4, 2026; revised the same afternoon on Alex's critique. Live at **https://alex11shuck.github.io/balance-onboarding-proto/** (add `?notes=1` for build notes; flow maps at `#/map/wishlist` and `#/map/constrained`). Source: [alex11shuck/balance-onboarding-proto](https://github.com/alex11shuck/balance-onboarding-proto). Inputs: Alex's talk-over ([calmer-alex-walkthrough-2026-09-04.md](competitors/calmer-alex-walkthrough-2026-09-04.md)), the [Calmer teardown](competitors/calmer-2026-08-21.md), the [deck map](baseline/deck-map.md), the [cross-app synthesis](competitors/synthesis-2026-08-20.md), the Sep 3 dry-run report (A3, A4, A5; Calmer lowest objection load), the [web funnel walkthrough](web-onboarding-2026-08-20.md), the [Meet-the-coaches decision](handcrafted-coaches-screen-angles.md) and the [23-app vertical benchmark](vertical-benchmarks-23-apps.md)._

## What it is

Two clickable flows, one URL, mobile-first (a BetaTesting tester can run it on an iPhone; the study design can be rerun against it). Both end on today's paywall as a static terminal screen with an ✕. Neither copies Calmer's paywall, wheel, countdown, agitation copy or AI companion.

| | Wish list | Constrained |
|---|---|---|
| Screens in deck | {len(W['cards'])} | {len(C['cards'])} |
| Asks (questions, pickers, entries) | {wa} | {ca} |
| Cost tags | {tags(W)} | {tags(C)} |
| Sign-up | after the trial starts (Swift bookend change) | before the paywall, as today |
| Branching | all four goal paths carry the ask, echo, teach, preview rhythm; sleep block fires on sleep *selection* | today's goal-1 branching kept intact; new cards only inserted |
| Result profile | computed sub-scores from answers actually given, insight echoes experience and schedule | named profile per goal on the primer card, no scores |
| Interpolation | name, symptoms, sources, schedule and 'look forward to' picks echoed | none, except the name on text cards (the engine already replaces a name placeholder there) |

## The slimming, in one view

Of the {len(W['cards'])} wish-list screens: **{kept} carry over unchanged**, **{adapted} are adapted** (same slot, existing template, usually static copy per goal branch instead of the user's own words), **{cut} is cut** (gender), and the proof screen splits back into 2 cards because the age stat and a testimonial are different templates. What the constrained version gives up, in order of how much it hurts:

1. **The user's own words read back.** Every echo beat and recap becomes static copy per goal branch. The engine replaces a name placeholder on text and textImage cards, so first-name echo survives; answer echo does not.
2. **The computed profile.** The named profile per goal survives on the primer card (kicker, name, insight); the sub-scores and the score number need a template.
3. **The two-column outcomes card built from the user's picks.** Becomes a one-column list per goal. Michal's paywall intro screen carries the two-column framing next week.
4. **Previews lose their paragraph.** textImage takes a headline and an image; the sentence of explanation goes behind Learn More.
5. **Small things:** the slider becomes a 4-option select, the praise line after the commitment pick is gone, HDYHAU's reason line rides as a second headline line (scrollableQuestion has no subtitle), the reviews carousel is one quote per card, and the step counter is out (hard limit).

Checked against what the Lua cards read (hoth, Aug 7 pin): `question` has `subTitle`, `allowMultipleAnswers`, per-answer `asset`; `multiselect`, `keyboard`, `setReminderTime` and `list` have `subTitle`; `text` and `textImage` replace the name placeholder and offer a Learn More panel; `goalMeditationPrimer` has title, text and subtext (the richest static card); `userReview` is one quote and one asset; `meditationLoading` takes upperText/lowerText pairs; `quizResult` scores a quiz and is not a profile card. Two flags for Matheus: F1D1 audio triggers are embedded in the onboarding sequence (inserted cards need a check), and Android only forwards whitelisted flags into the deck.

**Decisions taken at the plan (Alex, Sep 4):** public GitHub Pages repo with Work Sans standing in for Graphik · stop at today's paywall, no new paywall or decline path · wish list moves sign-up after the trial starts · all four goal paths written (mood and focus added on the critique).

## Wish list, screen by screen

{flow_table(W)}

## Constrained, screen by screen

{flow_table(C)}

## The whittle, card by card

{chr(10).join(m)}

## Verify before anything ships

{chr(10).join(fills)}

## Research and directives carried

- **Alex's talk-over:** proof up front, tell people what the questions do, who-you-are early, keep the goal screens as they are, the answer-echo recap, education and section previews of Balance content, whole-health questions, the positive-future question, mid-flow social proof, a longer named loading screen, the profile framed as on web, the progress graph, the commitment question, stop at the paywall.
- **Alex's critique (Sep 4 afternoon):** laurels replaced with plain badges · welcome headline is the live winning variant · health-professional option shortened to one line · mood and focus paths built out · more speak-back moments (friend referral, schedule, experience, 'look forward to' picks) · the three list screens differentiated: recap = what we heard, outcomes = what changes, benefits cut · reviews and the age stat combined into one proof screen · paywall note: the live paywall is the ReciMe version.
- **Round 2 dry run:** the named result profile is where 'it understood me' landed (A4). Calmer's explanations were named by 3 of 4 testers. Trial-reminder paywall praise (A3) and decline into content (A5) live in the paywall card's notes, not built.
- **Manufactured-headroom lesson (P18):** sub-scores derive only from answers given; unanswered dimensions are omitted.
- **March study:** B2 → multi-answer symptom questions; B4/B5 → sourced, age-specific stats; H3 → no 'free'-led framing at the commit moment; D1/F1 → previews and profile before the paywall.
- **23-app benchmark:** first name early; reason line on every question; reassurance beside age, ADHD, name; a number on the reminder ask; step counter wish-list only; deferred account gate and terminal paywall are the archetype's norm.

## Open for review

1. Gender question: keep in the wish list or drop, given the round-2 read on Calmer's gendered copy.
2. Headline register on the coaches card, and the profile names (content pass).
3. Whether the study rerun uses the wish list, the constrained flow, or both as arms.
4. The paywall mock is the Aug 16 carousel; swap for the ReciMe design if this is used for testing.
"""
open(OUT,'w').write(doc); print('spec written:', len(doc), 'chars;', 'kept',kept,'adapted',adapted,'cut',cut)
