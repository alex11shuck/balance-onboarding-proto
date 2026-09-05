#!/usr/bin/env python3
"""Builds decks/wishlist.json and decks/constrained.json from one source, then lints both.
The wish list is authored below; the constrained deck is derived by explicit overrides so the whittle is visible in one place.
Tags: existing | unused | copy | swift | superwall | new | cut.  Copy in [brackets] is a placeholder to verify.

Constrained mapping is checked against what the Lua cards actually read (hoth/endor/lua/session/cards, Aug 7 pin):
  question: text, subTitle (array), answers[text, answerId, color, asset], subAnswer, allowMultipleAnswers, shuffleAnswers
  scrollableQuestion: text, answers, subAnswer, shuffleAnswers (no subTitle)
  multiselect: text, subTitle, multiselectAnswers          keyboard: text, subTitle, placeholder, useNumpad, questionId
  text: text, title (small kicker), showTapToContinue, learnMore; name placeholder replaced (Common.replacePlaceholderText)
  textImage: text, asset, background, learnMore; name placeholder replaced (no subtitle)
  list: text, subTitle, items[title, subtitle, image]        userReview: text, asset (one quote per card)
  goalMeditationPrimer: title, text, subtext, textWidth      meditationLoading: personalizations[upperText, lowerText], animatedStrings
  goalsMetrics: text, subtext/subTitle, metrics              ageMetrics: title, text, subtext (count placeholder)
  setReminderTime: text, subTitle, defaultTimes, buttonTitle pushOptIn: text, subtext, reminderType
  quizResult: tied to quiz expectedAnswers ("You got N of M correct"), NOT a profile template."""
import json, copy, re, sys, os
from decklib import *

STRESS = "a.goal_1==='stress'"; SLEEP1 = "a.goal_1==='sleep'"; MOOD = "a.goal_1==='mood'"; FOCUS = "a.goal_1==='focus'"
SLEEP_ANY_NOT_FIRST = "a.goal_sleep==='yes' && a.goal_1!=='sleep'"
NO_SLEEP = "a.goal_sleep!=='yes'"
TWOWK = "Over the last 2 weeks."


W = []
def add(**c): W.append(c); return c

# ---------------- Part 1: Welcome ----------------
add(id="welcome", type="welcome", phase=1, longTitleOK=True, title=["Less stress. Better sleep.","Adapted to <b>you</b>."],
    laurels=BADGES, cta="Continue",
    sub="Already have an account? <span class='link'>Log in</span>",
    notes=N("welcome (remote config)","copy","Proof on screen 1 kept to the 3 badges (Alex: coaches plus awards was too much). Version B for the team to react to: the coach faces with 'Developed by neuroscientists, meditation teachers and behavioral coaches' instead of the badges. Headline is the variant winning the live welcome-card test (b_benefit). The welcome card is payload-configurable, so this is config, not a release.",
      calmer="#1 (welcome: 'built in collaboration with clinical psychologists')", evidence="Alex 1:40; ABCD test b_benefit; March A3; no clinical advisory claim exists, so the whitepaper's 'developed by experts in neuroscience, meditation instruction, and behavioral coaching' is the honest ceiling",
      fills=["Badges are text-only on purpose (Apple rejected a laurel with its logo in 2022); confirm wording with marketing","Rating and count pulled Sep 4, 2026 (4.88, 120,363 US ratings); refresh before shipping"]))
add(id="assessment_intro", type="text", phase=1, tap=True, title=["Let's start with a","few questions."],
    body="Answer a few questions to personalize your Plan. They shape what your first session focuses on, which Singles are ready for hard moments, and how your meditations adapt as you go. About 3 minutes.",
    notes=N("text","copy","Tell people what the questions do before asking them, keeping 'personalize your Plan' from today's card (Alex, Sep 5). 'Focuses on' replaced 'works on'; the two clauses now name Balance things (Singles, adapting meditations) instead of generic quiz copy.",
      calmer="#2 (assessment intro)", evidence="Alex 2:12; benchmark rule 2 (reason in the header)"))

# ---------------- Part 2: About you ----------------
add(id="first_name", type="keyboard", phase=2, questionId="name", title=["What should we","call you?"], placeholder="first name", noReason=True,
    notes=N("keyboard","existing","Name early is the cheapest enabler of the answer-echo register. The keyboard card validates first_name today, and text/textImage cards already replace a name placeholder.",
      evidence="Benchmark: name is the field's 2nd most common ask (74%); rule 3 (result points back to what you said)"))
add(id="age", type="question", phase=2, questionId="age_band", derive="ageBand", title=["How old are you?"], subtitle="Your guidance will be tailored to your age group.", reassure="Used only to tune your program. Never shown to anyone.", style="compact",
    options=[{"id":"13-17","text":"13 to 17","color":"purple_haze"},{"id":"18-24","text":"18 to 24","color":"polar_blue"},{"id":"25-34","text":"25 to 34","color":"mint_green"},{"id":"35-44","text":"35 to 44","color":"papaya_whip"},{"id":"45-54","text":"45 to 54","color":"apricot"},{"id":"55+","text":"55 and over","color":"misty_peach"}],
    notes=N("question","existing","Age bands instead of the numpad (the web funnel asks bands first). Existing subtitle kept as the reason line; reassurance added because the deck has none anywhere.",
      calmer="#4 (age)", evidence="Alex 2:34 (who-you-are first); benchmark rule 4; web funnel /age"))
add(id="gender", type="question", phase=2, questionId="gender", title=["How do you identify?"], noReason=True, reassure="Optional, and never shown anywhere.",
    options=[{"id":"woman","text":"Woman","color":"polar_blue"},{"id":"man","text":"Man","color":"mint_green"},{"id":"nonbinary","text":"Non-binary","color":"papaya_whip"},{"id":"prefer_not","text":"Prefer not to say","color":"purple_haze"}],
    notes=N("question","existing","Calmer opens on gender and echoes it later. Kept (Alex, Sep 4); the echo stays light because a round-2 tester read Calmer's gendered copy as 'given to every woman'. Subtitle cut Sep 5: the 'Prefer not to say' tile and the privacy line already say it is optional.",
      calmer="#3 (gender)", evidence="Alex 2:34; round 2 P6"))
add(id="hdyhau", type="scrollableQuestion", phase=2, questionId="hdyhau", title=["How did you hear","about us?"], noReason=True,
    options=[{"id":"app_or_play_store","text":"App Store"},{"id":"mobile_game","text":"Mobile game"},{"id":"facebook_or_instagram","text":"Facebook or Instagram"},{"id":"search_engine","text":"Search engine"},{"id":"elevate_or_spark","text":"Elevate or Spark"},{"id":"family_and_friends","text":"Family and friends"},{"id":"tiktok","text":"TikTok"},{"id":"health_professional","text":"Health professional"},{"id":"other","text":"Other"}],
    subAnswer={"id":"not_sure","text":"Not sure"},
    notes=N("scrollableQuestion","copy","Moved early (it sits next to the paywall today) and gains a one-line health-professional option so referrals become a proof signal. Reason line cut (Alex).",
      calmer="#1 (Alex's referral idea at 1:52)", evidence="Matheus: HDYHAU sits too close to the paywall; benchmark rule 2; Insight Timer offers 'Health Professional'",
      fills=["Confirm the new answer_id with data (Balance HDYHAU buckets differ from Elevate's)"]))
add(id="right_place", type="textImage", phase=2, tap=True, title=["{{a.name}}, you're in","the right place."],
    body="Balance has helped {{L.age_count}} people your age.{{H.pick(a.hdyhau==='family_and_friends',' Someone you know is one of them.','')}} Inside: a 10-minute session each day, assembled from your answers by 2 real coaches, 400+ meditations, a sleep library, and Singles for the moment you need one.",
    mock={"header":"Your program","pill":"Day 1","rows":[{"t":"Today's meditation","s":"10 min · with Ofosu","color":"polar_blue","hl":True},{"t":"Ofosu and Leah","s":"Your 2 coaches, every word theirs","color":"papaya_whip"},{"t":"Sleep library","s":"Stories, music, soundscapes","color":"purple_haze"},{"t":"Singles","s":"For the moment you need one","color":"mint_green"}]},
    notes=N("textImage","unused","Show the product before asking anything personal, and reflect back what the user just gave: their name, the age-specific member count (March's strongest confidence builder) and the friend referral when there was one. Kept early on Alex's call (Sep 5): the apps we studied say 'you're in the right place' up front, so this screen carries the broad library (coaches, catalog, sleep, Singles) and the stats card after the goal pick carries 'how Balance helps your goals'.",
      calmer="#5 (section preview right after age)", evidence="Alex 2:51; Alex Sep 5 2:16 to 3:46; round 2 A2 (newcomer gap); synthesis #10", fills=["Session length and the 'assembled from your answers' mechanism: confirm with Anna","Open (Alex, Sep 5): would a version right after the goal screens tell a more cohesive story, or proof too late?"]))

# ---------------- Part 3: Your goals ----------------
add(id="goals", type="goalRanking", phase=3, title=["Select the goals that","matter to you."], rankTitle=["Now select each goal","in order of importance."],
    notes=N("goalRanking","existing","Kept exactly as today, per Alex. Hardcoded in Lua, not authorable.", calmer="#13 (main priority)", evidence="Alex 4:35"))
add(id="goals_metrics", type="goalsMetrics", phase=3, title=["Members with your goals","say Balance works:"], lead={"text":"85% feel better overall"}, metrics=[{"goal":"stress","text":"81% cope better with anxious feelings"},{"goal":"mood","text":"82% feel more emotionally steady"},{"goal":"sleep","text":"69% report better sleep"},{"goal":"focus","text":"78% feel more present and focused"}],
    disclaimer=["From a 2025 survey of more than","3,700 Balance members."],
    notes=N("goalsMetrics","copy","Existing card, reframed as 'how Balance helps your goals' now that the right-place screen carries the broad library (Alex, Sep 5). Numbers are the whitepaper's (3,700+ members, 2025); a general 85% well-being row leads because Alex wants 80%+ where the survey has it, and the stress row uses the 81% anxious-feelings stat over the 77% stress stat for the same reason. Today's 95/92/82/75 line has no locatable source.", evidence="March B4/B5; whitepaper Personalization Pays Off (2025); Anna's Aug 11 DM; Alex Sep 5 12:30 to 12:55",
      fills=["Stress row: 81% 'cope better with anxious feelings' stands in for 77% 'respond to stress better'; content to confirm the swap reads honestly","Sleep has no 80%+ stat in the survey; 69% stays"]))

# --- stress path ---
add(id="stress_1", type="question", phase=3, branch=STRESS, questionId="how_often_feel_stress", title=["How often do you","feel stressed?"], subtitle=TWOWK+" It sets the pace of your first week.",
    options=[{"id":"always","text":"Almost always","color":"misty_peach","icon":"icon-stressed"},{"id":"sometimes","text":"Sometimes","color":"off_yellow","icon":"icon-neutral"},{"id":"rarely","text":"Rarely","color":"purple_haze","icon":"icon-nostress"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with a 2-week window and a reason line.", calmer="#19 (frequency item, 'over the last two weeks')", evidence="Synthesis #7 (reason-first framing)"))
add(id="stress_2", type="multiselect", phase=3, branch=STRESS, questionId="how_experience_stress", title=["How does stress usually","show up for you?"], subtitle="Select all that apply. Your sessions focus on what you pick.",
    options=[{"id":"anxious_thoughts","text":"Anxious thoughts","color":"mint_green"},{"id":"exhaustion_or_tension","text":"Physical discomfort","color":"misty_peach"},{"id":"moodiness","text":"Moodiness","color":"purple_haze"},{"id":"difficulty_sleeping","text":"Difficulty sleeping","color":"papaya_whip"}],
    notes=N("question (allowMultipleAnswers)","existing","Same question, now multi-answer. The top quiz friction in March was being forced to pick one symptom. The question card already supports allowMultipleAnswers (unused in today's deck), so the icons and pastel rows stay.", calmer="#6 ('Which of these feel familiar?')", evidence="March B2 (8 of 18)"))
add(id="stress_echo", type="text", phase=3, branch=STRESS, tap=True, kicker="You're not alone", title=["Stress like this is why","most people start."],
    body="You said stress shows up as {{H.lower(H.list(L.how_experience_stress))}}. That's the pattern members describe most, and Balance tailors your first sessions to exactly that. In a 2025 survey of 3,700+ members, 81% said they cope better with anxious feelings.",
    notes=N("text (answers written in)","new","Validation beat that reads the answer back within seconds, then says what Balance does with it in active voice (Alex, Sep 5: 'we'll tailor your first sessions to your specific symptoms', not 'built for it'). Today the flow asks 8 to 10 questions and reflects none of them until the loading screen.", calmer="#8 (validation interstitial)", evidence="Synthesis #1; Alex 5:00; Alex Sep 5 4:10 to 4:42", fills=[]))
add(id="stress_science", type="primer", phase=3, branch=STRESS, title=["Meditation lowers","stress and anxiety."], body="The most widely cited meta-analysis of meditation, 47 randomized trials and 3,500+ participants, found measurable improvements in anxiety, depression and pain.",
    sourceBadge="JAMA Internal Medicine", sourceBadgeLabel="Published in", cite="Goyal et al., 2014. Results vary from person to person. Balance is not a substitute for professional care.",
    notes=N("goalMeditationPrimer + journal badge","unused","Honest replacement for Calmer's agitation arc: one cited finding plus a disclaimer. The journal name now sits in a badge so the source reads as proof, not a footnote (Alex, Sep 5: 'logos proofing'). The DID-YOU-KNOW-with-citation template (title, text, subtext) exists and is unused; the badge is an asset on it.", calmer="#9 to #11 (agitation), #36 (hope stat with disclaimer)", evidence="Anna's citation set; March B5; Alex Sep 5 4:54 to 5:18", fills=["Disclaimer wording with content","The JAMA wordmark needs the publisher's permission; the prototype shows a styled citation badge, not the logo","Press that has cited Balance: none on file, marketing to supply if we add press logos elsewhere in the flow"]))
PANIC_OPTS=[{"id":"often","text":"Often","color":"misty_peach"},{"id":"sometimes","text":"Sometimes","color":"papaya_whip"},{"id":"rarely","text":"Rarely","color":"mint_green"}]
SOS_MOCK={"header":"Singles","rows":[{"t":"SOS","s":"3 min · when panic rises","color":"misty_peach","hl":True},{"t":"Before a hard conversation","s":"5 min","color":"papaya_whip"},{"t":"Unwind","s":"10 min","color":"polar_blue"}]}
SOS_BODY="{{H.panic(a)}}Singles are short sessions for right now: a rising panic, a hard conversation, a night you can't switch off. You've unlocked them from day 1."
add(id="stress_panic", type="question", phase=3, branch=STRESS, questionId="panic_spikes", title=["Do you get sudden spikes","of stress or panic?"], subtitle="Singles are made for those moments.", options=PANIC_OPTS, subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","existing","Calmer's panic question, copied on Alex's call (Sep 5): ask it, then show the SOS toolkit. New question on the existing card.", calmer="#19 to #20 (panic frequency, then the SOS preview)", evidence="Alex Sep 5 5:32 to 6:00"))
add(id="singles_preview", type="textImage", phase=3, branch=STRESS, tap=True, title=["Your SOS toolkit,","ready from day 1."], body=SOS_BODY, mock=SOS_MOCK,
    notes=N("textImage (answers written in)","unused","Section preview as felt value, and Calmer's 'look for the helicopter' trick: teach an affordance in onboarding that is visibly waiting on home. Opens by saying back the panic answer; 'you've unlocked them' replaces 'you'll find them on your Today screen' (Alex, Sep 5: clerical).", calmer="#20 (Panic SOS preview)", evidence="Alex 5:40 ('we literally have the same meditation, the SOS single'); Alex Sep 5 6:15 to 6:36", fills=["Real Single titles and durations from the catalog"]))
add(id="stress_3", type="question", phase=3, branch=STRESS, questionId="stress_source", title=["What's the biggest","source of your stress?"], subtitle="Your sessions are matched to it.",
    options=[{"id":"money","text":"Money","color":"purple_haze","icon":"icon-money"},{"id":"work_or_school","text":"Work or school","color":"polar_blue","icon":"icon-work"},{"id":"health","text":"Health","color":"mint_green","icon":"icon-health"},{"id":"relationships","text":"Relationships","color":"misty_peach","icon":"icon-people"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line.", calmer="#14 (stress drivers)"))
add(id="stress_recap", type="text", phase=3, branch=STRESS, kicker="Got it", title=["Here's what we","heard, {{a.name}}."],
    items=[{"text":"Stress shows up as {{H.lower(H.list(L.how_experience_stress))}}"},{"text":"{{L.stress_source}} is the biggest source right now","when":"a.stress_source && a.stress_source!=='unsure'"},{"text":"Better sleep matters to you too","when":"a.goal_sleep==='yes'"}],
    body="Balance builds your first sessions around exactly this.", cta="Continue",
    notes=N("text (answers written in)","new","The recap Alex called a major need, framed as what we heard (so it reads differently from the outcomes screen later), closing with what Balance does about it in active voice (Alex, Sep 5). Writing answers into the copy needs template work; the static per-goal version is a list card.", calmer="#15 (answer-echo checklist)", evidence="Alex 5:00 to 5:15; synthesis #1; Alex Sep 5 6:48"))

# --- sleep-first path ---
add(id="sleep_ready", type="question", phase=3, branch=SLEEP1, questionId="ready_to_sleep", title=["Do you need help falling","asleep right now?"], subtitle="If yes, your first session is a Sleep Single tonight.",
    options=[{"id":"yes","text":"Yes, I'm ready to sleep","color":"polar_blue"},{"id":"no","text":"No, I'm not ready for sleep","color":"purple_haze"}],
    notes=N("question","existing","Kept verbatim. Routes the post-onboarding destination (Sleep Single vs Plan) on the native side.", evidence="Alex Sep 5 23:28: this screen drew complaints in the March study", fills=["March complaints about this screen: decide whether it stays verbatim, moves, or gets a reason line"]))
add(id="sleep_1", type="question", phase=3, branch=SLEEP1, questionId="fall_asleep_time", title=["How long does it usually","take you to fall asleep?"], subtitle=TWOWK,
    options=[{"id":"0_15","text":"0 to 15 minutes","color":"mint_green"},{"id":"15_30","text":"15 to 30 minutes","color":"papaya_whip"},{"id":"30_plus","text":"30 minutes or more","color":"misty_peach"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with the 2-week window.", calmer="#24 (sleep frequency item)"))
add(id="sleep_2", type="multiselect", phase=3, branch=SLEEP1, questionId="keep_awake", title=["What tends to keep","you awake at night?"], subtitle="Select all that apply.",
    options=[{"id":"stress","text":"Stress","color":"misty_peach"},{"id":"discomfort","text":"Discomfort","color":"mint_green"},{"id":"noise","text":"Noise","color":"papaya_whip"},{"id":"cant_fall_asleep","text":"Just can't fall asleep","color":"purple_haze"}],
    notes=N("question (allowMultipleAnswers)","existing","Same question, now multi-answer (March B2).", calmer="#6"))
add(id="sleep_echo", type="text", phase=3, branch=SLEEP1, tap=True, kicker="You're not alone", title=["Most people who come","for sleep say the same."], body="You said {{H.lower(H.list(L.keep_awake))}} keep{{H.pick((a.keep_awake||[]).length===1,'s','')}} you up. Balance opens your Plan with a wind-down built for exactly that, and 69% of members in our survey reported better sleep.",
    notes=N("text (answers written in)","new","Validation echo for the sleep path.", calmer="#8", evidence="Synthesis #1"))
add(id="sleep_science", type="primer", phase=3, branch=SLEEP1, title=["A wind-down routine","helps you fall asleep."], body="In a randomized trial of adults with sleep trouble, a mindfulness program improved sleep quality more than sleep-hygiene education alone.",
    sourceBadge="JAMA Internal Medicine", sourceBadgeLabel="Published in", cite="Black et al., 2015. [Confirm with Anna.] Results vary from person to person.",
    notes=N("goalMeditationPrimer","unused","Cited education beat in place of Calmer's cortisol chart.", calmer="#26 (cortisol education)", evidence="Alex 6:33", fills=["Confirm the citation and wording with Anna"]))
add(id="sleep_library_preview", type="textImage", phase=3, branch=SLEEP1, tap=True, title=["Your sleep library is","ready when you are."], body="Sleep meditations, stories, music and soundscapes, plus the Sleep Single for nights you're ready to drift off right now.",
    mock={"header":"Sleep","rows":[{"t":"Sleep Single","s":"Tonight · 12 min","color":"purple_haze","hl":True},{"t":"Sleep stories","s":"[N] stories","color":"polar_blue"},{"t":"Soundscapes","s":"Rain, ocean, campfire","color":"mint_green"}]},
    notes=N("textImage","unused","Feature the sleep content more creatively than a stat row.", calmer="#25 (Stories preview)", evidence="Alex 6:15", fills=["Sleep catalog counts and titles"]))
add(id="sleep_3", type="question", phase=3, branch=SLEEP1, questionId="chronotype", title=["Morning person or","night person?"], subtitle="It sets when Balance suggests your sessions.",
    options=[{"id":"morning","text":"Morning person","color":"papaya_whip","icon":"icon-morningperson"},{"id":"night","text":"Night person","color":"purple_haze","icon":"icon-nightperson"},{"id":"both","text":"A bit of both","color":"polar_blue","icon":"icon-both"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="sleep_recap", type="text", phase=3, branch=SLEEP1, kicker="Got it", title=["Here's what we","heard, {{a.name}}."],
    items=[{"text":"{{H.list(L.keep_awake)}} keep{{H.pick((a.keep_awake||[]).length===1,'s','')}} you up"},{"text":"It takes you {{H.lower(L.fall_asleep_time)}} to fall asleep","when":"a.fall_asleep_time && a.fall_asleep_time!=='unsure'"},{"text":"You're a {{H.lower(L.chronotype)}}","when":"a.chronotype && a.chronotype!=='unsure' && a.chronotype!=='both'"},{"text":"Less stress matters to you too","when":"a.goal_stress==='yes'"}],
    body="Your Plan opens with a wind-down built around this.", cta="Continue",
    notes=N("text (answers written in)","new","What-we-heard recap for the sleep path.", calmer="#15"))

# --- mood path (full rhythm) ---
add(id="mood_1", type="question", phase=3, branch=MOOD, questionId="low_mood_freq", title=["How often does a low","mood get in the way?"], subtitle=TWOWK+" It sets the pace of your first week.", options=FREQ4, subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","existing","New frequency item with the 2-week window, so the mood path has a pace-setting question like stress does. Never scored as a screen.", calmer="#19"))
add(id="mood_2", type="question", phase=3, branch=MOOD, questionId="happiest_around", title=["Who do you usually","feel happiest around?"], subtitle="It shapes the examples in your sessions.",
    options=[{"id":"family","text":"Family","color":"papaya_whip"},{"id":"friends","text":"Friends","color":"mint_green"},{"id":"myself","text":"By myself","color":"purple_haze"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="mood_echo", type="text", phase=3, branch=MOOD, tap=True, kicker="You're not alone", title=["Hard weeks are why","most people start."], body="{{H.happy(a)}} 82% of members in our survey feel more emotionally steady.",
    notes=N("text (answers written in)","new","Validation echo for the mood path.", calmer="#8", evidence="Synthesis #1"))
add(id="mood_science", type="primer", phase=3, branch=MOOD, title=["A daily practice lifts","mood over a few weeks."], body="Across randomized trials, meditation programs reduced distress and lifted mood in everyday adults, not only in clinical groups.",
    sourceBadge="Nature Mental Health", sourceBadgeLabel="Published in", cite="Galante et al., 2023. Results vary from person to person. Balance is not a substitute for professional care.",
    notes=N("goalMeditationPrimer","unused","Cited education beat for the mood path.", calmer="#9 to #11", fills=[]))
add(id="mood_preview", type="textImage", phase=3, branch=MOOD, tap=True, title=["Check in, then","meet the day."], body="Each day starts with a 10-second mood check-in. Balance picks a session for how you feel, and Singles are there for the harder moments.",
    mock={"header":"Today","pill":"Mood check-in","rows":[{"t":"How are you feeling?","s":"Tap a mood","color":"papaya_whip","hl":True},{"t":"Today's meditation","s":"Picked for your mood · 10 min","color":"polar_blue"},{"t":"[Lift] Single","s":"5 min · for a low moment","color":"mint_green"}]},
    notes=N("textImage","unused","Section preview for the mood path: the daily mood check-in and mood Singles.", calmer="#12 (School preview)", evidence="Alex 4:15 ('think creatively about how sections of Balance could help')", fills=["Mood check-in mechanics and Single titles from the catalog"]))
add(id="mood_3", type="question", phase=3, branch=MOOD, questionId="improve_mood", title=["What do you usually do","to improve your mood?"], subtitle="No wrong answers. We build on what already works.",
    options=[{"id":"alone","text":"Spend time alone","color":"purple_haze"},{"id":"talk","text":"Talk to others","color":"polar_blue"},{"id":"distract","text":"Distract myself","color":"papaya_whip"},{"id":"sleep","text":"Sleep on it","color":"mint_green"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="mood_recap", type="text", phase=3, branch=MOOD, kicker="Got it", title=["Here's what we","heard, {{a.name}}."], items=[{"text":"A low mood gets in the way {{H.lower(L.low_mood_freq)}}","when":"a.low_mood_freq && a.low_mood_freq!=='unsure'"},{"text":"You're happiest {{H.pick(a.happiest_around==='myself','on your own','around '+H.lower(L.happiest_around))}}","when":"a.happiest_around && a.happiest_around!=='unsure'"},{"text":"{{L.improve_mood}} is what helps today","when":"a.improve_mood && a.improve_mood!=='unsure'"}],
    body="Balance tailors your first sessions to build on this.", cta="Continue",
    notes=N("text (answers written in)","new","What-we-heard recap for the mood path.", calmer="#15"))

# --- focus path (full rhythm) ---
add(id="focus_1", type="question", phase=3, branch=FOCUS, questionId="most_distracting", title=["What do you find the","most distracting?"], subtitle="Your sessions train attention around it.",
    options=[{"id":"thoughts","text":"My thoughts","color":"mint_green","icon":"icon-thoughts"},{"id":"surroundings","text":"My surroundings","color":"papaya_whip"},{"id":"technology","text":"Technology","color":"purple_haze"},{"id":"people","text":"Other people","color":"misty_peach","icon":"icon-people"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="focus_2", type="question", phase=3, branch=FOCUS, questionId="finishing_tasks", title=["Do you have difficulty","finishing tasks?"], subtitle=TWOWK,
    options=[{"id":"always","text":"Almost always","color":"misty_peach"},{"id":"depends","text":"Depends on the task","color":"papaya_whip"},{"id":"rarely","text":"Rarely","color":"purple_haze"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus the 2-week window."))
add(id="focus_echo", type="text", phase=3, branch=FOCUS, tap=True, kicker="You're not alone", title=["Attention wanders.","That's what it does."], body="You said {{H.pulls(a)}}. Meditation is practice at noticing that and coming back, and Balance tailors your first sessions to it. 78% of members in our survey feel more present and focused.",
    notes=N("text (answers written in)","new","Validation echo for the focus path.", calmer="#8", evidence="Synthesis #1; Alex Sep 5 14:44 (78% stays: the survey has no 80%+ focus stat)"))
add(id="focus_adhd", type="question", phase=3, branch=FOCUS, questionId="has_adhd_or_add", title=["Do you have ADD/ADHD?"], subtitle="These conditions can affect focus.", reassure="Stays in your program. Never shared, never used for anything else.",
    options=[{"id":"yes","text":"Yes","color":"purple_haze"},{"id":"maybe","text":"I think I do","color":"papaya_whip"},{"id":"no","text":"No","color":"misty_peach"},{"id":"not_shared","text":"I prefer not to share","color":"mint_green"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with a specific reassurance line beside the most sensitive ask in the flow.", evidence="Benchmark rule 4"))
add(id="focus_primer", type="primer", phase=3, branch=FOCUS, title=["Meditation can help with","ADHD and ADD symptoms."], body="[One line on the study Anna recommends.]", cite="[Citation]",
    notes=N("goalMeditationPrimer","copy","Existing DID YOU KNOW card, now with a citation line.", evidence="March B5", fills=["ADHD citation from Anna"]))
add(id="focus_preview", type="textImage", phase=3, branch=FOCUS, tap=True, title=["Built for a mind","with open tabs."], body="Short focus sessions before you start work, a timer for the task in front of you, and Singles made for ADHD brains.",
    mock={"header":"Focus","rows":[{"t":"[Focus] Single","s":"5 min · before you start","color":"polar_blue","hl":True},{"t":"[Task Timer]","s":"Work in focused blocks","color":"mint_green"},{"t":"[ADHD] Single","s":"10 min","color":"purple_haze"}]},
    notes=N("textImage","unused","Section preview for the focus path.", calmer="#12", evidence="Alex 4:15", fills=["Focus Single titles, the timer feature name, ADHD Single title"]))
add(id="focus_3", type="question", phase=3, branch=FOCUS, questionId="procrastinate", title=["How often do you","procrastinate on work?"], subtitle=TWOWK,
    options=[{"id":"always","text":"Almost always","color":"misty_peach"},{"id":"sometimes","text":"Sometimes","color":"papaya_whip"},{"id":"rarely","text":"Rarely","color":"purple_haze"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with the 2-week window."))
add(id="focus_recap", type="text", phase=3, branch=FOCUS, kicker="Got it", title=["Here's what we","heard, {{a.name}}."], items=[{"text":"{{H.pulls(a).charAt(0).toUpperCase()+H.pulls(a).slice(1)}}","when":"a.most_distracting && a.most_distracting!=='unsure'"},{"text":"Finishing tasks is hard {{H.lower(L.finishing_tasks)}}","when":"a.finishing_tasks && a.finishing_tasks!=='unsure'"},{"text":"You procrastinate {{H.lower(L.procrastinate)}}","when":"a.procrastinate && a.procrastinate!=='unsure'"}],
    body="Balance tailors your first sessions to train attention around this.", cta="Continue",
    notes=N("text (answers written in)","new","What-we-heard recap for the focus path.", calmer="#15"))

# --- everyone: coaches ---
add(id="coaches", type="coaches", phase=3, title=["Meet Ofosu and Leah,","your coaches."], subtitle="They'll guide you toward {{H.goalsPhrase(a)}}.", bios=[{"name":"Ofosu","text":"Has taught meditation for over 20 years, including at the Insight Meditation Society and Spirit Rock."},{"name":"Leah","text":"Brings neuroscience, psychology and her own practice to every session. Has taught in 16+ countries."}],
    body="Every session is written and recorded by the 2 of them. Balance assembles your meditations from that library, just for you, from what you share. Your first session is with Ofosu. Switch anytime.", cta="Continue",
    notes=N("list (2 items with image, title, subtitle)","unused","The decided 'made by humans' screen (angle 1), warmed up on Alex's note: it names the user's goals, gives a quick background on each coach, carries the handcrafted line from angle 2, and says the first session is with Ofosu and you can switch anytime (coach switching exists in the app). Showcase, not chooser; no 'AI' in the copy.",
      evidence="handcrafted-coaches-screen-angles.md; 3 competitors lean on teacher credibility; 'Balance assembles meditations just for you' is the website's own line (themindcompany.com/apps/balance)", fills=["Bios trimmed from the approved website bios; Cindy to confirm the one-liners","Headline: question-and-statement register"]))

COACHES_CARD = W.pop([i for i,c in enumerate(W) if c["id"]=="coaches"][0])
# ---------------- Part 4: Your routine ----------------
add(id="sleep_trouble", type="question", phase=4, branch=SLEEP_ANY_NOT_FIRST, questionId="sleep_trouble", derive="sleepTrouble", title=["How often have you had","trouble falling asleep?"], subtitle=TWOWK+" Even when you felt tired.",
    options=[{"id":"not_at_all","text":"Not at all","color":"mint_green"},{"id":"some","text":"Some nights","color":"papaya_whip"},{"id":"most","text":"Most nights","color":"apricot"},{"id":"nearly_every","text":"Nearly every night","color":"misty_peach"}],
    notes=N("question","existing","Sleep block now fires whenever sleep is selected, not only when it ranks first. Two-thirds of sleep-motivated users never see a sleep question today.", calmer="#24", evidence="Deck map: only goal #1 drives question blocks; sleep is the clearest PMF segment (March 4.83 vs 3.00)"))
add(id="sleep_preview_b", type="textImage", phase=4, branch=SLEEP_ANY_NOT_FIRST, tap=True, title=["Sleep is part of","your Plan too."], body="Sleep meditations, stories, music and soundscapes are ready on the nights you need them, alongside your daily session.",
    mock={"header":"Sleep","rows":[{"t":"Sleep Single","s":"Tonight · 12 min","color":"purple_haze","hl":True},{"t":"Sleep stories","s":"[N] stories","color":"polar_blue"},{"t":"Soundscapes","s":"Rain, ocean, campfire","color":"mint_green"}]},
    notes=N("textImage","unused","Sleep content preview for users who picked sleep as a secondary goal.", calmer="#25", evidence="Alex 6:15"))
STRESS_ANY_NOT_FIRST = "a.goal_stress==='yes' && a.goal_1!=='stress'"
add(id="stress_panic_b", type="question", phase=4, branch=STRESS_ANY_NOT_FIRST, questionId="panic_spikes", title=["Do you get sudden spikes","of stress or panic?"], subtitle="Singles are made for those moments.", options=PANIC_OPTS, subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","existing","The panic question for users who picked stress as a secondary goal (Alex, Sep 5: show the SOS toolkit to anyone with a stress goal, not only stress #1).", calmer="#19", evidence="Alex Sep 5 5:48 to 6:00"))
add(id="singles_preview_b", type="textImage", phase=4, branch=STRESS_ANY_NOT_FIRST, tap=True, title=["Your SOS toolkit,","ready from day 1."], body=SOS_BODY, mock=SOS_MOCK,
    notes=N("textImage (answers written in)","unused","SOS Singles preview for the stress-as-secondary-goal path.", calmer="#20", evidence="Alex Sep 5 5:48 to 6:00", fills=["Real Single titles and durations from the catalog"]))
add(id="exercise", type="slider", phase=4, questionId="exercise", title=["How often do you","move your body?"], subtitle="Exercise, walks, yoga. It all counts.", default=1, poles=["Rarely","Most days"],
    stops=[{"id":"0","label":"Rarely","caption":"I rarely exercise"},{"id":"1","label":"Once or twice a week","caption":"Once or twice a week"},{"id":"2","label":"A few times a week","caption":"A few times a week"},{"id":"3","label":"Most days","caption":"Most days"}],
    notes=N("slider","new","Whole-health question in Calmer's slider form. Sliders are on the deck map's hard-limits list, so the constrained version is a 4-option select.", calmer="#28 (exercise slider)", evidence="Alex 6:47"))
add(id="schedule", type="question", phase=4, questionId="schedule", title=["How busy is","your schedule?"], subtitle="Even 5 minutes can change your day. We'll make it work.",
    options=[{"id":"packed","text":"Packed, every day","color":"misty_peach"},{"id":"busy","text":"Busy most days","color":"papaya_whip"},{"id":"some","text":"Some room to breathe","color":"mint_green"},{"id":"open","text":"Pretty open","color":"polar_blue"}],
    notes=N("question","existing","Lifted from the web funnel, rationale line included (content-vetted copy).", evidence="web-onboarding-2026-08-20.md /schedule; Alex 8:58"))
add(id="no_judgment", type="text", phase=4, tap=True, title=["What you already do","counts for a lot."], body="{{H.Days(a)}}. Your first session runs 10 minutes, {{H.roomLine(a)}} No pressure, and no streak to protect.",
    notes=N("text (answers written in)","new","De-shaming beat that speaks back to the schedule answer, before the aspiration question. The first session is always 10 minutes (static); the back half changes with the schedule answer: 5-minute versions for packed days, longer versions for people with room to unwind (Alex, Sep 5).", calmer="#31 (non-judgment beat)", evidence="Alex: more moments that speak back to the user; Alex Sep 5 7:57 to 8:33", fills=["Session lengths are set per exercise in the app (supportedDurationsInMinutes); confirm the longest Plan session length with content before saying '20 minutes'"]))
add(id="future", type="multiselect", phase=4, questionId="future", max=3, kicker="When you feel better", title=["What do you look","forward to?"], subtitle="Pick up to 3.",
    options=[{"id":"calm_nights","text":"Calm nights and deep sleep","color":"purple_haze"},{"id":"clear_head","text":"A clearer head at work","color":"polar_blue"},{"id":"patience","text":"More patience with the people I love","color":"papaya_whip"},{"id":"present","text":"Feeling present instead of racing ahead","color":"mint_green"},{"id":"hard_moments","text":"Handling hard moments without spiraling","color":"misty_peach"},{"id":"energy","text":"Energy for the things I enjoy","color":"apricot"}],
    notes=N("multiselect","existing","Positive-future question, neutral framing. Picks come back on the outcomes screen and the program-ready card.", calmer="#32 ('reclaim' outcomes multi)", evidence="Alex 7:05 to 7:26"))
add(id="experience", type="question", phase=4, questionId="has_meditated_before", title=["What best describes your","meditation experience?"], subtitle="Your first sessions match your experience level.", options=MEDEXP,
    notes=N("question","copy","Existing card, one shared version with a reason line instead of 4 goal-specific copies."))

# ---------------- Part 5: Your program ----------------
add(id="proof", type="userReview", phase=5, title=["Members like you","say it works."], laurels=BADGES, reviews=REVIEWS, cta="Continue",
    notes=N("userReview","unused","One proof screen: badges and 3 verbatim reviews. The 'reviews verbatim from the App Store' line is cut (Alex, Sep 5: the cards already say App Store review); 'Members' stays. The age-specific member count moved up to the 'right place' screen so it reflects the age answer the moment it is given. userReview shows one quote per card in the deck.", calmer="#33 (social proof carousel)", evidence="Alex 7:28; Alex: combine reviews and the age stat, then reflect answers back earlier", fills=["Reviews are verbatim public App Store reviews (Sep 4, 2026); the 'real voices and not AI' line is in on Alex's call","Age counts on record date from Jan 2022; confirm the January 2026 refresh with Yana"]))
add(id="loading", type="assembly", phase=5, title=["Built by hand,","for you."],
    body="Ofosu and Leah recorded every segment themselves, in the studio. Balance chooses the ones that fit your answers, so your first session is tailored to exactly what you told us.", foot="Switch coaches anytime.", cta="Continue",
    sessions={"stress":{"title":"Settling a busy mind","coach":"Ofosu"},"sleep":{"title":"Letting the day go","coach":"Ofosu"},"mood":{"title":"Meeting the day as it is","coach":"Ofosu"},"focus":{"title":"Coming back to one thing","coach":"Ofosu"},"default":{"title":"Settling a busy mind","coach":"Ofosu"}},
    notes=N("meditationLoading (personalization reveal) + new animation","new","Option 3 (Alex, Sep 4): the coaches appear where the Plan gets made. Their faces, the user's answer chips, and the first session that comes out of them replace the generic Creating Program screen. Replaces dead time instead of adding a step; the standalone coaches card is gone from this version. Sep 5: 'recorded by hand' became 'recorded themselves, in the studio' (they do not record by hand), 'is choosing' became 'chooses', and the first session is always with Ofosu, since that is what the product does.", calmer="#34 (named-instrument loading), #37 (result reveal)", evidence="Round 2 A4; March D1/F1; Growth Gems principle 2; coaches prior art (angle 2); Alex Sep 5 9:36 to 10:47 and 24:46", fills=["Headline alternatives if 'Built by hand' overstates it: 'Recorded by 2 people. Assembled for you.' or 'Made by 2 people, for 1.'","The recording mechanism: confirm wording with Anna or Cindy","Session titles per goal from the catalog"]))
add(id="profile", type="profile", phase=5, kicker="Your Balance profile", title=["Your starting point."], subtitle="You today, from your answers. Next: where Balance takes it.", scoreLabel="Starting point", cta="Continue",
    scores=[{"label":"Stress load","from":"how_often_feel_stress","map":{"always":"low","sometimes":"mid","rarely":"good","unsure":"mid"},"text":{"low":"High","mid":"Moderate","good":"Low"}},
            {"label":"Mood","from":"low_mood_freq","map":{"not_at_all":"good","some":"mid","most":"low","nearly_every":"low","unsure":"mid"},"text":{"good":"Steady","mid":"Up and down","low":"Needs care"}},
            {"label":"Focus","from":"finishing_tasks","map":{"always":"low","depends":"mid","rarely":"good","unsure":"mid"},"text":{"low":"Scattered","mid":"Uneven","good":"Steady"}},
            {"label":"Sleep","from":"sleep_trouble","map":{"not_at_all":"good","some":"mid","most":"low","nearly_every":"low"},"text":{"good":"Steady","mid":"Uneven","low":"Needs care"}},
            {"label":"Sleep","from":"fall_asleep_time","map":{"0_15":"good","15_30":"mid","30_plus":"low","unsure":"mid"},"text":{"good":"Steady","mid":"Uneven","low":"Needs care"}},
            {"label":"Movement","from":"exercise","map":{"0":"low","1":"mid","2":"good","3":"good"},"text":{"low":"Rare","mid":"Some","good":"Regular"}},
            {"label":"Room in your day","from":"schedule","map":{"packed":"low","busy":"mid","some":"good","open":"good"},"text":{"low":"Tight","mid":"Some","good":"Open"}},
            {"label":"Experience","from":"has_meditated_before","map":{"none":"mid","once_or_twice":"mid","a_little":"good","a_lot":"good"},"text":{"mid":"Starting out","good":"Practicing"}}],
    profiles={"stress":{"name":"The Overdrive Mind","insight":"Your mind rarely gets to idle. {{H.exp(a)}} and {{H.days(a)}}, so {{H.week1(a)}}."},
              "sleep":{"name":"The Wired and Tired","insight":"Your body is ready for rest before your mind is. {{H.exp(a)}} and {{H.days(a)}}, so {{H.week1(a)}}."},
              "mood":{"name":"The Weather Watcher","insight":"Your mood moves with the day. {{H.exp(a)}} and {{H.days(a)}}, so {{H.week1(a)}}."},
              "focus":{"name":"The Open Browser","insight":"Attention keeps opening new tabs. {{H.exp(a)}} and {{H.days(a)}}, so {{H.week1(a)}}."}},
    cite="Based only on your answers. Not a clinical assessment.",
    notes=N("goalMeditationPrimer (static per goal) or new gauge template","new","A named result profile is where 'it understood me' landed in round 2. Sub-scores derive only from answers actually given, so no manufactured headroom (P18). The insight speaks back to experience and schedule, and the week-1 line now changes with the schedule answer (short sessions for packed days, longer ones for people with room to unwind) instead of assuming everyone is busy (Alex, Sep 5). A subtitle bridges from the assembly screen, which Alex felt this followed abruptly, and points at the projection next.", calmer="#37 (Mental Health Load gauge)", evidence="Round 2 A4; Alex 8:09; web funnel 'Here's Your Mental Health Profile / The Overdrive Mode'; Alex Sep 5 10:47 to 12:13", fills=["Profile names: content pass","Score mapping: agree the rules with DS so nothing reads as a diagnosis"]))
add(id="chart", type="chart", phase=5, title=["Feel better, faster,","with Balance."], weeks=["Today","Week 1","Week 3","Week 6"], withLabel="With Balance", aloneLabel="On your own",
    body="In a 2025 survey of 3,700+ members, 85% reported improved mental and emotional well-being{{H.goalStat(a)}}. On your own, most people report little change.", cite="Illustrative curve. Survey figures from the Balance whitepaper, 2025.", cta="Continue",
    notes=N("textImage (static image per goal) or Lottie","new","The progress graph Alex called 'so important': on your own vs with Balance, never 'Balance Premium'. The line and dots now draw in one after another (Alex, Sep 5: 'ding, ding, ding'), which makes it a Lottie rather than a still. Leads with the survey's 85% well-being figure, then the goal's own stat.", calmer="#38 (projection graph)", evidence="Alex 8:35 to 9:00; Alex Sep 5 12:21 to 12:55", fills=["Copy pass against the web funnel's Before/Day 2/Day 30 timeline","A Lottie per goal, or one animation with the stat line swapped"]))
add(id="comparison", type="comparison", phase=5, title=["What changes","with Balance."], withoutTitle="On your own", withTitle="With Balance",
    without=[{"text":"{{H.first(String(L.how_experience_stress||'').split(', '))||'Anxious thoughts'}} keep coming back","when":"a.goal_1==='stress'"},{"text":"Sleep stays hit and miss","when":"a.goal_sleep==='yes'"},{"text":"Low days run the week","when":"a.goal_1==='mood'"},{"text":"Attention keeps slipping","when":"a.goal_1==='focus'"},"Not sure where to start"],
    with_=[{"from":"future"},{"text":"A 10-minute session built for you, every day"}], cta="Continue",
    notes=N("list (static per goal)","new","Outcomes screen built from the user's own 'look forward to' picks. Distinct from the earlier recap (what we heard) and replaces the benefits checklist. Matches Michal's option-3 paywall intro screen going live next week; keep the two consistent.", calmer="#39 (comparison card)", evidence="Alex 8:46; Tangent paywall intro screen; Alex: differentiate the list screens"))
add(id="commitment", type="commitment", phase=5, questionId="commitment", title=["How many days a week","feels realistic?"], subtitle="Consistency matters more than length. 10 minutes counts.", cta="Set my goal",
    options=[{"id":"7","text":"Every day","sub":"Fastest results","color":"mint_green","praise":"Incredible. Daily practice is where members see the fastest change."},{"id":"5","text":"5 days a week","sub":"Weekdays","color":"polar_blue","praise":"Great. Weekdays are a strong rhythm."},{"id":"3","text":"3 days a week","sub":"Every other day","color":"papaya_whip","praise":"Good. 3 days builds a real habit."},{"id":"2","text":"Weekends","sub":"Sat and Sun","color":"purple_haze","praise":"A start. Balance will meet you there."}],
    notes=N("question","existing","Commitment device right before the reminder and paywall. Plain single-select; the praise line is a per-answer subtitle swap.", calmer="#41 (commitment pledge)", evidence="Synthesis #4; Alex 9:57", fills=[]))
add(id="reminder_time_sleep", type="setReminderTime", phase=5, branch="a.goal_sleep==='yes'", questionId="bedtime", title=["What is your","target bedtime?"], subtitle="Going to bed at the same time every night improves sleep quality.", default="10:00 pm", times=["9:00 pm","9:30 pm","10:00 pm","10:30 pm","11:00 pm","11:30 pm"],
    notes=N("setReminderTime","existing","Existing bedtime card (sleep track). Placement kept: earned and contextual.", evidence="Benchmark rule 7 vs its structural read: a prototype arm, not a defect"))
add(id="reminder_time", type="setReminderTime", phase=5, branch=NO_SLEEP, questionId="reminder_time", title=["When would you","like to be reminded?"], subtitle="A daily nudge for your 10 minutes.", default="6:00 pm", times=["7:00 am","8:00 am","12:00 pm","5:00 pm","6:00 pm","8:00 pm"],
    notes=N("setReminderTime","existing","Existing training-reminder card."))
add(id="push", type="pushOptIn", phase=5, questionId="push", title=["Get a reminder at","{{a.goal_sleep==='yes'?'your target bedtime':'your chosen time'}}"], body="{{a.goal_sleep==='yes'?'Reminders help you set a consistent sleep schedule.':'Reminders help you build better habits.'}}", cta="Continue",
    notes=N("pushOptIn","copy","Existing OS permission wrapper. Benchmark rule 8 wants a real opt-in number here; none exists in our data yet, so the line is out rather than invented.", evidence="Benchmark rule 8"))
add(id="program_ready", type="text", phase=5, title=["Your Plan is ready,","{{a.name}}."], body="Your first session is 10 minutes with Ofosu, built for {{H.goalsPhrase(a)}}.{{H.readyLine(a,L)}}{{H.pick(!!H.firstFuture(a,L),' Week 1 works toward '+H.firstFuture(a,L)+'.','')}}", cta="See my Plan",
    notes=N("Swift program-ready card (copy) / text","swift","Program-ready card that names the first session, echoes the goals, what the user told us (symptom, what keeps them up, what pulls attention) and the first 'look forward to' pick. 'You'll find it on your Today screen' is cut (Alex, Sep 5: we are not teaching people where to find things here). No 'free'-led framing at the commit moment (March H3).", evidence="March H3; angle 2's 'your first session' reveal parked; Alex Sep 5 13:17 to 14:00", fills=["Confirm with Matheus whether the Swift program-ready card can take the first name (the Lua text cards can)"]))
add(id="cytr", type="cytr", phase=5, title=["We'll remind you 2 days","before your trial ends"],
    notes=N("Superwall post_sign_up (trial reminder step)","superwall","Today's Choose-Your-Trial-Reminder screen, kept as is, right before the paywall (Alex).", evidence="CYTR +24.7% trial starts (prior art)"))
add(id="paywall", type="paywall", phase=5, design="live", headlines={"stress":"Reduce daily stress and anxiety","sleep":"Fall asleep faster, wake up rested","focus":"Sharpen your focus","mood":"Feel steadier every day","default":"Reduce daily stress and anxiety"},
    notes=N("Superwall post_sign_up (live design)","superwall","Terminal screen: the live paywall from Alex's screenshot ('7 days for free', $5.83 a month, 10M+ happy users and 4.9-star laurels, review carousel, no payment due now, 'Start your FREE week', 'View all plans'). Research ideas live here as notes: reminder-promise headline with a Day 0/5/7 timeline, an on-paywall 'how do I cancel' answer, echo bullets built from the picks.", calmer="#43 (trial timeline paywall, not copied)", evidence="Alex 10:05 to 10:18; round 2 A3; megan-balance-path-diff-2026-08-12.md screen 18", fills=["Paywall reviews: Tracy's is the live paywall's own; the other 2 are from our verified set"]))
add(id="signup", type="signup", phase=5, branch="a.paywall==='trial'", title=["Save your program."], body="Create an account so your program follows you across devices and your trial reminder reaches you.", sub="By creating your account, you agree to Balance's Terms and Privacy Policy.",
    notes=N("Swift auth bookend","swift","Wish list moves account creation after the trial starts. Sign-up before the paywall is a cross-device/CRM decision, so this is a Swift bookend change and a strategy call, not deck work.", evidence="Growth Gems item 3; benchmark: deferred account gate is the norm for Balance's archetype"))
add(id="end", type="end", title=["Prototype ends here."], body="In the app, a started trial hands off to the first session on the Today screen. A decline shows today's counter-offer, then lands on the Today screen with the program locked.",
    note="This is the wish-list version: the flow as we'd build it with no template limits. The constrained version keeps the same spine using only card templates that exist in the app today.",
    notes=N("(prototype only)","existing","End card for reviewers."))

PR = {
"welcome": [
[
"proof-early",
"arrival",
"keep-what-works"
],
"Screen 1 carries the awards and rating because a newcomer from an ad decides in seconds whether this is a real company. The headline is the variant winning the live test."
],
"assessment_intro": [
[
"payoff",
"arrival"
],
"Tell people what the questions do before the first one, in the words today's card already uses ('personalize your Plan'). 3 minutes is a promise about their time."
],
"first_name": [
[
"echo"
],
"A first name is the cheapest thing that lets every later screen speak to the person."
],
"age": [
[
"reassure",
"payoff",
"sourced"
],
"Age unlocks the age-specific member count on the next screen, so the ask pays back immediately. The reassurance line says where the answer goes."
],
"gender": [
[
"reassure",
"no-deficit"
],
"Optional, with a plain 'prefer not to say'. Kept for review; the echo stays light because a round-2 tester read Calmer's gendered copy as generic."
],
"hdyhau": [
[
"arrival",
"proof-early"
],
"Asked early so it does not sit next to the paywall, and so a health-professional referral can become a proof signal."
],
"right_place": [
[
"echo",
"proof-early",
"felt-value",
"arrival"
],
"The first thing the user sees after giving their name and age is their name, a member count for their age, and a picture of what they get."
],
"goals": [
[
"keep-what-works"
],
"The goal screens are unchanged. They test well and everything downstream branches on them."
],
"goals_metrics": [
[
"sourced",
"proof-early",
"payoff"
],
"Same card as today, reframed as how Balance helps the goals just picked, with numbers that have a source and a date."
],
"stress_1": [
[
"payoff",
"no-deficit"
],
"A 2-week window and a reason line make the question feel like an instrument without scoring it as one. 'Not sure' is always there."
],
"stress_2": [
[
"payoff",
"no-deficit"
],
"Multi-select, because being forced to pick one symptom was the top quiz friction in March."
],
"stress_echo": [
[
"echo",
"rhythm",
"sourced",
"no-deficit"
],
"The user's own symptoms read back within one screen, then a sourced number. Validation, not agitation."
],
"stress_science": [
[
"sourced",
"rhythm",
"no-deficit"
],
"One cited finding with a disclaimer, placed where Calmer puts the scare."
],
"stress_panic": [
[
"payoff",
"rhythm"
],
"Calmer's panic question. The answer sets up the SOS preview on the next screen."
],
"singles_preview": [
[
"felt-value",
"rhythm",
"payoff",
"echo"
],
"A look at the part of the product that answers the stress just described, and an affordance the user will find waiting on home."
],
"stress_panic_b": [
[
"payoff",
"rhythm"
],
"The panic question for people who picked stress as a secondary goal."
],
"singles_preview_b": [
[
"felt-value",
"echo"
],
"The SOS toolkit shown to anyone with a stress goal, not only stress #1."
],
"stress_3": [
[
"payoff"
],
"Reason line: your sessions are matched to it."
],
"stress_recap": [
[
"echo",
"payoff",
"rhythm"
],
"What we heard, in the user's words, before moving on. This is the screen Alex called a major need."
],
"sleep_ready": [
[
"keep-what-works"
],
"Existing routing question, kept verbatim."
],
"sleep_1": [
[
"payoff",
"no-deficit"
],
"2-week window."
],
"sleep_2": [
[
"payoff",
"no-deficit"
],
"Multi-select (March B2)."
],
"sleep_echo": [
[
"echo",
"rhythm",
"sourced"
],
"Says back what keeps them up, then a sourced sleep number."
],
"sleep_science": [
[
"sourced",
"rhythm"
],
"Cited education beat in place of Calmer's cortisol chart."
],
"sleep_library_preview": [
[
"felt-value",
"rhythm"
],
"The sleep content shown, not listed."
],
"sleep_3": [
[
"payoff"
],
"Reason line: it sets when Balance suggests sessions."
],
"sleep_recap": [
[
"echo",
"payoff",
"rhythm"
],
"What we heard on the sleep path."
],
"mood_1": [
[
"payoff",
"no-deficit"
],
"A pace-setting question with a 2-week window; never scored as a screen."
],
"mood_2": [
[
"payoff"
],
"Reason line."
],
"mood_echo": [
[
"echo",
"rhythm",
"no-deficit",
"sourced"
],
"Builds on what already lifts the user instead of diagnosing them."
],
"mood_science": [
[
"sourced",
"rhythm"
],
"One cited finding."
],
"mood_preview": [
[
"felt-value",
"rhythm"
],
"The daily mood check-in shown as it works."
],
"mood_3": [
[
"payoff",
"no-deficit"
],
"'No wrong answers' in the reason line."
],
"mood_recap": [
[
"echo",
"payoff",
"rhythm"
],
"What we heard on the mood path."
],
"focus_1": [
[
"payoff"
],
"Reason line."
],
"focus_2": [
[
"payoff"
],
"2-week window."
],
"focus_echo": [
[
"echo",
"rhythm",
"no-deficit",
"sourced"
],
"Normalizes wandering attention before teaching."
],
"focus_adhd": [
[
"reassure",
"no-deficit"
],
"The most sensitive ask in the flow gets a specific line about where the answer goes, and 'I prefer not to share'."
],
"focus_primer": [
[
"sourced"
],
"Existing DID YOU KNOW card with a citation."
],
"focus_preview": [
[
"felt-value",
"rhythm"
],
"Focus content shown, not listed."
],
"focus_3": [
[
"payoff"
],
"2-week window."
],
"focus_recap": [
[
"echo",
"payoff",
"rhythm"
],
"What we heard on the focus path."
],
"sleep_trouble": [
[
"payoff",
"keep-what-works"
],
"Sleep questions now fire whenever sleep is selected. Two-thirds of sleep-motivated users never see one today."
],
"sleep_preview_b": [
[
"felt-value"
],
"Sleep content for people who picked it as a secondary goal."
],
"exercise": [
[
"payoff",
"no-deficit"
],
"A whole-health question we never asked. It feeds the profile."
],
"schedule": [
[
"payoff",
"echo"
],
"Web-funnel question with its rationale line; the answer shapes the next screen and the profile."
],
"no_judgment": [
[
"no-deficit",
"echo",
"voice"
],
"De-shames the lifestyle answers and says back the schedule before the aspiration question."
],
"future": [
[
"echo",
"payoff"
],
"The picks come back on the outcomes screen and the program-ready card, so the question visibly matters."
],
"experience": [
[
"payoff",
"keep-what-works"
],
"Existing card with a reason line."
],
"proof": [
[
"proof-early",
"sourced",
"humans"
],
"Verbatim reviews and the awards right before the Plan is built. One review says 'real voices' in a user's words."
],
"loading": [
[
"humans",
"echo",
"felt-value",
"payoff"
],
"The coaches appear where the Plan gets made: their faces, the user's answers, and the first session that comes out of them. It answers 'is this AI' without the word and gives 10 questions a visible payoff."
],
"coaches": [
[
"humans",
"echo"
],
"Faces, first names, a quick background and the handcrafted line. Showcase, not chooser."
],
"age_metrics": [
[
"sourced",
"proof-early",
"echo"
],
"The age-specific stat, March's strongest confidence builder."
],
"profile": [
[
"echo",
"honest-result",
"no-deficit"
],
"You today, from the answers given: a named profile with an insight that names the user's experience and schedule, and a week 1 that fits their days. The next screen is you in a few weeks with Balance."
],
"chart": [
[
"sourced",
"felt-value"
],
"The trajectory with Balance vs alone, with the survey figures behind it named."
],
"comparison": [
[
"echo",
"felt-value"
],
"Outcomes in the user's own words from the 'look forward to' question. Never 'Balance Premium'."
],
"commitment": [
[
"commit",
"no-deficit"
],
"Consistency over length; a realistic goal before the trial ask."
],
"reminder_time_sleep": [
[
"commit",
"keep-what-works"
],
"Existing bedtime card."
],
"reminder_time": [
[
"commit",
"keep-what-works"
],
"Existing reminder card."
],
"push": [
[
"commit",
"payoff",
"keep-what-works"
],
"An earned, contextual permission ask."
],
"program_ready": [
[
"echo",
"felt-value",
"voice"
],
"Names the first session and the first thing the user said they look forward to. No 'free'-led framing at the commit moment."
],
"cytr": [
[
"trial-anxiety",
"keep-what-works"
],
"Says when the reminder comes before asking for the trial."
],
"paywall": [
[
"keep-what-works",
"trial-anxiety",
"proof-early"
],
"Today's live paywall, unchanged."
],
"signup": [
[
"keep-what-works"
],
"Account creation, as today in the constrained version; after the trial in the wish list."
]
}
for c in W:
    pk, how = PR.get(c["id"], ([], ""))
    if pk: c["principles"] = pk
    if how: c["how"] = how
WISH = {"id":"wishlist","name":"Wish list","principles":PRINCIPLES,"description":"Calmer's flow in Balance's skin, built as if templates were free. Proof up front, a question rhythm that gives something back after every ask or two, a named profile and a progress graph, then today's paywall.",
        "phases":["Welcome","About you","Your goals","Your routine","Your program"], "cards": W}

# ---------------- Constrained: derive by explicit overrides ----------------
ALLOWED = {"welcome","text","textImage","list","question","scrollableQuestion","multiselect","goalRanking","goalsMetrics","ageMetrics","keyboard","setReminderTime","pushOptIn","userReview","primer","loading","quizResult","coaches","paywall","signup","end","commitment","chart","comparison","cytr","legacyLoading"}
NAME_OK = {"text","textImage"}   # the engine replaces a name placeholder on these cards (Common.replacePlaceholderText)
C = copy.deepcopy(W)
by = {c["id"]: c for c in C}
def setnotes(cid, **kw): by[cid]["notes"].update(kw)
def drop(cid):
    global C, by
    C = [c for c in C if c["id"]!=cid]; by = {c["id"]: c for c in C}
def replace(cid, card):
    global C, by
    C = [card if c["id"]==cid else c for c in C]; by = {c["id"]: c for c in C}
def static_recap(cid, items, body, combos):
    by[cid].update({"title":["Here's what","we heard."],"items":[{"text":t} if isinstance(t,str) else t for t in items],"body":body})
    setnotes(cid, template="list (text, subTitle, items), one card per answer combination", tag="unused", why=f"What-we-heard recap that still reads the answers back (Alex, Sep 5: the prototype should show the echo here too). Every line is fixed copy shown by an answer rule, so production is one list card per answer combination ({combos}) on the branch predicates the deck already has, or the wish list's fill-in template.", loss="The name in the headline, and the card count grows with every question echoed.")
def inc(q, v): return f"(a.{q}||[]).includes('{v}')"
def eq(q, v): return f"a.{q}==='{v}'"

# welcome: kept (config)
# age: back to numpad keyboard
by["age"].update({"type":"keyboard","questionId":"age","numpad":True,"placeholder":"age","title":["How old are you?"],"subtitle":"Your guidance will be tailored to your age group."})
for k in ("options","derive","style"): by["age"].pop(k, None)
setnotes("age", template="keyboard", tag="existing", why="Today's numpad age entry, kept. Reason line is the existing subTitle; the reassurance line is a second subTitle line.", loss="Age bands (web-funnel style).")
setnotes("gender", why="Kept as an added question (Alex, Sep 4). Nothing downstream reads it in the constrained deck yet.", loss="No downstream use without answers written into copy.")
# hdyhau: scrollableQuestion has no subTitle
setnotes("hdyhau", why="Moved early and given the health-professional option (JSON).")
# right_place: no HDYHAU echo
by["right_place"]["body"] = "Inside Balance: a 10-minute session each day, assembled from your answers by 2 real coaches, 400+ meditations, a sleep library, and Singles for the moment you need one."
setnotes("right_place", why="Show the product before asking anything personal. textImage replaces the name placeholder, so the name stays; the age count lives on its own ageMetrics card later; the paragraph goes in the Learn More panel.", loss="The age-count and friend-referral echoes; the body paragraph is behind Learn More.")
# echo beats: static, on goalMeditationPrimer (title kicker, text, subtext)
by["stress_echo"].update({"body":"Anxious thoughts, tension and restless nights are how stress shows up for most members. Balance tailors your first sessions to the way it shows up for you. In a 2025 survey of 3,700+ members, 81% said they cope better with anxious feelings."})
setnotes("stress_echo", template="goalMeditationPrimer (title, text, subtext)", tag="unused", why="Static validation beat on the stress branch: kicker, headline, small line.", loss="The user's own words read back.")
by["sleep_echo"].update({"body":"Stress, discomfort and a mind that won't switch off are the usual reasons. Balance opens your Plan with a wind-down built for exactly that, and 69% of members in our survey reported better sleep."})
setnotes("sleep_echo", template="goalMeditationPrimer (title, text, subtext)", tag="unused", why="Static validation beat on the sleep branch.", loss="The user's own answer read back.")
by["mood_echo"].update({"body":"Whether you recharge alone or with the people you love, your sessions will help you protect that time. 82% of members in our survey feel more emotionally steady."})
setnotes("mood_echo", template="goalMeditationPrimer (title, text, subtext)", tag="unused", why="Static validation beat on the mood branch.", loss="The echoed answer.")
by["focus_echo"].update({"body":"Thoughts, screens, noise, other people: whatever pulls you away, meditation is practice at noticing it and coming back, and Balance tailors your first sessions to it. 78% of members in our survey feel more present and focused."})
setnotes("focus_echo", template="goalMeditationPrimer (title, text, subtext)", tag="unused", why="Static validation beat on the focus branch.", loss="The echoed answer.")
# recaps: static list per goal
static_recap("stress_recap", [
    {"text":"Stress shows up as anxious thoughts","when":inc("how_experience_stress","anxious_thoughts")},{"text":"Stress shows up in your body","when":inc("how_experience_stress","exhaustion_or_tension")},
    {"text":"Stress shows up as moodiness","when":inc("how_experience_stress","moodiness")},{"text":"Stress gets in the way of your sleep","when":inc("how_experience_stress","difficulty_sleeping")},
    {"text":"Stress that runs in the background","when":"!(a.how_experience_stress||[]).length"},
    {"text":"Money is the biggest source right now","when":eq("stress_source","money")},{"text":"Work or school is the biggest source right now","when":eq("stress_source","work_or_school")},
    {"text":"Health is the biggest source right now","when":eq("stress_source","health")},{"text":"Relationships are the biggest source right now","when":eq("stress_source","relationships")},
    {"text":"Better sleep matters to you too","when":"a.goal_sleep==='yes'"}], "Balance builds your first sessions around exactly this.", "4 symptoms x 4 sources")
static_recap("sleep_recap", [
    {"text":"Stress keeps you up","when":inc("keep_awake","stress")},{"text":"Discomfort keeps you up","when":inc("keep_awake","discomfort")},{"text":"Noise keeps you up","when":inc("keep_awake","noise")},{"text":"You just can't fall asleep","when":inc("keep_awake","cant_fall_asleep")},
    {"text":"You fall asleep within 15 minutes","when":eq("fall_asleep_time","0_15")},{"text":"It takes you 15 to 30 minutes to fall asleep","when":eq("fall_asleep_time","15_30")},{"text":"It takes you 30 minutes or more to fall asleep","when":eq("fall_asleep_time","30_plus")},
    {"text":"You're a morning person","when":eq("chronotype","morning")},{"text":"You're a night person","when":eq("chronotype","night")},
    {"text":"Less stress matters to you too","when":"a.goal_stress==='yes'"}], "Your Plan opens with a wind-down built around this.", "4 reasons x 3 times x 3 chronotypes")
static_recap("mood_recap", [
    {"text":"A low mood rarely gets in the way","when":eq("low_mood_freq","not_at_all")},{"text":"A low mood gets in the way some days","when":eq("low_mood_freq","some")},{"text":"A low mood gets in the way most days","when":eq("low_mood_freq","most")},{"text":"A low mood gets in the way nearly every day","when":eq("low_mood_freq","nearly_every")},
    {"text":"You're happiest around family","when":eq("happiest_around","family")},{"text":"You're happiest around friends","when":eq("happiest_around","friends")},{"text":"You're happiest on your own","when":eq("happiest_around","myself")},
    {"text":"Time alone is what helps today","when":eq("improve_mood","alone")},{"text":"Talking to others is what helps today","when":eq("improve_mood","talk")},{"text":"Distraction is what helps today","when":eq("improve_mood","distract")},{"text":"Sleeping on it is what helps today","when":eq("improve_mood","sleep")}],
    "Balance tailors your first sessions to build on this.", "4 x 3 x 4 answers")
static_recap("focus_recap", [
    {"text":"Your thoughts pull your attention away","when":eq("most_distracting","thoughts")},{"text":"Your surroundings pull your attention away","when":eq("most_distracting","surroundings")},{"text":"Technology pulls your attention away","when":eq("most_distracting","technology")},{"text":"Other people pull your attention away","when":eq("most_distracting","people")},
    {"text":"Finishing tasks is hard almost every time","when":eq("finishing_tasks","always")},{"text":"Finishing tasks depends on the task","when":eq("finishing_tasks","depends")},{"text":"Finishing tasks is rarely a problem","when":eq("finishing_tasks","rarely")},
    {"text":"You often put off tasks and projects","when":eq("procrastinate","always")},{"text":"You sometimes put off tasks and projects","when":eq("procrastinate","sometimes")},{"text":"Putting things off is rare for you","when":eq("procrastinate","rarely")}],
    "Balance tailors your first sessions to train attention around this.", "4 x 3 x 3 answers")
cc = copy.deepcopy(COACHES_CARD); cc["subtitle"] = "They'll guide you toward your goals."
cc["notes"] = N("list (2 items with image, title, subtitle)","unused","The constrained version keeps today's Creating Program animation, so the coaches get their own static card here instead of the assembly reveal (Alex, Sep 4). Faces, a quick background, the handcrafted line, 'switch anytime'.", evidence="handcrafted-coaches-screen-angles.md", loss="The Option 3 assembly reveal, and the goals named in the intro line.")
i_r = [k for k,c in enumerate(C) if c["id"]=="focus_recap"][0]
C.insert(i_r+1, cc); by = {c["id"]: c for c in C}
# previews: textImage loses the body paragraph (Learn More)
for cid in ("singles_preview","singles_preview_b"):
    by[cid]["body"] = "Singles are short sessions for right now: a rising panic, a hard conversation, a night you can't switch off. You've unlocked them from day 1."
for cid in ("singles_preview","singles_preview_b","sleep_library_preview","sleep_preview_b","mood_preview","focus_preview"):
    setnotes(cid, why=by[cid]["notes"]["why"]+" textImage takes a headline and an image asset; the paragraph goes in the Learn More panel.", loss="Body paragraph on screen (behind Learn More).")
# exercise: slider -> question
replace("exercise", {"id":"exercise","type":"question","phase":4,"questionId":"exercise","title":["How often do you","move your body?"],"subtitle":"Exercise, walks, yoga. It all counts.",
  "options":[{"id":"0","text":"Rarely","color":"misty_peach"},{"id":"1","text":"Once or twice a week","color":"papaya_whip"},{"id":"2","text":"A few times a week","color":"mint_green"},{"id":"3","text":"Most days","color":"polar_blue"}],
  "notes":N("question","existing","Same question as a 4-option select. Sliders need a new template.", calmer="#28", loss="The slider interaction and per-stop art.")})
# no_judgment static
by["no_judgment"]["body"] = "Your first session runs 10 minutes, with 5-minute versions for the days that get away from you and longer ones for when you have space to unwind. No pressure, and no streak to protect."
setnotes("no_judgment", template="text", tag="existing", why="De-shaming beat after the lifestyle questions. Static.", loss="The schedule answer read back.")
# proof: split back into ageMetrics + one userReview card
i = [k for k,c in enumerate(C) if c["id"]=="proof"][0]
age_card = {"id":"age_metrics","type":"ageMetrics","phase":5,"kicker":"Did you know?","title":["Balance has helped","<b>{{L.age_count}}</b> people your age."],"cite":"As of January 2026.",
  "notes":N("ageMetrics","copy","The age-specific stat, kept as its own card (the template computes the count).", evidence="March B4/B5", fills=["Confirm the January 2026 refresh of the age buckets with Yana"])}
review_card = {"id":"proof","type":"userReview","phase":5,"title":["Members like you","say it works."],"laurels":BADGES,"reviews":REVIEWS[:1],"cta":"Continue",
  "notes":N("userReview (one quote + image per card)","unused","One testimonial card. userReview shows a single quote and an asset, so the carousel is one card here (or several cards).", calmer="#33", loss="The combined age-stat headline and the 3-review carousel; badges depend on the asset.")}
C = C[:i] + [age_card, review_card] + C[i+1:]; by = {c["id"]: c for c in C}
# loading: static labels
replace("loading", {"id":"loading","type":"legacyLoading","phase":5,"title":["Creating program"],"texts":["your goals…","your experience…","your preferences…","your age…"],
  "notes":N("Swift Creating Program screen (Lottie)","existing","Today's Creating Program animation and copy, unchanged (Alex, Sep 4).", loss="The Option 3 assembly reveal: coach faces, answer chips and the first session card.")})
# profile -> static primer per goal
replace("profile", {"id":"profile","type":"quizResult","phase":5,"kicker":"Your Balance profile","title":["Your starting point."],"scoreLabel":"Starting point","cta":"Continue",
  "profiles":{"stress":{"name":"The Overdrive Mind","body":"Stress that runs in the background all day, with a mind that rarely gets to idle.","insight":"Week 1 is short sessions that teach your mind how to settle."},
              "sleep":{"name":"The Wired and Tired","body":"Ready for rest before your mind is.","insight":"Week 1 starts with the wind-down, then works on the stress underneath it."},
              "mood":{"name":"The Weather Watcher","body":"A mood that moves with the day.","insight":"Week 1 is short check-ins that notice what you feel before it takes over."},
              "focus":{"name":"The Open Browser","body":"Attention that keeps opening new tabs.","insight":"Week 1 trains it to come back in sessions short enough to finish."}},
  "cite":"Based on your goal. Not a clinical assessment.",
  "notes":N("goalMeditationPrimer (static per goal)","unused","Named profile per goal branch: kicker, profile name as the text, insight as the subtext. quizResult is not a profile template (it scores a quiz), so the primer card carries it.", calmer="#37", evidence="Round 2 A4", loss="Answer-derived sub-scores, the score number, and the experience/schedule echo.", fills=["Profile names: content pass"])})
by["chart"]["body"] = "In a 2025 survey of 3,700+ members, 85% reported improved mental and emotional well-being and 82% feel more emotionally steady. On your own, most people report little change."
setnotes("chart", template="textImage (static chart image per goal)", tag="unused", why="The same graph as a baked image per goal branch fits textImage. The prototype draws it in; production ships 4 stills, or a Lottie if the draw-in matters.", loss="The line drawing in, and the goal's own stat in the sentence.")
# comparison: one static list per goal
by["comparison"].update({"title":["What changes","with Balance."],
  "without":[{"text":"Anxious thoughts keep coming back","when":"a.goal_1==='stress'"},{"text":"Sleep stays hit and miss","when":"a.goal_sleep==='yes'"},{"text":"Low days run the week","when":"a.goal_1==='mood'"},{"text":"Attention keeps slipping","when":"a.goal_1==='focus'"},"Not sure where to start"],
  "with_":[{"text":"Calmer nights and deeper sleep","when":"a.goal_sleep==='yes'"},{"text":"A steadier response to stress","when":"a.goal_1==='stress'"},{"text":"A steadier mood through the day","when":"a.goal_1==='mood'"},{"text":"Attention that comes back","when":"a.goal_1==='focus'"},{"text":"A 10-minute session built for you, every day"},{"text":"Every word recorded by a real person"}]})
setnotes("comparison", template="textImage (one baked image per goal, both columns in it)", tag="unused", why="Both columns kept, static per goal branch, shipped as one image (Alex, Sep 5: a single 'with Balance' block loses the point of the screen, which is on your own vs with us). The paywall intro screen going live next week carries the same framing.", loss="The user's own 'look forward to' picks; the columns are a picture, not live text.")
for o in by["commitment"]["options"]: o.pop("praise", None)
setnotes("commitment", template="question", tag="existing", why="Plain single-select; the praise ladder needs per-answer copy the template does not do.", loss="The praise line after selection.")
by["push"].update({"title":["Get a daily reminder to","meet your goals"],"body":"Reminders help you build better habits."})
setnotes("push", why="Existing OS permission wrapper with a real number in the subtext. One shared copy instead of a per-track echo.")
by["program_ready"].update({"title":["Your Plan is ready,","{{a.name}}."],"body":"Your first session is 10 minutes with Ofosu, built around your top goal. Everything you told us is already in it."})
setnotes("program_ready", template="Swift program-ready card (copy)", tag="swift", why="Existing program-ready card with new copy and the name. No 'free'-led framing.", loss="Goal and 'look forward to' echo.")
sign = by["signup"]; sign.pop("branch", None); sign.update({"title":["Create an account to","save your program."],"body":"Your program follows you across devices."})
setnotes("signup", template="Swift auth bookend", tag="existing", why="Sign-up stays right after the program-ready card and before the trial reminder and paywall, as today (Alex, Sep 5: it just has to be before the paywall).", loss="Sign-up after the trial starts (wish list).")
order = [c["id"] for c in C]; su = C.pop(order.index("signup")); C.insert([c["id"] for c in C].index("cytr"), su); by = {c["id"]: c for c in C}
by["end"].update({"note":"This is the constrained version: only card templates that exist in the app today, the current goal-1 branching kept intact, new questions allowed. Every screen here is a session.json content change except the paywall (Superwall), program-ready and sign-up (Swift)."})
for c in C:
    if "principles" not in c:
        pk, how = PR.get(c["id"], ([], ""))
        if pk: c["principles"] = pk
        if how: c["how"] = how
CONS = {"id":"constrained","name":"Constrained","principles":PRINCIPLES,"description":"The same flow using only card templates that exist in the app today, with today's branching kept and new questions allowed. Answers written into the copy (except the name), the slider, the computed profile and the step counter are cut; each screen records what it loses.",
        "cards": C}


sys.exit(0 if finish([(WISH, False), (CONS, True)], ALLOWED, NAME_OK) else 1)
