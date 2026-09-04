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
TWOWK = "Over the last 2 weeks."

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

W = []
def add(**c): W.append(c); return c

# ---------------- Part 1: Welcome ----------------
add(id="welcome", type="welcome", phase=1, title=["Less stress. Better sleep.","Adapted to <b>you</b>."],
    authority={"avatars":True,"text":"Guided by Co-Heads of Meditation Ofosu and Leah. Developed by experts in neuroscience, meditation instruction and behavioral coaching."}, laurels=BADGES, cta="Continue",
    sub="Already have an account? <span class='link'>Log in</span>",
    notes=N("welcome (remote config)","copy","Proof on screen 1: coach faces, an authority line, three plain badges. Headline is the variant winning the live welcome-card test (b_benefit). The welcome card is payload-configurable (title, CTA, image, laurels), so this is config, not a release.",
      calmer="#1 (welcome: 'built in collaboration with clinical psychologists')", evidence="Alex 1:40; ABCD test b_benefit; March A3; no clinical advisory claim exists, so the whitepaper's 'developed by experts in neuroscience, meditation instruction, and behavioral coaching' is the honest ceiling",
      fills=["Badges are text-only on purpose (Apple rejected a laurel with its logo in 2022); confirm wording with marketing","Rating and count pulled Sep 4, 2026 (4.88, 120,363 US ratings); refresh before shipping"]))
add(id="assessment_intro", type="text", phase=1, tap=True, title=["Let's start with a","few questions."],
    body="Your answers shape your program: what your first session works on, how long it runs, and how Balance adapts from there. About 3 minutes.",
    notes=N("text","copy","Tell people what the questions do before asking them. Replaces the current 'Answer a few questions to personalize your experience' card.",
      calmer="#2 (assessment intro)", evidence="Alex 2:12; benchmark rule 2 (reason in the header)"))

# ---------------- Part 2: About you ----------------
add(id="first_name", type="keyboard", phase=2, questionId="name", title=["What should we","call you?"], subtitle="Your first name, so your program can speak to you.", placeholder="first name",
    reassure="Just a first name. No account yet, and nothing is shared.",
    notes=N("keyboard","existing","Name early is the cheapest enabler of the answer-echo register. The keyboard card validates first_name today, and text/textImage cards already replace a name placeholder.",
      evidence="Benchmark: name is the field's 2nd most common ask (74%); rule 3 (result points back to what you said)"))
add(id="age", type="question", phase=2, questionId="age_band", derive="ageBand", title=["How old are you?"], subtitle="Your guidance will be tailored to your age group.", reassure="Used only to tune your program. Never shown to anyone.", style="compact",
    options=[{"id":"13-17","text":"13 to 17","color":"purple_haze"},{"id":"18-24","text":"18 to 24","color":"polar_blue"},{"id":"25-34","text":"25 to 34","color":"mint_green"},{"id":"35-44","text":"35 to 44","color":"papaya_whip"},{"id":"45-54","text":"45 to 54","color":"apricot"},{"id":"55+","text":"55 and over","color":"misty_peach"}],
    notes=N("question","existing","Age bands instead of the numpad (the web funnel asks bands first). Existing subtitle kept as the reason line; reassurance added because the deck has none anywhere.",
      calmer="#4 (age)", evidence="Alex 2:34 (who-you-are first); benchmark rule 4; web funnel /age"))
add(id="gender", type="question", phase=2, questionId="gender", title=["How do you identify?"], subtitle="Optional. Some members prefer sessions that speak to their experience.", reassure="Optional, and never shown anywhere.",
    options=[{"id":"woman","text":"Woman","color":"polar_blue"},{"id":"man","text":"Man","color":"mint_green"},{"id":"nonbinary","text":"Non-binary","color":"papaya_whip"},{"id":"prefer_not","text":"Prefer not to say","color":"purple_haze"}],
    notes=N("question","existing","Calmer opens on gender and echoes it later. Kept (Alex, Sep 4); the echo stays light because a round-2 tester read Calmer's gendered copy as 'given to every woman'.",
      calmer="#3 (gender)", evidence="Alex 2:34; round 2 P6"))
add(id="hdyhau", type="scrollableQuestion", phase=2, questionId="hdyhau", title=["How did you hear","about us?"], subtitle="So we know where to say thanks.",
    options=[{"id":"app_or_play_store","text":"App Store"},{"id":"mobile_game","text":"Mobile game"},{"id":"facebook_or_instagram","text":"Facebook or Instagram"},{"id":"search_engine","text":"Search engine"},{"id":"elevate_or_spark","text":"Elevate or Spark"},{"id":"family_and_friends","text":"Family and friends"},{"id":"tiktok","text":"TikTok"},{"id":"health_professional","text":"Health professional"},{"id":"other","text":"Other"}],
    subAnswer={"id":"not_sure","text":"Not sure"},
    notes=N("scrollableQuestion","copy","Moved early (it sits next to the paywall today), given a reason line, and gains a one-line health-professional option so referrals become a proof signal.",
      calmer="#1 (Alex's referral idea at 1:52)", evidence="Matheus: HDYHAU sits too close to the paywall; benchmark rule 2; Insight Timer offers 'Health Professional'",
      fills=["Confirm the new answer_id with data (Balance HDYHAU buckets differ from Elevate's)"]))
add(id="right_place", type="textImage", phase=2, tap=True, title=["You're in the","right place."],
    body="{{a.hdyhau==='family_and_friends'?'Someone you know already uses Balance. ':''}}Balance builds a meditation program around you: a 10-minute session each day, made from your answers and guided by 2 real coaches. Plus a sleep library and single sessions for the moments you need one.",
    mock={"header":"Your program","pill":"Day 1","rows":[{"t":"Today's meditation","s":"10 min · with Ofosu","color":"polar_blue","hl":True},{"t":"Sleep library","s":"Stories, music, soundscapes","color":"purple_haze"},{"t":"Singles","s":"For the moment you need one","color":"mint_green"}]},
    notes=N("textImage","unused","Show the product before asking anything personal. Newcomers in round 2 reached a paywall without knowing what the app would do for them. Speaks back to the HDYHAU answer when a friend sent them.",
      calmer="#5 (section preview right after age)", evidence="Alex 2:51; round 2 A2 (newcomer gap); synthesis #10", fills=["Session length and 'made from your answers' mechanism: confirm with Anna"]))

# ---------------- Part 3: Your goals ----------------
add(id="goals", type="goalRanking", phase=3, title=["Select the goals that","matter to you."], rankTitle=["Now select each goal","in order of importance."],
    notes=N("goalRanking","existing","Kept exactly as today, per Alex. Hardcoded in Lua, not authorable.", calmer="#13 (main priority)", evidence="Alex 4:35"))
add(id="goals_metrics", type="goalsMetrics", phase=3, title=["Here's what our","members are saying:"], metrics=[{"goal":"stress","text":"77% respond to stress better"},{"goal":"mood","text":"82% feel more emotionally steady"},{"goal":"sleep","text":"69% report better sleep"},{"goal":"focus","text":"78% feel more present and focused"}],
    disclaimer=["From a 2025 survey of more than","3,700 Balance members."],
    notes=N("goalsMetrics","copy","Existing card with sourced, dated numbers from the Balance whitepaper (survey of 3,700+ members, 2025). Today's 95/92/82/75 line has no locatable source, and two different sleep numbers coexist in the codebase.", evidence="March B4/B5; whitepaper Personalization Pays Off (2025); Anna's Aug 11 DM"))

# --- stress path ---
add(id="stress_1", type="question", phase=3, branch=STRESS, questionId="how_often_feel_stress", title=["How often do you","feel stressed?"], subtitle=TWOWK+" It sets the pace of your first week.",
    options=[{"id":"always","text":"Almost always","color":"misty_peach","icon":"icon-stressed"},{"id":"sometimes","text":"Sometimes","color":"off_yellow","icon":"icon-neutral"},{"id":"rarely","text":"Rarely","color":"purple_haze","icon":"icon-nostress"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with a 2-week window and a reason line.", calmer="#19 (frequency item, 'over the last two weeks')", evidence="Synthesis #7 (reason-first framing)"))
add(id="stress_2", type="multiselect", phase=3, branch=STRESS, questionId="how_experience_stress", title=["How does stress usually","show up for you?"], subtitle="Select all that apply. Your sessions focus on what you pick.",
    options=[{"id":"anxious_thoughts","text":"Anxious thoughts","color":"mint_green"},{"id":"exhaustion_or_tension","text":"Physical discomfort","color":"misty_peach"},{"id":"moodiness","text":"Moodiness","color":"purple_haze"},{"id":"difficulty_sleeping","text":"Difficulty sleeping","color":"papaya_whip"}],
    notes=N("question (allowMultipleAnswers)","existing","Same question, now multi-answer. The top quiz friction in March was being forced to pick one symptom. The question card already supports allowMultipleAnswers (unused in today's deck), so the icons and pastel rows stay.", calmer="#6 ('Which of these feel familiar?')", evidence="March B2 (8 of 18)"))
add(id="stress_echo", type="text", phase=3, branch=STRESS, tap=True, kicker="You're not alone", title=["Most people come to","Balance for exactly this."],
    body="You said stress shows up as {{H.lower(H.list(L.how_experience_stress))}}. In a survey of 3,700+ members, 77% said they respond to stress better. Your first sessions are built for that.",
    notes=N("text (with interpolation)","new","Validation beat that reads the answer back within seconds. Today the flow asks 8 to 10 questions and reflects none of them until the loading screen.", calmer="#8 (validation interstitial)", evidence="Synthesis #1; Alex 5:00", fills=[]))
add(id="stress_science", type="primer", phase=3, branch=STRESS, title=["Regular meditation","measurably lowers","stress and anxiety."], body="The most widely cited meta-analysis of meditation, 47 randomized trials and 3,500+ participants, found measurable improvements in anxiety, depression and pain.",
    cite="Goyal et al., JAMA Internal Medicine, 2014. Results vary from person to person. Balance is not a substitute for professional care.",
    notes=N("goalMeditationPrimer","unused","Honest replacement for Calmer's agitation arc: one cited finding plus a disclaimer. The DID-YOU-KNOW-with-citation template (title, text, subtext) exists and is unused.", calmer="#9 to #11 (agitation), #36 (hope stat with disclaimer)", evidence="Anna's citation set; March B5", fills=["Disclaimer wording with content"]))
add(id="singles_preview", type="textImage", phase=3, branch=STRESS, tap=True, title=["For the moments","stress hits first."], body="Singles are short sessions for right now: a rising panic, a hard conversation, a night you can't switch off. Look for them on your Today screen from day 1.",
    mock={"header":"Singles","rows":[{"t":"SOS","s":"3 min · when panic rises","color":"misty_peach","hl":True},{"t":"Before a hard conversation","s":"5 min","color":"papaya_whip"},{"t":"Unwind","s":"10 min","color":"polar_blue"}]},
    notes=N("textImage","unused","Section preview as felt value, and Calmer's 'look for the helicopter' trick: teach an affordance in onboarding that is visibly waiting on home.", calmer="#20 (Panic SOS preview)", evidence="Alex 5:40 ('we literally have the same meditation, the SOS single')", fills=["Real Single titles and durations from the catalog"]))
add(id="stress_3", type="question", phase=3, branch=STRESS, questionId="stress_source", title=["What's the biggest","source of your stress?"], subtitle="We'll match your sessions to it.",
    options=[{"id":"money","text":"Money","color":"purple_haze","icon":"icon-money"},{"id":"work_or_school","text":"Work or school","color":"polar_blue","icon":"icon-work"},{"id":"health","text":"Health","color":"mint_green","icon":"icon-health"},{"id":"relationships","text":"Relationships","color":"misty_peach","icon":"icon-people"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line.", calmer="#14 (stress drivers)"))
add(id="stress_recap", type="text", phase=3, branch=STRESS, kicker="Got it", title=["Here's what","we heard, {{a.name}}."],
    items=[{"text":"Stress shows up as {{H.lower(H.list(L.how_experience_stress))}}"},{"text":"{{L.stress_source}} is the biggest source right now","when":"a.stress_source && a.stress_source!=='unsure'"},{"text":"Better sleep matters to you too","when":"a.goal_sleep==='yes'"}],
    body="Your first sessions start right there.", cta="Continue",
    notes=N("text (with interpolation)","new","The recap Alex called a major need, framed as what we heard (so it reads differently from the outcomes screen later). Interpolation needs template work; the static per-goal version is a list card.", calmer="#15 (answer-echo checklist)", evidence="Alex 5:00 to 5:15; synthesis #1"))

# --- sleep-first path ---
add(id="sleep_ready", type="question", phase=3, branch=SLEEP1, questionId="ready_to_sleep", title=["Do you need help falling","asleep right now?"], subtitle="If yes, your first session is a Sleep Single tonight.",
    options=[{"id":"yes","text":"Yes, I'm ready to sleep","color":"polar_blue"},{"id":"no","text":"No, I'm not ready for sleep","color":"purple_haze"}],
    notes=N("question","existing","Kept verbatim. Routes the post-onboarding destination (Sleep Single vs Plan) on the native side."))
add(id="sleep_1", type="question", phase=3, branch=SLEEP1, questionId="fall_asleep_time", title=["How long does it usually","take you to fall asleep?"], subtitle=TWOWK,
    options=[{"id":"0_15","text":"0 to 15 minutes","color":"mint_green"},{"id":"15_30","text":"15 to 30 minutes","color":"papaya_whip"},{"id":"30_plus","text":"30 minutes or more","color":"misty_peach"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with the 2-week window.", calmer="#24 (sleep frequency item)"))
add(id="sleep_2", type="multiselect", phase=3, branch=SLEEP1, questionId="keep_awake", title=["What tends to keep","you awake at night?"], subtitle="Select all that apply.",
    options=[{"id":"stress","text":"Stress","color":"misty_peach"},{"id":"discomfort","text":"Discomfort","color":"mint_green"},{"id":"noise","text":"Noise","color":"papaya_whip"},{"id":"cant_fall_asleep","text":"Just can't fall asleep","color":"purple_haze"}],
    notes=N("question (allowMultipleAnswers)","existing","Same question, now multi-answer (March B2).", calmer="#6"))
add(id="sleep_echo", type="text", phase=3, branch=SLEEP1, tap=True, kicker="You're not alone", title=["Most members who come","for sleep say the same."], body="You said {{H.lower(H.list(L.keep_awake))}} keeps you up. 69% of members in our survey reported better sleep, and the first thing your program works on is the wind-down that gets you there.",
    notes=N("text (with interpolation)","new","Validation echo for the sleep path.", calmer="#8", evidence="Synthesis #1"))
add(id="sleep_science", type="primer", phase=3, branch=SLEEP1, title=["A regular wind-down","practice shortens the time","it takes to fall asleep."], body="In a randomized trial of adults with sleep trouble, a mindfulness program improved sleep quality more than sleep-hygiene education alone.",
    cite="Black et al., JAMA Internal Medicine, 2015. [Confirm with Anna.] Results vary from person to person.",
    notes=N("goalMeditationPrimer","unused","Cited education beat in place of Calmer's cortisol chart.", calmer="#26 (cortisol education)", evidence="Alex 6:33", fills=["Confirm the citation and wording with Anna"]))
add(id="sleep_library_preview", type="textImage", phase=3, branch=SLEEP1, tap=True, title=["Your sleep library is","ready when you are."], body="Sleep meditations, stories, music and soundscapes, plus the Sleep Single for nights you're ready to drift off right now.",
    mock={"header":"Sleep","rows":[{"t":"Sleep Single","s":"Tonight · 12 min","color":"purple_haze","hl":True},{"t":"Sleep stories","s":"[N] stories","color":"polar_blue"},{"t":"Soundscapes","s":"Rain, ocean, campfire","color":"mint_green"}]},
    notes=N("textImage","unused","Feature the sleep content more creatively than a stat row.", calmer="#25 (Stories preview)", evidence="Alex 6:15", fills=["Sleep catalog counts and titles"]))
add(id="sleep_3", type="question", phase=3, branch=SLEEP1, questionId="chronotype", title=["Are you a morning","person or a night person?"], subtitle="It sets when Balance suggests your sessions.",
    options=[{"id":"morning","text":"Morning person","color":"papaya_whip","icon":"icon-morningperson"},{"id":"night","text":"Night person","color":"purple_haze","icon":"icon-nightperson"},{"id":"both","text":"A bit of both","color":"polar_blue","icon":"icon-both"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="sleep_recap", type="text", phase=3, branch=SLEEP1, kicker="Got it", title=["Here's what","we heard, {{a.name}}."],
    items=[{"text":"{{H.list(L.keep_awake)}} keep{{(a.keep_awake||[]).length===1?'s':''}} you up"},{"text":"It takes you {{H.lower(L.fall_asleep_time)}} to fall asleep","when":"a.fall_asleep_time && a.fall_asleep_time!=='unsure'"},{"text":"You're a {{H.lower(L.chronotype)}}","when":"a.chronotype && a.chronotype!=='unsure' && a.chronotype!=='both'"},{"text":"Less stress matters to you too","when":"a.goal_stress==='yes'"}],
    body="Your program starts with the wind-down.", cta="Continue",
    notes=N("text (with interpolation)","new","What-we-heard recap for the sleep path.", calmer="#15"))

# --- mood path (full rhythm) ---
add(id="mood_1", type="question", phase=3, branch=MOOD, questionId="low_mood_freq", title=["How often does a low mood","get in the way of your day?"], subtitle=TWOWK+" It sets the pace of your first week.", options=FREQ4, subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","existing","New frequency item with the 2-week window, so the mood path has a pace-setting question like stress does. Never scored as a screen.", calmer="#19"))
add(id="mood_2", type="question", phase=3, branch=MOOD, questionId="happiest_around", title=["Who do you usually","feel happiest around?"], subtitle="It shapes the examples in your sessions.",
    options=[{"id":"family","text":"Family","color":"papaya_whip"},{"id":"friends","text":"Friends","color":"mint_green"},{"id":"myself","text":"By myself","color":"purple_haze"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="mood_echo", type="text", phase=3, branch=MOOD, tap=True, kicker="You're not alone", title=["Most members start","Balance on a hard week."], body="{{a.happiest_around==='myself'?'Time to yourself is where you recharge, so your sessions will protect it.':'You feel happiest around '+H.lower(L.happiest_around||'people you love')+', so your sessions will help you show up for them.'}} 82% of members in our survey feel more emotionally steady.",
    notes=N("text (with interpolation)","new","Validation echo for the mood path.", calmer="#8", evidence="Synthesis #1"))
add(id="mood_science", type="primer", phase=3, branch=MOOD, title=["A short daily practice","lifts mood over","a few weeks."], body="An analysis of randomized trials found mindfulness programs reduce psychological distress in everyday adults, not only in clinical groups.",
    cite="Galante et al., Nature Mental Health, 2023. Results vary from person to person. Balance is not a substitute for professional care.",
    notes=N("goalMeditationPrimer","unused","Cited education beat for the mood path.", calmer="#9 to #11", fills=[]))
add(id="mood_preview", type="textImage", phase=3, branch=MOOD, tap=True, title=["Check in, then","meet the day."], body="Each day starts with a 10-second mood check-in, and Balance picks a session for how you actually feel. Singles are there for the harder moments.",
    mock={"header":"Today","pill":"Mood check-in","rows":[{"t":"How are you feeling?","s":"Tap a mood","color":"papaya_whip","hl":True},{"t":"Today's meditation","s":"Picked for your mood · 10 min","color":"polar_blue"},{"t":"[Lift] Single","s":"5 min · for a low moment","color":"mint_green"}]},
    notes=N("textImage","unused","Section preview for the mood path: the daily mood check-in and mood Singles.", calmer="#12 (School preview)", evidence="Alex 4:15 ('think creatively about how sections of Balance could help')", fills=["Mood check-in mechanics and Single titles from the catalog"]))
add(id="mood_3", type="question", phase=3, branch=MOOD, questionId="improve_mood", title=["What do you usually do","to improve your mood?"], subtitle="No wrong answers. We build on what already works.",
    options=[{"id":"alone","text":"Spend time alone","color":"purple_haze"},{"id":"talk","text":"Talk to others","color":"polar_blue"},{"id":"distract","text":"Distract myself","color":"papaya_whip"},{"id":"sleep","text":"Sleep on it","color":"mint_green"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="mood_recap", type="text", phase=3, branch=MOOD, kicker="Got it", title=["Here's what","we heard, {{a.name}}."], items=[{"text":"A low mood gets in the way {{H.lower(L.low_mood_freq)}}","when":"a.low_mood_freq && a.low_mood_freq!=='unsure'"},{"text":"You're happiest {{a.happiest_around==='myself'?'on your own':'around '+H.lower(L.happiest_around)}}","when":"a.happiest_around && a.happiest_around!=='unsure'"},{"text":"{{L.improve_mood}} is what helps today","when":"a.improve_mood && a.improve_mood!=='unsure'"}],
    body="Your first sessions build on that.", cta="Continue",
    notes=N("text (with interpolation)","new","What-we-heard recap for the mood path.", calmer="#15"))

# --- focus path (full rhythm) ---
add(id="focus_1", type="question", phase=3, branch=FOCUS, questionId="most_distracting", title=["What do you find the","most distracting?"], subtitle="Your sessions train attention around it.",
    options=[{"id":"thoughts","text":"My thoughts","color":"mint_green","icon":"icon-thoughts"},{"id":"surroundings","text":"My surroundings","color":"papaya_whip"},{"id":"technology","text":"Technology","color":"purple_haze"},{"id":"people","text":"Other people","color":"misty_peach","icon":"icon-people"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus a reason line."))
add(id="focus_2", type="question", phase=3, branch=FOCUS, questionId="finishing_tasks", title=["Do you have difficulty","finishing tasks?"], subtitle=TWOWK,
    options=[{"id":"always","text":"Almost always","color":"misty_peach"},{"id":"depends","text":"Depends on the task","color":"papaya_whip"},{"id":"rarely","text":"Rarely","color":"purple_haze"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card plus the 2-week window."))
add(id="focus_echo", type="text", phase=3, branch=FOCUS, tap=True, kicker="You're not alone", title=["Attention wanders.","That's what it does."], body="You said {{H.lower(L.most_distracting)}} pull{{a.most_distracting==='thoughts'||a.most_distracting==='people'?'':'s'}} you away most. Meditation is practice at noticing that and coming back, and 78% of members in our survey feel more present and focused.",
    notes=N("text (with interpolation)","new","Validation echo for the focus path.", calmer="#8", evidence="Synthesis #1"))
add(id="focus_adhd", type="question", phase=3, branch=FOCUS, questionId="has_adhd_or_add", title=["Do you have ADD/ADHD?"], subtitle="These conditions can affect focus.", reassure="Stays in your program. Never shared, never used for anything else.",
    options=[{"id":"yes","text":"Yes","color":"purple_haze"},{"id":"maybe","text":"I think I do","color":"papaya_whip"},{"id":"no","text":"No","color":"misty_peach"},{"id":"not_shared","text":"I prefer not to share","color":"mint_green"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with a specific reassurance line beside the most sensitive ask in the flow.", evidence="Benchmark rule 4"))
add(id="focus_primer", type="primer", phase=3, branch=FOCUS, title=["Meditation can help","with symptoms of","ADHD and ADD."], body="[One line on the study Anna recommends.]", cite="[Citation]",
    notes=N("goalMeditationPrimer","copy","Existing DID YOU KNOW card, now with a citation line.", evidence="March B5", fills=["ADHD citation from Anna"]))
add(id="focus_preview", type="textImage", phase=3, branch=FOCUS, tap=True, title=["Built for a mind","with open tabs."], body="Short focus sessions before you start work, a timer for the task in front of you, and Singles made for ADHD brains.",
    mock={"header":"Focus","rows":[{"t":"[Focus] Single","s":"5 min · before you start","color":"polar_blue","hl":True},{"t":"[Task Timer]","s":"Work in focused blocks","color":"mint_green"},{"t":"[ADHD] Single","s":"10 min","color":"purple_haze"}]},
    notes=N("textImage","unused","Section preview for the focus path.", calmer="#12", evidence="Alex 4:15", fills=["Focus Single titles, the timer feature name, ADHD Single title"]))
add(id="focus_3", type="question", phase=3, branch=FOCUS, questionId="procrastinate", title=["How often do you","procrastinate on work?"], subtitle=TWOWK,
    options=[{"id":"always","text":"Almost always","color":"misty_peach"},{"id":"sometimes","text":"Sometimes","color":"papaya_whip"},{"id":"rarely","text":"Rarely","color":"purple_haze"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question","copy","Existing card with the 2-week window."))
add(id="focus_recap", type="text", phase=3, branch=FOCUS, kicker="Got it", title=["Here's what","we heard, {{a.name}}."], items=[{"text":"{{L.most_distracting}} pull{{a.most_distracting==='thoughts'||a.most_distracting==='people'?'':'s'}} you away most","when":"a.most_distracting && a.most_distracting!=='unsure'"},{"text":"Finishing tasks is hard {{H.lower(L.finishing_tasks)}}","when":"a.finishing_tasks && a.finishing_tasks!=='unsure'"},{"text":"You procrastinate {{H.lower(L.procrastinate)}}","when":"a.procrastinate && a.procrastinate!=='unsure'"}],
    body="Your first sessions train attention to come back.", cta="Continue",
    notes=N("text (with interpolation)","new","What-we-heard recap for the focus path.", calmer="#15"))

# --- everyone: coaches ---
add(id="coaches", type="coaches", phase=3, title=["Your coaches are","Ofosu and Leah."], bios=[{"name":"Ofosu","text":"Over 20 years teaching meditation, including at the Insight Meditation Society and Spirit Rock."},{"name":"Leah","text":"Blends neuroscience, psychology and lived experience. Has taught in 16+ countries."}],
    body="Every session in Balance is written and recorded by the 2 of them.", cta="Continue",
    notes=N("list (2 items with image, title, subtitle)","unused","The decided 'made by humans' screen (angle 1, Sep 4). Showcase, not chooser; no 'AI' in the copy. Headline register to be matched in review.",
      evidence="handcrafted-coaches-screen-angles.md; 3 competitors lean on teacher credibility", fills=["Bios trimmed from the approved website bios; Cindy to confirm the one-liners","Headline: question-and-statement register"]))

# ---------------- Part 4: Your routine ----------------
add(id="sleep_trouble", type="question", phase=4, branch=SLEEP_ANY_NOT_FIRST, questionId="sleep_trouble", derive="sleepTrouble", title=["How often have you had","trouble falling asleep?"], subtitle=TWOWK+" Even when you felt tired.",
    options=[{"id":"not_at_all","text":"Not at all","color":"mint_green"},{"id":"some","text":"Some nights","color":"papaya_whip"},{"id":"most","text":"Most nights","color":"apricot"},{"id":"nearly_every","text":"Nearly every night","color":"misty_peach"}],
    notes=N("question","existing","Sleep block now fires whenever sleep is selected, not only when it ranks first. Two-thirds of sleep-motivated users never see a sleep question today.", calmer="#24", evidence="Deck map: only goal #1 drives question blocks; sleep is the clearest PMF segment (March 4.83 vs 3.00)"))
add(id="sleep_preview_b", type="textImage", phase=4, branch=SLEEP_ANY_NOT_FIRST, tap=True, title=["Sleep is part of","your program too."], body="Sleep meditations, stories, music and soundscapes are ready on the nights you need them, alongside your daily session.",
    mock={"header":"Sleep","rows":[{"t":"Sleep Single","s":"Tonight · 12 min","color":"purple_haze","hl":True},{"t":"Sleep stories","s":"[N] stories","color":"polar_blue"},{"t":"Soundscapes","s":"Rain, ocean, campfire","color":"mint_green"}]},
    notes=N("textImage","unused","Sleep content preview for users who picked sleep as a secondary goal.", calmer="#25", evidence="Alex 6:15"))
add(id="exercise", type="slider", phase=4, questionId="exercise", title=["How often do you","move your body?"], subtitle="Exercise, walks, yoga. It all counts.", default=1, poles=["Rarely","Most days"],
    stops=[{"id":"0","label":"Rarely","caption":"I rarely exercise"},{"id":"1","label":"Once or twice a week","caption":"Once or twice a week"},{"id":"2","label":"A few times a week","caption":"A few times a week"},{"id":"3","label":"Most days","caption":"Most days"}],
    notes=N("slider","new","Whole-health question in Calmer's slider form. Sliders are on the deck map's hard-limits list, so the constrained version is a 4-option select.", calmer="#28 (exercise slider)", evidence="Alex 6:47"))
add(id="schedule", type="question", phase=4, questionId="schedule", title=["How busy is","your schedule?"], subtitle="Even 5 minutes can change your day. We'll make it work.",
    options=[{"id":"packed","text":"Packed, every day","color":"misty_peach"},{"id":"busy","text":"Busy most days","color":"papaya_whip"},{"id":"some","text":"Some room to breathe","color":"mint_green"},{"id":"open","text":"Pretty open","color":"polar_blue"}],
    notes=N("question","existing","Lifted from the web funnel, rationale line included (content-vetted copy).", evidence="web-onboarding-2026-08-20.md /schedule; Alex 8:58"))
add(id="no_judgment", type="text", phase=4, tap=True, title=["The habits you already","have count for a lot."], body="{{({packed:'Your schedule is packed',busy:'You're busy most days',some:'You have some room to breathe',open:'Your schedule is pretty open'})[a.schedule]||'Your days fill up'}}, so your first sessions run 10 minutes or less, with 5-minute versions for the days that get away from you. No pressure, no streak to protect.",
    notes=N("text (with interpolation)","new","De-shaming beat that speaks back to the schedule answer, before the aspiration question.", calmer="#31 (non-judgment beat)", evidence="Alex: more moments that speak back to the user"))
add(id="future", type="multiselect", phase=4, questionId="future", max=3, title=["When you feel better,","what do you look","forward to?"], subtitle="Pick up to 3.",
    options=[{"id":"calm_nights","text":"Calm nights and deep sleep","color":"purple_haze"},{"id":"clear_head","text":"A clearer head at work","color":"polar_blue"},{"id":"patience","text":"More patience with the people I love","color":"papaya_whip"},{"id":"present","text":"Feeling present instead of racing ahead","color":"mint_green"},{"id":"hard_moments","text":"Handling hard moments without spiraling","color":"misty_peach"},{"id":"energy","text":"Energy for the things I enjoy","color":"apricot"}],
    notes=N("multiselect","existing","Positive-future question, neutral framing. Picks come back on the outcomes screen and the program-ready card.", calmer="#32 ('reclaim' outcomes multi)", evidence="Alex 7:05 to 7:26"))
add(id="experience", type="question", phase=4, questionId="has_meditated_before", title=["What best describes your","meditation experience?"], subtitle="Your first sessions match your experience level.", options=MEDEXP,
    notes=N("question","copy","Existing card, one shared version with a reason line instead of 4 goal-specific copies."))

# ---------------- Part 5: Your program ----------------
add(id="proof", type="userReview", phase=5, kicker="Did you know?", title=["Balance has helped","<b>{{L.age_count}}</b> people","your age."], laurels=BADGES, reviews=REVIEWS, cite="Member count as of January 2026. Reviews verbatim from the App Store.", cta="Continue",
    notes=N("ageMetrics + userReview","new","One proof screen instead of two: the age-specific stat (March's strongest confidence builder) as the headline, badges, and real reviews. In the deck these are two templates (ageMetrics; userReview shows one quote per card).", calmer="#33 (social proof carousel)", evidence="Alex: combine the reviews screen with the age stat; March B4 (12 of 18); Alex 7:28", fills=["Age counts on record date from Jan 2022; confirm the January 2026 refresh with Yana","Reviews are verbatim public App Store reviews (Sep 4, 2026); the 'real voices and not AI' line is in on Alex's call"]))
add(id="loading", type="loading", phase=5, title=["Building your","program, {{a.name}}."], bars=["{{H.goal(a.goal_1)}} patterns","Sleep habits","Routine and schedule","Meditation experience","Choosing your first session"],
    notes=N("meditationLoading","unused","Named-instrument loading: the bars name the question sections just answered. meditationLoading takes upperText/lowerText pairs; the name placeholder works on text cards.", calmer="#34 (5-bar 'Building your Calmer experience')", evidence="Alex 7:36; benchmark rule 3"))
add(id="profile", type="profile", phase=5, kicker="Your Balance profile", title=["Here's your","starting point."], scoreLabel="Starting point", cta="Continue",
    scores=[{"label":"Stress load","from":"how_often_feel_stress","map":{"always":"low","sometimes":"mid","rarely":"good","unsure":"mid"},"text":{"low":"High","mid":"Moderate","good":"Low"}},
            {"label":"Mood","from":"low_mood_freq","map":{"not_at_all":"good","some":"mid","most":"low","nearly_every":"low","unsure":"mid"},"text":{"good":"Steady","mid":"Up and down","low":"Needs care"}},
            {"label":"Focus","from":"finishing_tasks","map":{"always":"low","depends":"mid","rarely":"good","unsure":"mid"},"text":{"low":"Scattered","mid":"Uneven","good":"Steady"}},
            {"label":"Sleep","from":"sleep_trouble","map":{"not_at_all":"good","some":"mid","most":"low","nearly_every":"low"},"text":{"good":"Steady","mid":"Uneven","low":"Needs care"}},
            {"label":"Sleep","from":"fall_asleep_time","map":{"0_15":"good","15_30":"mid","30_plus":"low","unsure":"mid"},"text":{"good":"Steady","mid":"Uneven","low":"Needs care"}},
            {"label":"Movement","from":"exercise","map":{"0":"low","1":"mid","2":"good","3":"good"},"text":{"low":"Rare","mid":"Some","good":"Regular"}},
            {"label":"Room in your day","from":"schedule","map":{"packed":"low","busy":"mid","some":"good","open":"good"},"text":{"low":"Tight","mid":"Some","good":"Open"}},
            {"label":"Experience","from":"has_meditated_before","map":{"none":"mid","once_or_twice":"mid","a_little":"good","a_lot":"good"},"text":{"mid":"Starting out","good":"Practicing"}}],
    profiles={"stress":{"name":"The Overdrive Mind","insight":"Your mind rarely gets to idle. {{a.has_meditated_before==='none'?'You're new to this':'You've meditated before'}} and your days are {{H.lower(L.schedule||'busy')}}, so week 1 is short sessions that teach your mind how to settle."},
              "sleep":{"name":"The Wired and Tired","insight":"Your body is ready for rest before your mind is. {{a.has_meditated_before==='none'?'You're new to this':'You've meditated before'}}, so week 1 starts with the wind-down, then works on the stress underneath it."},
              "mood":{"name":"The Weather Watcher","insight":"Your mood moves with the day. {{a.has_meditated_before==='none'?'You're new to this':'You've meditated before'}} and your days are {{H.lower(L.schedule||'busy')}}, so week 1 is short check-ins that notice what you feel before it takes over."},
              "focus":{"name":"The Open Browser","insight":"Attention keeps opening new tabs. {{a.has_meditated_before==='none'?'You're new to this':'You've meditated before'}}, so week 1 trains it to come back in sessions short enough to finish."}},
    cite="Based only on your answers. Not a clinical assessment.",
    notes=N("goalMeditationPrimer (static per goal) or new gauge template","new","A named result profile is where 'it understood me' landed in round 2. Sub-scores derive only from answers actually given, so no manufactured headroom (P18). The insight speaks back to experience and schedule.", calmer="#37 (Mental Health Load gauge)", evidence="Round 2 A4; Alex 8:09; web funnel 'Here's Your Mental Health Profile / The Overdrive Mode'", fills=["Profile names: content pass","Score mapping: agree the rules with DS so nothing reads as a diagnosis"]))
add(id="chart", type="chart", phase=5, title=["Feel better, faster,","with Balance."], weeks=["Today","Week 1","Week 3","Week 6"], withLabel="With Balance", aloneLabel="On your own",
    body="In a 2025 survey of 3,700+ members, 77% said they respond to stress better and 69% reported better sleep. On your own, most people report little change.", cite="Illustrative curve. Survey figures from the Balance whitepaper, 2025.", cta="Continue",
    notes=N("textImage (static image per goal)","new","The progress graph Alex called 'so important': on your own vs with Balance, never 'Balance Premium'. A static image per goal fits textImage.", calmer="#38 (projection graph)", evidence="Alex 8:35 to 9:00", fills=["Copy pass against the web funnel's Before/Day 2/Day 30 timeline"]))
add(id="comparison", type="comparison", phase=5, title=["What changes","with Balance."], withoutTitle="On your own", withTitle="With Balance",
    without=[{"text":"{{H.first(L.how_experience_stress.split(', '))}} keep coming back","when":"a.goal_1==='stress'"},{"text":"Sleep stays hit and miss","when":"a.goal_sleep==='yes'"},{"text":"Low days run the week","when":"a.goal_1==='mood'"},{"text":"Attention keeps slipping","when":"a.goal_1==='focus'"},"Not sure where to start"],
    with_=[{"from":"future"},{"text":"A 10-minute session built for you, every day"}], cite="Same framing as the paywall intro screen going live next week; keep the two consistent.", cta="Continue",
    notes=N("list (static per goal)","new","Outcomes screen built from the user's own 'look forward to' picks. Distinct from the earlier recap (what we heard) and replaces the benefits checklist. Matches Michal's option-3 paywall intro screen.", calmer="#39 (comparison card)", evidence="Alex 8:46; Tangent paywall intro screen; Alex: differentiate the list screens"))
add(id="commitment", type="commitment", phase=5, questionId="commitment", title=["How many days a week","feels realistic?"], subtitle="Consistency matters more than length. 10 minutes counts.", cta="Set my goal",
    options=[{"id":"7","text":"Every day","sub":"Fastest results","color":"mint_green","praise":"Incredible. Daily practice is where members see the fastest change."},{"id":"5","text":"5 days a week","sub":"Weekdays","color":"polar_blue","praise":"Great. Weekdays are a strong rhythm."},{"id":"3","text":"3 days a week","sub":"Every other day","color":"papaya_whip","praise":"Good. 3 days builds a real habit."},{"id":"2","text":"Weekends","sub":"Sat and Sun","color":"purple_haze","praise":"A start. Balance will meet you there."}],
    notes=N("question","existing","Commitment device right before the reminder and paywall. Plain single-select; the praise line is a per-answer subtitle swap.", calmer="#41 (commitment pledge)", evidence="Synthesis #4; Alex 9:57", fills=[]))
add(id="reminder_time_sleep", type="setReminderTime", phase=5, branch="a.goal_sleep==='yes'", questionId="bedtime", title=["What is your","target bedtime?"], subtitle="Going to bed at the same time every night improves sleep quality.", default="10:00 pm", times=["9:00 pm","9:30 pm","10:00 pm","10:30 pm","11:00 pm","11:30 pm"],
    notes=N("setReminderTime","existing","Existing bedtime card (sleep track). Placement kept: earned and contextual.", evidence="Benchmark rule 7 vs its structural read: a prototype arm, not a defect"))
add(id="reminder_time", type="setReminderTime", phase=5, branch=NO_SLEEP, questionId="reminder_time", title=["When would you","like to be reminded?"], subtitle="A daily nudge for your 10 minutes.", default="6:00 pm", times=["7:00 am","8:00 am","12:00 pm","5:00 pm","6:00 pm","8:00 pm"],
    notes=N("setReminderTime","existing","Existing training-reminder card."))
add(id="push", type="pushOptIn", phase=5, questionId="push", title=["Get a reminder at","{{a.goal_sleep==='yes'?'your target bedtime':'your chosen time'}}"], body="{{a.goal_sleep==='yes'?'Reminders help you set a consistent sleep schedule.':'Reminders help you build better habits.'}}", cta="Continue",
    notes=N("pushOptIn","copy","Existing OS permission wrapper. Benchmark rule 8 wants a real opt-in number here; none exists in our data yet, so the line is out rather than invented.", evidence="Benchmark rule 8"))
add(id="program_ready", type="text", phase=5, title=["Your program is","ready, {{a.name}}."], body="Your first session is 10 minutes with Ofosu, built for {{H.lower(H.goal(a.goal_1))}}{{a.goal_sleep==='yes' && a.goal_1!=='sleep' ? ' and better sleep' : ''}}.{{(a.future||[]).length?' Week 1 works toward '+H.lower(H.first(L.future.split(', ')))+'.':''}} It's waiting on your Today screen.", cta="See my program",
    notes=N("Swift program-ready card (copy) / text","swift","Program-ready card that names the first session, echoes the goals and the first 'look forward to' pick. No 'free'-led framing at the commit moment (March H3).", evidence="March H3; angle 2's 'your first session' reveal parked"))
add(id="paywall", type="paywall", phase=5, design="recime", headlines={"stress":"Reduce daily stress and anxiety","sleep":"Fall asleep faster, wake up rested","focus":"Sharpen your focus","mood":"Feel steadier every day","default":"Reduce daily stress and anxiety"},
    notes=N("Superwall post_sign_up (ReciMe layout)","superwall","Terminal screen: the live ReciMe-style paywall ('Try Balance for free', trial badge, benefit list, annual vs monthly, 'Try for $0.00', Restore Purchase), rebuilt from the Aug 12 recording's layout with today's $69.99 / $9.99 / 7-day set. Research ideas live here as notes: reminder-promise headline with a Day 0/5/7 timeline, an on-paywall 'how do I cancel' answer, echo bullets built from the picks.", calmer="#43 (trial timeline paywall, not copied)", evidence="Alex 10:05 to 10:18; round 2 A3; megan-balance-path-diff-2026-08-12.md screen 18", fills=["Check the benefit bullets and badge copy against the live Superwall paywall"]))
add(id="signup", type="signup", phase=5, branch="a.paywall==='trial'", title=["Save your program."], body="Create an account so your program follows you across devices and your trial reminder reaches you.", sub="By creating your account, you agree to Balance's Terms and Privacy Policy.",
    notes=N("Swift auth bookend","swift","Wish list moves account creation after the trial starts. Sign-up before the paywall is a cross-device/CRM decision, so this is a Swift bookend change and a strategy call, not deck work.", evidence="Growth Gems item 3; benchmark: deferred account gate is the norm for Balance's archetype"))
add(id="end", type="end", title=["Prototype ends here."], body="In the app, a started trial hands off to the first session on the Today screen. A decline shows today's counter-offer, then lands on the Today screen with the program locked.",
    note="This is the wish-list version: the flow as we'd build it with no template limits. The constrained version keeps the same spine using only card templates that exist in the app today.",
    notes=N("(prototype only)","existing","End card for reviewers."))

WISH = {"id":"wishlist","name":"Wish list","description":"Calmer's package in Balance's skin: proof up front, questions in an ask, echo, teach, preview rhythm on every goal path, a named result profile and a progress graph, then today's paywall. Built as if templates were free.",
        "phases":["Welcome","About you","Your goals","Your routine","Your program"], "cards": W}

# ---------------- Constrained: derive by explicit overrides ----------------
ALLOWED = {"welcome","text","textImage","list","question","scrollableQuestion","multiselect","goalRanking","goalsMetrics","ageMetrics","keyboard","setReminderTime","pushOptIn","userReview","primer","loading","quizResult","coaches","paywall","signup","end","commitment","chart","comparison"}
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
def static_recap(cid, items, body):
    by[cid].update({"title":["Here's what","we heard."],"items":[{"text":t} if isinstance(t,str) else t for t in items],"body":body})
    setnotes(cid, template="list (text, subTitle, items)", tag="unused", why="Static what-we-heard recap for this goal branch on the list template. The branch already scopes it.", loss="Name and the user's own answers in the copy; the list card does not replace the name placeholder.")

# welcome: kept (config)
# age: back to numpad keyboard
by["age"].update({"type":"keyboard","questionId":"age","numpad":True,"placeholder":"age","title":["How old are you?"],"subtitle":"Your guidance will be tailored to your age group."})
for k in ("options","derive","style"): by["age"].pop(k, None)
setnotes("age", template="keyboard", tag="existing", why="Today's numpad age entry, kept. Reason line is the existing subTitle; the reassurance line is a second subTitle line.", loss="Age bands (web-funnel style).")
setnotes("gender", why="Kept as an added question (Alex, Sep 4). Nothing downstream reads it in the constrained deck yet.", loss="No downstream use without interpolation.")
# hdyhau: scrollableQuestion has no subTitle
by["hdyhau"]["subtitle"] = None; by["hdyhau"]["title"] = ["How did you hear about us?","So we know where to say thanks."]
setnotes("hdyhau", why="Moved early and given the health-professional option (JSON). scrollableQuestion has no subTitle, so the reason line rides as a second headline line.", loss="A proper small reason line under the headline.")
# right_place: no HDYHAU echo
by["right_place"]["body"] = "Balance builds a meditation program around you: a 10-minute session each day, made from your answers and guided by 2 real coaches. Plus a sleep library and single sessions for the moments you need one."
setnotes("right_place", why="Show the product before asking anything personal. textImage takes a headline and an image; the paragraph goes in the Learn More panel.", loss="The friend-referral echo; the body paragraph is behind Learn More.")
# echo beats: static, on goalMeditationPrimer (title kicker, text, subtext)
by["stress_echo"].update({"title":["Most people come to","Balance for exactly this."],"body":"Anxious thoughts, tension and restless nights are how stress shows up for most members. In a survey of 3,700+ members, 77% said they respond to stress better. Your first sessions are built for that."})
setnotes("stress_echo", template="goalMeditationPrimer (title, text, subtext)", tag="unused", why="Static validation beat on the stress branch: kicker, headline, small line.", loss="The user's own words read back.")
by["sleep_echo"].update({"body":"Stress, discomfort and a mind that won't switch off are the usual reasons. 69% of members in our survey reported better sleep, and the first thing your program works on is the wind-down that gets you there."})
setnotes("sleep_echo", template="goalMeditationPrimer (title, text, subtext)", tag="unused", why="Static validation beat on the sleep branch.", loss="The user's own answer read back.")
by["mood_echo"].update({"body":"Whether you recharge alone or with the people you love, your sessions will help you protect that time. 82% of members in our survey feel more emotionally steady."})
setnotes("mood_echo", template="goalMeditationPrimer (title, text, subtext)", tag="unused", why="Static validation beat on the mood branch.", loss="The echoed answer.")
by["focus_echo"].update({"body":"Thoughts, screens, noise, other people: whatever pulls you away, meditation is practice at noticing it and coming back. 78% of members in our survey feel more present and focused."})
setnotes("focus_echo", template="goalMeditationPrimer (title, text, subtext)", tag="unused", why="Static validation beat on the focus branch.", loss="The echoed answer.")
# recaps: static list per goal
static_recap("stress_recap", ["Stress that shows up in your thoughts, body or sleep","The pressure behind it: money, work, health or relationships",{"text":"Better sleep matters to you too","when":"a.goal_sleep==='yes'"}], "Your first sessions start right there.")
static_recap("sleep_recap", ["What keeps you up at night","How long it takes you to fall asleep",{"text":"Less stress matters to you too","when":"a.goal_stress==='yes'"}], "Your program starts with the wind-down.")
static_recap("mood_recap", ["How often a low mood gets in the way","Who you feel happiest around","What already helps"], "Your first sessions build on that.")
static_recap("focus_recap", ["What pulls your attention away","How hard finishing tasks feels","How often you procrastinate"], "Your first sessions train attention to come back.")
# previews: textImage loses the body paragraph (Learn More)
for cid in ("singles_preview","sleep_library_preview","sleep_preview_b","mood_preview","focus_preview"):
    setnotes(cid, why=by[cid]["notes"]["why"]+" textImage takes a headline and an image asset; the paragraph goes in the Learn More panel.", loss="Body paragraph on screen (behind Learn More).")
# exercise: slider -> question
replace("exercise", {"id":"exercise","type":"question","phase":4,"questionId":"exercise","title":["How often do you","move your body?"],"subtitle":"Exercise, walks, yoga. It all counts.",
  "options":[{"id":"0","text":"Rarely","color":"misty_peach"},{"id":"1","text":"Once or twice a week","color":"papaya_whip"},{"id":"2","text":"A few times a week","color":"mint_green"},{"id":"3","text":"Most days","color":"polar_blue"}],
  "notes":N("question","existing","Same question as a 4-option select. Sliders need a new template.", calmer="#28", loss="The slider interaction and per-stop art.")})
# no_judgment static
by["no_judgment"]["body"] = "Your first sessions run 10 minutes or less, with 5-minute versions for the days that get away from you. No pressure, no streak to protect."
setnotes("no_judgment", template="text", tag="existing", why="De-shaming beat after the lifestyle questions. Static.", loss="The schedule answer read back.")
# proof: split back into ageMetrics + one userReview card
i = [k for k,c in enumerate(C) if c["id"]=="proof"][0]
age_card = {"id":"age_metrics","type":"ageMetrics","phase":5,"kicker":"Did you know?","title":["Balance has helped","<b>{{L.age_count}}</b> people your age","improve mental wellness."],"cite":"As of January 2026.",
  "notes":N("ageMetrics","copy","The age-specific stat, kept as its own card (the template computes the count).", evidence="March B4/B5", fills=["Confirm the January 2026 refresh of the age buckets with Yana"])}
review_card = {"id":"proof","type":"userReview","phase":5,"title":["Members like you","say it works."],"laurels":BADGES,"reviews":REVIEWS[:1],"cite":"Verbatim from the App Store, Sep 2026.","cta":"Continue",
  "notes":N("userReview (one quote + image per card)","unused","One testimonial card. userReview shows a single quote and an asset, so the carousel is one card here (or several cards).", calmer="#33", loss="The combined age-stat headline and the 3-review carousel; badges depend on the asset.")}
C = C[:i] + [age_card, review_card] + C[i+1:]; by = {c["id"]: c for c in C}
# loading: static labels
by["loading"].update({"title":["Building your","program."],"bars":["Your goals","Sleep habits","Routine and schedule","Meditation experience","Choosing your first session"]})
setnotes("loading", template="meditationLoading (upperText/lowerText pairs)", tag="unused", why="Named bars with static labels on the existing personalization-reveal card.", loss="Goal name and first name in the labels (meditationLoading does not replace the name placeholder).")
# profile -> static primer per goal
replace("profile", {"id":"profile","type":"quizResult","phase":5,"kicker":"Your Balance profile","title":["Here's your","starting point."],"scoreLabel":"Starting point","cta":"Continue",
  "profiles":{"stress":{"name":"The Overdrive Mind","body":"Stress that runs in the background all day, with a mind that rarely gets to idle.","insight":"Week 1 is short sessions that teach your mind how to settle."},
              "sleep":{"name":"The Wired and Tired","body":"Ready for rest before your mind is.","insight":"Week 1 starts with the wind-down, then works on the stress underneath it."},
              "mood":{"name":"The Weather Watcher","body":"A mood that moves with the day.","insight":"Week 1 is short check-ins that notice what you feel before it takes over."},
              "focus":{"name":"The Open Browser","body":"Attention that keeps opening new tabs.","insight":"Week 1 trains it to come back in sessions short enough to finish."}},
  "cite":"Based on your goal. Not a clinical assessment.",
  "notes":N("goalMeditationPrimer (static per goal)","unused","Named profile per goal branch: kicker, profile name as the text, insight as the subtext. quizResult is not a profile template (it scores a quiz), so the primer card carries it.", calmer="#37", evidence="Round 2 A4", loss="Answer-derived sub-scores, the score number, and the experience/schedule echo.", fills=["Profile names: content pass"])})
setnotes("chart", template="textImage (static chart image per goal)", tag="unused", why="The same graph as a baked image per goal branch fits textImage. The prototype draws it live; production ships 4 images.", loss="Nothing visible; the curve is illustrative either way.")
# comparison: one static list per goal
by["comparison"].update({"title":["What changes","with Balance."],"without":[],"with_":[{"text":"Calmer nights and deeper sleep","when":"a.goal_sleep==='yes'"},{"text":"A steadier response to stress","when":"a.goal_1==='stress'"},{"text":"A steadier mood through the day","when":"a.goal_1==='mood'"},{"text":"Attention that comes back","when":"a.goal_1==='focus'"},{"text":"A 10-minute session built for you, every day"},{"text":"Every word recorded by a real person"}]})
setnotes("comparison", template="list (static per goal)", tag="unused", why="One static list per goal branch (the list card is single-column). The paywall intro screen going live next week carries the two-column framing.", loss="The two columns and the user's own 'look forward to' picks.")
for o in by["commitment"]["options"]: o.pop("praise", None)
setnotes("commitment", template="question", tag="existing", why="Plain single-select; the praise ladder needs per-answer copy the template does not do.", loss="The praise line after selection.")
by["push"].update({"title":["Get a daily reminder to","meet your goals"],"body":"Reminders help you build better habits."})
setnotes("push", why="Existing OS permission wrapper with a real number in the subtext. One shared copy instead of a per-track echo.")
by["program_ready"].update({"title":["Your program is","ready, {{a.name}}."],"body":"Your first session is 10 minutes with Ofosu, built around your top goal. It's waiting on your Today screen."})
setnotes("program_ready", template="Swift program-ready card (copy)", tag="swift", why="Existing program-ready card with new copy and the name. No 'free'-led framing.", loss="Goal and 'look forward to' echo.")
sign = by["signup"]; sign.pop("branch", None); sign.update({"title":["Create an account to","save your program."],"body":"Your program follows you across devices."})
setnotes("signup", template="Swift auth bookend", tag="existing", why="Sign-up stays before the paywall, as today.", loss="Sign-up after the trial starts (wish list).")
order = [c["id"] for c in C]; su = C.pop(order.index("signup")); C.insert([c["id"] for c in C].index("paywall"), su); by = {c["id"]: c for c in C}
by["end"].update({"note":"This is the constrained version: only card templates that exist in the app today, the current goal-1 branching kept intact, new questions allowed. Every screen here is a session.json content change except the paywall (Superwall), program-ready and sign-up (Swift)."})
CONS = {"id":"constrained","name":"Constrained","description":"The same spine built only from card templates that exist in the app today (in use or built-but-unused), with today's branching kept intact and new questions allowed. Interpolation (except the name on text cards), sliders, the computed profile, the two-column outcomes card and the step counter are cut; what each cut loses is recorded per screen.",
        "cards": C}

# ---------------- lint ----------------
def lint(deck, constrained=False):
    errs=[]; ids=set()
    for c in deck["cards"]:
        if c["id"] in ids: errs.append(f"dup id {c['id']}")
        ids.add(c["id"])
        if "notes" not in c: errs.append(f"{c['id']}: no notes")
        blob=json.dumps({k:v for k,v in c.items() if k not in ("notes","branch")})
        if constrained:
            if c["type"] not in ALLOWED: errs.append(f"{c['id']}: type {c['type']} not allowed in constrained")
            toks=re.findall(r"\{\{([^}]+)\}\}", blob)
            bad=[t for t in toks if not (t.strip()=="a.name" and c["type"] in NAME_OK) and not (t.strip()=="L.age_count" and c["type"]=="ageMetrics")]
            if bad: errs.append(f"{c['id']}: interpolation in constrained deck: {bad[:2]}")
            if c["type"]=="question" and len(c.get("options",[]))>6: errs.append(f"{c['id']}: >6 options on a standard select")
            if c["notes"].get("tag")=="new": errs.append(f"{c['id']}: tagged new in constrained deck")
        if c["type"] in ("question","scrollableQuestion","multiselect","keyboard","slider","commitment") and not (c.get("subtitle") or c.get("kicker") or (c["type"]=="scrollableQuestion" and len(c.get("title",[]))>1)):
            errs.append(f"{c['id']}: question without a reason line")
        if c["id"] in ("age","focus_adhd","first_name","gender") and not c.get("reassure"):
            errs.append(f"{c['id']}: sensitive ask without a reassurance line")
        for k in ("title","subtitle","body"):
            v=c.get(k); s=" ".join(v) if isinstance(v,list) else (v or "")
            if "—" in s or "–" in s: errs.append(f"{c['id']}: dash in {k}")
            if re.search(r"\bAI\b", s): errs.append(f"{c['id']}: 'AI' in {k}")
    return errs

ok=True
for deck, cons in ((WISH, False), (CONS, True)):
    for c in deck["cards"]:
        if "with_" in c: c["with"] = c.pop("with_")
    e = lint(deck, cons)
    print(f"{deck['id']}: {len(deck['cards'])} cards, lint {'OK' if not e else 'FAIL'}")
    for x in e: print("   -", x)
    ok = ok and not e
    json.dump(deck, open(os.path.join(ROOT,"decks",deck["id"]+".json"),"w"), indent=1, ensure_ascii=False)
sys.exit(0 if ok else 1)
