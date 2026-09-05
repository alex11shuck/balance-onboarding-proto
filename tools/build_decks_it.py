#!/usr/bin/env python3
"""Builds decks/it_wishlist.json and decks/it_constrained.json: Insight Timer's onboarding flow in Balance's skin.
Same shape as build_decks.py (Calmer): the wish list is authored below, the constrained deck is derived from it so the whittle is
visible in one place, and both go through decklib's lint, copy/edits.json applier and writer.

Base: the Insight Timer teardown (competitors/insighttimer-2026-08-12.md, 26 screens, Aug 12 recording). No talk-over exists for
this base; Alex's standing directives from the Calmer talk-over that are not Calmer-specific are carried (keep the goal screens,
stop at today's paywall, never 'Balance Premium', laurels, no chatbot companion, sign-up after the trial in the wish list, the
decided Meet-the-coaches screen), plus the round-2 reads on the Insight Timer arm (P1, P5, P9, P10, P11, P23).

What the constrained version keeps that the wish list drops: today's goal-1 question blocks and the three reminder tracks
(constraint #2: only add screens, keep the core branching). The wish list follows Insight Timer's architecture instead:
preferences and proof, no symptom diagnostics."""
import json, copy, re, sys, os
from decklib import *

STRESS = "a.goal_1==='stress'"; SLEEP1 = "a.goal_1==='sleep'"; MOOD = "a.goal_1==='mood'"; FOCUS = "a.goal_1==='focus'"
SLEEP_ANY = "a.goal_sleep==='yes'"; SLEEP_ANY_NOT_FIRST = "a.goal_sleep==='yes' && a.goal_1!=='sleep'"; NO_SLEEP = "a.goal_sleep!=='yes'"
KIDS = "(a.who_for||[]).includes('kids')"
WP = "Balance whitepaper, Personalization Pays Off, 2025 (survey of 3,700+ members)."
SOURCES = ("<b>Balance whitepaper, 2025.</b> Personalization Pays Off: a survey of more than 3,700 adult Balance members. 85% reported improved mental and emotional well-being, 82% feel more emotionally steady, 78% more present and focused, 77% respond to stress better, 69% better sleep, 86% a stronger sense of progress.<br><br>"
           "<b>Goyal et al., JAMA Internal Medicine, 2014.</b> Meta-analysis of 47 randomized trials, 3,500+ participants: mindfulness programs produce moderate, measurable improvements in anxiety, depression and pain.<br><br>"
           "<b>Galante et al., Nature Mental Health, 2023.</b> Mindfulness programs reduce psychological distress in general adult populations, not only clinical ones.<br><br>"
           "Curves on these screens are illustrative. Results vary from person to person. Balance is not a substitute for professional care.")

IT_PRINCIPLES = {k: PRINCIPLES[k] for k in ["arrival","proof-early","payoff","echo","sourced","felt-value","humans","reassure","no-deficit","commit","keep-what-works","voice","trial-anxiety"]}
IT_PRINCIPLES.update({
 "proof-density": {"name":"Proof density","text":"Insight Timer places proof 5 times before the paywall; Balance places it once. Numbers, faces and what is inside are spread across the flow, each with a source, so trust is built in layers rather than at the commit moment.","source":"Synthesis #3 (5 placements vs our 1); round 2: 4 of 5 Insight Timer testers named the statistics unprompted; March A3"},
 "interests": {"name":"Interests, not diagnoses","text":"Ask what the user wants and would use, not what is wrong with them. Insight Timer's flow can be completed without admitting a single problem, and its topic chips read as interests.","source":"Synthesis #9 (deficit-free framing); Megan's takeaways (Insight Timer, Happier); Insight Timer #6 and #8"},
 "dosage": {"name":"Lower the ask before you make it","text":"Show that a small daily dose is enough immediately before asking how much time the user will give. The chart makes the next question feel small.","source":"Insight Timer #16 to #17 (dosage chart placed right before the daily-minutes question)"},
 "plan-artifact": {"name":"A plan, not a spinner","text":"Replace loading theater with the user's own answers assembled into a first week. The plan is the visible payoff for every question asked.","source":"Insight Timer #20 (plan summary: answers animate in as checked chips); Happier's plan summary; synthesis headline finding (a plan artifact is one of the four substitutes for felt value)"}})

W = []
def add(**c): W.append(c); return c

# ---------------- Part 1: Welcome (Insight Timer #1 to #4: quiet welcome, then two proof screens before any question) ----------------
add(id="welcome", type="welcome", phase=1, longTitleOK=True, title=["Less stress. Better sleep.","Adapted to <b>you</b>."], laurels=BADGES, cta="Continue",
    sub="Already have an account? <span class='link'>Log in</span>",
    notes=N("welcome (remote config)","copy","Insight Timer opens quiet: a live 'here today' counter under the logo and a quote, no marketing copy, no CTA. Balance keeps the headline winning the live welcome test and the 3 text badges. The live counter needs a daily-active feed the deck has no source for today, so that line is out rather than invented.",
      ref="Insight Timer #2 (welcome: '543,857 here today' + quote)", evidence="ABCD test b_benefit; March A3 (store listing and awards were the strongest pre-app trust signal); proof-facts: only 'Trusted by millions' is a sourced member claim",
      fills=["A live member counter needs a DAU feed and a new template; decide whether it is worth pursuing","Badges are text-only on purpose (Apple rejected a laurel with its logo in 2022); rating and count pulled Sep 4, 2026"]))
add(id="outcome_donut", type="donut", phase=1, tap=True, pct=85, kicker="Trusted by millions of adults", title=["85 of every 100 members","feel better."],
    body="In a 2025 survey of more than 3,700 Balance members, 85% reported improved mental and emotional well-being, and 82% said they feel more emotionally steady.",
    cite=WP, learnMore=SOURCES,
    notes=N("pieChart (built, unused)","unused","Insight Timer's real start gate is a market-share donut that names Calm and Headspace on screen ('more time is spent here than on all other wellbeing apps. Combined.'). Balance cannot claim time-spent share, so the same donut carries a sourced outcome number. The pieChart card exists in the engine and is unused in today's deck.",
      ref="Insight Timer #3 (market-share donut, CTA 'Join 36 Million People')", evidence="Synthesis #3 (proof density); teardown: 'ours must lean on outcome stats instead'; whitepaper 2025",
      fills=["pieChart card: confirm its config shape and whether it animates (Matheus)"]))
add(id="library", type="chips", phase=1, title=["Everything inside,","made by 2 people."],
    chips=[{"n":"400+","text":"meditations"},{"n":"[N]","text":"sleep stories"},{"text":"Music and soundscapes"},{"text":"Breathing exercises"},{"text":"Singles for hard moments"},{"n":"2","text":"coaches, every word recorded by hand"}],
    body="A 10-minute session built for you each day, plus a sleep library and Singles for the moment you need one.", cta="Continue",
    notes=N("list (icon, title, subtitle rows)","new","Insight Timer's second proof screen: 7 library-scale chips stagger in ('301k Meditations / 26k Meditation Teachers / 1M Playlists'). Balance cannot win a raw-scale contest, so the same screen sells depth and turns the 2-coach roster into the feature. The stagger animation is new; the static rows are the list template in use today.",
      ref="Insight Timer #4 (library-scale chips)", evidence="Synthesis #10 (content breadth: Balance names 400+ meditations once, on the paywall); coaches angle 3 (small roster as consistency)",
      fills=["Catalog counts: meditations and sleep stories (the paywall says 400+; confirm with content)","Session length: confirm with Anna"]))
add(id="coaches", type="coaches", phase=1, title=["Meet Ofosu and Leah,","your coaches."], subtitle="You'll hear the same 2 voices every day.",
    bios=[{"name":"Ofosu","text":"Has taught meditation for over 20 years, including at the Insight Meditation Society and Spirit Rock."},{"name":"Leah","text":"Brings neuroscience, psychology and her own practice to every session. Has taught in 16+ countries."}],
    body="Every session is written and recorded by the 2 of them. No rotating narrators, no library to sort through. Switch between them anytime.", cta="Continue",
    notes=N("list (2 items with image, title, subtitle)","unused","The decided 'made by humans' screen (angle 1), placed where Insight Timer puts its teacher-count chip. Insight Timer sells 26,000 teachers; Balance inverts scale into consistency and faces. Showcase, not chooser; no 'AI' in the copy.",
      ref="Insight Timer #4 ('26k Meditation Teachers')", evidence="handcrafted-coaches-screen-angles.md (angle 1 chosen Sep 4, angle 3 framing); Marisa's Reddit read: users want one voice to attach to; round 2 P20 objected to instructor voice on Happier",
      fills=["Bios trimmed from the approved website bios; Cindy to confirm the one-liners","Headline register against the rest of the flow"]))

# ---------------- Part 2: About you (Insight Timer #5 to #10 plus HDYHAU) ----------------
add(id="who_for", type="multiselect", phase=2, questionId="who_for", title=["Who is Balance for?"], subtitle="Select all that apply. It shapes what we show you.",
    options=[{"id":"myself","text":"Myself","color":"polar_blue"},{"id":"kids","text":"My kids","color":"papaya_whip"},{"id":"someone","text":"Someone I care for","color":"mint_green"}],
    notes=N("multiselect","existing","Insight Timer's first question ('Who are you here to support? Myself / My kids / My clients', select all that apply). Balance has parent content, so 'My kids' routes to the existing parent-content proof card; the clinician option is out because Balance has no offering for it. Replaces the age-gated 'Are you a parent?' question.",
      ref="Insight Timer #5 (who is this for)", evidence="Deck map cards 15 to 16 (areYouCaregiver, testParentContentProof); round 2 P20 (a therapist screening apps for clients) shows the segment exists"))
add(id="parent_content", type="list", phase=2, branch=KIDS, title=["With Balance, you","and your kids get:"],
    items=[{"title":"Support for parents","subtitle":"Sessions for the hard days","color":"papaya_whip","icon":"🤍"},{"title":"Better bedtime habits","subtitle":"Wind-downs for the whole house","color":"polar_blue","icon":"🌙"},{"title":"Meditations to do together","subtitle":"Short and playful, made for kids","color":"mint_green","icon":"✦"}],
    cta="Continue",
    notes=N("list (testParentContentProof)","copy","Today's parent-content proof card ('With Balance, you get:'), fired by the who-for answer instead of the age gate plus a Yes. Proof placed right after the ask that earned it.",
      ref="Insight Timer #5 ('My kids')", evidence="Deck map card 16", fills=["Subtitles: confirm against the parent content that exists today"]))
add(id="goals", type="goalRanking", phase=2, title=["Select the goals that","matter to you."], rankTitle=["Now select each goal","in order of importance."],
    notes=N("goalRanking","existing","Kept exactly as today, per Alex. Insight Timer's version is 'Select topics of interest, choose up to 3' from 11 interest chips; Balance's goal tiles are the same ask and already read as interests rather than problems.",
      ref="Insight Timer #6 (topics of interest, 'choose up to 3')", evidence="Alex 4:35 (Calmer talk-over: keep the goal screens as they exist); synthesis #9"))
add(id="goals_metrics", type="goalsMetrics", phase=2, title=["Here's what our","members are saying:"], metrics=[{"goal":"stress","text":"77% respond to stress better"},{"goal":"mood","text":"82% feel more emotionally steady"},{"goal":"sleep","text":"69% report better sleep"},{"goal":"focus","text":"78% feel more present and focused"}],
    disclaimer=["From a 2025 survey of more than","3,700 Balance members."],
    notes=N("goalsMetrics","copy","Existing card with sourced, dated numbers from the whitepaper, kept right after the goal pick. In Insight Timer's flow this is where the first benefit interstitials sit: proof follows the interest ask.",
      ref="Insight Timer #11 to #13 (benefit interstitials after the interest asks)", evidence="March B4/B5 (sourced, age-specific stats were the strongest confidence builder); today's 95/92/82/75 line has no locatable source"))
add(id="sleep_ready", type="question", phase=2, branch=SLEEP1, questionId="ready_to_sleep", title=["Do you need help falling","asleep right now?"], subtitle="If yes, your first session is a Sleep Single tonight.",
    options=[{"id":"yes","text":"Yes, I'm ready to sleep","color":"polar_blue"},{"id":"no","text":"No, I'm not ready for sleep","color":"purple_haze"}],
    notes=N("question","existing","Kept verbatim. Routes the post-onboarding destination (Sleep Single vs Plan) on the native side. Insight Timer has no equivalent because it has no program to route into.", evidence="Deck map block 5"))
add(id="experience", type="question", phase=2, questionId="has_meditated_before", title=["Do you have","meditation experience?"], subtitle="Your first sessions match your level.", options=MEDEXP,
    notes=N("question","copy","Insight Timer asks it third, in 3 plain rows that auto-advance on tap. Balance's 4 existing options do the same; one shared version with a reason line instead of 4 goal-specific copies.",
      ref="Insight Timer #7 (meditation experience)", evidence="Deck map card 17"))
add(id="content", type="multiselect", phase=2, questionId="content", allId="all", title=["Which of these","would you use?"], subtitle="Select all that apply. Your Today screen starts with them.",
    options=[{"id":"guided","text":"Guided meditations","color":"polar_blue"},{"id":"sleep_content","text":"Sleep meditations and stories","color":"purple_haze"},{"id":"music","text":"Music and soundscapes","color":"mint_green"},{"id":"breathing","text":"Breathing exercises","color":"papaya_whip"},{"id":"singles","text":"Singles for tough moments","color":"misty_peach"},{"id":"all","text":"All of the above","color":"apricot"}],
    notes=N("multiselect","existing","Insight Timer's content-interest ask ('What sort of content interests you?', 9 chips with an 'All of the above' that selects everything). Interests, not symptoms: the user can finish this block without naming a problem. The picks come back on the plan summary.",
      ref="Insight Timer #8 (content interests, 'All of the above')", evidence="Synthesis #9 (deficit-free framing); Megan's takeaways; content-breadth gap (#10)",
      fills=["'All of the above' selecting every row is a template nicety; as a plain sixth option it is JSON","Confirm the 5 content categories against the catalog"]))
add(id="age", type="keyboard", phase=2, questionId="age", numpad=True, placeholder="age", title=["How old are you?"], subtitle="Your guidance will be tailored to your age group.", reassure="Used only to tune your program. Never shown to anyone.",
    notes=N("keyboard","existing","Today's numpad age entry with its existing reason line and a new reassurance line (the deck has none anywhere). Insight Timer scrolls a birth-year wheel from 2026, which adds nothing the numpad lacks.",
      ref="Insight Timer #9 (birth-year wheel)", evidence="Benchmark rule 4 (specific reassurance); 78% of the vertical asks age"))
add(id="age_metrics", type="ageMetrics", phase=2, kicker="Did you know?", title=["Balance has helped","<b>{{L.age_count}}</b> people your age."], cite="As of January 2026.",
    notes=N("ageMetrics","existing","Today's age-specific count, the single most effective confidence builder in the March study, kept right after the age ask so the ask pays back within one screen. Insight Timer has no equivalent; this is Balance's own proof placement.",
      evidence="March B4/B5 (12 of 18 testers)", fills=["Confirm the January 2026 refresh of the age buckets with Yana"]))
add(id="gender", type="question", phase=2, questionId="gender", title=["How do you identify?"], subtitle="Optional. It helps us personalize your recommendations.", reassure="Optional, and never shown anywhere.",
    options=[{"id":"woman","text":"Woman","color":"polar_blue"},{"id":"man","text":"Man","color":"mint_green"},{"id":"nonbinary","text":"Non-binary","color":"papaya_whip"},{"id":"prefer_not","text":"Prefer not to say","color":"purple_haze"}],
    notes=N("question","existing","Insight Timer asks 'Which gender best describes you? This will help us personalize your recommendations' with Male / Female / Other / Prefer not to say. Kept as an optional question (Alex kept it in both Calmer decks, Sep 4); nothing downstream echoes it.",
      ref="Insight Timer #10 (gender)", evidence="Alex, Sep 4; round 2 P6 read Calmer's gendered copy as generic"))
add(id="hdyhau", type="scrollableQuestion", phase=2, questionId="hdyhau", title=["How did you find us?"], noReason=True,
    options=[{"id":"app_or_play_store","text":"App Store"},{"id":"mobile_game","text":"Mobile game"},{"id":"facebook_or_instagram","text":"Facebook or Instagram"},{"id":"search_engine","text":"Search engine"},{"id":"elevate_or_spark","text":"Elevate or Spark"},{"id":"family_and_friends","text":"Family and friends"},{"id":"tiktok","text":"TikTok"},{"id":"health_professional","text":"Health professional"},{"id":"chatbot","text":"ChatGPT or another assistant"},{"id":"other","text":"Other"}],
    subAnswer={"id":"not_sure","text":"Not sure"},
    notes=N("scrollableQuestion","copy","Insight Timer asks it late (after the plan summary, right before the paywall) as a two-level list, and tracks chatbots as a channel. Balance keeps it in the about-you block, away from the paywall, adds the health-professional option Alex wanted and a chatbot option for attribution. The two-level expansion is a new template and is not built here.",
      ref="Insight Timer #21 (two-level HDYHAU with 'AI (ChatGPT, Claude, Gemini, etc.)')", evidence="Matheus: HDYHAU sits too close to the paywall today; synthesis: the chatbot channel is worth adding regardless of this test; Alex 1:52 (referral as proof)",
      fills=["Confirm the two new answer_ids with data (Balance HDYHAU buckets differ from Elevate's)"]))

# ---------------- Part 3: What works (Insight Timer #11 to #17: benefit beats, commitment, goal set, dosage, minutes) ----------------
add(id="benefit_wellbeing", type="benefit", phase=3, tap=True, viz="circles", labels=["Struggling","Low","Okay","Good","Great"], kicker="What members report", title=["Well-being grows with","consistent practice."],
    body="In a 2025 survey of more than 3,700 Balance members, 85% reported improved mental and emotional well-being.", cite=WP+" Illustrative chart.", learnMore=SOURCES,
    notes=N("textImage (static chart image)","new","Insight Timer's first benefit interstitial: 5 circles grow left to right under 'Mood improves with consistent practice', with a research-flavored footnote card. Balance's version carries a sourced number and opens the sources from the card. The grow animation is new; a baked image per card is textImage.",
      ref="Insight Timer #11 (mood circles)", evidence="Synthesis #3; round 2: 4 of 5 Insight Timer testers named the statistics unprompted; P5 asked to see the research"))
add(id="benefit_steady", type="benefit", phase=3, tap=True, viz="line", axis=["Session 1","Session 30"], kicker="What members report", title=["Steadiness builds","session by session."],
    body="82% of members in the same survey said they feel more emotionally steady, and 77% said they respond to stress better.", cite=WP+" Illustrative curve.", learnMore=SOURCES,
    notes=N("textImage (static chart image)","new","Insight Timer's equanimity chart: a line drawing up and right over 'Total Sessions completed'. Same shape, Balance's sourced figures, and no claim about the curve itself.",
      ref="Insight Timer #12 (equanimity line chart)", evidence="Synthesis #3"))
add(id="benefit_consistency", type="benefit", phase=3, tap=True, viz="week", kicker="What members report", title=["Consistency is","what unlocks it."],
    body="A few minutes most days does more than an hour once a week. 86% of members in the survey report a stronger sense of progress.", cite=WP+" [The consistency line needs a source or a content pass.]", learnMore=SOURCES,
    notes=N("textImage (static chart image)","new","Insight Timer's Mon to Sun fill under 'Consistency is the key to unlock these benefits'. Sets up the commitment question that follows it.",
      ref="Insight Timer #13 (consistency week)", fills=["No Balance consistency stat is on record; the first sentence is a plain claim and needs content sign-off or a number"]))
add(id="commitment", type="commitment", phase=3, questionId="commitment_days", title=["How many days in a row","will you practice?"], subtitle="Pick a goal you can keep. Balance tracks it with you.", cta="Set my goal",
    options=[{"id":"3","text":"3 days","sub":"A real start","color":"papaya_whip","praise":"Good. 3 days in a row is where a habit begins."},{"id":"5","text":"5 days","sub":"A working week","color":"mint_green","praise":"Great. 5 days carries you through the week."},{"id":"7","text":"7 days","sub":"A full week","color":"polar_blue","praise":"A full week. Balance will check in with you each day."},{"id":"10","text":"10 days","sub":"A new routine","color":"purple_haze","praise":"Ambitious. Balance will meet you there."}],
    notes=N("question","existing","Insight Timer's commitment device: 'How many days will you look after yourself?' with 3 / 5 / 7 / 10 consecutive days labelled Good / Great / Amazing / Incredible, then echoed on home as 'day 1 of 7'. Round 2's P11 called their question unclear and picked 10 'just for fun', so Balance's version says what the goal is for. Plain single-select; the praise line after selection is per-answer copy the template does not do.",
      ref="Insight Timer #14 (commitment picker with praise ladder)", evidence="Synthesis #4 (cheapest high-leverage steal in the set); round 2 P11"))
add(id="goal_set", type="goalSet", phase=3, title=["Goal set."], body="{{L.commitment_days}} in a row. Balance will track it with you.",
    notes=N("autoAdvanceText","existing","Insight Timer's 1-second full-screen checkmark after the commitment. The auto-advance text card exists in the engine (built for the never-launched auto-advance test).",
      ref="Insight Timer #15 ('Goal Set')", evidence="Deck map card 2 (autoAdvanceGetStarted)"))
add(id="dosage", type="benefit", phase=3, tap=True, viz="area", axis=["5 min","10","15","20","25","30+"], axisLabel="Minutes a day", kicker="Before you pick a length", title=["10 minutes a day","is enough."],
    body="Most of the benefit members report comes from a short daily session. Your sessions run 10 minutes, with 5-minute versions for the days that get away from you.", cite="[Session lengths: confirm with Anna. The curve is illustrative.]", learnMore=SOURCES,
    notes=N("textImage (static chart image)","new","Insight Timer's dosage-lowering chart ('Just 5 min a day is enough to notice improvements in wellbeing', benefit vs daily minutes plateauing after 5), placed immediately before the daily-minutes question so the ask feels small. An ordering trick; nothing new beyond the chart.",
      ref="Insight Timer #16 (dosage chart)", evidence="Teardown: 'lowers the ask before the duration question'",
      fills=["Session length and 5-minute versions: confirm with Anna","No dosage stat on record; the first sentence is a plain claim and needs a number or content sign-off"]))
add(id="minutes", type="commitment", phase=3, questionId="daily_minutes", title=["How long should your","daily session be?"], subtitle="You can change it before any session.", cta="Continue",
    options=[{"id":"5","text":"5 minutes","sub":"For busy days","color":"mint_green","praise":"Short and steady still counts."},{"id":"10","text":"10 minutes","sub":"The standard session","color":"polar_blue","praise":"The length your first sessions are built for."},{"id":"15","text":"15 minutes","sub":"Room to settle in","color":"purple_haze","praise":"Room to settle in before the day starts."}],
    notes=N("question","existing","Insight Timer's daily-minutes question (5 / 10 / 20) with a footnote that appears only after selecting 10 ('See further improvements to mood & resilience'): praise the choice you want more of. Balance's version reinforces the pick without an outcome claim. The conditional footnote is per-answer copy.",
      ref="Insight Timer #17 (daily minutes with dynamic footnote)", fills=["Which session lengths Balance offers in the Plan: confirm"]))

# ---------------- Part 4: Your routine (Insight Timer #18 to #19: time of day straight into the push ask) ----------------
add(id="when", type="question", phase=4, questionId="when_to_meditate", title=["When would you","like to practice?"], subtitle="We'll suggest sessions around it.",
    options=[{"id":"morning","text":"Morning","color":"papaya_whip","icon":"🌅"},{"id":"afternoon","text":"Afternoon","color":"mint_green","icon":"☀️"},{"id":"evening","text":"Evening","color":"purple_haze","icon":"🌙"}], subAnswer={"id":"unsure","text":"Not sure"},
    notes=N("question (meditationTime)","copy","Today's 'When would you like to meditate?' card, now asked of everyone (today it skips anyone who picked sleep). Insight Timer runs the same 4 rows with sunrise / sun / moon icons and goes straight into the push ask.",
      ref="Insight Timer #18 (time of day)", evidence="Deck map card 18 (meditationTime)"))
add(id="reminder_time_sleep", type="setReminderTime", phase=4, branch=SLEEP_ANY, questionId="bedtime", title=["What is your","target bedtime?"], subtitle="Going to bed at the same time every night improves sleep quality.", default="10:00 pm", times=["9:00 pm","9:30 pm","10:00 pm","10:30 pm","11:00 pm","11:30 pm"],
    notes=N("setReminderTime","existing","Existing bedtime card for anyone who picked sleep (today it fires only when sleep ranks first, or late for sleep ranked 2 to 4).", evidence="Deck map blocks 5 and 11"))
add(id="reminder_time", type="setReminderTime", phase=4, branch=NO_SLEEP, questionId="reminder_time", title=["When should we","remind you?"], subtitle="A daily nudge {{H.whenPhrase(a)}}.",
    default="{{({morning:'8:00 am',afternoon:'12:00 pm',evening:'6:00 pm'})[a.when_to_meditate]||'6:00 pm'}}", times=["7:00 am","8:00 am","12:00 pm","5:00 pm","6:00 pm","8:00 pm"],
    notes=N("setReminderTime","existing","Existing training-reminder card; the default follows the time-of-day answer, which the template already does (branchable defaults keyed off the answer).", evidence="Deck map card 18 (setReminderTimeNonSleep: morning 8am / afternoon 12pm / evening 6pm)"))
add(id="push", type="pushOptIn", phase=4, questionId="push", title=["Get a reminder at","{{a.goal_sleep==='yes'?'your target bedtime':'your chosen time'}}"], body="{{a.goal_sleep==='yes'?'Reminders help you set a consistent sleep schedule.':'Reminders help you build better habits.'}}", cta="Continue",
    notes=N("pushOptIn","copy","Insight Timer puts the OS dialog over a backdrop that repeats the question, with a hand-drawn arrow pointing at Allow. Balance already ties the ask to the reminder time; the arrow overlay is polish and a new template, low priority. Benchmark rule 8 wants a real opt-in number here; none exists yet, so the line is out.",
      ref="Insight Timer #19 (contextual push with arrow overlay)", evidence="Benchmark rules 7 and 8"))

# ---------------- Part 5: Your plan (Insight Timer #20 to #26: plan summary, outlook, paywall; no account, ever) ----------------
add(id="summary", type="summary", phase=5, kicker="Your first 7 days", title=["Here's your plan,","built from your answers."],
    chips=[{"from":"goals"},{"from":"content","max":2},{"text":"{{L.commitment_days}} in a row","when":"a.commitment_days"},{"text":"{{L.daily_minutes}} a day","when":"a.daily_minutes"},{"text":"{{L.when_to_meditate}} sessions","when":"a.when_to_meditate && a.when_to_meditate!=='unsure'"}],
    body="Balance turns these into a daily session with Ofosu or Leah, and adds sleep content on the nights you need it.", cta="Continue",
    notes=N("meditationLoading (personalization reveal) or new template","new","Insight Timer's plan summary: 'Over the next 7 days, we'll help you build momentum to create lasting change', with the user's own answers animating in as checked chips. It replaces the Creating Program spinner with a plan artifact, so the questions get a visible payoff. Answer playback needs a template; a static per-goal list is the constrained version.",
      ref="Insight Timer #20 (plan summary with answer chips)", evidence="Synthesis #1 (answer echo is the biggest gap vs the field); Alex 5:00 (the recap is 'a major need'); Happier's plan summary"))
add(id="projection", type="chart", phase=5, kicker="Your outlook", title=["By {{H.dateIn(6)}}, this is","where you could be."], weeks=["Today","Week 2","Week 4","Week 6"], withLabel="With Balance", aloneLabel="On your own",
    body="{{H.outcome(a)}} On your own, most people report little change.", cite="Illustrative curve. Survey figures from the Balance whitepaper, 2025. Results vary from person to person.", learnMore=SOURCES, cta="Let's do this",
    notes=N("textImage (static image per goal)","new","Insight Timer's outcome projection: a date 3 months out ('By Nov 12th'), a curve colored from Today to Month 3, and 'it's scientifically proven that you'll be feeling much better'. Balance keeps the date and the curve, drops the proof claim, names the survey figure for the user's top goal, and never says 'Balance Premium'. Round 2's P5 asked to see the research at exactly this screen, so the sources open from the card.",
      ref="Insight Timer #22 (outcome projection, 'By Nov 12th', 'scientifically proven')", evidence="Round 2 P5 unaided O4 ('could I see the research for this?'); Alex 8:35 to 9:00 (the graph is 'so important'; 'with Balance', never 'Balance Premium'); legal note in the teardown",
      fills=["Copy pass against the web funnel's Before / Day 2 / Day 30 timeline"]))
add(id="cytr", type="cytr", phase=5, title=["We'll remind you 2 days","before your trial ends"],
    notes=N("Superwall post_sign_up (trial reminder step)","superwall","Today's Choose-Your-Trial-Reminder screen, kept. Insight Timer's paywall headline is the same promise ('We'll remind you 2 days before your trial ends'); Balance already owns the mechanic as its own step right before the paywall.",
      ref="Insight Timer #23 (reminder-promise headline)", evidence="CYTR +24.7% trial starts (prior art); round 2 A3 (the trial-reminder paywall was praised unprompted)"))
add(id="paywall", type="paywall", phase=5, design="live", headlines={"stress":"Reduce daily stress and anxiety","sleep":"Fall asleep faster, wake up rested","focus":"Sharpen your focus","mood":"Feel steadier every day","default":"Reduce daily stress and anxiety"},
    notes=N("Superwall post_sign_up (live design)","superwall","Terminal screen: today's live paywall, unchanged. Insight Timer's paywall ideas live here as notes for Superwall work, not built: the reminder promise as the headline with a Join / Today / Day 5 / Day 7 timeline, an on-paywall 'How can I cancel?' card with the literal steps, a Free-vs-Plus table, a single SKU with no plan picker, and Skip visible from first paint. The decline off-ramp ('Free / No ads / Forever') is not copied: it only works when the free library is the acquisition engine, and a literal copy would tank Balance trial starts. The transferable part is tone.",
      ref="Insight Timer #23 to #25 (soft paywall, App Store sheet, free off-ramp)", evidence="Alex 10:05 (stop at the paywall); teardown 'adapt, don't copy'; round 2: Insight Timer's decline into the free app was the only in-session resolution of the try-first objection (P9, P11), and P10 could not find the dismiss control",
      fills=["Paywall reviews: Tracy's is the live paywall's own; the other 2 are from our verified set"]))
add(id="signup", type="signup", phase=5, branch="a.paywall==='trial'", title=["Save your program."], body="Create an account so your program follows you across devices and your trial reminder reaches you.", sub="By creating your account, you agree to Balance's Terms and Privacy Policy.",
    notes=N("Swift auth bookend","swift","Insight Timer never creates an account: no email, no SSO, anonymous through home. Balance's trial needs one, so the adaptation is to ask after the trial starts rather than before the paywall. A Swift bookend change and a strategy call, not deck work.",
      ref="Insight Timer #26 (home reached with no sign-up ever)", evidence="Teardown: 'move sign-up after the paywall decision rather than before it, not removal'; benchmark: the deferred account gate is the archetype's norm"))
add(id="end", type="end", title=["Prototype ends here."], body="In the app, a started trial hands off to the first session on the Today screen. A decline shows today's counter-offer, then lands on the Today screen with the program locked.",
    note="This is the wish-list version of Insight Timer's flow: proof and preferences in place of symptom questions, built as if templates were free. The constrained version keeps today's goal-1 question blocks and reminder tracks and inserts Insight Timer's screens around them.",
    notes=N("(prototype only)","existing","End card for reviewers."))

PR = {
 "welcome": (["proof-early","arrival","keep-what-works"], "Screen 1 carries the awards and rating because a newcomer from an ad decides in seconds whether this is a real company. Insight Timer's quiet open is kept in spirit: no pitch, just proof."),
 "outcome_donut": (["proof-density","sourced","arrival"], "Insight Timer's start gate is a proof screen, not a question. Balance's version is one sourced outcome number, large, before anything is asked."),
 "library": (["proof-density","felt-value","humans"], "What is inside, shown as a catalog before the first question, with the 2-coach roster sold as consistency rather than hidden as a small number."),
 "coaches": (["humans","proof-density"], "Faces and first names where Insight Timer puts '26k teachers'. Showcase, not chooser."),
 "who_for": (["interests","payoff"], "The first question is about who the user is here for, not what is wrong with them. The kids answer pays back on the next screen."),
 "parent_content": (["payoff","proof-density"], "Proof for the answer just given, within one screen."),
 "goals": (["keep-what-works","interests"], "The goal screens are unchanged. They test well and everything downstream branches on them."),
 "goals_metrics": (["sourced","proof-density"], "Same card as today, with numbers that have a source and a date."),
 "sleep_ready": (["keep-what-works"], "Existing routing question, kept verbatim."),
 "experience": (["payoff","keep-what-works"], "Existing card with a reason line."),
 "content": (["interests","payoff","echo"], "Asks what the user would use, never what they struggle with. The picks come back on the plan."),
 "age": (["reassure","payoff","sourced"], "Age unlocks the age-specific member count on the next screen, so the ask pays back immediately. The reassurance line says where the answer goes."),
 "age_metrics": (["sourced","proof-density","echo"], "The age-specific stat, March's strongest confidence builder, one screen after the age ask."),
 "gender": (["reassure","no-deficit"], "Optional, with a plain 'Prefer not to say'."),
 "hdyhau": (["arrival","proof-early"], "Asked in the about-you block so it does not sit next to the paywall, with a health-professional referral available as a proof signal."),
 "benefit_wellbeing": (["proof-density","sourced"], "A chart-backed benefit beat between question blocks, with the source on screen and a sources sheet behind it."),
 "benefit_steady": (["proof-density","sourced"], "Second benefit beat: the same survey, the steadiness figures."),
 "benefit_consistency": (["proof-density","commit"], "Sets up the commitment question by making consistency the thing worth committing to."),
 "commitment": (["commit","payoff"], "A consecutive-days goal with a reason line, so the question is clear (round 2's P11 found Insight Timer's version unclear). The praise line rewards the pick."),
 "goal_set": (["commit","echo"], "A 1-second confirmation that says the goal back."),
 "dosage": (["dosage","sourced"], "The chart that makes the next question feel small."),
 "minutes": (["dosage","payoff"], "Asked right after the dosage chart, with a line that reinforces the pick without an outcome claim."),
 "when": (["payoff","keep-what-works"], "Existing card, asked of everyone, feeding the reminder default."),
 "reminder_time_sleep": (["commit","keep-what-works"], "Existing bedtime card."),
 "reminder_time": (["commit","keep-what-works","echo"], "Existing reminder card; the default follows the time-of-day answer."),
 "push": (["commit","payoff","keep-what-works"], "An earned, contextual permission ask."),
 "summary": (["plan-artifact","echo","payoff"], "The user's own answers assembled into a first week, in place of a spinner. This is where the questions pay off."),
 "projection": (["sourced","felt-value","honest-result"], "A dated outlook with the survey figure for the user's top goal, and the research one tap away. No 'scientifically proven'."),
 "cytr": (["trial-anxiety","keep-what-works"], "Says when the reminder comes before asking for the trial."),
 "paywall": (["keep-what-works","trial-anxiety","proof-early"], "Today's live paywall, unchanged."),
 "signup": (["keep-what-works"], "Account creation after the trial in the wish list; before the paywall in the constrained version."),
 # constrained-only cards (today's goal-1 blocks)
 "reminder_time_sleep_early": (["keep-what-works","commit"], "Today's early bedtime card for sleep-first users."),
 "push_sleep_early": (["keep-what-works","commit"], "Today's early push ask for sleep-first users."),
 "stress_1": (["keep-what-works","payoff"], "Today's card with a reason line."), "stress_2": (["keep-what-works","payoff"], "Today's card with a reason line."), "stress_3": (["keep-what-works","payoff"], "Today's card with a reason line."),
 "mood_2": (["keep-what-works","payoff"], "Today's card with a reason line."), "mood_3": (["keep-what-works","no-deficit"], "Today's card with a reason line."),
 "focus_1": (["keep-what-works","payoff"], "Today's card with a reason line."), "focus_2": (["keep-what-works","payoff"], "Today's card with a reason line."), "focus_3": (["keep-what-works","payoff"], "Today's card with a reason line."),
 "focus_adhd": (["reassure","no-deficit","keep-what-works"], "The most sensitive ask in the flow gets a specific line about where the answer goes."), "focus_primer": (["sourced","keep-what-works"], "Existing DID YOU KNOW card with a citation."),
 "sleep_ready_b": (["keep-what-works"], "Today's late routing question for sleep ranked 2 to 4."),
 "sleep_1": (["keep-what-works","payoff"], "Today's card with a reason line."), "sleep_2": (["keep-what-works","payoff"], "Today's card with a reason line."), "sleep_3": (["keep-what-works","payoff"], "Today's card with a reason line."),
 "reminder_time_sleep_late": (["keep-what-works","commit"], "Today's late bedtime card for sleep ranked 2 to 4."), "push_sleep_late": (["keep-what-works","commit"], "Today's late push ask for sleep ranked 2 to 4."),
 "loading": (["keep-what-works"], "Today's Creating Program animation, unchanged."), "program_ready": (["keep-what-works","voice"], "Existing program-ready card with plain copy."),
}
def stamp(cards):
    for c in cards:
        pk, how = PR.get(c["id"], ([], ""))
        if pk and "principles" not in c: c["principles"] = pk
        if how and "how" not in c: c["how"] = how
stamp(W)
WISH = {"id":"it_wishlist","name":"Wish list","pair":"it_constrained","pairName":"constrained","principles":IT_PRINCIPLES,
        "description":"Insight Timer's flow in Balance's skin: proof stacked before the first question, interests instead of diagnoses, chart-backed benefit beats, a consecutive-days commitment with a praise ladder, a dosage-lowering chart before the minutes ask, a plan built from the answers and a dated outlook, then today's paywall. Built as if templates were free.",
        "phases":["Welcome","About you","What works","Your routine","Your plan"], "cards": W}

# ---------------- Constrained: today's flow kept, Insight Timer's screens inserted ----------------
ALLOWED = {"welcome","text","textImage","list","question","scrollableQuestion","multiselect","goalRanking","goalsMetrics","ageMetrics","keyboard","setReminderTime","pushOptIn","userReview","primer","coaches","paywall","signup","end","cytr","legacyLoading","donut","chips","benefit","goalSet","chart"}
STATIC_ONLY = {"donut","chips","benefit","chart"}   # allowed in the constrained deck only as static renderings of pieChart / list / textImage
NAME_OK = {"text","textImage"}
C0 = copy.deepcopy(W); by = {c["id"]: c for c in C0}
def setnotes(cid, **kw): by[cid]["notes"].update(kw)

by["outcome_donut"]["static"] = True
setnotes("outcome_donut", why="Static donut on the pieChart card (built, unused). No animation until the card's config is confirmed.", loss="The draw-in animation.")
by["library"].update({"static":True}); setnotes("library", template="list (icon, title, subtitle rows)", tag="existing", why="Static rows on today's list template (the value-prop card).", loss="The stagger animation.")
by["content"].pop("allId", None); setnotes("content", why="Today's multiselect template with 'All of the above' as a plain sixth option.", loss="'All of the above' selecting every row.")
for cid in ("benefit_wellbeing","benefit_steady","benefit_consistency","dosage"):
    by[cid]["static"] = True; setnotes(cid, tag="unused", why=by[cid]["notes"]["why"]+" Here the chart is a baked image on the textImage card (built, unused); the prototype draws it live.", loss="The grow / draw animation.")
for cid in ("commitment","minutes"):
    for o in by[cid]["options"]: o.pop("praise", None)
    by[cid]["type"] = "question"; by[cid].pop("cta", None)
    setnotes(cid, why=by[cid]["notes"]["why"].split(" Plain single-select")[0].split(" The conditional footnote")[0]+" Plain single-select here.", loss="The praise / footnote line after selection (per-answer copy).")
by["commitment"]["style"] = "compact"
by["goal_set"]["body"] = "Balance will track it with you."; setnotes("goal_set", loss="The goal said back (answers written into the copy).")
by["reminder_time"].update({"subtitle":"A daily nudge for your session.","default":"6:00 pm"})
setnotes("reminder_time", why="Existing training-reminder card. The template keys its default off the time-of-day answer in production; the prototype shows the static default here.", loss="Default time following the answer (production does this; the prototype's constrained deck does not interpolate).")
by["when"]["branch"] = NO_SLEEP; setnotes("when", why="Today's 'When would you like to meditate?' card on today's branch (no sleep goal).", loss="Asking sleep users when they practice.")
by["push"].update({"title":["Get a daily reminder to","meet your goals"],"body":"Reminders help you build better habits.","branch":NO_SLEEP}); setnotes("push", why="Today's non-sleep push ask, copy unchanged.", loss="The per-track echo in the headline.")
by.pop("reminder_time_sleep")   # replaced by today's early + late bedtime tracks below
by["summary"] = {"id":"summary","type":"text","phase":5,"kicker":"Your first 7 days","title":["Here's your plan."],
  "items":[{"text":"A daily session for less stress","when":STRESS},{"text":"A daily session for better sleep","when":SLEEP1},{"text":"A daily session for a steadier mood","when":MOOD},{"text":"A daily session for sharper focus","when":FOCUS},{"text":"Sleep content on the nights you need it","when":SLEEP_ANY_NOT_FIRST},{"text":"A practice goal Balance tracks with you"},{"text":"A reminder at your chosen time"}],
  "body":"Built from your answers. Your first session is with Ofosu.","cta":"Continue",
  "notes":N("list (one card per goal branch)","existing","Static first-week summary on the list template, one card per goal branch. Insight Timer's chips echo the user's own answers; that needs a template.", ref="Insight Timer #20", loss="The user's own picks read back (content, days, minutes, time of day)."),
  "principles":["plan-artifact","payoff"],"how":"A static plan card in place of the answer-echo chips."}
by["projection"].update({"static":True,"title":["Where 6 weeks with","Balance gets you."],"body":"In a 2025 survey of 3,700+ members, 77% said they respond to stress better and 69% reported better sleep. On your own, most people report little change."})
by["projection"].pop("kicker", None); setnotes("projection", tag="unused", template="textImage (static image per goal)", why="The same graph as a baked image per goal branch on textImage. The prototype draws it live; production ships 4 images.", loss="The computed date and the goal-specific figure in the body.")
sign = by["signup"]; sign.pop("branch", None); sign.update({"title":["Create an account to","save your program."],"body":"Your program follows you across devices."})
setnotes("signup", template="Swift auth bookend", tag="existing", why="Sign-up stays before the paywall, as today.", loss="Sign-up after the trial starts (wish list).")
by["end"].update({"note":"This is the constrained version of Insight Timer's flow: today's goal-1 question blocks and reminder tracks kept intact, Insight Timer's screens inserted around them, only card templates that exist in the app today. Every screen here is a session.json content change except the paywall and trial reminder (Superwall), Creating Program, program-ready and sign-up (Swift)."})

# today's cards (deck map, Aug 7 pin), with a reason line each; kept only in the constrained version
TWOWK = "Over the last 2 weeks."
def Q(id, branch, qid, title, subtitle, options, sub=True, **extra):
    c = {"id":id,"type":"question","phase":2,"branch":branch,"questionId":qid,"title":title,"subtitle":subtitle,"options":options}
    if sub: c["subAnswer"] = {"id":"unsure","text":"Not sure"}
    c.update(extra); return c
TODAY = [
 {"id":"reminder_time_sleep_early","type":"setReminderTime","phase":2,"branch":SLEEP1,"questionId":"bedtime","title":["What is your","target bedtime?"],"subtitle":"Going to bed at the same time every night improves sleep quality.","default":"10:00 pm","times":["9:00 pm","9:30 pm","10:00 pm","10:30 pm","11:00 pm","11:30 pm"],
  "notes":N("setReminderTime","existing","Today's early bedtime card (sleep ranked first), kept in its place.", evidence="Deck map block 5")},
 {"id":"push_sleep_early","type":"pushOptIn","phase":2,"branch":SLEEP1,"questionId":"push","title":["Get a reminder at","your target bedtime"],"body":"Reminders help you set a consistent sleep schedule.","cta":"Continue",
  "notes":N("pushOptIn","existing","Today's early push ask for sleep-first users, kept in its place (the benchmark's 'interrupts the sequence' read vs its rule 7; a prototype arm, not a defect).", evidence="Deck map block 5")},
 Q("stress_1", STRESS, "how_often_feel_stress", ["How often do you","feel stressed?"], TWOWK, [{"id":"always","text":"Almost always","color":"misty_peach","icon":"icon-stressed"},{"id":"sometimes","text":"Sometimes","color":"off_yellow","icon":"icon-neutral"},{"id":"rarely","text":"Rarely","color":"purple_haze","icon":"icon-nostress"}], notes=N("question","copy","Today's card with a 2-week window as the reason line.", evidence="Deck map block 6")),
 Q("stress_2", STRESS, "how_experience_stress", ["How do you usually","experience stress?"], "Your sessions focus on what you pick.", [{"id":"anxious_thoughts","text":"Anxious thoughts","color":"mint_green","icon":"icon-thoughts"},{"id":"exhaustion_or_tension","text":"Physical discomfort","color":"misty_peach","icon":"icon-discomfort"},{"id":"moodiness","text":"Moodiness","color":"purple_haze","icon":"icon-moodiness"},{"id":"difficulty_sleeping","text":"Difficulty sleeping","color":"papaya_whip","icon":"icon-difficultysleeping"}], sub=False, notes=N("question","copy","Today's single-select card with a reason line (the Calmer decks make it multi-answer; this deck keeps today's card).", evidence="Deck map block 6; March B2 argues for multi-answer")),
 Q("stress_3", STRESS, "stress_source", ["What's the biggest","source of your stress?"], "Your sessions are matched to it.", [{"id":"money","text":"Money","color":"purple_haze","icon":"icon-money"},{"id":"work_or_school","text":"Work or school","color":"polar_blue","icon":"icon-work"},{"id":"health","text":"Health","color":"mint_green","icon":"icon-health"},{"id":"relationships","text":"Relationships","color":"misty_peach","icon":"icon-people"}], notes=N("question","copy","Today's card plus a reason line.", evidence="Deck map block 6")),
 Q("mood_2", MOOD, "happiest_around", ["Who do you usually","feel happiest around?"], "It shapes the examples in your sessions.", [{"id":"family","text":"Family","color":"papaya_whip"},{"id":"friends","text":"Friends","color":"mint_green"},{"id":"myself","text":"By myself","color":"purple_haze"}], notes=N("question","copy","Today's card plus a reason line.", evidence="Deck map block 7")),
 Q("mood_3", MOOD, "improve_mood", ["What do you usually do","to improve your mood?"], "No wrong answers. We build on what already works.", [{"id":"alone","text":"Spend time alone","color":"purple_haze"},{"id":"talk","text":"Talk to others","color":"polar_blue"},{"id":"distract","text":"Distract myself","color":"papaya_whip"},{"id":"sleep","text":"Sleep on it","color":"mint_green"}], notes=N("question","copy","Today's card plus a reason line.", evidence="Deck map block 7")),
 Q("focus_1", FOCUS, "most_distracting", ["What do you find the","most distracting?"], "Your sessions train attention around it.", [{"id":"thoughts","text":"My thoughts","color":"mint_green","icon":"icon-thoughts"},{"id":"surroundings","text":"My surroundings","color":"papaya_whip"},{"id":"technology","text":"Technology","color":"purple_haze"},{"id":"people","text":"Other people","color":"misty_peach","icon":"icon-people"}], notes=N("question","copy","Today's card plus a reason line.", evidence="Deck map block 8")),
 Q("focus_2", FOCUS, "finishing_tasks", ["Do you have difficulty","finishing tasks?"], TWOWK, [{"id":"always","text":"Almost always","color":"misty_peach"},{"id":"depends","text":"Depends on the task","color":"papaya_whip"},{"id":"rarely","text":"Rarely","color":"purple_haze"}], notes=N("question","copy","Today's card plus the 2-week window.", evidence="Deck map block 8")),
 Q("focus_3", FOCUS, "procrastinate", ["How often do you","procrastinate on work?"], TWOWK, [{"id":"always","text":"Almost always","color":"misty_peach"},{"id":"sometimes","text":"Sometimes","color":"papaya_whip"},{"id":"rarely","text":"Rarely","color":"purple_haze"}], notes=N("question","copy","Today's card plus the 2-week window.", evidence="Deck map block 8")),
 Q("focus_adhd", FOCUS, "has_adhd_or_add", ["Do you have ADD/ADHD?"], "These conditions can affect focus.", [{"id":"yes","text":"Yes","color":"purple_haze"},{"id":"maybe","text":"I think I do","color":"papaya_whip"},{"id":"no","text":"No","color":"misty_peach"},{"id":"not_shared","text":"I prefer not to share","color":"mint_green"}], reassure="Stays in your program. Never shared, never used for anything else.", notes=N("question","copy","Today's card with a specific reassurance line beside the most sensitive ask in the flow.", evidence="Deck map block 8; benchmark rule 4")),
 {"id":"focus_primer","type":"primer","phase":2,"branch":FOCUS,"title":["Meditation can help with","ADHD and ADD symptoms."],"body":"[One line on the study Anna recommends.]","cite":"[Citation]",
  "notes":N("goalMeditationPrimer","copy","Today's DID YOU KNOW card, now with a citation line.", evidence="Deck map block 8; March B5", fills=["ADHD citation from Anna"])},
 Q("sleep_ready_b", SLEEP_ANY_NOT_FIRST, "ready_to_sleep", ["Do you need help falling","asleep right now?"], "If yes, your first session is a Sleep Single tonight.", [{"id":"yes","text":"Yes, I'm ready to sleep","color":"polar_blue"},{"id":"no","text":"No, I'm not ready for sleep","color":"purple_haze"}], sub=False, notes=N("question","existing","Today's late routing question for sleep ranked 2 to 4 (needHelpFallingAsleepOtherGoals).", evidence="Deck map card 9")),
 Q("sleep_1", SLEEP1, "fall_asleep_time", ["How long does it usually","take you to fall asleep?"], TWOWK, [{"id":"0_15","text":"0 to 15 minutes","color":"mint_green"},{"id":"15_30","text":"15 to 30 minutes","color":"papaya_whip"},{"id":"30_plus","text":"30 minutes or more","color":"misty_peach"}], notes=N("question","copy","Today's card with the 2-week window.", evidence="Deck map block 10")),
 Q("sleep_2", SLEEP1, "keep_awake", ["What tends to keep","you awake at night?"], "Your wind-down is matched to it.", [{"id":"stress","text":"Stress","color":"misty_peach","icon":"icon-stress"},{"id":"discomfort","text":"Discomfort","color":"mint_green","icon":"icon-pain"},{"id":"noise","text":"Noise","color":"papaya_whip","icon":"icon-noise"},{"id":"cant_fall_asleep","text":"Just can't fall asleep","color":"purple_haze","icon":"icon-sleep"}], sub=False, notes=N("question","copy","Today's single-select card plus a reason line.", evidence="Deck map block 10")),
 Q("sleep_3", SLEEP1, "chronotype", ["Morning person or","night person?"], "It sets when Balance suggests your sessions.", [{"id":"morning","text":"Morning person","color":"papaya_whip","icon":"icon-morningperson"},{"id":"night","text":"Night person","color":"purple_haze","icon":"icon-nightperson"},{"id":"both","text":"A bit of both","color":"polar_blue","icon":"icon-both"}], notes=N("question","copy","Today's card plus a reason line.", evidence="Deck map block 10")),
 {"id":"reminder_time_sleep_late","type":"setReminderTime","phase":4,"branch":SLEEP_ANY_NOT_FIRST,"questionId":"bedtime","title":["What is your","target bedtime?"],"subtitle":"Going to bed at the same time every night improves sleep quality.","default":"10:00 pm","times":["9:00 pm","9:30 pm","10:00 pm","10:30 pm","11:00 pm","11:30 pm"],
  "notes":N("setReminderTime","existing","Today's late bedtime card for sleep ranked 2 to 4 (OfferSleepHelp track), kept in its place.", evidence="Deck map block 11")},
 {"id":"push_sleep_late","type":"pushOptIn","phase":4,"branch":SLEEP_ANY_NOT_FIRST,"questionId":"push","title":["Get a reminder at","your target bedtime"],"body":"Reminders help you set a consistent sleep schedule.","cta":"Continue",
  "notes":N("pushOptIn","existing","Today's late push ask for sleep ranked 2 to 4, kept in its place.", evidence="Deck map block 11")},
 {"id":"loading","type":"legacyLoading","phase":5,"title":["Creating program"],"texts":["your goals…","your experience…","your preferences…","your age…"],
  "notes":N("Swift Creating Program screen (Lottie)","existing","Today's Creating Program animation and copy, unchanged. Insight Timer has no spinner; its plan summary follows here as an added card.", ref="Insight Timer #20 (no fake progress bar)")},
 {"id":"program_ready","type":"text","phase":5,"title":["Your Plan is ready."],"body":"Your first session is 10 minutes with Ofosu, built around your top goal. You'll find it on your Today screen.","cta":"Continue",
  "notes":N("Swift program-ready card (copy)","swift","Existing program-ready card with plain copy and no 'free'-led framing at the commit moment.", evidence="March H3")},
]
for c in TODAY: by[c["id"]] = c
stamp(list(by.values()))
ORDER = ["welcome","outcome_donut","library","coaches",
         "who_for","parent_content","goals","goals_metrics",
         "sleep_ready","reminder_time_sleep_early","push_sleep_early",
         "stress_1","stress_2","stress_3","mood_2","mood_3","focus_1","focus_2","focus_3","focus_adhd","focus_primer",
         "sleep_ready_b","sleep_1","sleep_2","sleep_3",
         "experience","content","age","age_metrics","gender","hdyhau",
         "benefit_wellbeing","benefit_steady","benefit_consistency","commitment","goal_set","dosage","minutes",
         "when","reminder_time","push","reminder_time_sleep_late","push_sleep_late",
         "loading","summary","program_ready","signup","projection","cytr","paywall","end"]
missing = [i for i in ORDER if i not in by]; assert not missing, missing
unused = [i for i in by if i not in ORDER]; assert not unused, unused
C = [by[i] for i in ORDER]
CONS = {"id":"it_constrained","name":"Constrained","pair":"it_wishlist","pairName":"wish list","principles":IT_PRINCIPLES,
        "description":"Today's flow kept intact (goal-1 question blocks, three reminder tracks, Creating Program, account before the paywall) with Insight Timer's screens inserted around it, using only card templates that exist in the app today. Animations, the answer-echo plan and the dated outlook become static cards; what each cut loses is recorded per screen.",
        "phases":["Welcome","About you","What works","Your routine","Your plan"], "cards": C}

# extra lint: static-only types must be static in the constrained deck
errs = [c["id"] for c in C if c["type"] in STATIC_ONLY and not c.get("static")]
if errs: print("constrained: non-static chart types:", errs); sys.exit(1)
sys.exit(0 if finish([(WISH, False), (CONS, True)], ALLOWED, NAME_OK) else 1)
