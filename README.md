# Balance onboarding prototypes

Competitor onboarding flows rebuilt in Balance's skin, from welcome to today's paywall, two versions each. Built Sep 4, 2026 for the Balance top-of-funnel bet; revised Sep 5 on Alex's screen-by-screen review. The flows and their cost estimates were drafted with Claude and have not had an engineering review.

- **Calmer's flow**: `index.html` (`#/wishlist`, `#/constrained`). The quiz-funnel reference, built from Alex's talk-over of the Calmer recording. This is the one under review.
- **Insight Timer's flow**: `insight-timer.html` (`#/it_wishlist`, `#/it_constrained`). The proof-density reference, built from the Insight Timer teardown without a talk-over. Unreviewed, kept on its own page so feedback on the Calmer flow lands first.

For each base:

- **Wish list**: the flow as we'd build it with no template limits.
- **Constrained**: the same spine using only card templates that exist in the app today, with the current goal-1 branching kept intact and new questions allowed.

Open over HTTP (`python3 -m http.server`) or the GitHub Pages URL. `?why=1` shows the idea behind each screen (for content design and marketing), `?notes=1` shows build notes (template, cost tag, competitor reference, evidence, things to verify); both can be on at once. `#/map/<deck>` is the screen-by-screen spec view. The landing page's "Start the review" button opens the wish list in Why mode, which is the path reviewers should take.

## How it's built

The real Balance onboarding is a JSON card array (`hoth/assets/onboarding/config/session.json`) read by a Lua card engine, with per-card branch predicates. This prototype copies that shape: `decks/*.json` are card arrays with `branch` expressions, rendered by `engine.js`. Every card carries `notes` with the production template it maps to and a cost tag.

One builder per base: `tools/build_decks.py` (Calmer) and `tools/build_decks_it.py` (Insight Timer). Each authors its wish list and derives its constrained deck by explicit overrides, so the whittle is visible in one place. `tools/decklib.py` holds what they share: the note helper, the sourced proof constants, the principles glossary, the lint (template allowlist, 6-option cap, no answers written into copy in the constrained deck, reason line on every question, reassurance beside sensitive asks, no dashes, no "AI"), the `copy/edits.json` applier and the write step. `decks/index.json` and `decks/index-it.json` are the two landing-page manifests. `tools/build_spec.py` and `tools/build_spec_it.py` regenerate the spec docs in the context directory.

Fonts: Work Sans stands in for Graphik (licensed font kept out of a public repo). Colors and layout from the kamino design system. Icons and goal art are frame-crops from the Aug 16 recordings. Coach photos are the in-app thumbnails.

## Editing the copy

Open the site with `?edit=1`. Every line of copy on a screen becomes editable in place (dashed outline; amber outline means the line is personalized and built from an expression). Taps stop navigating; the bar at the bottom moves you back and forward. Edits save on your device as you go. **Export** hands back `edits.json`; save it as `copy/edits.json` in this repo (or send it to Alex) and the next build applies it last, so those edits always win. A personalized line edited without its `{{ }}` tokens becomes fixed text, and the build says so.

Copy in [brackets] is a placeholder to verify before anything ships.
