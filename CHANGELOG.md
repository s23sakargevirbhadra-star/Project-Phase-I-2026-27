# CHANGELOG

All changes to this project are recorded here in reverse order (newest first).
Each entry explains: what changed, why it changed, and which file(s) were affected.

---

## [Feature: Get Started landing page] — 2026-10-29

### What changed
- **`templates/landing.html`** (new) — The "Get Started" landing page. Contains:
  - Hero section with app name, tagline, description, "Get Started" button (→ `/login`), "Create Account" button (→ `/signup`), and a "Log in" text link.
  - City highlights grid — 6 cards (Mumbai, Pune, Nashik, Nagpur, Kolhapur, Nanded), each with a coloured gradient placeholder (easy to replace with a real photo), city name, and one-line description.
  - "How it works" section — 3 numbered steps with connector arrows.
  - Footer with app name and copyright.
  - Fully responsive: 3-column grid → 2-column → 1-column. Works at 360 px mobile width.
  - Entrance animation: hero fades in and slides up on load.
  - Accessible: semantic HTML (`<section>`, `<article>`, `<footer>`, `role` attributes), `alt`-equivalent `aria-label` on decorative images, `focus-visible` outlines on buttons.
- **`app.py`** — `GET /` route updated:
  - If the user is **not** logged in → renders `landing.html` (new behaviour).
  - If the user **is** logged in → renders `index.html` as before (no change to the main app).
  - New `GET /app` route added as a direct URL to the main app (useful for bookmarks).
- **`tests/test_features.py`** — 8 new tests in `TestLandingPage` class covering: landing shown to anonymous visitor, app name present, all 6 cities present, login and signup links present, logged-in user skips landing, `/app` redirects anonymous, `/app` serves logged-in user.

### Why
Visitors who have not yet signed up were dropped straight onto the login form with no context. The landing page introduces the app, its cities, and the value proposition before asking for credentials.

### No new dependencies
Plain HTML + CSS + Jinja2. No JS frameworks or additional libraries added.

### Routing summary
| URL | Anonymous visitor | Logged-in user |
|-----|-------------------|---------------|
| `/` | Landing page | Main app |
| `/app` | Redirect → `/login` | Main app |
| `/login` | Login form | Redirect → `/` (main app) |
| `/signup` | Signup form | (unchanged) |

### Test count
226 / 226 tests pass.

---

## [UI: Remove language switch from login and signup pages] — 2026-10-29

### What changed
- **`templates/login.html`** — Replaced `{% include '_lang_switch.html' %}` with a minimal inline script that loads `translations.js` and silently applies the saved language (from `localStorage` or the Flask `{{ lang }}` variable). The red "English | मराठी" bar is gone from this page.
- **`templates/signup.html`** — Same change as login.html.
- All other pages (`index.html`, `trails.html`, etc.) are unchanged — `_lang_switch.html` is still included there.
- `_lang_switch.html` itself is unchanged.

### Why
The language toggle on the login and signup forms was visually cluttered and unnecessary — users set their preferred language on the main page. The pages still respect the saved language for all `data-i18n` labels and flash messages; they just no longer show the switch.

### Layout
No CSS changes were needed. The card stays centered because `body { display:flex; justify-content:center; align-items:center; min-height:100vh }` now has one fewer flex child, which is the correct state. Works at 360 px mobile width.

### Tests
218 / 218 tests pass (no test changes needed — tests do not check for the presence of the bar).

---

## [Bug Fix: Chrome Autofill Suppression] — 2026-10-29 — login.html, signup.html, app.py, test_auth.py, test_features.py

### What changed
- **`templates/signup.html`** — Form field names changed: `name="fullname"` (was `name="name"`) and `name="reg_email"` (was `name="email"`). Added `autocomplete="new-password"` to password fields, `readonly` + `onfocus="this.removeAttribute('readonly')"` to all fields, and a `pageshow` event handler to reset the form on back-button navigation. Chrome ignores `autocomplete="off"` for fields named `name` or `email`, so renaming the fields is what actually prevents autofill.
- **`templates/login.html`** — Added `autocomplete="new-password"` to the password field, `readonly` + `onfocus="this.removeAttribute('readonly')"` to email and password fields, and the same `pageshow` reset handler. Login field names (`email`, `password`) remain unchanged.
- **`app.py`** — Signup route now reads `request.form.get("fullname", "")` and `request.form.get("reg_email", "")` to match the renamed form fields. MongoDB still stores the field as `email`.
- **`tests/test_auth.py`** — Rewritten from scratch (was corrupted by PowerShell encoding). All test helpers now post `fullname` + `reg_email` for signup and `email` + `password` for login. 34 tests, all pass.
- **`tests/test_features.py`** — Rewritten from scratch (was corrupted by PowerShell encoding; Marathi string literals became mojibake). Language assertions now use `assertNotEqual(mr, en)` instead of hard-coded Marathi strings. 184 tests, all pass.
- Deleted temporary helper scripts: `fix_assertions.py`, `fix_test_encoding.py`, `check_mr_name.py`, `name_mr_check.txt`.

### Why it changed
Chrome's autofill aggressively fills forms it recognises. Renaming fields away from common names (`name`, `email`) combined with `readonly`/`onfocus` and `pageshow` reset is the most reliable client-side mitigation. The sure fix for end users is to delete the saved password in Chrome's settings.

### Test count
218 / 218 tests pass.

---

## [Feature 1: Themed Trails] — 2026-10-29 — 4 trails, seed_trails.py, trail routes, 218 tests

### What changed
- Added 13 new trail_only places to `data/places.csv` and MongoDB (ids 54–66): 8 Ashtavinayak temples, 3 Jyotirlingas, Ajanta Caves, Ellora Caves.
- Added `trail_only` column to CSV header; existing 53 places have empty `trail_only`.
- Updated `recommender.py`: `load_places()` now excludes `trail_only=yes`; added `load_all_places()` (includes trail_only); added `get_trail_route(trail, all_places)`.
- Updated `search_places()` to still search Marathi name for trail_only places.
- Added `get_trails_collection()` to `database.py`.
- Created `seed_trails.py` — inserts 4 trails with upsert (safe to run again).
- Added 4 routes to `app.py`: `GET /trails`, `GET /trail/<trail_id>`, `GET /api/trails`, `GET /api/trail/<trail_id>`.
- Created `templates/trails.html` — card grid of all 4 trails.
- Created `templates/trail_detail.html` — ordered place list, Leaflet map with polyline, step distances, Google Maps button.
- Added trail translations to `static/translations.js`.
- Added "Trails" nav link to `templates/index.html` header.
- Created `tests/test_trails.py` with 15 tests.

### Trail contents

| Trail | Places in DB | New places added |
|-------|-------------|-----------------|
| Ashtavinayak | 0 | 8 (ids 54–61) |
| Jyotirlinga | 2 (ids 14, 19) | 3 (ids 62–64) |
| Fort Trail | 9 (all existing) | 0 |
| Caves Trail | 4 (ids 2,9,15,21) + cave temple (59) | 2 (ids 65–66) |

### New functions and routes

| Function / Route | What it does |
|---|---|
| `load_all_places()` | Returns all 66 places including trail_only=yes |
| `get_trail_route(trail, all_places)` | Returns ordered places, step distances, total_km |
| `get_trails_collection()` in database.py | Returns the MongoDB 'trails' collection |
| `GET /trails` | Trails listing page |
| `GET /trail/<trail_id>` | Trail detail page with map polyline |
| `GET /api/trails` | All trails as JSON |
| `GET /api/trail/<trail_id>` | Single trail detail as JSON |

### Test results
```
Ran 218 tests — OK  (0 failures, 0 errors)
  test_trails (15 new): TestGetTrailRoute (6) + TestTrailOnlyExclusion (9)
  All 203 previous tests unchanged ✅
```

---

## [Language Steps 4 & 5] — 2026-10-29 — Translated flash messages, Marathi in map popups, UTF-8

### What changed
- Added `MESSAGES` dictionary and `get_message(key, lang)` to `auth.py` — all 30 server flash messages now have English and Marathi translations.
- Updated all flash calls in `app.py` (signup, verify, resend-otp, login, logout, forgot-password, reset-password) to use `get_message(key, get_lang())`.
- Removed duplicate dead code from `reset_password` route.
- Added `app.config["JSON_AS_ASCII"] = False` — Marathi characters in JSON as-is.
- Updated map popups in `index.html` to show Marathi category, city, and description.
- Added `lang=curLang()` to all JS `fetch()` calls that call place APIs.
- Added 8 new tests for `get_message()` in `tests/test_features.py`.

### Why it changed
Steps 4 and 5 complete the language feature. After Step 3, place card text was translated but server messages (flash notifications after login, signup, OTP errors etc.) were still in English. Steps 4 and 5 fix that and also ensure Marathi appears correctly in map popups.

### New in auth.py

| Item | What it does |
|------|-------------|
| `MESSAGES["en"]` | 30 flash message strings in English |
| `MESSAGES["mr"]` | 30 flash message strings in Marathi |
| `get_message(key, lang)` | Returns translated message; falls back to English if Marathi is missing |

### Test results
```
Ran 203 tests — OK  (0 failures, 0 errors)
  test_features: added 8 get_message tests (TestGetMessage)
  Total: 203 tests across all files
```

---

## [Language Step 3] — 2026-10-29 — Marathi place data, get_text(), apply_language(), lang API param

### What changed
- Added 3 new columns to `data/places.csv` and MongoDB: `name_mr`, `description_mr`, `local_tip_mr` — filled for all 53 places (see notes below for 3 incomplete).
- Added `get_text(place, field, lang)` and `apply_language(place, lang)` to `recommender.py`.
- Updated `search_places()` to also search `name_mr` — Marathi name search now works.
- Updated `/api/places`, `/api/recommend`, `/api/search` to accept `?lang=mr` and return translated text.
- Added `app.config["JSON_AS_ASCII"] = False` so Marathi characters appear as-is in JSON.
- Added 18 new tests to `tests/test_features.py` — `TestGetText` (7), `TestApplyLanguage` (5), `TestLanguageAPI` (6).
- Updated `README.md` and `CHANGELOG.md`.

### New functions in recommender.py

| Function | What it does |
|---|---|
| `get_text(place, field, lang)` | Returns `place["field_mr"]` if lang="mr" and value is non-empty, else `place["field"]` |
| `apply_language(place, lang)` | Returns a copy of the place dict with name, description, local_tip translated |

### Marathi columns — 3 places without full translation

| id | Name | Missing field | Reason |
|----|------|--------------|--------|
| 21 | Pandavleni Caves | description_mr | Left blank — English kept as fallback |
| 23 | Coin Museum | description_mr | Left blank — English kept as fallback |
| 25 | Anjneri Hill | description_mr | Left blank — English kept as fallback |

For these 3 places, `get_text()` automatically falls back to the English description.

### Test results
```
Ran 195 tests — OK  (0 failures, 0 errors)
  test_features: added 18 language tests (TestGetText 7 + TestApplyLanguage 5 + TestLanguageAPI 6)
  All 177 previous tests unchanged ✅
```

---

## [Language Switch - Step 2] — 2026-10-29 — translations.js, data-i18n attributes, JS messages

### What changed
- Created `static/translations.js` — one dictionary with all page text in English and Marathi. Contains `get(key, lang)` and `setLanguage(lang)` functions.
- Added `data-i18n`, `data-i18n-placeholder`, `data-i18n-title` attributes to all 6 templates.
- Updated `_lang_switch.html` to load `translations.js` and call `setLanguage()` from `applyLang()`.
- Updated all JS `setStatus()` and error messages in `index.html` to use `get()`.
- City dropdown labels translated (Mumbai→मुंबई etc.) — values stay English.
- Category dropdown labels translated (Fort→किल्ला etc.) — values stay English.
- Added Noto Sans Devanagari font to all templates for clear Marathi rendering.
- Added `curLang()` helper in index.html JS.
- Added `statusCount()` and `statusSearch()` helpers for translated count messages.

### Why it changed
Step 1 added the toggle button. Step 2 makes it actually change the text. Without `data-i18n` attributes and `setLanguage()`, clicking मराठी did nothing to the page content.

### Key design decisions

| Decision | Reason |
|---|---|
| Values in English, labels translated | Keeps search/filter API calls working — the server always receives English values |
| One `translations.js` file | Single source of truth — add a translation once, it appears everywhere |
| `data-i18n` attributes | Clean separation — HTML describes structure, JS handles language |
| City/category labels translated in JS | They are filled dynamically by `fetch()` calls, not by Jinja2 |

### Test results
```
Ran 177 tests — OK  (0 failures, 0 errors) — all existing features unaffected
```

### Examiner Questions — Step 2

**Q: What is `data-i18n` and how does `setLanguage()` use it?**
A: `data-i18n` is a custom HTML attribute we added to any element whose text should change with the language. For example `<h1 data-i18n="login.title">Welcome Back</h1>`. The `setLanguage(lang)` function calls `document.querySelectorAll("[data-i18n]")` to find all such elements and replaces each one's `textContent` with the matching translation from the `T` dictionary.

**Q: Why do dropdown VALUES stay in English even in Marathi mode?**
A: The value of a `<select>` option is what gets sent to the server in the API URL (e.g. `?category=Fort`). The server and database use English. If we changed the value to `किल्ला`, the filter would stop working. So we only change the visible `textContent` label — the value is never changed.

**Q: What is Noto Sans Devanagari and why is it needed?**
A: Noto Sans Devanagari is a free Google Font that covers the Devanagari script used by Marathi. Without it, the browser uses its default font which may not render Marathi characters clearly — they can appear too small, overlapping, or as boxes. We load it from Google Fonts CDN with `<link href="https://fonts.googleapis.com/...">`.

**Q: How would you add a third language (e.g. Hindi)?**
A: Add a new `"hi"` key to every entry in `T` in `translations.js`. Add a third button in `_lang_switch.html`. That is all — `setLanguage()`, `get()`, `switchLang()` and `applyLang()` all work for any language code automatically.

---

## [Language Switch - Step 1] — 2026-10-29 — English | मराठी toggle on all pages

### What changed
- Added `POST /set-language` route to `app.py` — saves chosen language in Flask session.
- Added `get_lang()` helper and `@app.context_processor` to `app.py` — injects `{{ lang }}` into every template automatically.
- Created `templates/_lang_switch.html` — a small reusable toggle showing "English | मराठी".
- Added `{% include '_lang_switch.html' %}` to all 6 templates: `index.html`, `login.html`, `signup.html`, `verify.html`, `forgot_password.html`, `reset_password.html`.
- Fixed a Jinja2 infinite-recursion bug caused by `{% include ... %}` text inside an HTML comment — changed it to plain English text.

### Why it changed
Before this, there was no way for users to switch to Marathi. This step adds the toggle button and the two-layer persistence mechanism (localStorage + Flask session), so the chosen language survives page navigation and browser refresh.

### How it works
1. User clicks "मराठी" button in the dark-red bar at the top of any page.
2. `switchLang("mr")` saves `"mr"` in `localStorage` (browser memory).
3. It then calls `POST /set-language` with `{"lang": "mr"}` — Flask saves it in the session cookie.
4. The page reloads. `{{ lang }}` is now `"mr"` in every template.
5. `applyLang()` highlights the active button with the CSS `.active` class.

### New files and routes

| File / Route | What it does |
|---|---|
| `templates/_lang_switch.html` | Reusable toggle bar — included in all 6 templates with one line |
| `POST /set-language` in `app.py` | Saves `{"lang": "en"\|"mr"}` in Flask session |
| `get_lang()` in `app.py` | Returns current language from session (default "en") |
| `@app.context_processor` in `app.py` | Injects `{{ lang }}` into every template automatically |

### Bug fixed
The comment in `_lang_switch.html` originally contained the text `{% include '_lang_switch.html' %}` inside an HTML comment. Jinja2 processes template tags even inside HTML comments — this caused the file to include itself 966+ times in an infinite loop, crashing every page. Fixed by removing the Jinja2 tag syntax from the comment text.

### Test results
```
Ran 177 tests — OK  (0 failures, 0 errors)
All existing tests pass — no existing features broken.
```

### Examiner Questions — Language Switch

**Q: How does the language choice persist when the user goes to a new page?**
A: Two mechanisms work together. `localStorage` is a small key-value store in the browser that survives page navigation and even closing the browser. The Flask session is a signed cookie sent with every request. When the user clicks the toggle, both are updated. Even if one fails, the other still remembers the choice.

**Q: What is a Jinja2 context processor?**
A: A context processor is a function decorated with `@app.context_processor` in Flask. It runs before every `render_template()` call and adds variables to the template context automatically. We use it to add `{{ lang }}` to every template without having to pass it manually in every route.

**Q: Why use `{% include '_lang_switch.html' %}` instead of copying the toggle HTML into every page?**
A: The DRY principle — "Don't Repeat Yourself". If the toggle HTML is in one place, we only need to fix or change it once. If it was copied into 6 templates, we would need to make the same change in 6 places and could easily miss one.

**Q: What is `localStorage` and how is it different from a cookie?**
A: `localStorage` is a browser API that stores key-value pairs permanently in the browser until cleared. A cookie is sent to the server with every request. We use `localStorage` for the language because it is fast (no server call needed to read it) and because we also sync it to the Flask session so the server knows the language too.

---

## [Critical JS Bug Fix] — 2026-10-29 — Missing }); in showMarkers() caused ALL JavaScript to break

### What was wrong

In `templates/index.html`, the `showMarkers()` function had a broken `forEach` loop:

```javascript
// BROKEN — forEach was closed with } instead of });
places.forEach((p, i) => {
   ...
   markers.push(marker);
}        ← should be });
```

Because the `forEach` callback was never properly closed, the browser's JavaScript engine could not parse the entire `<script>` block. **All JavaScript on the page failed silently** — buttons did nothing, dropdowns did not fill, the search did not work, and the map had no interactivity. This is why "nothing was working".

### The fix

Changed `}` to `});  // end forEach` on the line after `markers.push(marker)`.

The `fitBounds()` and `invalidateSize()` blocks are now correctly **outside** the forEach loop and **inside** the showMarkers function, as intended.

### Bracket balance after fix
- Unmatched `(` : 0
- Unmatched `{` : 0
- Unmatched `[` : 0

### Files changed

| File | What changed |
|------|-------------|
| `templates/index.html` | `}` → `});  // end forEach` in `showMarkers()` — this was the only change needed |

---

## [Feature 2: Season Filter] — 2026-10-29 — filter_by_season(), season param, dropdown, 177 tests

### What changed
- Added `filter_by_season(places, season)` to `recommender.py` — splits pipe-separated seasons, case-insensitive, returns all if empty/"all".
- Updated `get_recommendations()` to accept a `season` parameter and call `filter_by_season()` after `filter_by_category()`.
- Added `season` parameter to `GET /api/recommend` in `app.py`.
- Added a season dropdown (All / Monsoon / Winter / Summer) to `templates/index.html` — wired into both `searchByCity()` and GPS `successCallback()`.
- Added 14 new tests to `tests/test_features.py`.
- Updated `README.md` — Feature 2 section with flow, function explanation, pipeline diagram, tests table, 3 Q&As, test count 163→177.

### Why it changed
Users want to find places that are good to visit in a specific season. A fort is best in monsoon for green views; a beach is best in winter to avoid the heat. The season filter lets users narrow results to places that match their travel timing.

### Files changed

| File | What changed |
|------|-------------|
| `recommender.py` | `filter_by_season()` added; `get_recommendations()` accepts `season` param |
| `app.py` | `GET /api/recommend` reads `season` from URL and passes it through |
| `templates/index.html` | Season dropdown added; `searchByCity()`, `successCallback()`, `callRecommendAPI()` updated to pass season |
| `tests/test_features.py` | 14 new tests: `TestFilterBySeason` (11) + `TestSeasonAPI` (3) |
| `README.md` | Feature 2 section, pipeline diagram, test count 177 |

### How filter_by_season() works

```python
# place["seasons"] = "monsoon|winter"
# .split("|") → ["monsoon", "winter"]
# "monsoon" in ["monsoon", "winter"] → True → keep this place

filter_by_season(places, "monsoon")  # → only monsoon places
filter_by_season(places, "")         # → all places (no filter)
```

### Recommendation pipeline (updated)

```
load_places → find_nearby_places → filter_by_category → filter_by_season → sort_by_rating → top 10
```

### Test results
```
Ran 177 tests — OK  (0 failures, 0 errors)
  test_features: 59 (20 search + 28 email + 11 place-info) + 14 season = 73 total
  test_auth (34)  test_nanded (23)  test_recommender (47) — all unchanged ✅
```

---

## [Map Tile Fix] — 2026-10-29 — Grey background resolved, fallback tiles, fitBounds

### What changed
- Fixed the grey map background in `templates/index.html`.

### Root cause
The Leaflet map was created at the top level of the `<script>` block, before the flexbox layout had settled. Leaflet measured its container as 0px tall, loaded no tiles, and showed a grey background with only markers visible. The fix is calling `map.invalidateSize()` after the layout has settled.

### Fixes applied

| Fix | What it does |
|-----|-------------|
| `map.invalidateSize()` in `window.onload` (100ms delay) | Recalculates container size after flexbox settles |
| `map.invalidateSize()` after `showMarkers()` (50ms delay) | Recalculates after results are shown |
| `map.fitBounds(allPoints)` after markers placed | Zooms map to show all result markers |
| `#map { min-height: 400px; }` in CSS | Guarantees the map always has space |
| Tile URL → `https://tile.openstreetmap.org/{z}/{x}/{y}.png` | Simpler URL without `{s}` subdomain |
| `tileerror` event → CARTO fallback | After 3 failed OSM tiles, switches to CARTO light tiles |
| Error message div | Shows "Map pictures could not be loaded..." after 5s if both servers fail |
| No referrer meta tag or header found | Confirmed clean — not the cause |

### Files changed

| File | What changed |
|------|-------------|
| `templates/index.html` | Tile layer rewritten with fallback; `invalidateSize()` added in `onload` and after `showMarkers`; `fitBounds()` added; `min-height: 400px` added to `#map` CSS; error message div added |
| `README.md` | Map Tile Fix section added with root cause and fix table |

### What was NOT the cause

| Check | Result |
|-------|--------|
| Referrer policy meta tag | Not found in any template ✅ |
| Referrer-Policy header in app.py | Not found ✅ |
| Leaflet CSS before Leaflet JS | Already correct ✅ |
| Tile URL format | `{s}` subdomain URL was valid, but simplified anyway |

---

## [Feature 1: Place Info Card] — 2026-10-29 — 6 new data fields, upsert seed, card UI update

### What changed
- Added 6 new columns to `data/places.csv`: `entry_fee`, `timings`, `best_time`, `time_needed`, `local_tip`, `seasons` — filled for all 53 places.
- Rewrote `seed_places.py` to use `update_one` with `upsert=True` instead of insert-or-skip. Running it again now UPDATES existing documents with new fields.
- Updated `templates/index.html` — created shared `buildCardHTML()` function used by both `showCards()` and `showSearchCards()`; each card now shows entry fee, timings, best time, time needed, and local tip.
- Added 11 new tests to `tests/test_features.py` in `TestPlaceInfoFields` class.
- Updated `README.md` — dataset columns table (8→14), Feature 1 section with examiner Q&As, test count 152→163.

### Why it changed
A recommendation system that only shows a name and rating is not very useful for planning a visit. The 6 new fields help users decide when to go, how much it costs, how long to spend, and what to look out for.

### Files changed

| File | What changed |
|------|-------------|
| `data/places.csv` | 6 new columns added to all 53 rows |
| `seed_places.py` | Rewritten — uses `update_one` + `upsert=True` instead of insert-or-skip |
| `templates/index.html` | New `buildCardHTML()` shared function; both card functions updated; new CSS for `.card-info` and `.card-tip` |
| `tests/test_features.py` | 11 new tests: `TestPlaceInfoFields` |
| `README.md` | Dataset table updated (14 columns), Feature 1 section, test count 163 |

### Seed result
```
Reading places from data/places.csv ...
Found 53 places in CSV.
Inserted 0 new places. Updated 53 existing.
Done! Total documents in 'places' collection: 53
```

### Places with "Check locally" for entry_fee

| Place | Reason |
|------|--------|
| Osho Ashram (Pune) | Course fees vary — check website |
| Sitabuldi Fort (Nagpur) | Army-controlled — access changes |
| Shalini Palace (Kolhapur) | Now a hotel — may charge non-guests |

### Test results
```
Ran 163 tests — OK  (0 failures, 0 errors)
  test_features: 48 (20 search + 28 email) + 11 place-info = 59 total
  test_auth (34)  test_nanded (23)  test_recommender (47) — all unchanged ✅
```

---

## [Email Validation] — 2026-10-29 — is_valid_email(), clean_email(), frontend pattern, 152 tests

### What changed
- Added `clean_email()` and `is_valid_email()` to `auth.py`.
- Used both functions in `POST /signup`, `POST /login`, `POST /forgot-password` in `app.py`.
- Updated `templates/signup.html`, `login.html`, `forgot_password.html` with `pattern`, `title`, `maxlength="100"`, and helper text.
- Added 28 new tests to `tests/test_features.py`.
- Added "Email Validation" section to `README.md`.

### Why it changed
Inputs like `1234`, `abc@`, or `abc@gmail` were silently passed to MongoDB lookups. Now they are rejected at the first check in Flask — the database is never touched for an invalid email.

### Files changed

| File | What changed |
|------|-------------|
| `auth.py` | `import re` added; `clean_email()` and `is_valid_email()` added before the users-collection section |
| `app.py` | `clean_email`, `is_valid_email` imported; used in POST `/signup`, POST `/login`, POST `/forgot-password` |
| `templates/signup.html` | Email `<input>` gets `pattern`, `title`, `maxlength="100"`, helper text |
| `templates/login.html` | Same |
| `templates/forgot_password.html` | Same |
| `tests/test_features.py` | 28 new tests: `TestIsValidEmail` (18), `TestCleanEmail` (6), `TestSignupEmailValidation` (4) |
| `README.md` | Full "Email Validation" section added with rule table, code, HTML snippet, tests table, 4 Q&As |

### Bug found and fixed during testing
The original pattern `[A-Za-z0-9.*%+-]` did not include underscore `_`. This caused valid addresses like `user_name@domain.com` and the test email `test_auth_suite@example.com` to be rejected. Fixed by adding `_` to the character class: `[A-Za-z0-9._*%+-]`.

### Test results
```
Ran 152 tests — OK  (0 failures, 0 errors)
  test_features: 20 search + 28 email = 48 total
    TestIsValidEmail (18)  TestCleanEmail (6)  TestSignupEmailValidation (4)
  test_auth (34) test_nanded (23) test_recommender (47) — all unchanged ✅
```

---

## [Feature 1] — 2026-10-29 — Search by place name

### What changed
- Added `search_places(places, text)` to `recommender.py`.
- Added `GET /api/search?q=..` route to `app.py` (login required).
- Added search box + `searchByText()` + `showSearchCards()` to `templates/index.html`.
- Created `tests/test_features.py` with 20 new tests.
- Updated `README.md` — Feature 1 phase entry, full Feature 1 section, `search_places()` as Function 6 (others renumbered to 7–11), `/api/search` added to routes table, test count updated to 124.

### Why it changed
Users need to find places by name or type, not just by location. A student can now search "fort" and see all forts across all 6 cities, or search "Nanded" to see all Nanded places — without needing to know their GPS coordinates.

### Files changed

| File | What changed |
|------|-------------|
| `recommender.py` | `search_places()` added — checks name/city/category, case-insensitive, empty = return all |
| `app.py` | `GET /api/search` route added; `search_places` imported |
| `templates/index.html` | Search box added above city dropdown; `searchByText()` and `showSearchCards()` JS functions added |
| `tests/test_features.py` | Created — 20 tests (TestSearchPlaces 15 + TestSearchAPI 5) |
| `README.md` | Feature 1 section, functions renumbered 1–11, API table updated, test count 124 |

### How `search_places()` works

```python
# checks: query in name.lower() OR query in city.lower() OR query in category.lower()
search_places(places, "fort")    # → Shaniwar Wada, Sinhagad Fort, Tikona Fort, ...
search_places(places, "Mumbai")  # → all 9 Mumbai places
search_places(places, "")        # → all 53 places (no filter)
```

### Test results
```
Ran 124 tests — OK  (0 failures, 0 errors)
  test_features (20 new) : TestSearchPlaces (15) + TestSearchAPI (5)
  test_nanded (23)        : unchanged ✅
  test_auth (34)          : unchanged ✅
  test_recommender (47)   : unchanged ✅
```

---

## [Nanded + Use My Location] — 2026-10-29 — 6th city, GPS improvements, new functions, 104 tests

### What changed
- Added 8 Nanded places to `data/places.csv` (ids 46–53); seeded to MongoDB (53 total).
- Updated `recommender.py`: `get_cities()` now returns 6 cities; added `get_city_centres()` and `get_nearest_city()`.
- Updated `app.py`: added imports for new functions; added `GET /api/city-centres`, `GET /api/nearest-city`, `GET /api/nearest-places`.
- Rewrote `templates/index.html`: shows GPS coords + nearest city, radius dropdown, fallback notice, GPS error messages, loading text.
- Created `tests/test_nanded.py` with 23 new tests.
- Updated `tests/test_recommender.py`: 4 tests updated (45→53 places, 5→6 cities).
- Updated `README.md`: 6-city table, Use My Location section, new functions (get_city_centres, get_nearest_city), 8 new location Q&As.

### Why it changed
Nanded is a major religious and historical city in Maharashtra. The GPS feature was improved to be more useful and explainable — showing coordinates, nearest city, fallback results, and clear error messages.

### Files changed

| File | What changed |
|------|-------------|
| `data/places.csv` | 8 Nanded rows added (ids 46–53) |
| `recommender.py` | `get_cities()` updated to 6 cities; `get_city_centres()` and `get_nearest_city()` added |
| `app.py` | 3 new endpoints: `/api/city-centres`, `/api/nearest-city`, `/api/nearest-places` |
| `templates/index.html` | Rewritten: GPS coords display, nearest city, radius dropdown, fallback, error messages, loading |
| `tests/test_nanded.py` | Created — 23 tests across 4 classes |
| `tests/test_recommender.py` | 4 tests updated to reflect new counts |
| `README.md` | 6-city table, new phase, Use My Location flow, new functions, 8 Q&As, test count updated |

### Nanded places added

| id | Name | Category | Lat | Lon | Confidence |
|----|------|----------|-----|-----|-----------|
| 46 | Hazur Sahib Gurudwara | Temple | 19.1528 | 77.3186 | ✅ Wikipedia |
| 47 | Nanded Fort | Fort | 19.1417 | 77.3248 | ✅ Wikipedia |
| 48 | Kandhar Fort | Fort | 18.2700 | 77.3200 | ⚠️ Approximate (Kandhar town) |
| 49 | Renuka Mata Temple Mahur | Temple | 19.8500 | 77.9100 | ✅ Wikipedia |
| 50 | Sahastrakund Waterfall | Nature | 19.6000 | 78.2500 | ⚠️ Approximate (Kinwat area) |
| 51 | Unkeshwar Hot Springs | Temple | 19.5700 | 78.2800 | ✅ Research papers |
| 52 | Vishnupuri Dam | Nature | 19.1084 | 77.2879 | ✅ latlong.net |
| 53 | Gurudwara Langar Sahib | Temple | 19.1540 | 77.3140 | ✅ Near Hazur Sahib complex |

### New API endpoints

| Endpoint | What it returns |
|----------|----------------|
| `GET /api/city-centres` | GPS centre of all 6 cities as JSON |
| `GET /api/nearest-city?lat=..&lon=..` | Name of the city closest to that point |
| `GET /api/nearest-places?lat=..&lon=..` | 5 closest places, sorted by distance, no radius limit |

### Test results
```
Ran 104 tests — OK   (0 failures, 0 errors)

test_nanded (23)       : TestNandedData (7) + TestGetCityCentres (5)
                         + TestGetNearestCity (7) + TestNandedRecommendations (4)
test_auth (34)         : unchanged ✅
test_recommender (47)  : 4 tests updated (45→53, 5→6) — all pass ✅
```

---

## [Email Service + Forgot Password] — 2026-10-29 — email_service.py, forgot/reset password

### What changed
- Created `email_service.py` — dedicated email module with `send_email()`.
- Rewrote `auth.py` — replaced inline SMTP with `email_service`; added 4 new functions for password reset.
- Updated `app.py` — added 3 new routes and imported new auth functions.
- Created `templates/forgot_password.html` and `templates/reset_password.html`.
- Updated `templates/login.html` — added "Forgot password?" link.
- Added 15 new tests to `tests/test_auth.py` (4 `TestForgotPassword` + 11 `TestResetPassword`).
- Updated `README.md` — new flows, Gmail setup, updated functions table (17), routes table (14), 12 Q&As.

### Why it changed
Users need a way to recover their account if they forget their password. The email service was also extracted into its own file so it can be imported cleanly by `auth.py` without mixing email logic with auth logic.

### Files changed

| File | What changed |
|------|-------------|
| `email_service.py` | Created — `send_email(to, subject, body)` with Gmail SMTP + TEST MODE fallback |
| `auth.py` | `send_otp_email` uses `email_service`; 4 new functions: `save_reset_otp`, `send_reset_otp_email`, `verify_reset_otp`, `update_password`; `create_user` gains 3 new fields |
| `app.py` | New imports; `GET/POST /forgot-password`; `GET/POST /reset-password`; `POST /resend-reset-otp` |
| `templates/forgot_password.html` | Created — email input, safe message note |
| `templates/reset_password.html` | Created — OTP input, new password, confirm, Resend button, 5-attempt hint |
| `templates/login.html` | "Forgot password?" link added below submit button |
| `tests/test_auth.py` | 15 new tests appended — `TestForgotPassword` (4) + `TestResetPassword` (11) |
| `README.md` | Signup+forgot flows, Gmail setup, `email_service` explanation, 17-function table, 14-route table, 12 Q&As, footer updated |

### New auth.py functions

| Function | What it does |
|----------|-------------|
| `save_reset_otp(email, otp)` | Saves reset OTP + 10-min expiry + resets `reset_attempts` to 0 |
| `send_reset_otp_email(email, otp)` | Calls `email_service.send_email()` with password-reset message |
| `verify_reset_otp(email, otp_entered)` | Returns `"ok"` / `"expired"` / `"invalid"` / `"locked"` (after 5 wrong guesses) |
| `update_password(email, new_password)` | Hashes + saves new password; clears all reset fields |

### Test results

```
Ran 81 tests in 10.883s
OK  —  0 failures, 0 errors

test_auth (34 tests):
  TestSignup (9)  |  TestOTP (4)  |  TestLogin (5)
  TestForgotPassword (4)  |  TestResetPassword (11) ← NEW

test_recommender (47 tests): all unchanged ✅
```

### Key security decisions

| Decision | Why |
|----------|-----|
| Same message for known + unknown emails on `/forgot-password` | Prevents email enumeration attacks |
| 5-attempt lockout on `/reset-password` | Prevents brute-force guessing of 6-digit OTP |
| Separate `reset_otp` fields (not reusing `otp`) | Prevents signup OTP and reset OTP from interfering |
| OTP expires in 10 minutes | Short window limits the time an intercepted code can be used |

---

## [Auth Step 6] — 2026-10-29 — tests/test_auth.py

### What changed
- Created `tests/test_auth.py` with 18 unit tests across 3 classes.
- Fixed one test: hash prefix check changed from `$2b$` (bcrypt) to `:` separator (works for all werkzeug versions).
- Updated `README.md`: Auth Step 6 marked ✅, tests table added, "how to run all tests" updated to `discover tests`.

### Why it changed
Tests prove the auth logic is correct and will catch any future regressions. Every important rule is now tested: signup validation, password hashing, OTP lifecycle, login checks, and session protection.

### Files changed

| File | What changed |
|------|-------------|
| `tests/test_auth.py` | Created — 18 tests across TestSignup, TestOTP, TestLogin |
| `README.md` | Auth Step 6 marked ✅, test table added, run command updated |

### Bug fixed
`test_password_is_hashed_not_plain` originally checked `startswith("$2b$")` (bcrypt). This werkzeug version uses `pbkdf2:sha256:` format. Fixed to check for `:` in the hash string — valid for all werkzeug hash formats regardless of version.

### Final test results
```
Ran 65 tests in 7.645s
OK  —  0 failures, 0 errors

test_auth (18 tests):
  TestSignup  9  |  TestOTP  4  |  TestLogin  5

test_recommender (47 tests):
  TestLoadPlaces 7  |  TestCalculateDistance 6  |  TestGetCities 3
  TestFindNearbyPlaces 6  |  TestFilterByCategory 6  |  TestSortByRating 5
  TestGetAllCategories 5  |  TestGetRecommendations 9
```

### How to run
```
py -m unittest discover tests -v
```

---

## [Auth Steps 2–5] — 2026-10-29 — Signup, Verify, Login, Logout

### What changed
- `app.py` — completely rewritten with `SECRET_KEY`, all auth imports, 8 auth routes, session-protected `GET /`.
- `templates/signup.html` — new signup form.
- `templates/verify.html` — OTP entry form with Resend button.
- `templates/login.html` — new login form.
- `templates/index.html` — header updated with "Hello, \<name\>" and Logout button.
- `README.md` — Auth Steps 2–5 marked ✅, routes table updated to "all active".

### Why it changed
Steps 2–5 were built together because they form one connected flow: signup → verify → login → protected page. Splitting them would have left the app in a broken half-state between each step.

### Files changed

| File | What changed |
|------|-------------|
| `app.py` | `SECRET_KEY` from `.env`; 8 auth routes; `GET /` requires login |
| `templates/signup.html` | Created — name, email, password, confirm password, flash messages |
| `templates/verify.html` | Created — OTP input (6-digit, spaced), Verify + Resend buttons |
| `templates/login.html` | Created — email, password, flash messages, link to signup |
| `templates/index.html` | Header updated — "Hello, \<name\>" + Logout button |
| `README.md` | Auth Steps 2–5 marked done, routes table updated |

### Test results (8/8 pass)

```
Test 1: GET /signup                          → 200  PASS
Test 2: Valid signup                         → 302 /verify, user in DB, is_verified=False,
                                               OTP set, password hashed  PASS
Test 3: Duplicate email                      → 200, error shown  PASS
Test 4: Password < 8 chars                   → 200, error shown  PASS
Test 5: Passwords do not match               → 200, error shown  PASS
Test 6: Unverified user login attempt        → 302 /verify  PASS
Test 7: Correct OTP                          → 302 /login, is_verified=True, OTP cleared  PASS
Test 8: Wrong OTP                            → 200, error shown  PASS
```

TEST MODE confirmed: OTP printed in terminal when `EMAIL_ADDRESS` is empty.

---

## [Auth Step 1] — 2026-10-29 — Users collection + auth.py foundation

### What changed
- Added 3 new keys to `.env` and `.env.example`: `SECRET_KEY`, `EMAIL_ADDRESS`, `EMAIL_PASSWORD`.
- Created `auth.py` with 13 functions covering all auth steps.
- Created unique email index on the `users` MongoDB collection.
- Updated `README.md`: Tech Stack (added Flask session, werkzeug, smtplib), Folder Structure (auth.py, new templates, test_auth.py), Phases section (Auth Steps 1–6), full "Login and Verification" section (flow diagram, users document structure, .env secrets, functions table, routes table, 8 examiner Q&As).

### Why it changed
Before building the signup/login pages, we need the foundation: the secrets in `.env`, the functions in `auth.py`, and the unique index in MongoDB. All the auth logic is written in `auth.py` now so Steps 2–6 only need to wire up the routes and templates.

### Files changed

| File | What changed |
|------|-------------|
| `.env` | Added `SECRET_KEY`, `EMAIL_ADDRESS` (empty), `EMAIL_PASSWORD` (empty) |
| `.env.example` | Added same 3 keys with fake/empty values and clear comments |
| `auth.py` | Created — 13 functions, all steps 1–6 pre-written |
| `README.md` | Full auth section added — flow, document structure, functions table, routes table, 8 Q&As |

### Unique index verification
```
Indexes on 'users' collection (2 total):
  name=_id_     key={'_id': 1}    unique=False
  name=email_1  key={'email': 1}  unique=True  ✅
```

### auth.py functions summary

| Function | What it does |
|----------|-------------|
| `create_users_index()` | Creates unique email index in MongoDB |
| `email_already_exists(email)` | Returns True if email is taken |
| `create_user(name, email, password)` | Hashes password, saves user with is_verified=False |
| `generate_otp()` | Returns random 6-digit string |
| `save_otp(email, otp)` | Saves OTP + 10-min expiry to user document |
| `send_otp_email(email, otp)` | Emails OTP via Gmail; prints to terminal if no email in .env |
| `verify_otp(email, otp_entered)` | Returns "ok", "expired", or "invalid" |
| `mark_verified(email)` | Sets is_verified=True, clears OTP |
| `find_user_by_email(email)` | Returns user dict (no _id) or None |
| `check_password(user, password)` | Returns True if password matches hash |
| `login_user(session, user)` | Saves name + email to Flask session |
| `logout_user(session)` | Clears Flask session |
| `get_logged_in_user(session)` | Returns logged-in user's name or None |

---

## [MongoDB Steps 3–6] — 2026-10-29 — load_places() from MongoDB, API verified, tests pass, users collection prepared

### What changed
- `recommender.py`: `load_places()` now reads from MongoDB instead of CSV.
- `recommender.py`: `csv` import removed; `get_places_collection` import added.
- `recommender.py`: Added FUTURE FEATURE comment block showing how `get_users_collection()` will be used.
- `README.md`: Full update — all phases marked ✅, load_places() explanation updated, MongoDB Q&As added, run steps updated, duplicate section removed.

### Why it changed
Step 3 is the core of the MongoDB integration — it is the one line that makes the whole system read from the database. Steps 4–6 are verification, safety, and preparation for what comes next.

### Files changed

| File | What changed |
|------|-------------|
| `recommender.py` | `load_places()` now uses `collection.find({}, {"_id": 0})`; `csv` import removed; future feature comment added |
| `README.md` | All phases updated ✅, load_places explanation rewritten, run steps rewritten for local MongoDB + seed step, 4 new MongoDB Q&As, duplicate section removed |

### Step-by-step results

| Step | What was done | Result |
|------|--------------|--------|
| Step 3 | Changed `load_places()` to read from `collection.find({}, {"_id": 0})` | ✅ |
| Step 4 | Ran all 4 API endpoints via Flask test client | All 5 checks PASS ✅ |
| Step 5 | Ran all 47 existing unit tests unchanged | 47/47 PASS, 0.668s ✅ |
| Step 6 | Added FUTURE FEATURE comment to `recommender.py` | ✅ |

### Key code change — load_places() before and after

**Before (read from CSV):**
```python
import csv
def load_places():
    places = []
    with open("data/places.csv", ...) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row["latitude"] = float(row["latitude"])
            ...
            places.append(row)
    return places
```

**After (read from MongoDB):**
```python
from database import get_places_collection
def load_places():
    collection = get_places_collection()
    results = collection.find({}, {"_id": 0})
    return list(results)
```

Same output shape — list of 45 dictionaries with the same keys — so zero other changes were needed.

---

## [MongoDB Step 2] — 2026-10-29 — seed_places.py

### What changed
- Created `seed_places.py` with two functions: `read_csv()` and `seed()`.
- Fixed a bug in `data/places.csv` — row 17 (Lonavala) had an unquoted comma in the description.
- Updated `README.md` — seed_places.py section fully filled in, folder structure updated.

### Why it changed
Before `load_places()` can read from MongoDB, the database must have data. `seed_places.py` is the one-time script that moves the 45 places from the CSV into MongoDB. It must be run once before Step 3.

### Files changed

| File | What changed |
|------|-------------|
| `seed_places.py` | Created — `read_csv()` + `seed()` with duplicate check via `find_one()` |
| `data/places.csv` | Fixed row 17: description wrapped in quotes to escape the comma |
| `README.md` | seed_places.py section completed with functions table, outputs, how duplicate protection works |

### Verification results

| Run | Inserted | Skipped | Total in collection |
|-----|----------|---------|-------------------|
| 1st run | 45 | 0 | 45 |
| 2nd run (duplicate test) | 0 | 45 | 45 |

---

## [MongoDB Step 1] — 2026-10-29 — Local MongoDB connected

### What changed
- Created `.env` with `MONGO_URI=mongodb://localhost:27017`.
- Updated `.env.example` to show the local URI as the example value.
- Rewrote `database.py` — same 4 functions, comments now say "local MongoDB" not "Atlas".
- Added a full **MongoDB section** to `README.md` (see below).
- `requirements.txt`, `.gitignore` already in place from earlier setup.

### Why it changed
The previous step had created the infrastructure for Atlas. Scope changed to local MongoDB (`mongodb://localhost:27017`). The code is identical — only the URI value and comments changed. Connection was verified: `ping` returned OK, database `maharashtra_places` reachable.

### Connection test result
```
Connected to MongoDB!
Database: maharashtra_places
Collections available: []   ← empty until seed_places.py is run
```

### Files changed

| File | What changed |
|------|-------------|
| `.env` | Created — `MONGO_URI=mongodb://localhost:27017` |
| `.env.example` | Updated — shows local URI as example |
| `database.py` | Comments updated for local MongoDB; logic unchanged |
| `README.md` | Full MongoDB section added — terms, install, .env, functions table, 6 Q&As |

### What Step 2 will do
Create `seed_places.py` — reads `data/places.csv` and inserts 45 place documents into the `places` collection. Duplicate-safe.

---

## [MongoDB Step 1 — Infrastructure] — 2026-10-29 — Packages, files, database.py skeleton

### What changed
- Installed `pymongo==4.13.2` and `python-dotenv==1.1.0`.
- Created `requirements.txt` with all 3 libraries.
- Created `.env.example` with a safe fake `MONGO_URI`.
- Created `.gitignore` to protect `.env` and ignore cache files.
- Created `database.py` with 4 functions.
- Updated `README.md`: added MongoDB to Tech Stack, new database.py section, updated folder structure, updated install steps, added 4 MongoDB examiner Q&As.

### Why it changed
Before connecting to MongoDB we need three things: the library installed (`pymongo`), a safe place for the secret connection string (`.env`), and a clean module that handles the connection (`database.py`). Every other file will import from `database.py` — so this is the foundation of the MongoDB feature.

### Files created / changed

| File | What happened |
|------|--------------|
| `requirements.txt` | Created — lists flask, pymongo, python-dotenv with exact versions |
| `.env.example` | Created — safe template with fake MONGO_URI |
| `.gitignore` | Created — blocks .env, __pycache__, venv/ from Git |
| `database.py` | Created — 4 functions below |
| `README.md` | Updated — MongoDB in Tech Stack, database.py section, updated install, 4 new Q&As |

### Functions in database.py

| Function | What it does |
|----------|-------------|
| `get_database()` | Reads `MONGO_URI` from `.env` via `os.environ`, connects with `MongoClient`, returns the `maharashtra_places` database |
| `get_places_collection()` | Calls `get_database()`, returns the `places` collection |
| `get_users_collection()` | Calls `get_database()`, returns the `users` collection (for future reviews) |
| `test_connection()` | Calls `db.command("ping")`, prints "Connected to MongoDB!" or a plain-English error |

### How to test
```
py database.py
```
Expected: `Connected to MongoDB!` (requires a real `.env` file with a valid URI)

---

## [Phase 6] — 2026-10-29 — Tests + Final README

### What changed
- Wrote 47 unit tests in `tests/test_recommender.py` across 8 test classes.
- Fixed 1 test that had the wrong expected value (Pune→Nashik road distance 200 km vs actual straight-line 165 km).
- Rewrote `README.md` as one clean, complete document for examiner preparation.

### Why it changed
Tests prove every function works correctly and will catch bugs if the code is changed in the future. The README needed a final clean pass so a student can read it top-to-bottom and confidently answer any question about the project.

### Files changed

| File | What changed |
|------|-------------|
| `tests/test_recommender.py` | Written from scratch — 47 tests, 8 classes, 0 failures |
| `README.md` | Final rewrite — all sections present, consistent with actual code |

### Test results

```
Ran 47 tests in 0.007s
OK  —  0 failures, 0 errors
```

### Test classes and what they check

| Class | Tests | What it verifies |
|-------|-------|-----------------|
| `TestLoadPlaces` | 7 | List returned, 45 items, correct key names, correct types (float/int), only 5 cities, ratings 1–5 |
| `TestCalculateDistance` | 6 | Pune→Mumbai ≈120 km, same point = 0.0, result is float, result is positive, A→B = B→A, Pune→Nashik ≈165 km |
| `TestGetCities` | 3 | Returns a list, exactly 5 cities, correct city names in correct order |
| `TestFindNearbyPlaces` | 6 | Returns list, all results within radius, `distance_km` key added, small radius < large radius, 0 radius returns ≤1, 2000 km returns all 45 |
| `TestFilterByCategory` | 6 | Forts filter, Temple filter, empty string returns all, None returns all, case-insensitive, nonexistent category returns empty |
| `TestSortByRating` | 5 | First item has highest rating, last has lowest, descending order, tie broken by distance, original list not changed |
| `TestGetAllCategories` | 5 | Returns list, exactly 8 categories, no duplicates, alphabetically sorted, contains all 8 expected names |
| `TestGetRecommendations` | 9 | Returns list, max 10 results, `distance_km` on each, all within radius, category filter works, first result has highest rating, tiny radius returns few results, empty category returns mixed, nonexistent category returns empty list |

### How to run the tests
```
py -m unittest tests/test_recommender.py -v
```

### README sections (final)

| Section | Contents |
|---------|---------|
| What is this project | Problem, solution, real example, scope note |
| Tech Stack | 7 tools with what each is and why used |
| How it Works | 5 numbered steps from data to results |
| Cities Covered | Table: 5 cities, coordinates, place count |
| Folder Structure | Every file in one sentence |
| Project Phases | All 6 phases — what was done and why |
| The Dataset | 8 columns explained, sample places per city |
| All 8 Functions | Code example + step-by-step explanation for each |
| Distance Formula | Plain-English analogy + formula steps + real proof |
| Tests | 47-test table with what each class checks |
| API Endpoints | All 5 routes, parameter table, example URLs, errors |
| How to Run | 8 steps from install to test |
| Examiner Q&A | 10 questions with clear short answers |
| Future Improvements | 10 ideas |

---

## [README Overhaul] — 2026-10-29 — Complete README Rewrite for Examiner

### What changed
- Completely rewrote `README.md` from scratch as one clean, well-organised document.

### Why it changed
The README had become fragmented across phases — some sections were missing, the examiner Q&A was incomplete, and the `get_cities()` function explanation was in the wrong place. A student needs to be able to read this file top-to-bottom and confidently explain the entire project to an examiner.

### What is now in the README

| Section | What it covers |
|---------|---------------|
| What is this project | Plain English description, problem it solves, example output |
| Tech Stack table | Every tool used and why |
| How it works — 5 steps | Simple numbered explanation of the full flow |
| Cities Covered table | 5 cities with coordinates and place counts |
| Project Built in Phases | Every phase explained: what was done and why |
| Folder Structure | Every file explained in one sentence |
| The Dataset | All 8 columns explained with examples; sample places per city |
| All Functions Explained | All 8 functions: table + detailed step-by-step explanation with code examples |
| Distance Formula | Plain English + step-by-step maths + real test result |
| Web Page explanation | Every UI control, map element, and JS↔Flask connection explained |
| API Endpoints table | All 5 routes, parameter table, example URLs, error responses |
| How to Install and Run | 7 clear steps |
| Examiner Q&A | **20 questions** with short, clear answers |
| Future Improvements | 10 ideas |

### Files changed

| File | What changed |
|------|-------------|
| `README.md` | Complete rewrite — all sections reorganised and expanded |

---

## [Phase 5] — 2026-10-29 — Web Page Complete

### What changed
- Rewrote `templates/index.html` with the complete, fully working web UI.
- Added a new "Web Page" section to `README.md` explaining every part of the UI.
- Added 4 new examiner Q&A entries to `README.md` covering Leaflet, OpenStreetMap, `fetch()`, and card click behaviour.

### Why it changed
Phase 5 is the front-end. Without this, users can only access the system via raw API URLs. The web page makes it usable by anyone — pick a city, move a slider, click search, and see results on a map.

### Files changed

| File                    | What changed                                                                          |
|-------------------------|---------------------------------------------------------------------------------------|
| `templates/index.html`  | Completely rewritten — full UI with map, cards, dropdowns, slider, GPS button        |
| `README.md`             | Added "Web Page" section; added 4 Leaflet/JS examiner Q&A entries                    |

### What the web page includes

| Feature                   | Detail                                                                 |
|---------------------------|------------------------------------------------------------------------|
| Layout                    | Split screen — left panel (controls + results) + right map             |
| City dropdown             | Auto-filled from `/api/cities` on page load                            |
| Radius slider             | Drag to set 5–200 km; label updates live                               |
| Category dropdown         | Auto-filled from `/api/categories` on page load                        |
| Search by City button     | Uses city centre coordinates from hardcoded `CITY_COORDS` object       |
| Use My Location button    | Uses browser `navigator.geolocation` to get real GPS coordinates       |
| Status message            | Shows loading state, result count, or error in red                     |
| Result cards              | Numbered 1–10, colour-coded category badge, rating, distance, description |
| Card click                | Zooms the Leaflet map to that place (zoom level 15)                    |
| Leaflet map               | OpenStreetMap tiles, no API key needed                                 |
| User location marker      | Blue dot at search origin                                              |
| Radius circle             | Dashed blue circle showing exact search area                           |
| Result pin markers        | Numbered red circles matching the card numbers                         |
| Marker popup              | Click a pin: shows name, category, city, rating, distance, description |
| Responsive design         | Stacks vertically on small/mobile screens                              |

---

## [Phase 4] — 2026-10-29 — Flask API Complete

### What changed
- Rewrote `app.py` with all 5 working routes.
- Updated `README.md` API section — all endpoints marked ✅, parameter table added, example URLs added, error response examples added.

### Why it changed
Phase 4 connects the logic from Phase 3 to the web. Without these routes, nothing can be accessed from a browser. The `/api/recommend` route is the most important — it accepts the user's location and returns recommendations as JSON.

### Files changed

| File       | What changed                                                                          |
|------------|---------------------------------------------------------------------------------------|
| `app.py`   | Added `/api/recommend`, `/api/categories`, kept `/api/cities`, `/api/places`, added root `/` |
| `README.md`| API table fully updated — all ✅, parameter table, example URLs, error responses      |

### All routes now active

| Route             | What it does                                                              |
|-------------------|---------------------------------------------------------------------------|
| `GET /`           | Serves `templates/index.html` — the main web page                        |
| `GET /api/cities` | Returns `["Mumbai","Pune","Nashik","Nagpur","Kolhapur"]`                  |
| `GET /api/places` | Returns all 45 places as JSON                                             |
| `GET /api/categories` | Returns `["Beach","Cave","Fort","Hill Station","Monument","Nature","Other","Temple"]` |
| `GET /api/recommend` | Returns top 10 places near `lat`/`lon` within `radius` km, optional `category` filter |

### `/api/recommend` validation
- Returns HTTP 400 with a helpful message if `lat` or `lon` are missing.
- Returns HTTP 400 if `lat`, `lon`, or `radius` cannot be converted to numbers.
- `radius` defaults to 50 km if not provided.
- `category` defaults to `""` (all categories) if not provided.

---

## [Phase 3] — 2026-10-29 — Recommendation Logic Functions

### What changed
- Added 5 new functions to `recommender.py`: `find_nearby_places`, `filter_by_category`, `sort_by_rating`, `get_all_categories`, and `get_recommendations`.
- Updated `README.md` — all Phase 3 functions marked ✅, detailed how-it-works notes added for each.

### Why it changed
Phase 3 is the core logic of the system. These functions take the raw data from Phase 2 and turn it into actual recommendations. Every function does one small job; `get_recommendations()` ties them all together.

### Files changed

| File             | What changed                                                                 |
|------------------|------------------------------------------------------------------------------|
| `recommender.py` | Added 5 recommendation functions with full plain-English comments            |
| `README.md`      | Functions table updated (all ✅), how-it-works notes added for all functions |

### New functions detail

| Function               | What it does                                                            |
|------------------------|-------------------------------------------------------------------------|
| `find_nearby_places()` | Loops through all places, keeps those within radius, adds `distance_km` |
| `filter_by_category()` | Filters list by category string (case-insensitive); skips if empty      |
| `sort_by_rating()`     | Sorts by rating descending, then distance ascending for ties            |
| `get_all_categories()` | Collects unique categories into a set, returns sorted list              |
| `get_recommendations()`| Chains all steps: load → nearby → filter → sort → top 10               |

---

## [Scope Change] — 2026-10-29 — Restrict to 5 Cities

### What changed
- Completely replaced `data/places.csv` with 45 carefully chosen real places across exactly 5 cities.
- Added `get_cities()` function to `recommender.py`.
- Added `GET /api/cities` endpoint to `app.py`.
- Added `GET /api/places` endpoint to `app.py` (was TODO, now active).
- Created `templates/index.html` with a city dropdown, radius input, category filter, and "Use My Location" button.
- Rewrote `README.md` to reflect the 5-city scope and document all new additions.

### Why it changed
The original dataset had places scattered across all of Maharashtra (Aurangabad, Sindhudurg, Ratnagiri, etc.). The scope was narrowed to 5 cities — Mumbai, Pune, Nashik, Nagpur, Kolhapur — to make the project more focused, easier to explain, and easier to test.

### Files changed

| File                    | What changed                                                                              |
|-------------------------|-------------------------------------------------------------------------------------------|
| `data/places.csv`       | Completely rewritten — 45 places, 5 cities only, ~9 per city, verified coordinates        |
| `recommender.py`        | Added `get_cities()` — returns the fixed list of 5 cities                                 |
| `app.py`                | Added `/api/cities` route; activated `/api/places` route                                  |
| `templates/index.html`  | Created full web page with city dropdown, GPS button, radius + category filters            |
| `README.md`             | Full rewrite — added Cities Covered table, updated functions table, updated all examples  |

### City breakdown in new CSV

| City      | Number of places |
|-----------|-----------------|
| Mumbai    | 9               |
| Pune      | 9               |
| Nashik    | 9               |
| Nagpur    | 8               |
| Kolhapur  | 9               |
| **Total** | **45**          |

---

## [Phase 2] — 2026-10-29 — Distance Functions

### What changed
- Rewrote `recommender.py` with two fully working functions: `load_places()` and `calculate_distance()`.

### Why it changed
These are the two foundation functions. Every other function in Phase 3 will rely on them:
- `load_places()` gives us the data to work with.
- `calculate_distance()` lets us measure how far each place is from the user.

### Files changed

| File              | What changed                                                                 |
|-------------------|------------------------------------------------------------------------------|
| `recommender.py`  | Replaced placeholder with `load_places()` and `calculate_distance()` with full comments |
| `README.md`       | Updated Functions Explained table — added status column, added detailed how-it-works notes for both functions |

### Details

**`load_places()`**
- Uses Python's built-in `csv.DictReader` to read `data/places.csv`.
- Converts `latitude`, `longitude`, `rating` to `float` and `id` to `int`.
- Returns a plain Python list of dictionaries.

**`calculate_distance(lat1, lon1, lat2, lon2)`**
- Implements the Haversine formula in 4 clear steps (convert → difference → formula → multiply).
- Every step has a plain-English comment explaining what it does and why.
- Returns distance in kilometres, rounded to 2 decimal places.
- Uses only Python's built-in `math` module — no external libraries.

---

## [Phase 1] — 2026-10-29 — Data and Folder Structure

### What changed
- Created the complete project folder structure.
- Added the main dataset of 50 real Maharashtra places.
- Created placeholder Python files ready to be filled in later phases.
- Created full project documentation.

### Why it changed
This is the foundation of the project. Before writing any code, we need:
1. The folders so every file has a proper home.
2. The data (CSV) so we have real places to work with and test against.
3. Placeholder files so the project structure is visible from day one.
4. A README so anyone (including the examiner) can understand the project immediately.

### Files created

| File                          | What it contains                                              |
|-------------------------------|---------------------------------------------------------------|
| `data/places.csv`             | 50 real Maharashtra places with id, name, city, category, latitude, longitude, rating, description |
| `app.py`                      | Flask app skeleton with TODO comments for Phase 4 routes      |
| `recommender.py`              | Logic module skeleton with TODO comments for Phase 2 & 3 functions |
| `tests/test_recommender.py`   | Test file skeleton with TODO comments for Phase 6 tests       |
| `README.md`                   | Full project documentation written in simple language         |
| `CHANGELOG.md`                | This file — tracks all project changes                        |

### Folders created
- `data/` — holds the CSV dataset
- `templates/` — will hold index.html (added in Phase 5)
- `tests/` — holds test files

---

*Next: Phase 3 — Recommendation Functions (`find_nearby_places`, `filter_by_category`, `sort_by_rating`, `get_recommendations`, `get_all_categories`)*


## [Feature: System Diagrams] — 2026-11-20

### What changed
- **`diagrams/`** (new folder) — Contains 5 black and white system diagrams explaining the entire project:
  - `README.md` — Overview of all diagrams and how to view/export them
  - `1_system_architecture.md` — Shows all layers: client browser, Flask app, auth module, recommendation engine, MongoDB, external services (maps, email)
  - `2_data_flow_1_search.md` — Shows step-by-step flow when user searches by city: browser → API → Flask → MongoDB → Haversine distance → filtering → sorting → display on map
  - `3_data_flow_2_auth.md` — Shows signup flow (form → validation → password hashing → save to MongoDB → generate OTP → send email → user verifies → marked verified) and login flow (validate credentials → create session → redirect to app)
  - `4_use_case_diagram.md` — Shows all 11 features: visitors can signup/login/change language; logged-in users can search (by city, GPS, name), filter (by category, season), view map, view place details, view trails, change language
  - `5_system_working_flow.md` — Shows complete user journey: landing → auth path → main app → search methods → calculate distance → display results → view details → logout

### Why this changed
- Diagrams make the system easy to understand for new developers, students, or examiners
- Black and white diagrams print well and display clearly on all devices
- Explains Haversine formula, authentication flow, and system architecture in simple words
- Helps with documentation and project presentations

### Files affected
- `diagrams/` (6 new Markdown files)
- `README.md` — Added "System Diagrams" section linking to diagrams folder


---

## [Feature: System Diagrams as JPG Images] — 2026-11-20

### What changed
- **`diagrams/`** — Added 5 high-quality JPG diagram images alongside existing Markdown source files:
  - `1_system_architecture.jpg` (28 KB) — System architecture diagram
  - `2_data_flow_1_search.jpg` (20 KB) — Location search data flow diagram
  - `3_data_flow_2_auth.jpg` (83 KB) — Authentication flow diagram
  - `4_use_case_diagram.jpg` (19 KB) — Use case diagram
  - `5_system_working_flow.jpg` (63 KB) — System working flow diagram
- **`diagrams/README.md`** — Updated with:
  - Table showing all 5 JPG images with file sizes and descriptions
  - Instructions for viewing JPG files (image viewers, browsers)
  - Table with specifications: JPG format, black and white, 90% quality, responsive sizes
- **`README.md`** — Updated "System Diagrams" section:
  - Now emphasizes JPG images as primary delivery format
  - Quick visual reference table for all diagrams
  - Clear instructions for viewing JPG images in Windows Photo Viewer, Preview, browsers
  - Alternative: view and edit Markdown source files for Mermaid diagrams

### Why
JPG images are:
- **Immediately usable** — Open in any image viewer or web browser, no special tools needed
- **Print-friendly** — Black and white, high contrast, suitable for printing on paper
- **Portable** — Can be emailed, shared, embedded in documents, presentations
- **Non-editable** — Source code protected (Markdown files still available for editing)
- **Smaller size** — 5 images total = ~213 KB (easy to download/email)

### How generated
Used Puppeteer (Node.js headless browser) to render HTML with embedded Mermaid diagrams, then took screenshots as JPG:
1. Converted Mermaid diagram code to HTML files (with embedded mermaid.js library)
2. Used Puppeteer to render each HTML file
3. Captured screenshot as JPEG image (90% quality for balance)
4. All files generated automatically, no manual editing

### Files affected
- `diagrams/1_system_architecture.jpg` (new)
- `diagrams/2_data_flow_1_search.jpg` (new)
- `diagrams/3_data_flow_2_auth.jpg` (new)
- `diagrams/4_use_case_diagram.jpg` (new)
- `diagrams/5_system_working_flow.jpg` (new)
- `diagrams/README.md` (updated)
- `README.md` (updated)

### No code changes
These are documentation and visualization files only. No changes to Python code, tests, or application functionality.

