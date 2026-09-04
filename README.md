# Balance onboarding prototype

Two clickable versions of a Calmer-style onboarding flow in Balance's skin, from welcome to today's paywall. Built Sep 4, 2026 for the Balance top-of-funnel bet.

- **Wish list**: the flow as we'd build it with no template limits.
- **Constrained**: the same spine using only card templates that exist in the app today, with the current goal-1 branching kept intact and new questions allowed.

Open `index.html` over HTTP (`python3 -m http.server`) or the GitHub Pages URL. Add `?notes=1` to see build notes per screen (template, feasibility tag, Calmer reference, evidence, things to verify) and `?why=1` for the principles behind each screen (for content design and marketing); both can be on at once. `#/map/wishlist` and `#/map/constrained` are the screen-by-screen spec views.

## How it's built

The real Balance onboarding is a JSON card array (`hoth/assets/onboarding/config/session.json`) read by a Lua card engine, with per-card branch predicates. This prototype copies that shape: `decks/*.json` are card arrays with `branch` expressions, rendered by `engine.js`. Every card carries `notes` with the production template it maps to and a cost tag.

`tools/build_decks.py` is the single source: it authors the wish list, derives the constrained deck by explicit overrides (so the whittle is visible in one place), and lints both (template allowlist, 6-option cap, no interpolation in the constrained deck, reason line on every question, reassurance beside sensitive asks, no dashes, no "AI").

Fonts: Work Sans stands in for Graphik (licensed font kept out of a public repo). Colors and layout from the kamino design system. Icons and goal art are frame-crops from the Aug 16 recordings. Coach photos are the in-app thumbnails.

## Editing the copy

Open the site with `?edit=1`. Every line of copy on a screen becomes editable in place (dashed outline; amber outline means the line is personalized and built from an expression). Taps stop navigating; the bar at the bottom moves you back and forward. Edits save on your device as you go. **Export** hands back `edits.json`; save it as `copy/edits.json` in this repo (or send it to Alex) and the next build applies it last, so those edits always win. A personalized line edited without its `{{ }}` tokens becomes fixed text, and the build says so.

Copy in [brackets] is a placeholder to verify before anything ships.
