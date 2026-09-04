#!/usr/bin/env python3
"""Regenerates the Insight Timer package spec in the context directory from decks/it_wishlist.json and decks/it_constrained.json."""
import json, os, re
R=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'decks')
OUT='/Users/alexshuck/Desktop/context-directory/projects/balance-onboarding-prototypes/prototype-insighttimer-package-v1.md'
W=json.load(open(R+'/it_wishlist.json')); C=json.load(open(R+'/it_constrained.json'))
cw={c['id']:c for c in W['cards']}; cc={c['id']:c for c in C['cards']}
TAG={'existing':'existing template','unused':'built, unused','copy':'copy change','swift':'Swift bookend','superwall':'Superwall','new':'new template','cut':'cut'}
def title(c):
    t=c.get('title') or c['id']; t=' '.join(t) if isinstance(t,list) else t
    t=re.sub(r'<[^>]+>','',t); return re.sub(r'\{\{[^}]+\}\}','[…]',t)
def br(c):
    b=c.get('branch')
    if not b: return 'everyone'
    return (b.replace("a.goal_1==='stress'","stress #1").replace("a.goal_1==='sleep'","sleep #1").replace("a.goal_1==='mood'","mood #1").replace("a.goal_1==='focus'","focus #1")
             .replace("a.goal_sleep==='yes' && a.goal_1!=='sleep'","sleep selected, not #1").replace("a.goal_sleep!=='yes'","no sleep goal").replace("a.goal_sleep==='yes'","sleep selected").replace("a.paywall==='trial'","trial started")
             .replace("(a.who_for||[]).includes('kids')","'My kids' picked"))
asks={'question','scrollableQuestion','multiselect','keyboard','slider','commitment','goalRanking'}
def flow_table(d):
    g=d.get('principles',{})
    out=["| # | Screen | Type | Shown when | Cost | Insight Timer | Why it's here (build) | Principles (why mode) |","|---|---|---|---|---|---|---|---|"]
    for i,c in enumerate(d['cards'],1):
        n=c.get('notes',{}); pr=', '.join(g.get(k,{}).get('name',k) for k in c.get('principles',[]))
        out.append(f"| {i} | **{title(c)}** (`{c['id']}`) | {c['type']} | {br(c)} | {TAG.get(n.get('tag'),n.get('tag',''))} | {n.get('ref','')} | {n.get('why','')} | {pr}{(': '+c['how']) if c.get('how') else ''} |")
    return '\n'.join(out)
REPLACED={'reminder_time_sleep':"Replaced by today's early (sleep #1) and late (sleep 2 to 4) bedtime cards"}
m=["| Wish-list screen | In the constrained version | Production template | Cost | What we lose |","|---|---|---|---|---|"]
kept=adapted=cut=0
for c0 in W['cards']:
    cid=c0['id']; c=cc.get(cid)
    if c is None:
        cut+=1; m.append(f"| `{cid}` | **{REPLACED.get(cid,'Cut')}** | | cut | {c0.get('notes',{}).get('why','')[:160]} |"); continue
    n=c.get('notes',{})
    changed = json.dumps({k:v for k,v in c0.items() if k not in ('notes','how','principles')},sort_keys=True)!=json.dumps({k:v for k,v in c.items() if k not in ('notes','how','principles')},sort_keys=True)
    if changed: adapted+=1
    else: kept+=1
    m.append(f"| `{cid}` | {('Adapted: '+n.get('why','')) if changed else 'Kept as is'} | `{n.get('template',c['type'])}` | {TAG.get(n.get('tag'),n.get('tag',''))} | {n.get('loss','')} |")
added=[c for c in C['cards'] if c['id'] not in cw]
for c in added: m.append(f"| (today's card, constrained only) `{c['id']}` | {c['notes'].get('why','')} | `{c['notes'].get('template',c['type'])}` | {TAG.get(c['notes'].get('tag'))} | |")
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
doc=f"""# Balance onboarding prototype v1: Insight Timer's package, two versions

_Built Sep 4, 2026 (evening), autonomously and **unreviewed**: Alex asked for the Calmer prototyping process rerun with Insight Timer as the base and without his input, so there is no talk-over for this one. Live at **https://alex11shuck.github.io/balance-onboarding-proto/** (the landing page now lists both packages; deep links `#/it_wishlist` and `#/it_constrained`, flow maps at `#/map/it_wishlist` and `#/map/it_constrained`; `?notes=1`, `?why=1` and `?edit=1` work the same way). Source: [alex11shuck/balance-onboarding-proto](https://github.com/alex11shuck/balance-onboarding-proto), builder `tools/build_decks_it.py`. Inputs: the [Insight Timer teardown](competitors/insighttimer-2026-08-12.md) (26 screens, Megan's Aug 12 recording), the [deck map](baseline/deck-map.md), the [cross-app synthesis](competitors/synthesis-2026-08-20.md), [Megan's takeaways triage](competitors/megan-takeaways-triage-2026-08-21.md), the round-2 reads on the Insight Timer arm (P1, P5, P9, P10, P11, P23 in [researcher-coding-corrections.md](researcher-coding-corrections.md) and the Sep 3 dry run), the [proof facts](proof-facts-2026-09-04.md), the [Meet-the-coaches decision](handcrafted-coaches-screen-angles.md), the [23-app vertical benchmark](vertical-benchmarks-23-apps.md), and the standing directives from Alex's [Calmer talk-over](competitors/calmer-alex-walkthrough-2026-09-04.md) that are not Calmer-specific (keep the goal screens, stop at today's paywall, never 'Balance Premium', laurels, no chatbot companion, sign-up after the trial in the wish list)._

## What it is

Two clickable flows on the same URL as the Calmer package, mobile-first, both ending on today's live paywall as a static terminal screen with an ✕. Insight Timer's model is the inverse of Balance's (a huge free library with premium as an upsell), so three things are deliberately **not** copied: the skippable paywall, the "Free / No ads / Forever" decline off-ramp, and the absence of any account. What is copied is the architecture the teardown named: **proof density instead of diagnostics**, interests instead of symptoms, chart-backed benefit beats, a consecutive-days commitment with a praise ladder, a dosage-lowering chart right before the minutes ask, a plan built from the answers instead of a spinner, and a dated outlook instead of a result gauge.

| | Wish list | Constrained |
|---|---|---|
| Screens in deck | {len(W['cards'])} | {len(C['cards'])} |
| Asks (questions, pickers, entries) | {wa} | {ca} |
| Cost tags | {tags(W)} | {tags(C)} |
| Goal-1 question blocks (stress_1 to 3, sleep_1 to 3, mood, focus, ADHD) | **dropped**, as Insight Timer has none; preferences and proof replace them | kept intact, in today's order and branching |
| Reminder tracks | one: time of day for everyone, bedtime for anyone with a sleep goal | today's three (sleep-first early, sleep 2 to 4 late, no-sleep training reminder) |
| Sign-up | after the trial starts (Swift bookend change) | before the paywall, as today |
| Plan moment | plan summary built from the user's own answers replaces Creating Program | today's Creating Program animation, then a static first-week list, then program-ready |
| Outlook | dated projection (6 weeks out) with the survey figure for the top goal | static graph, no date, shared figures |
| Coaches | angle 1 (Meet the coaches) as its own screen, in Insight Timer's teacher-count slot | same, static |
| Interpolation | the plan summary chips, the goal-set echo, the reminder default, the dated outlook | none |

## How it differs from the Calmer package

| | Calmer's package | Insight Timer's package |
|---|---|---|
| Asks in the wish list | 25 | {wa} |
| Spine | ask, echo, teach, preview on every goal path | proof stacked before the first question, then interests, then benefit beats between short question blocks |
| What the questions are about | symptoms, sources, routine, aspirations | who it is for, goals, experience, what content you would use, commitment, minutes, time |
| Result | named profile with answer-derived sub-scores and a gauge | a dated outlook with a sourced figure; no score, no profile name |
| Echo | recaps in the user's words after each goal block | one plan summary with the answers as checked chips |
| Proof | welcome badges, one proof screen, the coaches at the plan moment | 5 placements: badges, outcome donut, library chips, coaches, age count, plus 3 benefit charts |
| Round-2 read | lowest total objection load (5 across 4 sessions); explanations named by 3 of 4 | statistics named unprompted by 4 of 5; the only in-session resolution of try-first came from the free app, which this deck does not copy |

## The slimming, in one view

Of the {len(W['cards'])} wish-list screens: **{kept} carry over unchanged**, **{adapted} are adapted** (static rendering, praise lines stripped, interpolation removed), **{cut} cut**, and **{len(added)} of today's cards are added back** (the goal-1 question blocks, the early and late bedtime tracks, Creating Program and program-ready) because constraint #2 keeps the core branching. What the constrained version gives up, in order of how much it hurts:

1. **The plan built from the user's answers.** The summary becomes a static first-week list per goal branch. Insight Timer's chips are the one screen where its questions visibly pay off.
2. **The dated outlook.** The date and the goal-specific figure need interpolation; the constrained card is the same graph as a baked image per goal with shared figures.
3. **The praise ladder and the dynamic footnote.** Commitment and minutes become plain single-selects. Round 2's P11 chose Insight Timer's maximum "just for fun" when the question was unclear, so the reason line matters more than the praise.
4. **Animation.** The donut draw-in, the chip stagger and the four benefit charts render static; production ships an image per card on textImage.
5. **Length.** The constrained deck is {len(C['cards'])} screens because today's diagnostics come back. That is the honest cost of constraint #2 against this base, and it is the first thing to decide (see Open for review).

## The principles (why mode)

Turn on with `?why=1`. Shared with the Calmer package where the principle is the same; four are new to this base.

{chr(10).join(f"- **{v['name']}.** {v['text']} _{v.get('source','')}_" for v in W['principles'].values())}

## Wish list, screen by screen

{flow_table(W)}

## Constrained, screen by screen

{flow_table(C)}

## The whittle, card by card

{chr(10).join(m)}

## Verify before anything ships

{chr(10).join(fills)}

## Research and directives carried

- **Insight Timer teardown (what they do that we don't):** market-share donut naming competitors (adapted to an outcome number), benefit-evidence interstitials between question blocks, the commitment picker with praise ladder, the Goal Set beat, dosage-lowering before the minutes ask, the plan summary replaying answers, the personalized outcome date, the two-level HDYHAU with a chatbot channel (options added, expansion not built), the contextual push ask. Documented as inseparable from the free-library model and not copied: no auth at all, the skippable paywall and free off-ramp, raw library-scale claims, the "Join 36 Million" CTA.
- **Alex's standing directives (from the Calmer talk-over, not Calmer-specific):** keep the goal screens as they exist, stop at today's paywall, "with Balance" never "Balance Premium", laurels, no chatbot companion, sign-up after the trial in the wish list, the answer-echo recap as "a major need", the decided Meet-the-coaches screen (angle 1), gender kept as optional, HDYHAU health-professional option shortened to one line.
- **Round 2, Insight Timer arm:** 4 of 5 testers named the statistics unprompted (proof density lands); P5 asked "could I see the research for this?" at the projection graph (so the sources open from the card); P11 found the commitment question unclear and picked 10 "just for fun" (so the reason line says what the goal is for); P5 wanted "morning and evening" where the control allows one; P10 could not find the paywall's dismiss control; P9 and P11 resolved the try-first objection only through the free app, which is not copied; P20 preferred Insight Timer "because it feels like it has more free stuff".
- **Synthesis:** #3 proof density and placement, #4 commitment devices, #9 deficit-free framing, #10 content-breadth selling, #6 trial-anxiety paywall framing (Superwall notes on the paywall card).
- **March study:** B4/B5 sourced, age-specific stats; H3 no "free"-led framing at the commit moment; A3 store listing and awards as the strongest pre-app trust signal.
- **23-app benchmark:** reason line on every question; reassurance beside age, gender and ADHD; deferred account gate is the archetype's norm; notification placement is a prototype arm, not a defect (today's early sleep push kept in the constrained deck).
- **Proof facts:** every number on screen comes from [proof-facts-2026-09-04.md](proof-facts-2026-09-04.md) (whitepaper 2025, App Store rating pulled Sep 4, approved coach bios). Two claims are written plainly with a bracketed flag because no number exists: the consistency line and the dosage line.

## Open for review (Alex)

1. **The wish list drops today's goal-1 diagnostic blocks.** That is what "closest to Insight Timer" means (it has none), and Yana's cost reducer says the answers need not feed personalization for the flow to work. It is also the biggest departure from anything tested so far. Decide whether that is the version to test, or whether the constrained deck (today's blocks plus Insight Timer's inserts) is the fairer arm.
2. **HDYHAU placement.** Insight Timer asks it after the plan summary, right before the paywall. Both decks keep it in the about-you block because Matheus flagged today's proximity to the paywall. Say if you want the Insight Timer placement as an arm.
3. **The donut.** Insight Timer's names Calm and Headspace on screen. Balance's carries the 85% well-being figure instead. If marketing has a category claim Balance can make, this is the slot for it.
4. **No first-name ask in either deck.** Insight Timer is anonymous end to end and the Calmer decks added the name early. This deck follows Insight Timer; the echo screens do not need it.
5. **Which version the study rerun uses,** and whether the Calmer and Insight Timer wish lists are two arms of one round.
6. **Two plain claims need numbers or content sign-off:** "A few minutes most days does more than an hour once a week" and "Most of the benefit members report comes from a short daily session."
"""
open(OUT,'w').write(doc); print('spec written:', len(doc), 'chars;', 'kept',kept,'adapted',adapted,'cut',cut,'added',len(added))
