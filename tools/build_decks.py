#!/usr/bin/env python3
"""Builds decks/wishlist.json and decks/constrained.json from one source, then lints both.
The wish list is authored below; the constrained deck is derived by explicit overrides so the whittle is visible in one place.
Tags: existing | unused | copy | swift | superwall | new | cut.  Copy in [brackets] is a placeholder to verify."""
import json, copy, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def N(template, tag, why, calmer=None, evidence=None, fills=None, loss=None):
    d = {"template": template, "tag": tag, "why": why}
    if calmer: d["calmer"] = calmer
    if evidence: d["evidence"] = evidence
    if fills: d["fills"] = fills
    if loss: d["loss"] = loss
    return d

STRESS = "a.goal_1==='stress'"; SLEEP1 = "a.goal_1==='sleep'"; MOOD = "a.goal_1==='mood'"; FOCUS = "a.goal_1==='focus'"
SLEEP_ANY_NOT_FIRST = "a.goal_sleep==='yes' && a.goal_1!=='sleep'"
NO_SLEEP = "a.goal_sleep!=='yes'"

MEDEXP = [
  {"id":"none","text":"New to meditation","color":"misty_peach","icon":"icon-new"},
  {"id":"once_or_twice","text":"Tried it once or twice","color":"mint_green","icon":"icon-tried"},
  {"id":"a_little","text":"Meditate occasionally","color":"papaya_whip","icon":"icon-occasionally"},
  {"id":"a_lot","text":"Meditate often","color":"polar_blue","icon":"icon-often"}]
LAURELS = [{"l":"App of the Day","s":"App Store, [N] countries"},{"l":"Best of [2024]","s":"Google Play"},{"stars":True,"l":"180k+ 5-star reviews","s":"[re-verify]"}]
REVIEWS = [
  {"text":"[Verified review 1: a stress user, 2 to 3 sentences, verbatim from the App Store]","who":"[Name], App Store review, [2026]"},
  {"text":"[Verified review 2: a sleep user]","who":"[Name], App Store review, [2026]"},
  {"text":"[Verified review 3: mentions the coaches or the daily program]","who":"[Name], App Store review, [2026]"}]

W = []  # wish list cards
def add(**c): W.append(c); return c

# ---------------- Part 1: Welcome ----------------
add(id="welcome", type="welcome", phase=1, title=["Balance: A meditation","and sleep program that","adapts to <b>you</b>."],
    authority={"avatars":True,"text":"Guided by meditation teachers Ofosu and Leah. [Built with clinical advisors.]"}, laurels=LAURELS, cta="Continue",
    sub="Already have an account? <span class='link'>Log in</span>",
    notes=N("welcome","copy","Proof on screen 1: coach faces, an authority line, laurels. The welcome card is already payload-configurable (title, CTA, image, laurels), so this is config, not a release. Headline stays the live control while the ABCD test runs.",
      calmer="#1 (welcome: 'built in collaboration with clinical psychologists')", evidence="Alex 1:40; web funnel /social-proof laurels; March A3 (store listing is the strongest pre-app trust signal)",
      fills=["Authority line: confirm the clinical-advisor claim with Anna or Cindy","App of the Day country count (Alex to pull)","Google Play award and year","180k+ 5-star reviews: re-verify the web funnel figure"]))
add(id="assessment_intro", type="text", phase=1, tap=True, title=["Let's start with a","few questions."],
    body="Your answers shape your program: what your first session works on, how long it runs, and how Balance adapts from there. About 3 minutes.",
    notes=N("text","copy","Tell people what the questions do before asking them. Replaces the current 'Answer a few questions to personalize your experience' card.",
      calmer="#2 (assessment intro)", evidence="Alex 2:12; benchmark rule 2 (reason in the header)"))

# ---------------- Part 2: About you ----------------
add(id="first_name", type="keyboard", phase=2, questionId="name", title=["What should we","call you?"], subtitle="Your first name, so your program can speak to you.", placeholder="first name",
    reassure="Just a first name. No account yet, and nothing is shared.",
    notes=N("keyboard","existing","Name early is the cheapest enabler of the answer-echo register. The keyboard card already validates first_name; today the name is only captured at auth.",
      evidence="Benchmark: name is the field's 2nd most common ask (74%); rule 3 (result points back to what you said)"))
add(id="age", type="question", phase=2, questionId="age_band", derive="ageBand", title=["How old are you?"], subtitle="Your guidance will be tailored to your age group.", reassure="Used only to tune your program. Never shown to anyone.", style="compact",
    options=[{"id":"13-17","text":"13 to 17","color":"purple_haze"},{"id":"18-24","text":"18 to 24","color":"polar_blue"},{"id":"25-34","text":"25 to 34","color":"mint_green"},{"id":"35-44","text":"35 to 44","color":"papaya_whip"},{"id":"45-54","text":"45 to 54","color":"apricot"},{"id":"55+","text":"55 and over","color":"misty_peach"}],
    notes=N("question","existing","Age bands instead of the numpad (the web funnel asks bands first). Existing subtitle kept as the reason line; reassurance line added because the deck has none anywhere.",
      calmer="#4 (age)", evidence="Alex 2:34 (who-you-are first); benchmark rule 4 (specific reassurance beside sensitive asks); web funnel /age"))
add(id="gender", type="question", phase=2, questionId="gender", title=["How do you identify?"], subtitle="Optional. Some members prefer sessions that speak to their experience.", reassure="Optional, and never shown anywhere.",
    options=[{"id":"woman","text":"Woman","color":"polar_blue"},{"id":"man","text":"Man","color":"mint_green"},{"id":"nonbinary","text":"Non-binary","color":"papaya_whip"},{"id":"prefer_not","text":"Prefer not to say","color":"purple_haze"}],
    notes=N("question","existing","Calmer opens on gender and echoes it later. Kept in the wish list because Alex flagged it as interesting; the echo stays light because a tester read Calmer's gendered copy as 'given to every woman'.",
      calmer="#3 (gender)", evidence="Alex 2:34; round 2 P6 on the gendered screen (suspicion, not personalization)", loss=None))
add(id="hdyhau", type="scrollableQuestion", phase=2, questionId="hdyhau", title=["How did you hear","about us?"], subtitle="So we know where to say thanks.",
    options=[{"id":"app_or_play_store","text":"App Store"},{"id":"mobile_game","text":"Mobile game"},{"id":"facebook_or_instagram","text":"Facebook or Instagram"},{"id":"search_engine","text":"Search engine"},{"id":"elevate_or_spark","text":"Elevate or Spark"},{"id":"family_and_friends","text":"Family and friends"},{"id":"tiktok","text":"TikTok"},{"id":"health_professional","text":"A doctor, therapist or health professional"},{"id":"other","text":"Other"}],
    subAnswer={"id":"not_sure","text":"Not sure"},
    notes=N("scrollableQuestion","copy","Moved early (it sits next to the paywall today), given a reason line (it is the one ask with no payoff for the user), and gains a health-professional option so referrals become a proof signal.",
      calmer="#1 (Alex's referral idea at 1:52)", evidence="Matheus: HDYHAU sits too close to the paywall; benchmark rule 2 (extractive ask); Insight Timer offers 'Health Professional'",
      fills=["Confirm the new answer_id with data (Balance HDYHAU buckets differ from Elevate's)"]))
add(id="right_place", type="textImage", phase=2, tap=True, title=["You're in the","right place."],
    body="Balance builds a meditation program around you: a 10-minute session each day, made from your answers and guided by 2 real coaches. Plus a sleep library and single sessions for the moments you need one.",
    mock={"header":"Your program","pill":"Day 1","rows":[{"t":"Today's meditation","s":"10 min · with Ofosu","color":"polar_blue","hl":True},{"t":"Sleep library","s":"Stories, music, soundscapes","color":"purple_haze"},{"t":"Singles","s":"For the moment you need one","color":"mint_green"}]},
    notes=N("textImage","unused","Show the product before asking anything personal. Newcomers in round 2 reached a paywall without knowing what the app would do for them.",
      calmer="#5 (section preview right after age)", evidence="Alex 2:51 ('you've come to the right place'); round 2 A2 (newcomer gap); synthesis #10 (content breadth)", fills=["Session length and 'made from your answers' mechanism: confirm with Anna"]))

# ---------------- Part 3: Your goals ----------------
add(id="goals", type="goalRanking", phase=3, title=["Select the goals that","matter to you."], rankTitle=["Now select each goal","in order of importance."],
    notes=N("goalRanking","existing","Kept exactly as today, per Alex. Hardcoded in Lua, not authorable.", calmer="#13 (main priority)", evidence="Alex 4:35: keep our goal screens as they exist"))
add(id="goals_metrics", type="goalsMetrics", phase=3, title=["Here's what our","members are saying:"], metrics=[{"goal":"stress","text":"95% report less stress"},{"goal":"mood","text":"92% report improved mood"},{"goal":"sleep","text":"82% report better sleep"},{"goal":"focus","text":"75% report increased focus"}],
    disclaimer=["Based on a study of members who use","Balance 5 times per week. [Study, year.]"],
    notes=N("goalsMetrics","copy","Existing card, restyled, with a dated source line. Age-specific and sourced stats were March's single strongest confidence builder; ours are unsourced.", evidence="March B4/B5"))

# --- stress path (fully written) ---
add(id="stress_1", type="question", phase=3, branch=STRESS, questionId="how_often_feel_stress", title=["How often do you","feel stressed?"], subtitle="Over the last 2 weeks. It sets the pace of your first week.",
    options=[{"id":"always","text":"Almost always","color":"misty_peach","icon":"icon-stressed"},{"id":"sometimes","text":"Sometimes","color":"off_yellow","icon":"icon-neutral"},{"id":"rarely","text":"Rarely","color":"purple_haze","icon":"icon-nostress"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with a 2-week window and a reason line. Borrowing the screening-instrument window makes the question feel like an instrument; honest as long as we never score it as one.", calmer="#19 (frequency item, 'over the last two weeks')", evidence="Synthesis #7 (reason-first framing)"))
add(id="stress_2", type="multiselect", phase=3, branch=STRESS, questionId="how_experience_stress", title=["How does stress usually","show up for you?"], subtitle="Select all that apply. Your sessions focus on what you pick.",
    options=[{"id":"anxious_thoughts","text":"Anxious thoughts","color":"mint_green"},{"id":"exhaustion_or_tension","text":"Physical discomfort","color":"misty_peach"},{"id":"moodiness","text":"Moodiness","color":"purple_haze"},{"id":"difficulty_sleeping","text":"Difficulty sleeping","color":"papaya_whip"}],
    notes=N("multiselect","existing","Same question, now multi-select. The top quiz friction in March was being forced to pick one symptom. multiselect is an existing template.", calmer="#6 ('Which of these feel familiar? Select what resonates')", evidence="March B2 (8 of 18)"))
add(id="stress_echo", type="text", phase=3, branch=STRESS, tap=True, kicker="You're not alone", title=["Most people come to","Balance for exactly this."],
    body="You said stress shows up as {{H.lower(H.list(L.how_experience_stress))}}. [61%] of members who start with stress describe it the same way. Your first sessions are built for that.",
    notes=N("text (with interpolation)","new","Validation beat that reads the user's own answer back within seconds. Today the flow asks 8 to 10 questions and reflects none of them until the loading screen.", calmer="#8 (validation interstitial)", evidence="Synthesis #1 (answer echo, the biggest gap); Alex 5:00", fills=["61%: pull the real share from onboarding answers"]))
add(id="stress_science", type="primer", phase=3, branch=STRESS, title=["Regular meditation","measurably lowers","stress and anxiety."], body="A review of 47 clinical trials found that meditation programs reduce anxiety, depression and pain over 8 weeks of practice.",
    cite="Goyal et al., JAMA Internal Medicine, 2014. Results vary from person to person. Balance is not a substitute for professional care.",
    notes=N("goalMeditationPrimer","unused","Honest replacement for Calmer's agitation arc: one cited finding plus a disclaimer, placed where Calmer puts the scare. The DID-YOU-KNOW-with-citation template exists and is unused.", calmer="#9 to #11 (agitation), #36 (hope stat with disclaimer)", evidence="Anna's citation set; March B5 (stats need sources)", fills=["Confirm the Goyal 2014 summary wording with Anna","Disclaimer wording with content"]))
add(id="singles_preview", type="textImage", phase=3, branch=STRESS, tap=True, title=["For the moments","stress hits first."], body="Singles are short sessions for right now: a rising panic, a hard conversation, a night you can't switch off. Look for them on your Today screen from day 1.",
    mock={"header":"Singles","rows":[{"t":"SOS","s":"3 min · when panic rises","color":"misty_peach","hl":True},{"t":"Before a hard conversation","s":"5 min","color":"papaya_whip"},{"t":"Unwind","s":"10 min","color":"polar_blue"}]},
    notes=N("textImage","unused","Section preview as felt value, and Calmer's 'look for the helicopter' trick: teach an affordance in onboarding that is visibly waiting on home.", calmer="#20 (Panic SOS preview)", evidence="Alex 5:40 ('we literally have the same meditation, the SOS single')", fills=["Real Single titles and durations from the catalog"]))
add(id="stress_3", type="question", phase=3, branch=STRESS, questionId="stress_source", title=["What's the biggest","source of your stress?"], subtitle="We'll match your sessions to it.",
    options=[{"id":"money","text":"Money","color":"purple_haze","icon":"icon-money"},{"id":"work_or_school","text":"Work or school","color":"polar_blue","icon":"icon-work"},{"id":"health","text":"Health","color":"mint_green","icon":"icon-health"},{"id":"relationships","text":"Relationships","color":"misty_peach","icon":"icon-people"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line.", calmer="#14 (stress drivers)"))
add(id="stress_recap", type="text", phase=3, branch=STRESS, kicker="Got it", title=["Here's how Balance","will help, {{a.name}}."],
    items=[{"text":"Ease stress that shows up as {{H.lower(H.list(L.how_experience_stress))}}"},{"text":"Build steadier ways through stress from {{H.lower(L.stress_source)}}","when":"a.stress_source && a.stress_source!=='unsure'"},{"text":"Fall asleep faster and wake up rested","when":"a.goal_sleep==='yes'"},{"text":"Learn a practice you can carry into any moment"}], cta="Continue",
    notes=N("text (with interpolation)","new","The recap Alex called a major need: here's what you told us, here's how we'll help. Interpolation needs template work; a static per-goal version is JSON.", calmer="#15 (answer-echo checklist)", evidence="Alex 5:00 to 5:15; synthesis #1"))

# --- sleep-first path (fully written) ---
add(id="sleep_ready", type="question", phase=3, branch=SLEEP1, questionId="ready_to_sleep", title=["Do you need help falling","asleep right now?"], subtitle="If yes, your first session is a Sleep Single tonight.",
    options=[{"id":"yes","text":"Yes, I'm ready to sleep","color":"polar_blue"},{"id":"no","text":"No, I'm not ready for sleep","color":"purple_haze"}],
    notes=N("question","existing","Kept verbatim. Routes the post-onboarding destination (Sleep Single vs Plan) on the native side."))
add(id="sleep_1", type="question", phase=3, branch=SLEEP1, questionId="fall_asleep_time", title=["How long does it usually","take you to fall asleep?"], subtitle="Over the last 2 weeks.",
    options=[{"id":"0_15","text":"0 to 15 minutes","color":"mint_green"},{"id":"15_30","text":"15 to 30 minutes","color":"papaya_whip"},{"id":"30_plus","text":"30 minutes or more","color":"misty_peach"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with the 2-week window.", calmer="#24 (sleep frequency item)"))
add(id="sleep_2", type="multiselect", phase=3, branch=SLEEP1, questionId="keep_awake", title=["What tends to keep","you awake at night?"], subtitle="Select all that apply.",
    options=[{"id":"stress","text":"Stress","color":"misty_peach"},{"id":"discomfort","text":"Discomfort","color":"mint_green"},{"id":"noise","text":"Noise","color":"papaya_whip"},{"id":"cant_fall_asleep","text":"Just can't fall asleep","color":"purple_haze"}],
    notes=N("multiselect","existing","Same question, now multi-select (March B2).", calmer="#6"))
add(id="sleep_echo", type="text", phase=3, branch=SLEEP1, tap=True, kicker="You're not alone", title=["Most members who come","for sleep say the same."], body="You said {{H.lower(H.list(L.keep_awake))}} keeps you up. [82%] of members report better sleep, and the first thing your program works on is the wind-down that gets you there.",
    notes=N("text (with interpolation)","new","Validation echo for the sleep path.", calmer="#8", evidence="Synthesis #1"))
add(id="sleep_science", type="primer", phase=3, branch=SLEEP1, title=["A regular wind-down","practice shortens the time","it takes to fall asleep."], body="In a randomized trial of adults with sleep trouble, a mindfulness program improved sleep quality more than sleep-hygiene education alone.",
    cite="Black et al., JAMA Internal Medicine, 2015. [Confirm with Anna.] Results vary from person to person.",
    notes=N("goalMeditationPrimer","unused","Cited education beat in place of Calmer's cortisol chart.", calmer="#26 (cortisol education)", evidence="Alex 6:33 ('education about the condition itself')", fills=["Confirm the citation and wording with Anna"]))
add(id="sleep_library_preview", type="textImage", phase=3, branch=SLEEP1, tap=True, title=["Your sleep library is","ready when you are."], body="Sleep meditations, stories, music and soundscapes, plus the Sleep Single for nights you're ready to drift off right now.",
    mock={"header":"Sleep","rows":[{"t":"Sleep Single","s":"Tonight · 12 min","color":"purple_haze","hl":True},{"t":"Sleep stories","s":"[N] stories","color":"polar_blue"},{"t":"Soundscapes","s":"Rain, ocean, campfire","color":"mint_green"}]},
    notes=N("textImage","unused","Feature the sleep content more creatively than a stat row.", calmer="#25 (Stories preview)", evidence="Alex 6:15", fills=["Sleep catalog counts and titles"]))
add(id="sleep_3", type="question", phase=3, branch=SLEEP1, questionId="chronotype", title=["Are you a morning","person or a night person?"], subtitle="It sets when Balance suggests your sessions.",
    options=[{"id":"morning","text":"Morning person","color":"papaya_whip","icon":"icon-morningperson"},{"id":"night","text":"Night person","color":"purple_haze","icon":"icon-nightperson"},{"id":"both","text":"A bit of both","color":"polar_blue","icon":"icon-both"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="sleep_recap", type="text", phase=3, branch=SLEEP1, kicker="Got it", title=["Here's how Balance","will help, {{a.name}}."],
    items=[{"text":"Fall asleep faster when {{H.lower(H.list(L.keep_awake))}} keeps you up"},{"text":"Build a wind-down you'll actually keep"},{"text":"Wake up rested more often"},{"text":"Ease the stress underneath it","when":"a.goal_stress==='yes'"}], cta="Continue",
    notes=N("text (with interpolation)","new","Answer-echo recap for the sleep path.", calmer="#15"))

# --- mood path (existing cards, lighter interstitials) ---
add(id="mood_2", type="question", phase=3, branch=MOOD, questionId="happiest_around", title=["Who do you usually","feel happiest around?"], subtitle="It shapes the examples in your sessions.",
    options=[{"id":"family","text":"Family","color":"papaya_whip"},{"id":"friends","text":"Friends","color":"mint_green"},{"id":"myself","text":"By myself","color":"purple_haze"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line. Mood path keeps its cards; full rhythm is a follow-up."))
add(id="mood_3", type="question", phase=3, branch=MOOD, questionId="improve_mood", title=["What do you usually do","to improve your mood?"], subtitle="No wrong answers. We build on what already works.",
    options=[{"id":"alone","text":"Spend time alone","color":"purple_haze"},{"id":"talk","text":"Talk to others","color":"polar_blue"},{"id":"distract","text":"Distract myself","color":"papaya_whip"},{"id":"sleep","text":"Sleep on it","color":"mint_green"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="mood_echo", type="text", phase=3, branch=MOOD, tap=True, kicker="You're not alone", title=["Most members start","Balance on a hard week."], body="[92%] of members report improved mood. Your first sessions focus on noticing what you feel without judging it, which is where mood work starts.",
    notes=N("text","existing","Static validation beat (no interpolation). Follow-up: write the full mood rhythm.", calmer="#8"))
add(id="mood_recap", type="text", phase=3, branch=MOOD, kicker="Got it", title=["Here's how Balance","will help, {{a.name}}."], items=[{"text":"Steady your mood with a short daily practice"},{"text":"Notice hard feelings before they take over"},{"text":"Build on what already lifts you, like time {{a.happiest_around==='myself'?'to yourself':'with the people you love'}}"}], cta="Continue",
    notes=N("text (with interpolation)","new","Recap for the mood path.", calmer="#15"))

# --- focus path (existing cards, lighter interstitials) ---
add(id="focus_1", type="question", phase=3, branch=FOCUS, questionId="most_distracting", title=["What do you find the","most distracting?"], subtitle="Your sessions train attention around it.",
    options=[{"id":"thoughts","text":"My thoughts","color":"mint_green","icon":"icon-thoughts"},{"id":"surroundings","text":"My surroundings","color":"papaya_whip"},{"id":"technology","text":"Technology","color":"purple_haze"},{"id":"people","text":"Other people","color":"misty_peach","icon":"icon-people"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="focus_2", type="question", phase=3, branch=FOCUS, questionId="finishing_tasks", title=["Do you have difficulty","finishing tasks?"], subtitle="Over the last 2 weeks.",
    options=[{"id":"always","text":"Almost always","color":"misty_peach"},{"id":"depends","text":"Depends on the task","color":"papaya_whip"},{"id":"rarely","text":"Rarely","color":"purple_haze"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus the 2-week window."))
add(id="focus_adhd", type="question", phase=3, branch=FOCUS, questionId="has_adhd_or_add", title=["Do you have ADD/ADHD?"], subtitle="These conditions can affect focus.", reassure="Stays in your program. Never shared, never used for anything else.",
    options=[{"id":"yes","text":"Yes","color":"purple_haze"},{"id":"maybe","text":"I think I do","color":"papaya_whip"},{"id":"no","text":"No","color":"misty_peach"},{"id":"not_shared","text":"I prefer not to share","color":"mint_green"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with a specific reassurance line beside the most sensitive ask in the flow.", evidence="Benchmark rule 4 (Strava, Gentler Streak: highest trust ratings in the set)"))
add(id="focus_primer", type="primer", phase=3, branch=FOCUS, title=["Meditation can help","with symptoms of","ADHD and ADD."], body="[Add the study Anna recommends, one line.]", cite="[Citation]",
    notes=N("text","copy","Existing DID YOU KNOW card, now with a citation line.", evidence="March B5"))
add(id="focus_recap", type="text", phase=3, branch=FOCUS, kicker="Got it", title=["Here's how Balance","will help, {{a.name}}."], items=[{"text":"Train attention to return when {{H.lower(L.most_distracting)}} pull{{a.most_distracting==='people'||a.most_distracting==='thoughts'?'':'s'}} you away"},{"text":"Finish what you start more often"},{"text":"Short sessions that fit a busy day"}], cta="Continue",
    notes=N("text (with interpolation)","new","Recap for the focus path.", calmer="#15"))

# --- everyone: coaches ---
add(id="coaches", type="coaches", phase=3, title=["Your coaches are","Ofosu and Leah."], bios=[{"name":"Ofosu","text":"[One credential line, e.g. has taught meditation for 20 years]"},{"name":"Leah","text":"[One credential line]"}],
    body="Every session in Balance is written and recorded by the 2 of them.", cta="Continue",
    notes=N("textImage / list","unused","The decided 'made by humans' screen (angle 1, Sep 4). Showcase, not chooser; no 'AI' in the copy. Headline register to be matched to the flow in review.",
      evidence="handcrafted-coaches-screen-angles.md; 3 competitors lean on teacher credibility, our flow names ours nowhere", fills=["Cindy's approved bios for the credential lines","Headline: question-and-statement register"]))

# ---------------- Part 4: Your routine ----------------
add(id="sleep_trouble", type="question", phase=4, branch=SLEEP_ANY_NOT_FIRST, questionId="sleep_trouble", derive="sleepTrouble", title=["How often have you had","trouble falling asleep?"], subtitle="Over the last 2 weeks, even when you felt tired.",
    options=[{"id":"not_at_all","text":"Not at all","color":"mint_green"},{"id":"some","text":"Some nights","color":"papaya_whip"},{"id":"most","text":"Most nights","color":"apricot"},{"id":"nearly_every","text":"Nearly every night","color":"misty_peach"}],
    notes=N("question","existing","Sleep block now fires whenever sleep is selected, not only when it ranks first. Two-thirds of sleep-motivated users never see a sleep question today.", calmer="#24", evidence="Deck map: only goal #1 drives question blocks; sleep is the clearest PMF segment (March 4.83 vs 3.00)"))
add(id="sleep_preview_b", type="textImage", phase=4, branch=SLEEP_ANY_NOT_FIRST, tap=True, title=["Sleep is part of","your program too."], body="Sleep meditations, stories, music and soundscapes are ready on the nights you need them, alongside your daily session.",
    mock={"header":"Sleep","rows":[{"t":"Sleep Single","s":"Tonight · 12 min","color":"purple_haze","hl":True},{"t":"Sleep stories","s":"[N] stories","color":"polar_blue"},{"t":"Soundscapes","s":"Rain, ocean, campfire","color":"mint_green"}]},
    notes=N("textImage","unused","Sleep content preview for users who picked sleep as a secondary goal.", calmer="#25", evidence="Alex 6:15"))
add(id="exercise", type="slider", phase=4, questionId="exercise", title=["How often do you","move your body?"], subtitle="Exercise, walks, yoga. It all counts.", default=1, poles=["Rarely","Most days"],
    stops=[{"id":"0","label":"Rarely","caption":"I rarely exercise"},{"id":"1","label":"Once or twice a week","caption":"Once or twice a week"},{"id":"2","label":"A few times a week","caption":"A few times a week"},{"id":"3","label":"Most days","caption":"Most days"}],
    notes=N("slider","new","Whole-health question in Calmer's slider form. Sliders are on the deck map's hard-limits list, so the constrained version is a 4-option select.", calmer="#28 (exercise slider)", evidence="Alex 6:47 ('we don't ask any questions like that')"))
add(id="schedule", type="question", phase=4, questionId="schedule", title=["How busy is","your schedule?"], subtitle="Even 5 minutes can change your day. We'll make it work.",
    options=[{"id":"packed","text":"Packed, every day","color":"misty_peach"},{"id":"busy","text":"Busy most days","color":"papaya_whip"},{"id":"some","text":"Some room to breathe","color":"mint_green"},{"id":"open","text":"Pretty open","color":"polar_blue"}],
    notes=N("question","existing","Lifted from the web funnel, rationale line included (content-vetted copy).", evidence="web-onboarding-2026-08-20.md /schedule; Alex 8:58 (copy from the web flow)"))
add(id="no_judgment", type="text", phase=4, tap=True, title=["The habits you already","have count for a lot."], body="Balance isn't here to add pressure. Your program fits around your routine, starting with sessions that take 10 minutes or less.",
    notes=N("text","existing","De-shaming beat after the lifestyle questions, before the aspiration question.", calmer="#31 (non-judgment beat)"))
add(id="future", type="multiselect", phase=4, questionId="future", max=3, title=["When you feel better,","what do you look","forward to?"], subtitle="Pick up to 3.",
    options=[{"id":"calm_nights","text":"Calm nights and deep sleep","color":"purple_haze"},{"id":"clear_head","text":"A clearer head at work","color":"polar_blue"},{"id":"patience","text":"More patience with the people I love","color":"papaya_whip"},{"id":"present","text":"Feeling present instead of racing ahead","color":"mint_green"},{"id":"hard_moments","text":"Handling hard moments without spiraling","color":"misty_peach"},{"id":"energy","text":"Energy for the things I enjoy","color":"apricot"}],
    notes=N("multiselect","existing","Positive-future question, neutral framing (no 'finally enjoy again' presupposition). Picks come back on the comparison card.", calmer="#32 ('reclaim' outcomes multi)", evidence="Alex 7:05 to 7:26"))
add(id="experience", type="question", phase=4, questionId="has_meditated_before", title=["What best describes your","meditation experience?"], subtitle="Your first sessions match your experience level.", options=MEDEXP,
    notes=N("question","copy","Existing card, one shared version with a reason line instead of 4 goal-specific copies."))

# ---------------- Part 5: Your program ----------------
add(id="reviews", type="userReview", phase=5, title=["Members like you","say it works."], laurels=LAURELS, reviews=REVIEWS, cite="[Source: App Store reviews, 2026. Use verbatim, verified reviews only.]", cta="Continue",
    notes=N("userReview","unused","Testimonial carousel mid-flow. The template was live before the Jun 17 cleanup and is still in the engine.", calmer="#33 (social proof carousel)", evidence="Alex 7:28 ('ours is so basic and ugly compared to this'); synthesis #3 (proof density)", fills=["3 verified App Store reviews, verbatim, with first names"]))
add(id="age_metrics", type="ageMetrics", phase=5, kicker="Did you know?", title=["Balance has helped","<b>{{L.age_count}}</b> people your age","improve mental wellness."], cite="As of [January 2026]. [Add the source.]",
    notes=N("ageMetrics","copy","Kept: the age-specific stat was March's strongest confidence builder (12 of 18). Needs a current date and a source.", evidence="March B4/B5"))
add(id="loading", type="loading", phase=5, title=["Building your","program, {{a.name}}."], bars=["{{H.goal(a.goal_1)}} patterns","Sleep habits","Routine and schedule","Meditation experience","Choosing your first session"],
    notes=N("meditationLoading","unused","Named-instrument loading: the bars name the question sections just answered, so the quiz reads as an instrument. Today's Creating Program screen is brief and generic.", calmer="#34 (5-bar 'Building your Calmer experience')", evidence="Alex 7:36; benchmark rule 3"))
add(id="profile", type="profile", phase=5, kicker="Your Balance profile", title=["Here's your","starting point."], scoreLabel="Starting point", cta="Continue",
    scores=[{"label":"Stress load","from":"how_often_feel_stress","map":{"always":"low","sometimes":"mid","rarely":"good","unsure":"mid"},"text":{"low":"High","mid":"Moderate","good":"Low"}},
            {"label":"Sleep","from":"sleep_trouble","map":{"not_at_all":"good","some":"mid","most":"low","nearly_every":"low"},"text":{"good":"Steady","mid":"Uneven","low":"Needs care"}},
            {"label":"Sleep","from":"fall_asleep_time","map":{"0_15":"good","15_30":"mid","30_plus":"low","unsure":"mid"},"text":{"good":"Steady","mid":"Uneven","low":"Needs care"}},
            {"label":"Movement","from":"exercise","map":{"0":"low","1":"mid","2":"good","3":"good"},"text":{"low":"Rare","mid":"Some","good":"Regular"}},
            {"label":"Room in your day","from":"schedule","map":{"packed":"low","busy":"mid","some":"good","open":"good"},"text":{"low":"Tight","mid":"Some","good":"Open"}},
            {"label":"Experience","from":"has_meditated_before","map":{"none":"mid","once_or_twice":"mid","a_little":"good","a_lot":"good"},"text":{"mid":"Starting out","good":"Practicing"}}],
    profiles={"stress":{"name":"The Overdrive Mind","insight":"Your mind rarely gets to idle. Your program starts with short sessions that teach it how, then builds from there."},
              "sleep":{"name":"The Wired and Tired","insight":"Your body is ready for rest before your mind is. Your program starts with the wind-down, then works on the stress underneath it."},
              "mood":{"name":"The Weather Watcher","insight":"Your mood moves with the day. Your program starts with noticing what you feel before it takes over."},
              "focus":{"name":"The Open Browser","insight":"Attention keeps opening new tabs. Your program trains it to come back, in sessions short enough to finish."}},
    cite="Based only on your answers. Not a clinical assessment.",
    notes=N("quizResult / pieChart (static) or new gauge template","new","A named result profile is where 'it understood me' landed in round 2. Sub-scores are derived only from answers actually given, so no manufactured headroom (P18 set his diet to healthy and got 'Fair').", calmer="#37 (Mental Health Load gauge)", evidence="Round 2 A4; Alex 8:09 ('your health score, framed the way the web does'); web funnel 'Here's Your Mental Health Profile / The Overdrive Mode'", fills=["Profile names: content pass","Score mapping: agree the rules with DS so nothing reads as a diagnosis"]))
add(id="chart", type="chart", phase=5, title=["Feel better, faster,","with Balance."], weeks=["Today","Week 1","Week 3","Week 6"], withLabel="With Balance", aloneLabel="On your own",
    body="Members who practice [5] days a week report less stress within [2 weeks] and better sleep within [a month]. On your own, most people report little change.", cite="[Illustrative curve. Replace with the member-survey figures the web funnel uses.]", cta="Continue",
    notes=N("chart (new) / textImage static per goal","new","The progress graph Alex called 'so important': on your own vs with Balance, never 'Balance Premium'. A static image per goal fits textImage.", calmer="#38 (projection graph)", evidence="Alex 8:35 to 9:00", fills=["Survey figures behind the curve","Copy pass against the web funnel's Before/Day 2/Day 30 timeline"]))
add(id="comparison", type="comparison", phase=5, title=["You, with Balance."], withoutTitle="On your own", withTitle="With Balance",
    without=[{"text":"{{H.list(L.how_experience_stress)}} keep coming back","when":"a.goal_1==='stress'"},{"text":"Sleep stays hit and miss","when":"a.goal_sleep==='yes'"},{"text":"Stress from {{H.lower(L.stress_source)}} follows you home","when":"a.goal_1==='stress' && a.stress_source && a.stress_source!=='unsure'"},{"text":"Hard moments take over the day","when":"a.goal_1==='mood'"},{"text":"Attention keeps slipping","when":"a.goal_1==='focus'"},"Not sure where to start"],
    with_=[{"from":"future"},{"text":"A 10-minute session built for you, every day"}], cite="Same framing as the paywall intro screen going live next week; keep the two consistent.", cta="Continue",
    notes=N("list (static per goal) or new template","new","Comparison card assembled from the user's own picks: Calmer's strongest personalization moment. Matches Michal's option-3 paywall intro screen (you without Balance / you with Balance).", calmer="#39 (comparison card)", evidence="Alex 8:46 ('on your own, with Balance'); Tangent paywall intro screen, live next week"))
add(id="benefits", type="benefits", phase=5, title=["Unlimited access","with Balance."], laurels=LAURELS, cta="Continue",
    items=[{"title":"A new meditation every day, built from your answers"},{"title":"[400]+ meditations for stress, sleep, focus and mood"},{"title":"Sleep stories, music and soundscapes"},{"title":"Singles for the moments you need one"},{"title":"Every word recorded by a real person"}],
    notes=N("list","existing","Laurels plus what you get. Alex: the screen may not be necessary, but laurels and the benefits are. Candidate to merge with the chart in review. Last item is the 'made by humans' plain statement (angle 5).", calmer="#40 (benefits checklist with laurels)", evidence="Alex 9:04 to 9:52", fills=["Meditation count","Laurel facts"]))
add(id="commitment", type="commitment", phase=5, questionId="commitment", title=["How many days a week","feels realistic?"], subtitle="Consistency matters more than length. 10 minutes counts.", cta="Set my goal",
    options=[{"id":"7","text":"Every day","sub":"Fastest results","color":"mint_green","praise":"Incredible. Daily practice is where members see the fastest change."},{"id":"5","text":"5 days a week","sub":"Weekdays","color":"polar_blue","praise":"Great. Weekdays are a strong rhythm."},{"id":"3","text":"3 days a week","sub":"Every other day","color":"papaya_whip","praise":"Good. 3 days builds a real habit."},{"id":"2","text":"Weekends","sub":"Sat and Sun","color":"purple_haze","praise":"A start. Balance will meet you there."}],
    foot="[Members who set a goal here practice N times more often in week 1.]",
    notes=N("question","existing","Commitment device right before the reminder and paywall. Plain single-select; the praise line is a per-answer subtitle swap.", calmer="#41 (commitment pledge)", evidence="Synthesis #4 (Insight Timer's praise ladder, cheapest high-leverage steal); Alex 9:57", fills=["The real number for the footer, or drop the line"]))
add(id="reminder_time_sleep", type="setReminderTime", phase=5, branch="a.goal_sleep==='yes'", questionId="bedtime", title=["What is your","target bedtime?"], subtitle="Going to bed at the same time every night improves sleep quality.", default="10:00 pm", times=["9:00 pm","9:30 pm","10:00 pm","10:30 pm","11:00 pm","11:30 pm"],
    notes=N("setReminderTime","existing","Existing bedtime card (sleep track). Placement kept: earned and contextual.", evidence="Benchmark rule 7 vs its structural read: a prototype arm, not a defect"))
add(id="reminder_time", type="setReminderTime", phase=5, branch=NO_SLEEP, questionId="reminder_time", title=["When would you","like to be reminded?"], subtitle="A daily nudge for your 10 minutes.", default="{{a.when_to_meditate==='morning'?'8:00 am':a.when_to_meditate==='afternoon'?'12:00 pm':'6:00 pm'}}", times=["7:00 am","8:00 am","12:00 pm","5:00 pm","6:00 pm","8:00 pm"],
    notes=N("setReminderTime","existing","Existing training-reminder card."))
add(id="push", type="pushOptIn", phase=5, questionId="push", title=["Get a reminder at","{{a.goal_sleep==='yes'?'your target bedtime':'your chosen time'}}"], body="{{a.goal_sleep==='yes'?'Reminders help you set a consistent sleep schedule.':'Reminders help you build better habits.'}}", foot="[Members who turn on reminders are N times more likely to keep going in week 1.]", cta="Continue",
    notes=N("pushOptIn","copy","Existing OS permission wrapper with a real number attached to the ask.", evidence="Benchmark rule 8 (Yazio cites a 78% opt-in rate)", fills=["The real reminder number, or drop the line"]))
add(id="program_ready", type="text", phase=5, title=["Your program is","ready, {{a.name}}."], body="Your first session is 10 minutes with Ofosu, built for {{H.lower(H.goal(a.goal_1))}}{{a.goal_sleep==='yes' && a.goal_1!=='sleep' ? ' and better sleep' : ''}}. It's waiting on your Today screen.", cta="See my program",
    notes=N("text (with interpolation)","new","Program-ready card that names the first session and echoes the goals. No 'free'-led framing at the commit moment (March H3).", evidence="March H3; angle 2's 'your first session' reveal parked for a later round"))
add(id="paywall", type="paywall", phase=5, headlines={"stress":"Reduce daily stress and anxiety","sleep":"Fall asleep faster, wake up rested","focus":"Sharpen your focus","mood":"Feel steadier every day","default":"Reduce daily stress and anxiety"},
    notes=N("Superwall post_sign_up (carousel)","superwall","Today's carousel paywall, unchanged, as the terminal screen (Alex: stop at the paywall, don't copy Calmer's). Paywall ideas from the research live here as notes: reminder-promise headline with a Day 0/5/7 timeline, an on-paywall 'how do I cancel' answer, echo bullets built from the picks.", calmer="#43 (trial timeline paywall, not copied)", evidence="Alex 10:05 to 10:18; round 2 A3 (trial-reminder paywall praised unprompted, 3 of 9)", fills=["Sleep/focus/mood headlines: use the carousel's actual copy"]))
add(id="signup", type="signup", phase=5, branch="a.paywall==='trial'", title=["Save your program."], body="Create an account so your program follows you across devices and your trial reminder reaches you.", sub="By creating your account, you agree to Balance's Terms and Privacy Policy.",
    notes=N("Swift auth bookend","swift","Wish list moves account creation after the trial starts. Sign-up before the paywall is a cross-device/CRM decision, so this is a Swift bookend change and a strategy call, not deck work.", evidence="Growth Gems item 3; benchmark: deferred account gate is the norm for Balance's archetype; Calmer and Insight Timer take no account before the paywall"))
add(id="end", type="end", title=["Prototype ends here."], body="In the app, a started trial hands off to the first session on the Today screen. A decline shows today's counter-offer, then lands on the Today screen with the program locked.",
    note="This is the wish-list version: the flow as we'd build it with no template limits. The constrained version keeps the same spine using only card templates that exist in the app today.",
    notes=N("(prototype only)","existing","End card for reviewers."))

WISH = {"id":"wishlist","name":"Wish list","description":"Calmer's package in Balance's skin: proof up front, questions in an ask, echo, teach, preview rhythm, a named result profile and a progress graph, then today's paywall. Built as if templates were free.",
        "phases":["Welcome","About you","Your goals","Your routine","Your program"], "cards": W}

# ---------------- Constrained: derive by explicit overrides ----------------
ALLOWED = {"welcome","text","textImage","list","question","scrollableQuestion","multiselect","goalRanking","goalsMetrics","ageMetrics","keyboard","setReminderTime","pushOptIn","userReview","primer","loading","quizResult","coaches","paywall","signup","end","commitment","chart","comparison","benefits"}
# chart -> textImage (static image per goal), comparison -> list (static per goal), benefits -> list: the prototype renderer is shared, the production template is named in each card's notes.
# `commitment`, `coaches`, `primer` map onto existing templates (question / textImage / goalMeditationPrimer); `loading` = meditationLoading.
C = copy.deepcopy(W)
by = {c["id"]: c for c in C}
def strip(s):  # remove interpolation, caller supplies static text
    return s
def setnotes(cid, **kw):
    by[cid]["notes"].update(kw)

# welcome: keep (config), laurels stay
# age: back to numpad keyboard
by["age"].update({"type":"keyboard","questionId":"age","numpad":True,"placeholder":"age","title":["How old are you?"],"subtitle":"Your guidance will be tailored to your age group."}); 
for k in ("options","derive","style"): by["age"].pop(k, None)
setnotes("age", template="keyboard", tag="existing", why="Today's numpad age entry, kept. Reassurance line is copy.", loss="Age bands (web-funnel style).")
# gender: cut
C = [c for c in C if c["id"]!="gender"]; by = {c["id"]: c for c in C}
# stress_echo: static
by["stress_echo"].update({"title":["Most people come to","Balance for exactly this."],"body":"Anxious thoughts, tension and restless nights are how stress shows up for most members. [61%] of members who start with stress describe it that way. Your first sessions are built for that."})
setnotes("stress_echo", template="text", tag="existing", why="Static validation beat on the stress branch. Same slot, no interpolation.", loss="The user's own words read back.")
by["stress_recap"].update({"title":["Here's how Balance","will help."],"items":[{"text":"Ease anxious thoughts, tension and restless nights"},{"text":"Build steadier ways through the stress in your day"},{"text":"Fall asleep faster and wake up rested","when":"a.goal_sleep==='yes'"},{"text":"Learn a practice you can carry into any moment"}]})
setnotes("stress_recap", template="list", tag="unused", why="Static recap per goal branch using the list template (icon + title rows). Branch already scopes it to stress.", loss="Name and the user's own symptoms and stress source in the copy.")
by["sleep_echo"].update({"title":["Most members who come","for sleep say the same."],"body":"Stress, discomfort and a mind that won't switch off are the usual reasons. [82%] of members report better sleep, and the first thing your program works on is the wind-down that gets you there."})
setnotes("sleep_echo", template="text", tag="existing", why="Static validation beat on the sleep branch.", loss="The user's own answer read back.")
by["sleep_recap"].update({"title":["Here's how Balance","will help."],"items":[{"text":"Fall asleep faster on the nights your mind won't settle"},{"text":"Build a wind-down you'll actually keep"},{"text":"Wake up rested more often"},{"text":"Ease the stress underneath it","when":"a.goal_stress==='yes'"}]})
setnotes("sleep_recap", template="list", tag="unused", why="Static recap for the sleep branch.", loss="Name and the user's own answer in the copy.")
by["mood_recap"].update({"title":["Here's how Balance","will help."],"items":[{"text":"Steady your mood with a short daily practice"},{"text":"Notice hard feelings before they take over"},{"text":"Build on what already lifts you"}]})
setnotes("mood_recap", template="list", tag="unused", why="Static recap for the mood branch.", loss="Name and the echoed answer.")
by["focus_recap"].update({"title":["Here's how Balance","will help."],"items":[{"text":"Train attention to come back when it wanders"},{"text":"Finish what you start more often"},{"text":"Short sessions that fit a busy day"}]})
setnotes("focus_recap", template="list", tag="unused", why="Static recap for the focus branch.", loss="Name and the echoed answer.")
# exercise: slider -> question
by["exercise"] = {"id":"exercise","type":"question","phase":4,"questionId":"exercise","title":["How often do you","move your body?"],"subtitle":"Exercise, walks, yoga. It all counts.",
  "options":[{"id":"0","text":"Rarely","color":"misty_peach"},{"id":"1","text":"Once or twice a week","color":"papaya_whip"},{"id":"2","text":"A few times a week","color":"mint_green"},{"id":"3","text":"Most days","color":"polar_blue"}],
  "notes":N("question","existing","Same question as a 4-option select. Sliders need a new template.", calmer="#28", loss="The slider interaction and per-stop art.")}
C = [by[c["id"]] if c["id"]=="exercise" else c for c in C]; by = {c["id"]: c for c in C}
# loading: static labels
by["loading"].update({"title":["Building your","program."],"bars":["Your goals","Sleep habits","Routine and schedule","Meditation experience","Choosing your first session"]})
setnotes("loading", template="meditationLoading", tag="unused", why="Named bars with static labels. meditationLoading exists; alternatively a Swift copy change on the Creating Program bars.", loss="Goal name and first name in the labels.")
# profile: quizResult static per goal
by["profile"] = {"id":"profile","type":"quizResult","phase":5,"kicker":"Your Balance profile","title":["Here's your","starting point."],"scoreLabel":"Starting point","cta":"Continue",
  "profiles":{"stress":{"name":"The Overdrive Mind","body":"Stress that runs in the background all day, with a mind that rarely gets to idle.","insight":"Your program starts with short sessions that teach your mind how to settle, then builds from there."},
              "sleep":{"name":"The Wired and Tired","body":"Ready for rest before your mind is.","insight":"Your program starts with the wind-down, then works on the stress underneath it."},
              "mood":{"name":"The Weather Watcher","body":"A mood that moves with the day.","insight":"Your program starts with noticing what you feel before it takes over."},
              "focus":{"name":"The Open Browser","body":"Attention that keeps opening new tabs.","insight":"Your program trains it to come back, in sessions short enough to finish."}},
  "cite":"Based on your goal. Not a clinical assessment.",
  "notes":N("quizResult","unused","Named profile per goal branch using the built-but-unused quizResult template. The name does most of the work in round 2; the computed sub-scores are what need engineering.", calmer="#37", evidence="Round 2 A4", loss="Answer-derived sub-scores and the score number.", fills=["Profile names: content pass"])}
C = [by[c["id"]] if c["id"]=="profile" else c for c in C]; by = {c["id"]: c for c in C}
# chart: static image per goal (rendered the same way in the prototype, tagged as an asset)
setnotes("chart", template="textImage (static chart image per goal)", tag="unused", why="The same graph as a baked image per goal branch fits textImage. The prototype draws it live; production ships 4 images.", loss="Nothing visible; the curve is illustrative either way.")
# comparison: static list per goal
by["comparison"].update({"without":[{"text":"Anxious thoughts keep coming back","when":"a.goal_1==='stress'"},{"text":"Sleep stays hit and miss","when":"a.goal_sleep==='yes'"},{"text":"Stress follows you home","when":"a.goal_1==='stress'"},{"text":"Hard moments take over the day","when":"a.goal_1==='mood'"},{"text":"Attention keeps slipping","when":"a.goal_1==='focus'"},"Not sure where to start"],
                         "with_":[{"text":"Calmer nights and deeper sleep","when":"a.goal_sleep==='yes'"},{"text":"A steadier response to stress","when":"a.goal_1==='stress'"},{"text":"A steadier mood through the day","when":"a.goal_1==='mood'"},{"text":"Attention that comes back","when":"a.goal_1==='focus'"},{"text":"A 10-minute session built for you, every day"}]})
setnotes("comparison", template="list (static per goal)", tag="unused", why="Two static lists per goal branch. In production this is a list card per branch; the paywall intro screen going live next week carries the same framing.", loss="The user's own 'look forward to' picks on the With Balance side.")
# commitment: praise ladder -> subtitle only
for o in by["commitment"]["options"]: o.pop("praise", None)
setnotes("commitment", template="question", tag="existing", why="Plain single-select; the praise ladder needs per-answer copy the template does not do.", loss="The praise line after selection.")
# reminder default: static
by["reminder_time"]["default"] = "6:00 pm"
by["push"].update({"title":["Get a daily reminder to","meet your goals"],"body":"Reminders help you build better habits."})
setnotes("push", why="Existing OS permission wrapper with a real number attached (copy). One shared copy instead of a per-track echo.")
# program_ready static
by["program_ready"].update({"title":["Your program","is ready."],"body":"Your first session is 10 minutes with Ofosu, built around your top goal. It's waiting on your Today screen."})
setnotes("program_ready", template="text", tag="copy", why="Existing program-ready card with new copy. No 'free'-led framing.", loss="First name and goal echo.")
# age_metrics: keep (existing card interpolates its own count)
# signup: back before the paywall
sign = by["signup"]; sign.pop("branch", None); sign.update({"title":["Create an account to","save your program."],"body":"Your program follows you across devices."})
setnotes("signup", template="Swift auth bookend", tag="existing", why="Sign-up stays before the paywall, as today.", loss="Sign-up after the trial starts (wish list).")
order = [c["id"] for c in C]; i_pw = order.index("paywall"); i_su = order.index("signup")
su = C.pop(i_su); C.insert(i_pw, su)
by = {c["id"]: c for c in C}
by["end"].update({"note":"This is the constrained version: only card templates that exist in the app today, the current goal-1 branching kept intact, new questions allowed. Every screen here is a session.json content change except the paywall (Superwall) and sign-up (Swift)."})
# phases: constrained keeps the progress bar only (step counter is a hard limit)
CONS = {"id":"constrained","name":"Constrained","description":"The same spine built only from card templates that exist in the app today (in use or built-but-unused), with today's branching kept intact and new questions allowed. Interpolation, sliders, the computed profile and the step counter are cut; what each cut loses is recorded per screen.",
        "cards": C}

# ---------------- lint ----------------
def lint(deck, constrained=False):
    errs=[]; ids=set()
    sensitive={"age","focus_adhd","first_name","gender","sleep_trouble","sleep_1"}
    for c in deck["cards"]:
        if c["id"] in ids: errs.append(f"dup id {c['id']}")
        ids.add(c["id"])
        if "notes" not in c: errs.append(f"{c['id']}: no notes")
        blob=json.dumps({k:v for k,v in c.items() if k!="notes"})
        if constrained:
            if c["type"] not in ALLOWED: errs.append(f"{c['id']}: type {c['type']} not allowed in constrained")
            if "{{" in blob and c["type"] not in ("ageMetrics",): errs.append(f"{c['id']}: interpolation in constrained deck")
            if c["type"]=="question" and len(c.get("options",[]))>6: errs.append(f"{c['id']}: >6 options on a standard select")
            if c["notes"].get("tag")=="new": errs.append(f"{c['id']}: tagged new in constrained deck")
        if c["type"] in ("question","scrollableQuestion","multiselect","keyboard","slider","commitment") and not (c.get("subtitle") or c.get("kicker")):
            errs.append(f"{c['id']}: question without a reason line")
        if c["id"] in sensitive and c["id"] in ("age","focus_adhd","first_name","gender") and not c.get("reassure"):
            errs.append(f"{c['id']}: sensitive ask without a reassurance line")
        for k in ("title","subtitle","body"):
            v=c.get(k); s=" ".join(v) if isinstance(v,list) else (v or "")
            if "—" in s or "–" in s: errs.append(f"{c['id']}: dash in {k}")
            if re.search(r"\bAI\b", s): errs.append(f"{c['id']}: 'AI' in {k}")
    return errs

for deck, cons in ((WISH, False), (CONS, True)):
    for c in deck["cards"]:
        if "with_" in c: c["with"] = c.pop("with_")
    e = lint(deck, cons)
    print(f"{deck['id']}: {len(deck['cards'])} cards, lint {'OK' if not e else 'FAIL'}")
    for x in e: print("   -", x)
    json.dump(deck, open(os.path.join(ROOT,"decks",deck["id"]+".json"),"w"), indent=1, ensure_ascii=False)
if any(lint(WISH,False)) or any(lint(CONS,True)): sys.exit(1)
