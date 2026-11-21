# Location Based Recommendation System — Popular Places of Maharashtra

---

## What is this project?

This project helps you find popular places to visit in Maharashtra, India.

You tell the system where you are — by picking a city from a dropdown or sharing your GPS location — and it shows you the best nearby places like forts, temples, beaches, caves, and monuments, sorted by rating.

**Real example:** Pick Pune with a 50 km radius → the system returns Aga Khan Palace (5.91 km, ⭐4.5), Sinhagad Fort (20.23 km, ⭐4.5), Torna Fort (36.73 km, ⭐4.5), Shaniwar Wada (0.18 km, ⭐4.4), and more.

**The problem it solves:** Maharashtra has hundreds of great places but most people do not know what is nearby. This system gives free, instant suggestions — no paid API, no machine learning, no complicated setup.

> This project covers **6 cities**: Mumbai, Pune, Nashik, Nagpur, Kolhapur and Nanded — with 53 real places in the dataset.

---

## Tech Stack

| Tool | What it is | Why we used it |
|------|-----------|----------------|
| Python 3 | Programming language | Simple, easy to read |
| Flask | Python web framework | Turns Python into a web server |
| Flask session | Cookie-based login memory | Remembers who is logged in |
| MongoDB (local) | Database on your computer | Stores places and users |
| pymongo | Python driver for MongoDB | Lets Python talk to MongoDB |
| python-dotenv | Reads the `.env` file | Keeps secrets out of code |
| werkzeug.security | Password hashing (comes with Flask) | Hashes passwords so plain text is never stored |
| smtplib | Email sender (built into Python) | Sends OTP verification emails |
| CSV file | Simple data file | Backup and seeding source |
| HTML + CSS + JavaScript | Web page languages | Builds the browser UI |
| Leaflet.js | Free map library | Draws interactive map with pins |
| OpenStreetMap | Free world map | Map background tiles, no API key |
| unittest | Python's built-in test module | Tests every function |

---

## How it Works — 5 Simple Steps

1. **Load the data** — Read all 53 places from the MongoDB `places` collection (45 original + 8 Nanded).

2. **Get your location** — Pick a city (system uses its centre coordinates) or click "Use My Location" (browser shares real GPS).

3. **Calculate distance** — For every place returned from MongoDB, calculate how far it is from you using the **Haversine formula** (explained below).

4. **Filter and rank** — Keep only places within your chosen radius. Filter by category if you want. Sort: highest rating first; closest first if ratings are equal.

5. **Show results** — Top 10 places appear as cards on the left and numbered red pins on the map on the right.

---

## How "Use My Location" Works — 5 Simple Steps

1. **Click the button** — The page calls `navigator.geolocation.getCurrentPosition()`. This is a function built into every modern browser. The browser asks the user for permission.

2. **Browser shares GPS** — If the user allows, the browser returns `position.coords.latitude` and `position.coords.longitude`. These are shown on the page: `"Your location: 19.1383, 77.3210"`. If the user denies or GPS fails, a clear error message is shown (see below).

3. **Nearest city** — JavaScript calls `GET /api/nearest-city?lat=19.14&lon=77.32`. Flask runs `get_nearest_city()` which calls `calculate_distance()` for each of the 6 cities and returns the name of the closest one. The page shows: `"Nearest city: Nanded"`.

4. **Recommend API call** — JavaScript calls `GET /api/recommend?lat=19.14&lon=77.32&radius=50`. Flask runs `get_recommendations()` and returns the top 10 nearby places.

5. **Fallback if no results** — If the radius returns 0 places, JavaScript calls `GET /api/nearest-places?lat=...&lon=...`. This endpoint ignores the radius and returns the 5 closest places in the entire dataset, sorted by distance. The page shows: `"No places within 50 km. Showing the nearest places instead."`

### GPS error messages

| What happened | Error code | Message shown to user |
|---|---|---|
| User clicked "Block" | 1 (PERMISSION_DENIED) | "Location permission denied. Please allow location access or choose a city." |
| GPS hardware unavailable | 2 (POSITION_UNAVAILABLE) | "Location not available. Your device could not determine your position." |
| Took too long | 3 (TIMEOUT) | "Location request timed out. Please try again or choose a city." |

---

## Cities Covered

| City | Centre (lat, lon) | Places |
|------|------------------|--------|
| Mumbai | 19.0760, 72.8777 | 9 |
| Pune | 18.5204, 73.8567 | 9 |
| Nashik | 20.0059, 73.7897 | 9 |
| Nagpur | 21.1458, 79.0882 | 9 |
| Kolhapur | 16.7050, 74.2433 | 9 |
| Nanded | 19.1383, 77.3210 | 8 |
| **Total** | | **53** |

---

## Folder Structure — Every File Explained

```
maharashtra-places/
│
├── app.py                  ← Flask server. Has 5 place routes + auth routes.
│
├── recommender.py          ← All 8 recommendation logic functions.
│
├── database.py             ← MongoDB connection functions.
│
├── email_service.py        ← Sends emails via Gmail SMTP (port 587, TLS).
│                             Falls back to terminal print if credentials missing.
│                             One function: send_email(to_email, subject, body).
│
├── auth.py                 ← All 17 authentication functions: signup, login,
│                             OTP, email, session, forgot password, reset password.
│
├── seed_places.py          ← One-time script. Inserts 45 places into MongoDB.
│
├── data/
│   └── places.csv          ← Dataset backup. 45 rows, 8 columns.
│
├── templates/
│   ├── index.html          ← Main web page (map + results).
│   ├── signup.html         ← Signup form (name, email, password).
│   ├── verify.html         ← OTP entry form + Resend button.
│   ├── login.html          ← Login form + Forgot password? link.
│   ├── forgot_password.html← "Enter your email" form for password reset.
│   └── reset_password.html ← OTP + new password form. Resend + 5-attempt lock.
│
├── tests/
│   ├── test_recommender.py ← 47 tests for recommendation functions.
│   └── test_auth.py        ← 34 tests for all auth functions.
│
├── .env                    ← YOUR SECRET FILE. MONGO_URI, SECRET_KEY,
│                             EMAIL_ADDRESS, EMAIL_PASSWORD. Never share.
│
├── .env.example            ← Safe template with fake values. Safe to share.
├── .gitignore              ← Blocks .env, __pycache__, venv/ from Git.
├── requirements.txt        ← All Python libraries. pip install -r requirements.txt
├── README.md               ← This file.
└── CHANGELOG.md            ← Diary of every change.
```

---

## Project Phases — What Was Built and Why

### Phase 1 — Data and Folder Structure
**Done:** Created all folders, `data/places.csv` (initially 50 places), and placeholder files for `app.py`, `recommender.py`, and `tests/`.

**Why:** The foundation. You need a folder structure and real data before writing any code.

---

### Scope Change — Restricted to 5 Cities
**Done:** Replaced the CSV with 45 places across exactly 5 cities. Added `get_cities()` function and `/api/cities` route. Added city dropdown to the web page.

**Why:** Narrowing to 5 major cities keeps the project focused, manageable, and easy to test and explain.

---

### Phase 2 — Distance Functions
**Done:** Wrote `load_places()` (reads CSV → list of dicts) and `calculate_distance()` (Haversine formula).

**Verified:** Pune → Mumbai = **120.15 km** ✅

**Why:** These are the foundation functions. Every other function depends on them.

---

### Phase 3 — Recommendation Logic
**Done:** Wrote `find_nearby_places()`, `filter_by_category()`, `sort_by_rating()`, `get_all_categories()`, and `get_recommendations()`.

**Why:** This is the brain of the system — turns raw data into actual recommendations.

---

### Phase 4 — Flask API
**Done:** Wrote all 5 routes in `app.py`: `GET /`, `/api/cities`, `/api/places`, `/api/categories`, `/api/recommend`. Added input validation with helpful error messages.

**Why:** Connects the Python logic to the browser. Without routes, no one can access the system.

---

### Phase 5 — Web Page
**Done:** Built the full `templates/index.html` — split layout (panel + map), city dropdown, radius slider (5–200 km), category filter, result cards with colour badges, Leaflet map with user circle and numbered red pins.

**Why:** Makes the system usable by anyone — not just developers who know how to type API URLs.

---

### MongoDB Step 1 — Packages, database.py, .env setup ✅
**Done:**
- Installed `pymongo` and `python-dotenv`.
- Created `requirements.txt`, `.env`, `.env.example`, `.gitignore`.
- Created `database.py` with 4 functions: `get_database()`, `get_places_collection()`, `get_users_collection()`, `test_connection()`.
- Verified: `py database.py` → `Connected to MongoDB!`

**Why:** The foundation for MongoDB. `database.py` is the single place that handles the connection — every other file just imports from it.

---

### MongoDB Step 2 — Seed the database ✅
**Done:** Created `seed_places.py` — reads `data/places.csv` and inserts 45 place documents into MongoDB. Duplicate-safe via `find_one()` check.

**Verified:**
- Run 1: `Inserted 45 new places. Total: 45` ✅
- Run 2: `0 new places inserted (45 already existed, skipped). Total: 45` ✅

**Also fixed:** Row 17 (Lonavala) in `data/places.csv` had an unquoted comma in its description. Wrapped in double quotes to fix the CSV parse error.

---

### MongoDB Step 3 — load_places() reads from MongoDB ✅
**Done:** Changed `load_places()` in `recommender.py` to call `collection.find({}, {"_id": 0})` instead of opening the CSV. `{"_id": 0}` hides MongoDB's internal `_id` field so the rest of the code is unaffected. Removed the `csv` import. All other 7 functions unchanged.

**Why:** This is the only line where data comes from — changing it here changes the entire system. The Haversine logic, filtering, and sorting all stay exactly the same.

---

### MongoDB Step 4 — All API endpoints verified ✅
**Done:** Ran all 4 endpoints against MongoDB data using Flask's test client.

| Endpoint | Result |
|----------|--------|
| `GET /api/places` | 200, 45 docs, no `_id` field ✅ |
| `GET /api/cities` | 200, 5 cities ✅ |
| `GET /api/categories` | 200, 8 categories ✅ |
| `GET /api/recommend?lat=18.52&lon=73.85&radius=50` | 200, 6 results, `distance_km` present, no `_id` ✅ |

---

### MongoDB Step 5 — Tests still pass ✅
**Done:** Ran all 47 existing tests unchanged. All pass.

`Ran 47 tests in 0.668s — OK`

No test changes needed — MongoDB returns data in the same shape as the CSV did.

---

### MongoDB Step 6 — get_users_collection() prepared for future login ✅
**Done:** Added a clearly labelled comment block at the bottom of `recommender.py` showing how `get_users_collection()` will be used when the login/reviews feature is built. Includes stub code for `save_user()` and `find_user_by_email()`. All commented out — no active code added yet.

**Why:** The `users` collection exists in MongoDB and `get_users_collection()` is ready. The comment shows the examiner that the design is thought through even though the feature is not built yet.

---

### Auth Step 1 — Users collection + auth.py foundation ✅
**Done:**
- Added `SECRET_KEY`, `EMAIL_ADDRESS`, `EMAIL_PASSWORD` to `.env` and `.env.example`.
- Created `auth.py` with all 13 authentication functions (Steps 1–6 pre-written).
- Created a **unique index** on the `email` field of the `users` collection in MongoDB.

**Verified:**
```
Indexes on 'users' collection (2 total):
  name=_id_    key={'_id': 1}     unique=False   ← default MongoDB index
  name=email_1 key={'email': 1}   unique=True    ← our new index ✅
```

**Why:** The unique index on `email` means MongoDB will automatically reject any attempt to register a second account with the same email address. This is the database-level safety net — even if the code has a bug, the database will not allow duplicates.

---

### Auth Step 2 — Signup, Verify, Login, Logout pages ✅
**Done:**
- Rewrote `app.py` — added `SECRET_KEY`, all 8 auth routes, session protection on `GET /`.
- Created `templates/signup.html` — name, email, password, confirm password, flash messages.
- Created `templates/verify.html` — OTP input (6-digit, spaced), Verify button, Resend Code button.
- Created `templates/login.html` — email, password, flash messages, link to signup.
- Updated `templates/index.html` — header shows "Hello, \<name\>" and a Logout button.

**All 8 flow tests passed:**

| Test | Result |
|------|--------|
| GET /signup returns 200 | ✅ |
| Valid signup → redirect to /verify, user in DB, is_verified=False, OTP set, password hashed | ✅ |
| Duplicate email rejected with error message | ✅ |
| Password < 8 chars rejected | ✅ |
| Mismatched passwords rejected | ✅ |
| Unverified user → redirected to /verify on login attempt | ✅ |
| Correct OTP → is_verified=True, OTP cleared, redirect to /login | ✅ |
| Wrong OTP → stays on /verify with error message | ✅ |

**TEST MODE confirmed:** OTP printed to terminal when `EMAIL_ADDRESS` is empty in `.env`.

---

### Auth Step 3 — OTP email verification `[covered in Step 2 ✅]`

---

### Auth Step 4 — Login page `[covered in Step 2 ✅]`

---

### Auth Step 5 — Session + protect main page `[covered in Step 2 ✅]`

---

### Auth Step 6 — tests/test_auth.py ✅

**Done:** Wrote 18 unittest tests across 3 classes in `tests/test_auth.py`. All pass.

**One bug fixed during this step:** The test checking that passwords are hashed assumed werkzeug always produces a `$2b$` prefix (bcrypt). This version of werkzeug uses `pbkdf2:sha256:` instead — equally secure, just a different algorithm. The test was fixed to check for `:` in the hash (which all werkzeug formats use) rather than a specific prefix.

**Full test suite: 65 tests, 0 failures ✅**

| Class | Tests | What it checks |
|---|---|---|
| `TestSignup` | 9 | Page loads, valid signup, user in DB, password hashed, is_verified=False, OTP generated, duplicate email, short password, mismatched passwords |
| `TestOTP` | 4 | Wrong OTP rejected, correct OTP marks verified, OTP cleared after use, redirect to /login |
| `TestLogin` | 5 | Page loads, verified user can login, wrong password, unknown email, unverified user redirected |

**How to run all tests:**
```
py -m unittest discover tests -v
```

### Map Tile Fix ✅
**Done:** Fixed grey map background in `templates/index.html`.

**Root cause:** The Leaflet map was initialized at the top level of the script before the flexbox layout had settled. Leaflet thought its container was 0px tall and loaded no tiles — resulting in a grey background with only markers visible.

**Fixes applied:**

| Fix | What it does |
|-----|-------------|
| `map.invalidateSize()` in `window.onload` | Tells Leaflet to recalculate container size after the page layout has settled (100ms delay) |
| `map.invalidateSize()` after `showMarkers()` | Recalculates after results are displayed |
| `map.fitBounds()` after markers placed | Zooms the map to show all result markers at once |
| `min-height: 400px` on `#map` CSS | Guarantees the map div always has enough space |
| Tile URL changed to `https://tile.openstreetmap.org/{z}/{x}/{y}.png` | Simpler URL without subdomain prefix |
| CARTO fallback on `tileerror` | If OSM tiles fail 3+ times, switches to CARTO light tiles |
| Error message div under map | Shows "Map pictures could not be loaded..." if both fail (after 5s check) |

---

### Feature 2: Season filter ✅
**Done:**
- Added `filter_by_season(places, season)` to `recommender.py` — splits pipe-separated seasons field, case-insensitive, returns all if empty or "all".
- Added `season` parameter to `get_recommendations()` and `GET /api/recommend?...&season=monsoon`.
- Added a season dropdown (All / Monsoon / Winter / Summer) to `templates/index.html` — wired into both city search and GPS search.
- Added 14 new tests (11 unit + 3 API) to `tests/test_features.py`.

**Total test suite: 177 tests, 0 failures ✅**

---

### Feature 1: Place info card ✅
**Done:**
- Added 6 new columns to `data/places.csv`: `entry_fee`, `timings`, `best_time`, `time_needed`, `local_tip`, `seasons` — filled for all 53 places.
- Updated `seed_places.py` to use `update_one` with `upsert=True` — running it again UPDATES existing places with new fields instead of skipping them.
- Updated `templates/index.html` — both `showCards()` and `showSearchCards()` now display entry fee, timings, best time, time needed, and local tip on each card.
- Added 11 new tests in `tests/test_features.py`.

**Total test suite: 163 tests, 0 failures ✅**

---

### Feature 1 — Search by place name ✅
**Done:**
- Added `search_places(places, text)` to `recommender.py` — checks `name`, `city`, and `category` fields, case-insensitive, returns all if empty.
- Added `GET /api/search?q=..` to `app.py` — login required, returns matching places as JSON.
- Added a search box to `templates/index.html` with Enter-key support and `searchByText()` + `showSearchCards()` JS functions.
- Added 20 tests to `tests/test_features.py` — 15 unit tests on `search_places()` and 5 API tests on `/api/search`.

**Total test suite: 124 tests, 0 failures ✅**

---

### Nanded city + improved GPS location feature ✅
**Done:**
- Added 8 Nanded places to `data/places.csv` (ids 46–53) and seeded to MongoDB (53 total).
- Added `Nanded` to `get_cities()` — now 6 cities.
- Added `get_city_centres()` — returns GPS centre of all 6 cities.
- Added `get_nearest_city()` — uses `calculate_distance()` to find the closest city.
- Added 3 new API endpoints: `/api/city-centres`, `/api/nearest-city`, `/api/nearest-places`.
- Rewrote `templates/index.html`:
  - Shows `"Your location: 19.1383, 77.3210"` after GPS fires.
  - Shows `"Nearest city: Nanded"` using `/api/nearest-city`.
  - Radius is now a **dropdown** (10, 25, 50, 100, 200 km).
  - If no places found within radius → shows yellow fallback notice + 5 nearest places.
  - Clear error messages for each GPS failure reason (denied, unavailable, timeout).
  - `"Finding places near you..."` loading message while waiting for GPS.
- Added 23 new tests in `tests/test_nanded.py`.
- Updated `test_recommender.py` — 4 old tests updated (45→53 places, 5→6 cities).

**Total test suite: 104 tests, 0 failures ✅**

---

### Email Service + Forgot Password ✅
**Done:**
- Created `email_service.py` with `send_email(to_email, subject, body)` — Gmail SMTP, port 587, TLS. Falls back to terminal print in TEST MODE.
- Updated `auth.py` — `send_otp_email` now uses `email_service`; 4 new forgot/reset password functions added.
- Added routes to `app.py`: `GET/POST /forgot-password`, `GET/POST /reset-password`, `POST /resend-reset-otp`.
- Created `templates/forgot_password.html` and `templates/reset_password.html`; added "Forgot password?" link to `login.html`.
- Added 15 new tests (4 forgot + 11 reset) to `tests/test_auth.py`.

**Total test suite: 81 tests, 0 failures ✅**

---

### Phase 6 — Tests ✅
**Done:** Wrote 47 unit tests across 8 classes in `tests/test_recommender.py`. All 47 pass.

**Why:** Tests prove every function works correctly and will catch bugs if the code is changed later.

---

## The Dataset — data/places.csv

14 columns per row:

| Column | What it means | Example |
|--------|--------------|---------|
| id | Unique number 1–53 | 1 |
| name | Name of the place | Gateway of India |
| city | One of the 6 city names | Mumbai |
| category | Type of place | Monument |
| latitude | GPS north-south (decimal degrees) | 18.9220 |
| longitude | GPS east-west (decimal degrees) | 72.8347 |
| rating | Rating out of 5 | 4.7 |
| description | One-sentence description | Iconic arch monument... |
| entry_fee | Entry cost — "Free", "Rs 25", or "Check locally" | Free |
| timings | Opening hours | 24 hours |
| best_time | Best months to visit | October to February |
| time_needed | How long to spend there | 1 hour |
| local_tip | A one-line insider tip | Best viewed at sunset from the seafront |
| seasons | Pipe-separated: monsoon, winter, summer | winter|summer |

**8 categories:** Beach, Cave, Fort, Hill Station, Monument, Nature, Other, Temple

**Sample places:**

| City | Places |
|------|--------|
| Mumbai | Gateway of India, Marine Drive, Elephanta Caves, Siddhivinayak Temple, Juhu Beach |
| Pune | Shaniwar Wada, Sinhagad Fort, Aga Khan Palace, Karla Caves, Torna Fort |
| Nashik | Trimbakeshwar Temple, Sula Vineyards, Kalaram Temple, Ramkund, Pandavleni Caves |
| Nagpur | Deekshabhoomi, Dragon Palace Temple, Futala Lake, Ambazari Lake, Sitabuldi Fort |
| Kolhapur | Mahalaxmi Temple, Panhala Fort, Rankala Lake, Jyotiba Temple, New Palace |

---

---

## MongoDB — Simple Explanation

### What is MongoDB?

MongoDB is a **database** — a program that stores and organises data so your app can read and save it quickly.

In this project MongoDB replaces the CSV file as the place where places are stored.

**Simple words for three key MongoDB terms:**

| Word | What it means | Real-world comparison |
|------|--------------|----------------------|
| **Database** | A container that holds all your data for one project | A cupboard |
| **Collection** | A group of similar items inside the database | A shelf inside the cupboard |
| **Document** | One single item in a collection | One book on the shelf |

So in this project:
- **Database** → `maharashtra_places`
- **Collection** → `places` (holds 45 place documents), `users` (empty, for future use)
- **Document** → one place, e.g. `{"name": "Gateway of India", "city": "Mumbai", "rating": 4.7, ...}`

A MongoDB document looks exactly like a Python dictionary. That is why pymongo is so easy to use — you already know how to read dictionaries.

---

### How to Install Local MongoDB

1. Go to https://www.mongodb.com/try/download/community
2. Choose **MongoDB Community Server**, your OS, and click Download.
3. Run the installer. Accept all defaults.
4. MongoDB runs automatically as a Windows service on `localhost:27017`.

**Optional — MongoDB Compass (visual tool):**
1. Go to https://www.mongodb.com/try/download/compass
2. Download and install it.
3. Open Compass, connect with: `mongodb://localhost:27017`
4. You can see your database, collections, and documents visually — very useful for checking that the seed script worked.

---

### .env File Setup

The `.env` file holds your MongoDB connection string. It stays on your computer only — never uploaded to GitHub.

**Steps:**
1. The `.env` file was already created for you with:
   ```
   MONGO_URI=mongodb://localhost:27017
   ```
2. If you need to recreate it, copy `.env.example`:
   ```
   copy .env.example .env
   ```
3. For local MongoDB you do **not** need to change anything. The default value works.

**Why keep it in `.env`?**
If you later switch to MongoDB Atlas (cloud), you only need to change the value in `.env`. The code stays exactly the same. And if your URI ever contains a username and password, `.gitignore` makes sure it never leaks to GitHub.

---

### database.py — Functions

| Function | What it does |
|----------|-------------|
| `get_database()` | Reads `MONGO_URI` from `.env`, connects with `MongoClient`, returns the `maharashtra_places` database object |
| `get_places_collection()` | Calls `get_database()` and returns the `places` collection |
| `get_users_collection()` | Calls `get_database()` and returns the `users` collection (empty, reserved for future login feature) |
| `test_connection()` | Pings MongoDB and prints "Connected to MongoDB!" or a plain error message |

**Test the connection:**
```
py database.py
```
Expected output:
```
Connected to MongoDB!
Database: maharashtra_places
Collections available: []
```

**Q: What does `load_places()` do now that MongoDB is connected?**
A: It calls `get_places_collection()` to get the MongoDB `places` collection, then calls `collection.find({}, {"_id": 0})` to fetch all 45 documents. The `{"_id": 0}` hides MongoDB's internal `_id` field. It returns a plain Python list — the same shape as before, so all other functions work unchanged.

**Q: What does `{"_id": 0}` mean in the MongoDB query?**
A: Every document MongoDB stores gets an automatic field called `_id` — a unique identifier MongoDB creates itself. If we return it to the browser or pass it to other functions, it causes errors. `{"_id": 0}` is a projection that tells MongoDB: "include everything except `_id`". The `0` means "exclude this field".

**Q: Why did the 47 tests still pass after switching to MongoDB?**
A: Because `load_places()` returns data in exactly the same shape — a list of dictionaries with the same keys (`id`, `name`, `city`, `rating`, etc.) — whether it reads from CSV or MongoDB. The tests check the shape and values of the data, not where it comes from.

**Q: What is `get_users_collection()` for?**
A: It is reserved for a future login and reviews feature. Right now it returns the empty `users` collection from MongoDB. When the feature is built, it will store user documents like `{"name": "...", "email": "...", "password_hash": "..."}`. The function is already written in `database.py` and ready to use.

---

### seed_places.py — Load the CSV into MongoDB ✅

`seed_places.py` is a **one-time script** that reads `data/places.csv` and inserts each row as a document into the MongoDB `places` collection.

**Two functions inside seed_places.py:**

| Function | What it does |
|----------|-------------|
| `read_csv()` | Opens `data/places.csv`, reads every row as a dictionary, converts numeric columns to the right type (`int` / `float`), returns a list of 45 dictionaries |
| `seed()` | Loops through the 45 places; for each one calls `find_one()` to check if it already exists; inserts only if it does not; prints a summary at the end |

**How to run it (once only):**
```
py seed_places.py
```

**Output on first run:**
```
Reading places from data/places.csv ...
Found 45 places in CSV.
Inserted 45 new places into MongoDB.
Done! Total documents in 'places' collection: 45
```

**Output if you run it again (duplicate protection):**
```
Reading places from data/places.csv ...
Found 45 places in CSV.
0 new places inserted (45 already existed, skipped).
Done! Total documents in 'places' collection: 45
```

**How duplicate protection works:**
Before inserting each place, the script calls:
```python
existing = collection.find_one({"id": place["id"]})
```
`find_one()` searches the collection for a document where `id` matches. If it finds one, the place already exists and is skipped. If it returns `None`, the place is new and gets inserted.

**CSV bug fixed during Step 2:**
Row 17 (Lonavala) had a comma inside its description that was not wrapped in quotes. This caused Python's CSV reader to split the row incorrectly, creating a `None` key in the dictionary. Fixed by wrapping the description in double quotes in `data/places.csv`. All 45 rows are now clean.

**After running, check in MongoDB Compass:**
- Connect to `mongodb://localhost:27017`
- Open database `maharashtra_places`
- Open collection `places`
- You should see 45 documents, each with fields: `id`, `name`, `city`, `category`, `latitude`, `longitude`, `rating`, `description`

---

### Examiner Questions — MongoDB

**Q: What is MongoDB?**
A: MongoDB is a database that stores data as documents (like Python dictionaries). Each document is one record — in this project, one place. Documents live inside collections, and collections live inside a database.

**Q: What is the difference between a collection and a document?**
A: A collection is a group of similar items — like the `places` collection which holds all 45 places. A document is one single item inside a collection — like the document for "Gateway of India". A collection is like a shelf; a document is like a book on that shelf.

**Q: Why use MongoDB instead of a CSV file?**
A: A CSV file is simple but limited — it cannot be searched efficiently, it cannot handle multiple users writing at the same time, and it cannot store complex nested data. MongoDB can do all of these things and scales easily when the dataset grows.

**Q: What is pymongo?**
A: pymongo is the official Python library for MongoDB. It lets Python code talk to MongoDB — for example, `collection.find({})` reads all documents, `collection.insert_one(doc)` adds one document. We use it in `database.py` and `recommender.py`.

**Q: Why is the connection string in a .env file?**
A: The connection string may contain a username and password. Putting it in the code and uploading to GitHub would expose those credentials to everyone. The `.env` file stays only on your computer. `.gitignore` makes sure it is never uploaded.

**Q: What does `load_dotenv()` do?**
A: It is a function from the `python-dotenv` library. It reads the `.env` file and loads each `KEY=VALUE` line into Python's environment variables (`os.environ`). After calling it, `os.environ.get("MONGO_URI")` returns your connection string.

---

---

## Feature 1 — Search by Place Name

### What this feature does

The user types any text in the search box (a place name, a city, or a category) and the system returns all matching places. The search is **not case-sensitive**, so "fort", "Fort", and "FORT" all give the same result.

The search box sits at the top of the left panel. Press **Enter** or click the 🔍 button to search. Results appear as cards just like location-based results.

### How it works — step by step

```
1. User types "fort" in the search box and presses Enter
         ↓
2. JavaScript calls  GET /api/search?q=fort
         ↓
3. Flask reads q, loads all 53 places from MongoDB,
   calls search_places(places, "fort")
         ↓
4. search_places() loops through every place.
   For each place it checks:
     "fort" in name.lower()      e.g. "Sinhagad Fort"  ✓
     "fort" in city.lower()      e.g. no city = "fort"
     "fort" in category.lower()  e.g. category="Fort"  ✓
         ↓
5. Returns matching places as JSON.
   JavaScript shows them as result cards.
```

### New function — `search_places(places, text)`

```python
results = search_places(places, "Mumbai")
# Returns all places whose name, city or category contains "Mumbai"
# (case-insensitive).

results = search_places(places, "")
# Returns all 53 places — empty text means no filter.
```

**How it works inside:**
- Converts the search text to lowercase once: `query = text.strip().lower()`
- Loops through every place and checks if `query` appears in `name.lower()`, `city.lower()`, or `category.lower()`
- Returns a new list with only the matching places
- Returns all places unchanged if `text` is empty, `None`, or only spaces

### New API endpoint — `GET /api/search`

| Detail | Value |
|--------|-------|
| URL | `/api/search?q=fort` |
| Method | GET |
| Auth | Login required (returns 401 if not logged in) |
| Parameter | `q` — the search text (optional, default = empty = return all) |
| Returns | JSON list of matching place dictionaries |

**Example requests:**
```
/api/search?q=fort          → all places with "fort" in name/city/category
/api/search?q=Mumbai        → all Mumbai places
/api/search?q=Temple        → all Temple places
/api/search?q=              → all 53 places (no filter)
/api/search?q=xyznotreal    → []  (empty list)
```

### Tests — `tests/test_features.py`

20 tests were added for Feature 1:

| Class | Tests | What it checks |
|-------|-------|---------------|
| `TestSearchPlaces` | 15 | Name match, city match, category match, partial name, case-insensitive (upper/lower/mixed), empty string, None, whitespace, no match, returns list, returns dicts, cross-field match |
| `TestSearchAPI` | 5 | 401 without login, 200 with login, returns only matching places, empty q returns all 53, no match returns `[]` |

### Examiner Questions — Search

**Q: How does `search_places()` work?**
A: It takes a list of place dictionaries and a search text. It converts the text to lowercase once (`query = text.strip().lower()`), then loops through every place and checks if that lowercase text appears anywhere in the place's `name`, `city`, or `category` (all converted to lowercase too). It returns a new list with only the matching places. If the text is empty or `None`, it returns all places unchanged.

**Q: Why is the search case-insensitive?**
A: Because users type in different ways — someone might type "fort", "Fort", or "FORT". All three mean the same thing. Using `.lower()` on both the search text and the place fields makes the comparison fair regardless of how the user typed it.

**Q: Why does `/api/search` require login?**
A: Only registered, verified users should be able to use the system's features. The route checks `get_logged_in_user(session)` — if no user is logged in, it returns HTTP 401 (Unauthorized). This is the same protection as the main page.

---

## Email Validation

### What this feature does

Every email address entered anywhere in the app — signup, login, and forgot password — is now **validated before the database is touched**. Inputs like `1234`, `abc@`, `@gmail.com`, or `abc@gmail` are rejected immediately with a clear error message.

There are two layers of checking:

1. **Browser check (frontend):** The `<input type="email">` with a `pattern` attribute stops the form from being submitted if the format looks wrong. The user sees a browser tooltip instantly.

2. **Backend check (most important):** Even if someone bypasses the browser and sends a raw HTTP request, Flask calls `is_valid_email()` before doing anything. No database query is made for an invalid email.

---

### The validation rule in plain words

A valid email must follow this structure:

```
[username]  @  [domain name]  .  [2+ letters]
```

- **Username:** one or more letters, numbers, dots, underscores, `*`, `%`, `+`, or `-`
- **Then:** the `@` symbol
- **Domain:** one or more letters, numbers, dots, or dashes
- **Then:** a literal dot (`.`)
- **Extension:** at least 2 letters (e.g. `com`, `in`, `edu`, `uk`)

| Input | Valid? | Why |
|-------|--------|-----|
| `name@gmail.com` | ✅ | correct format |
| `a.b@college.edu.in` | ✅ | subdomain + multi-part extension |
| `user_name@domain.org` | ✅ | underscore is allowed in usernames |
| `user+tag@domain.com` | ✅ | `+` is allowed |
| `1234` | ❌ | no `@` or domain |
| `abc` | ❌ | no `@` |
| `abc@` | ❌ | nothing after `@` |
| `@gmail.com` | ❌ | nothing before `@` |
| `abc@gmail` | ❌ | no dot + extension |
| `abc @gmail.com` | ❌ | space is not allowed |
| `(>100 chars)` | ❌ | too long — max 100 characters |

---

### New functions in auth.py

| Function | What it does | Example |
|----------|-------------|---------|
| `clean_email(email)` | Strips spaces from both ends and converts to lowercase | `" Alice@Gmail.COM "` → `"alice@gmail.com"` |
| `is_valid_email(email)` | Returns `True` if the email matches the pattern, `False` otherwise | `is_valid_email("abc@")` → `False` |

### How `is_valid_email()` works

```python
import re   # re = regular expressions — Python's built-in pattern matching module

pattern = r"^[A-Za-z0-9._*%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
#           ^                                                     $   = full string match
#            [A-Za-z0-9._*%+-]+  = username (letters, numbers, ._*%+-)
#                               @  = the @ symbol
#                                [A-Za-z0-9.-]+  = domain name
#                                               \.  = literal dot
#                                                   [A-Za-z]{2,}  = 2+ letter extension

return re.match(pattern, email) is not None
# re.match() returns a Match object if the pattern fits, or None if not
```

### Where validation is applied

| Route | What happens |
|-------|-------------|
| `POST /signup` | `clean_email()` cleans the input; `is_valid_email()` checks it; error shown if invalid, database NOT touched |
| `POST /login` | Same — invalid email shows error, no database lookup |
| `POST /forgot-password` | Same — invalid email shows error; the safe "If registered..." message is NOT shown for invalid emails |

### Frontend pattern (HTML)

All three email inputs now have:
```html
<input
  type="email"
  pattern="[A-Za-z0-9._*%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"
  title="Enter a valid email like name@gmail.com"
  maxlength="100"
/>
<p>Enter a valid email like name@gmail.com</p>
```

- `type="email"` — browser does a basic format check
- `pattern` — our stricter rule shown as a browser tooltip on mismatch
- `maxlength="100"` — matches the backend 100-character limit
- Helper text below the box — always visible

### Tests — in tests/test_features.py

28 new tests were added for email validation:

| Class | Tests | What it checks |
|-------|-------|---------------|
| `TestIsValidEmail` | 18 | Valid: gmail, edu.in, +tag, underscore, numbers, hyphen domain, 2-letter TLD. Invalid: numbers only, letters only, missing domain, missing username, missing TLD, space, empty, None, too long (101 chars), 1-letter TLD, double @ |
| `TestCleanEmail` | 6 | Strip spaces, lowercase, both together, already clean, None → `""`, empty → `""` |
| `TestSignupEmailValidation` | 4 | Invalid email stays on page (200), shows error text, NOT saved in MongoDB, valid email passes (302) |

### Examiner Questions — Email Validation

**Q: What is a regular expression?**
A: A regular expression (regex) is a pattern that describes what a valid piece of text should look like. For example, the pattern `[A-Za-z]+` means "one or more letters". Python's built-in `re` module lets us use regex with `re.match(pattern, text)` — it returns a Match object if the pattern fits, or `None` if it does not.

**Q: Why do you check email both in the browser and in the backend?**
A: Browser validation (the `pattern` attribute) gives the user instant feedback without a server round-trip — it is fast and friendly. But browser checks can be bypassed by anyone who sends a direct HTTP request (using tools like Postman). The backend check (`is_valid_email()` in Flask) is the real safety net — it runs no matter how the request was sent.

**Q: Why did you add underscore `_` to the allowed characters?**
A: Underscores are valid in email local parts (the username before the `@`) according to the email standard (RFC 5321). The original pattern `[A-Za-z0-9.*%+-]` missed underscore, so addresses like `user_name@domain.com` were incorrectly rejected. Adding `_` to the character class fixed this.

**Q: What does `clean_email()` do and why is it a separate function?**
A: `clean_email()` removes spaces from both ends (`.strip()`) and converts to lowercase (`.lower()`). It is a separate function so every route calls exactly the same cleaning logic — no risk of one route forgetting to strip spaces or lowercase. A user might accidentally type `" Alice@Gmail.COM "` with a leading space; after cleaning it becomes `"alice@gmail.com"`, which is the standard form stored in MongoDB.

---

## Feature 1: Place Info Card

### What this feature does

Every place card now shows 6 extra details that help the user plan their visit: entry fee, timings, best time to visit, time needed, a local tip, and which seasons the place is good for.

### The 6 new fields

| Field | What it stores | Example |
|-------|---------------|---------|
| `entry_fee` | Cost to enter — "Free", "Rs 25", or "Check locally" | Free |
| `timings` | Opening hours | 9 AM to 5 PM (closed Mondays) |
| `best_time` | Best months to visit | October to February |
| `time_needed` | How long a typical visit takes | 2 hours |
| `local_tip` | A one-line insider tip from locals | Carry water — 200 steps with no shade |
| `seasons` | Pipe-separated list of good seasons | winter|summer |

### seed_places.py — now uses upsert

The old `seed_places.py` checked if a place existed by `id` and skipped it. Now it uses `update_one` with `upsert=True`:

```python
collection.update_one(
    {"id": place["id"]},    # find by id
    {"$set": place},         # set ALL fields to latest CSV values
    upsert=True              # insert if not found, update if found
)
```

Running `py seed_places.py` after adding new columns to the CSV will **update** all existing MongoDB documents with the new fields — no duplicates, no data loss.

### Places with "Check locally"

Three places have `entry_fee = "Check locally"` because their fees are uncertain or variable:

| Place | Why uncertain |
|-------|--------------|
| Osho Ashram (Pune) | Meditation courses have separate fees — check their website |
| Sitabuldi Fort (Nagpur) | Army-controlled — access and fees vary |
| Shalini Palace (Kolhapur) | Now a hotel — may charge for non-guests |

### Tests — in `tests/test_features.py`

11 new tests were added:

| Class | Tests | What it checks |
|-------|-------|---------------|
| `TestPlaceInfoFields` | 11 | All 53 places have all 6 new fields; seasons uses pipe separator; seasons only has valid values (monsoon/winter/summer); entry_fee not empty; "Check locally" is a valid value; API returns new fields |

### Examiner Questions — Place Info Card

**Q: Why did you add these 6 fields to the dataset?**
A: A recommendation system that only shows a name and rating is not very useful for planning a visit. Knowing the entry fee, timings, best season, and a local tip helps the user decide not just WHERE to go but WHEN and HOW.

**Q: What does "upsert" mean and why did you change seed_places.py to use it?**
A: "Upsert" is a MongoDB term meaning "update or insert". `update_one({"id": 1}, {"$set": place}, upsert=True)` finds the document with id=1 and updates all its fields. If no document with id=1 exists, it inserts a new one. This is better than the old insert-or-skip approach because running the seed script after adding new CSV columns will update existing documents with the new fields.

**Q: Why do some places have "Check locally" as the entry fee?**
A: For places like Osho Ashram (meditation course fees vary), Sitabuldi Fort (army-controlled, access changes), and Shalini Palace (now a hotel), the fee depends on circumstances we cannot know in advance. Writing "Check locally" is honest — it tells the user to verify rather than giving wrong information.

---

---

## Feature 2: Season Filter

### What this feature does

The user can now filter places by the best season to visit. A new dropdown offers four options: **All seasons**, **Monsoon**, **Winter**, and **Summer**. When a season is selected, the recommendation pipeline keeps only places whose `seasons` field includes that season.

### How it works

Each place in the dataset has a `seasons` field stored as a pipe-separated string, e.g. `"monsoon|winter"`. The `filter_by_season()` function splits this string by `|` and checks if the chosen season is in the resulting list.

```
User picks "Monsoon" from dropdown
         ↓
JavaScript adds &season=monsoon to the /api/recommend URL
         ↓
Flask calls get_recommendations(lat, lon, radius, category, "monsoon")
         ↓
filter_by_season() keeps only places where "monsoon" is in the seasons field
         ↓
Results are sorted by rating and returned as cards + map pins
```

### New function — `filter_by_season(places, season)`

```python
filter_by_season(places, "monsoon")  # → only places good in monsoon
filter_by_season(places, "")         # → all places (no filter)
filter_by_season(places, "all")      # → all places (case-insensitive)
```

**How it works inside:**
1. If `season` is empty, `None`, or `"all"` (case-insensitive) — returns all places unchanged.
2. Converts `season` to lowercase once.
3. For each place, splits `place["seasons"]` by `|` (e.g. `"monsoon|winter"` → `["monsoon", "winter"]`).
4. Keeps the place if the lowercase season is found in that list.

### New API parameter

| Parameter | Required | Default | Example |
|-----------|----------|---------|---------|
| `season` | No | `""` (all seasons) | `monsoon` |

**Example URL:**
```
/api/recommend?lat=18.5204&lon=73.8567&radius=200&season=monsoon
```

### How the recommendation pipeline now works

```
1. load_places()           → all 53 places from MongoDB
2. find_nearby_places()    → only places within radius_km
3. filter_by_category()    → only places matching category (if given)
4. filter_by_season()      → only places matching season (if given)  ← NEW
5. sort_by_rating()        → best rating first
6. [:10]                   → top 10 results
```

### Tests — in `tests/test_features.py`

14 new tests were added:

| Class | Tests | What it checks |
|-------|-------|---------------|
| `TestFilterBySeason` | 11 | Monsoon filter, winter filter, summer filter, empty=all, "all"=all (lowercase + uppercase), None=all, case-insensitive, nonexistent season=empty, returns list, does not include wrong season |
| `TestSeasonAPI` | 3 | API with season=monsoon returns only monsoon places, no season returns all, category+season combined works |

### Examiner Questions — Season Filter

**Q: How does `filter_by_season()` work?**
A: It takes a list of places and a season string. If the season is empty, None, or "all", it returns all places unchanged. Otherwise it converts the season to lowercase, then loops through each place, splits the place's `seasons` field by `|` (e.g. `"monsoon|winter"` becomes `["monsoon", "winter"]`), and keeps the place only if the chosen season is in that list.

**Q: Why use pipe `|` as the separator instead of commas?**
A: Because the CSV file already uses commas as the column separator. If we used commas inside the `seasons` field too, the CSV parser would think the seasons are separate columns. Pipe `|` is safe because it never appears in any other field.

**Q: Where does the season filter sit in the recommendation pipeline?**
A: It runs after `filter_by_category()` and before `sort_by_rating()`. The full chain is: load all places → keep only nearby ones → filter by category → filter by season → sort by rating → return top 10. Each filter makes the list smaller before the next step runs, so the sort operates on fewer items.

---

## All Functions Explained (recommender.py)

All functions are in `recommender.py`. Each does **exactly one thing** and is under 15 lines.

### Function 1 — `load_places()`

**What it does:** Reads all 45 places from the MongoDB `places` collection and returns a plain Python list of dictionaries, one per place.

```python
places = load_places()
# places[0] looks like:
# {'id': 1, 'name': 'Gateway of India', 'city': 'Mumbai',
#  'category': 'Monument', 'latitude': 18.922, 'longitude': 72.8347,
#  'rating': 4.7, 'description': 'Iconic arch monument...'}
```

**How it works step by step:**
1. Calls `get_places_collection()` from `database.py` to get the MongoDB `places` collection.
2. Calls `collection.find({}, {"_id": 0})`.
   - `{}` is an empty filter — means "get all documents, no conditions".
   - `{"_id": 0}` tells MongoDB to leave out its internal `_id` field from every result.
3. `find()` returns a MongoDB cursor — think of it like a for-loop over the database.
4. `list()` turns that cursor into a plain Python list so the rest of the code works normally.
5. Returns the list of 45 dictionaries — same shape as before when we read from CSV.

**Note:** `data/places.csv` is kept as a backup and is used by `seed_places.py` to load data into MongoDB. It is not used by `load_places()` any more.

---

### Function 2 — `calculate_distance(lat1, lon1, lat2, lon2)`

**What it does:** Returns the straight-line distance in kilometres between two GPS points.

```python
dist = calculate_distance(18.5204, 73.8567, 19.0760, 72.8777)
# dist = 120.15  (Pune to Mumbai)
```

**How it works step by step:**
1. Takes 4 numbers: your latitude, longitude and the place's latitude, longitude.
2. Converts all 4 from degrees to radians (`math.radians`).
3. Finds the difference in latitude (Δlat) and longitude (Δlon).
4. Applies the Haversine formula (see section below).
5. Multiplies by Earth's radius (6371 km).
6. Returns the result rounded to 2 decimal places.

---

### Function 3 — `get_cities()`

**What it does:** Returns the fixed list of 5 city names.

```python
get_cities()
# → ['Mumbai', 'Pune', 'Nashik', 'Nagpur', 'Kolhapur']
```

Hardcoded (not read from CSV) because the list never changes and hardcoding is simpler and faster. Used by `/api/cities` to fill the city dropdown.

---

### Function 3 — `get_cities()`

```python
get_cities()
# → ['Mumbai', 'Pune', 'Nashik', 'Nagpur', 'Kolhapur', 'Nanded']
```

Returns the hardcoded list of all 6 cities. Used by `/api/cities` to fill the city dropdown.

---

### Function 4 — `get_city_centres()`

```python
get_city_centres()
# → {'Mumbai': {'lat': 19.076, 'lon': 72.877}, 'Pune': ..., 'Nanded': {'lat': 19.1383, 'lon': 77.3210}}
```

Returns a dictionary mapping each city name to its GPS centre coordinates. Used by the web page (via `/api/city-centres`) to search from a city's centre, and by `get_nearest_city()` to calculate which city is closest.

---

### Function 5 — `get_nearest_city(user_lat, user_lon)`

```python
get_nearest_city(19.1383, 77.3210)
# → "Nanded"
```

**How it works:**
1. Calls `get_city_centres()` to get all 6 city centres.
2. Loops through each city, calling `calculate_distance()` between the user and that city.
3. Keeps track of the smallest distance seen so far.
4. Returns the name of the city with the smallest distance.

---

### Function 6 — `search_places(places, text)`

**What it does:** Searches all places and keeps only those whose `name`, `city`, or `category` contains the search text. Case-insensitive.

```python
search_places(places, "fort")
# → all places with "fort" in name, city, or category

search_places(places, "Mumbai")
# → all Mumbai places (city field matches)

search_places(places, "")
# → all 53 places — empty text means no filter
```

**How it works:**
1. If `text` is empty, `None`, or only spaces — returns all places unchanged.
2. Converts `text` to lowercase once: `query = text.strip().lower()`.
3. Loops through every place; checks if `query` appears in `name.lower()`, `city.lower()`, or `category.lower()`.
4. Returns a new list of matching places.

---

### Function 7 — `find_nearby_places(places, user_lat, user_lon, radius_km)`

**What it does:** Keeps only places within `radius_km` of the user. Also adds a `distance_km` key to each kept place.

```python
nearby = find_nearby_places(places, 18.5204, 73.8567, 30)
# Returns places within 30 km of Pune.
# Each place now has: nearby[0]['distance_km'] = 0.18
```

**How it works:**
1. Loops through every place.
2. Calls `calculate_distance()` for each one.
3. If the distance ≤ `radius_km`, adds `distance_km` to the dict and keeps it.
4. Returns the filtered list.

---

### Function 8 — `filter_by_category(places, category)`

**What it does:** Keeps only places matching the category. Returns all places if category is empty.

```python
filter_by_category(places, "Fort")   # → only forts
filter_by_category(places, "")       # → all places unchanged
filter_by_category(places, "fort")   # → also works (case-insensitive)
```

**How it works:** Uses `.lower()` on both sides before comparing, so `"fort"`, `"Fort"`, and `"FORT"` all match. If `category` is `""` or `None`, returns the list unchanged.

---

### Function 9 — `sort_by_rating(places)`

**What it does:** Returns a new list sorted by rating (highest first). Uses distance as a tie-breaker.

```python
sorted_p = sort_by_rating(places)
# sorted_p[0] has the highest rating.
# If two places share a rating, the closer one comes first.
```

**How it works:** Uses Python's `sorted()` with two keys: `-rating` (minus = descending) and `distance_km` (ascending). The second key only applies when ratings are equal. Does **not** change the original list.

---

### Function 10 — `get_all_categories(places)`

**What it does:** Returns a sorted list of all unique category names in the data.

```python
get_all_categories(places)
# → ['Beach', 'Cave', 'Fort', 'Hill Station', 'Monument', 'Nature', 'Other', 'Temple']
```

**How it works:** Loops through all places, adds each `category` to a Python `set` (sets remove duplicates automatically), then returns `sorted(set)`.

---

### Function 11 — `get_recommendations(user_lat, user_lon, radius_km, category="")`

**What it does:** The main function. Chains all the other functions and returns the top 10 best nearby places.

```python
get_recommendations(18.5204, 73.8567, 50, "Fort")
# → top forts within 50 km of Pune, best rating first, max 10 results
```

**The chain:**
```
1. load_places()           → all 45 places from MongoDB
2. find_nearby_places()    → only places within radius_km (adds distance_km)
3. filter_by_category()    → only places matching category (skip if empty)
4. sort_by_rating()        → best rating first, closest first for ties
5. [:10]                   → keep only the top 10
```

---

## How the Distance Formula Works

The Earth is **round**, not flat. Subtracting two latitudes gives the wrong answer because it ignores the curve of the Earth. The **Haversine formula** solves this.

**Simple analogy:** Imagine pressing a pin into a globe at Pune and another at Mumbai, then stretching a string along the globe's surface between them. The Haversine formula tells you exactly how long that string is.

**The formula step by step:**

```
Step 1 — Convert degrees to radians
         Python's sin() and cos() use radians, not degrees.
         radians = degrees × (π ÷ 180)

Step 2 — Find the differences
         Δlat = lat2 − lat1    (north-south gap)
         Δlon = lon2 − lon1    (east-west gap)

Step 3 — Haversine formula
         a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
         c = 2 × atan2(√a, √(1−a))

Step 4 — Multiply by Earth's radius
         distance = 6371 × c      (6371 km = Earth's average radius)
```

**Real proof:** Pune (18.5204, 73.8567) → Mumbai (19.0760, 72.8777) = **120.15 km** ✅

---

## The Tests — tests/test_recommender.py

We use Python's built-in `unittest` module. No extra libraries needed.

**How to run all tests (recommender + auth together):**
```
py -m unittest discover tests -v
```
Expected: `Ran 177 tests ... OK`

| Test Class | Tests | What it checks |
|---|---|---|
| `TestLoadPlaces` | 7 | Returns a list, 45 items, correct types, 5 cities, ratings 1–5 |
| `TestCalculateDistance` | 6 | Pune→Mumbai ≈120km, same point=0, positive, symmetric, float |
| `TestGetCities` | 3 | Returns list, exactly 5 cities, correct names |
| `TestFindNearbyPlaces` | 6 | Returns list, all within radius, distance_km added, large/small radius |
| `TestFilterByCategory` | 6 | Forts, temples, empty string, None, case-insensitive, nonexistent |
| `TestSortByRating` | 5 | First=highest, last=lowest, descending order, tie-breaker, no mutation |
| `TestGetAllCategories` | 5 | Returns list, 8 items, no duplicates, alphabetical, correct names |
| `TestGetRecommendations` | 9 | List, max 10, distance_km, within radius, category filter, top rating first |

---

## API Endpoints — All Routes in app.py

| Route | What it returns |
|-------|----------------|
| `GET /` | Serves the web page (`templates/index.html`) |
| `GET /api/cities` | `["Mumbai","Pune","Nashik","Nagpur","Kolhapur"]` |
| `GET /api/places` | All 45 places as JSON |
| `GET /api/categories` | `["Beach","Cave","Fort","Hill Station","Monument","Nature","Other","Temple"]` |
| `GET /api/recommend?lat=..&lon=..&radius=..&category=..` | Up to 10 recommended places with `distance_km` |

**`/api/recommend` parameters:**

| Parameter | Required | Default | Example |
|-----------|----------|---------|---------|
| `lat` | YES | — | `18.5204` |
| `lon` | YES | — | `73.8567` |
| `radius` | No | `50` | `100` |
| `category` | No | `""` (all) | `Fort` |

**Example URLs (paste in browser while Flask is running):**
```
http://127.0.0.1:5000/api/recommend?lat=18.5204&lon=73.8567&radius=50
http://127.0.0.1:5000/api/recommend?lat=19.0760&lon=72.8777&radius=100&category=Fort
http://127.0.0.1:5000/api/recommend?lat=20.0059&lon=73.7897&radius=20&category=Temple
http://127.0.0.1:5000/api/categories
http://127.0.0.1:5000/api/cities
```

**Error responses:**
```json
{"error": "lat and lon are required. Example: ?lat=18.52&lon=73.85&radius=50"}
{"error": "lat, lon and radius must be numbers."}
```

---

## How to Run the Project from Scratch

### Step 1 — Check Python is installed
```
py --version
```
You need Python 3. Download from https://python.org if not installed.

### Step 2 — Install all libraries at once
```
pip install -r requirements.txt
```
This installs Flask, pymongo, and python-dotenv in one command.

### Step 3 — Create your .env file
The `.env` file is already included with:
```
MONGO_URI=mongodb://localhost:27017
```
If it is missing, copy from `.env.example`:
```
copy .env.example .env
```

### Step 4 — Make sure MongoDB is running
MongoDB should start automatically as a Windows service. To check, open **MongoDB Compass** and connect to `mongodb://localhost:27017`. If it connects, MongoDB is running.

### Step 5 — Seed the database (first time only)
```
py seed_places.py
```
Expected: `Done! Total documents in 'places' collection: 45`

You only need to run this once. After that the data lives in MongoDB permanently.

### Step 6 — Test the MongoDB connection
```
py database.py
```
Expected: `Connected to MongoDB!`

### Step 7 — Start the server
```
py app.py
```
You will see:
```
 * Running on http://127.0.0.1:5000
```

### Step 8 — Open the web page
Open your browser and go to:
```
http://127.0.0.1:5000
```

### Step 9 — Run the tests (optional)
```
py -m unittest tests/test_recommender.py -v
```
Expected output: `Ran 47 tests ... OK`

### Step 10 — Stop the server
Press `Ctrl + C` in the terminal.

---

## Questions an Examiner May Ask

**Q1. What is this project and what problem does it solve?**
This is a Location Based Recommendation System for popular places in Maharashtra. It solves the problem of not knowing what tourist places are nearby. You enter your location and get the top 10 nearby places sorted by rating.

**Q2. Why did you add Nanded to the system?**
Nanded is one of Maharashtra's most significant religious and historical cities, home to the Hazur Sahib Gurudwara (one of Sikhism's five Takhts) and several other important sites. Adding it makes the system more representative of Maharashtra's diversity.

**Q3. What is `navigator.geolocation.getCurrentPosition()` and what does it do?**
It is a function built into every modern browser. When called, it asks the user for permission to share their GPS location. If allowed, it returns the device's latitude and longitude. We pass it a success callback (runs when GPS works) and an error callback (runs when GPS fails or is denied).

**Q4. How do you show the user's coordinates on the page?**
After the browser returns the GPS position, JavaScript reads `position.coords.latitude` and `position.coords.longitude`. It rounds them to 4 decimal places with `.toFixed(4)` and sets the text of a hidden `<div>` to `"Your location: 19.1383, 77.3210"`. The div is made visible (`display:block`) only after GPS succeeds.

**Q5. How does `get_nearest_city()` work?**
It calls `get_city_centres()` to get the GPS centre of each of the 6 cities. It loops through all 6, calling `calculate_distance()` for each one, and keeps track of the smallest distance found. At the end it returns the name of the city with the smallest distance.

**Q6. What happens if no places are found within the chosen radius?**
`/api/recommend` returns an empty list. JavaScript detects this and calls `/api/nearest-places` instead. This endpoint ignores the radius and returns the 5 closest places in the entire dataset, sorted by distance. The page shows: `"No places within 50 km. Showing the nearest places instead."`

**Q7. What GPS error messages are shown and why are there three?**
There are three GPS error codes: 1=PERMISSION_DENIED (user clicked Block), 2=POSITION_UNAVAILABLE (device hardware failed), 3=TIMEOUT (took too long). Each gets its own friendly message so the user knows exactly what went wrong and what to do next.

**Q8. What is `get_city_centres()` and why is it a separate function?**
It returns a dictionary with the GPS centre coordinates of all 6 cities. It is a separate function (not hardcoded in the web page) so the same data is used in both the dropdown search and the nearest-city calculation. It also means if coordinates need to be updated, there is only one place to change them.

**Q2. Why did you choose only 6 cities?**
To keep the project focused and easy to explain. Mumbai, Pune, Nashik, Nagpur, Kolhapur, and Nanded are major cities representing different regions of Maharashtra. Adding more cities is easy — just add rows to the CSV and seed MongoDB.

**Q3. What is the Haversine formula and why do you use it?**
It is a maths formula that calculates the real distance between two GPS points on a round Earth. We use it instead of simply subtracting latitudes because the Earth is round and simple subtraction gives the wrong answer. It uses `sin`, `cos`, and `atan2` from Python's `math` module.

**Q4. What does `load_places()` do?**
It opens `data/places.csv` using Python's `csv.DictReader`, reads each row as a dictionary, converts the numeric columns from strings to numbers (`float` and `int`), and returns a list of 45 dictionaries.

**Q5. What does `get_recommendations()` do?**
It is the main function that chains four steps: load all places, keep only those within the radius, filter by category if given, sort by rating, and return the top 10. It calls `load_places`, `find_nearby_places`, `filter_by_category`, and `sort_by_rating`.

**Q6. Why do you sort by rating first and not by distance?**
Because a highly-rated place a bit farther away gives a better visitor experience than a poorly-rated place that is slightly closer. Distance is only used as a tie-breaker when two places have the same rating.

**Q7. What does Flask do in this project?**
Flask is a Python web framework. It listens for HTTP requests from the browser, reads the URL parameters (like `lat`, `lon`, `radius`), calls the right Python function from `recommender.py`, and sends back the result as JSON.

**Q8. What is JSON and why do we use it?**
JSON stands for JavaScript Object Notation. It is a simple text format for sending data between a server and a browser. It looks exactly like a Python dictionary. We use it because both Python (Flask) and JavaScript (browser) can read and write it easily.

**Q9. What is Leaflet.js and how does the map work?**
Leaflet is a free open-source JavaScript library for interactive maps. It downloads map background images (called tiles) from OpenStreetMap. We place markers on it using `L.marker()` and draw circles using `L.circle()`. No API key is needed.

**Q10. What are the tests and how do you run them?**
We wrote 47 unit tests in `tests/test_recommender.py` using Python's built-in `unittest` module. Each test checks one specific thing about one function — for example, that `calculate_distance` returns 0 for the same point, or that `filter_by_category` is case-insensitive. Run them with: `py -m unittest tests/test_recommender.py -v`. All 47 pass.

**Q11. What is MongoDB Atlas?**
MongoDB Atlas is a cloud database service. Instead of storing data in a CSV file on your computer, Atlas stores it on a remote server on the internet. You get a connection string (called a URI) which your Python code uses to connect to it, just like a URL for a website.

**Q12. What is pymongo and what does it do?**
pymongo is the official Python library for MongoDB. It lets Python code talk to MongoDB. For example, `collection.find({})` fetches all documents, just like reading all rows from a CSV. We use it in `database.py`.

**Q13. Why do you keep the connection string in a .env file?**
The connection string contains your MongoDB username and password. If you put it directly in the code and upload it to GitHub, anyone can see it and access your database. The `.env` file stays only on your computer. `.gitignore` makes sure it is never uploaded. `.env.example` shows others what it looks like without revealing the real password.

**Q14. What does `load_dotenv()` do?**
`load_dotenv()` is a function from the `python-dotenv` library. It reads the `.env` file and loads each line as an environment variable. After calling it, `os.environ.get("MONGO_URI")` returns your connection string, which `get_database()` uses to connect.

---

## Future Improvements

1. **More cities** — Add all districts of Maharashtra (Aurangabad, Raigad, Sindhudurg, etc.).
2. **More places** — Grow the dataset from 45 to 200+ places.
3. **User reviews** — Let users submit their own ratings and comments.
4. **Driving route** — Show a route on the map from your location to the chosen place.
5. **Marathi language** — Add a Marathi language toggle for local users.
6. **Photo per place** — Add one image per place to make cards more attractive.
7. **Filter by minimum rating** — Let users show only places rated 4.5 or above.
8. **SQLite database** — Replace the CSV with a database for faster searches at scale.
9. **Mobile app** — Convert the web app into a mobile app using Flutter.
10. **Offline mode** — Bundle everything so the app works without internet.

---

---

## Login and Email Verification

### Signup + Verification flow

```
1. User fills in Signup form (name, email, password)
         ↓
2. System checks: email not already used, password ≥ 8 chars
         ↓
3. System saves user to MongoDB with is_verified = False
         ↓
4. System generates a 6-digit OTP, saves it with 10-min expiry, emails it
         ↓
5. User enters OTP on the Verify page
         ↓
6. If OTP correct + not expired → is_verified = True → redirect to Login
         ↓
7. User logs in with email + password
         ↓
8. System checks: password matches hash AND is_verified = True
         ↓
9. User saved in session → main page shows "Hello, <name>" + Logout button
```

---

### Forgot Password flow (5 simple steps)

```
1. User clicks "Forgot password?" on the login page
         ↓
2. User enters their email on /forgot-password
   → System always shows "If this email is registered, a reset code has been sent."
   → (Same message whether email exists or not — for security)
         ↓
3. If email is found: system generates reset OTP, saves it with 10-min expiry,
   emails it (or prints in terminal in TEST MODE)
         ↓
4. User enters OTP + new password on /reset-password
   → 5 wrong attempts = locked (must click Resend to get a new code)
   → Expired OTP = must click Resend
         ↓
5. Correct OTP + valid password → new password saved as hash →
   old password no longer works → redirect to /login
```

---

### The users collection — document structure

Each user in MongoDB looks like this:

```json
{
  "name":             "Virbhadra",
  "email":            "virbhadra@gmail.com",
  "password_hash":    "pbkdf2:sha256:260000$...(scrambled, not the real password)",
  "is_verified":      false,
  "otp":              "483920",
  "otp_expiry":       "2026-10-29T14:35:00",
  "reset_otp":        null,
  "reset_otp_expiry": null,
  "reset_attempts":   0
}
```

| Field | What it stores | Example |
|-------|---------------|---------|
| `name` | User's display name | Virbhadra |
| `email` | Login identifier — must be unique | virbhadra@gmail.com |
| `password_hash` | Hashed password — never the plain text | `pbkdf2:sha256:...` |
| `is_verified` | Has the user confirmed their email? | `false` → `true` after OTP |
| `otp` | Signup verification OTP (6 digits) | `483920` |
| `otp_expiry` | When the signup OTP expires | 10 minutes from generation |
| `reset_otp` | Password reset OTP (separate from signup OTP) | `719043` or `null` |
| `reset_otp_expiry` | When the reset OTP expires | 10 minutes from generation |
| `reset_attempts` | Wrong reset OTP guesses (locked at 5) | `0` to `5` |

---

### .env secrets for auth

| Key | What it is | Example value |
|-----|-----------|--------------|
| `SECRET_KEY` | Flask signs session cookies with this | `my-super-secret-key-123` |
| `EMAIL_ADDRESS` | Gmail address that sends OTP emails. Leave empty for TEST MODE | `yourapp@gmail.com` |
| `EMAIL_PASSWORD` | Gmail App Password — NOT your normal Gmail password | `abcd efgh ijkl mnop` |

**TEST MODE:** If `EMAIL_ADDRESS` or `EMAIL_PASSWORD` are empty in `.env`, all emails are printed in the terminal instead of sent:
```
[TEST MODE — no email sent]
  To     : virbhadra@gmail.com
  Subject: Your Maharashtra Places verification code
  Body   : Your Maharashtra Places verification code is: 483920...
```

---

### How to set up Gmail App Password

A Gmail App Password is a special 16-character password that lets your Python app send emails through your Gmail account. It is **not** your normal Gmail password.

**Steps:**
1. Go to your Google Account → **Security**
2. Make sure **2-Step Verification** is turned ON (required)
3. Search for **"App passwords"** and click it
4. Choose **"Mail"** as the app and **"Windows Computer"** as the device
5. Click **Generate** — Google shows a 16-character password like `abcd efgh ijkl mnop`
6. Copy it and paste it as `EMAIL_PASSWORD` in your `.env` file
7. Also set `EMAIL_ADDRESS` to your Gmail address

> **Note:** If you just want to demo the project, leave both empty. The OTP will print in the terminal and everything still works.

---

### email_service.py — send_email()

```python
sent = send_email("alice@gmail.com", "Your code", "Your code is: 483920...")
# sent = True  if the email was delivered
# sent = False if TEST MODE or sending failed (OTP printed in terminal)
```

- Reads `EMAIL_ADDRESS` and `EMAIL_PASSWORD` from `.env`.
- Connects to `smtp.gmail.com` on port `587`.
- Calls `server.starttls()` to upgrade to an encrypted connection.
- Calls `server.login()` then `server.sendmail()`.
- If credentials are missing → prints to terminal → returns `False`.
- If sending fails for any reason → prints to terminal → returns `False`.

---

### auth.py — All Functions

All 17 functions live in `auth.py`. Each does exactly one thing.

| # | Function | What it does |
|---|----------|-------------|
| 1 | `create_users_index()` | Creates unique index on `email` in MongoDB. Run once at setup. |
| 2 | `email_already_exists(email)` | Returns `True` if the email is already registered, `False` if free. |
| 3 | `create_user(name, email, password)` | Hashes password, saves user with `is_verified=False` and reset fields. |
| 4 | `generate_otp()` | Returns a random 6-digit string e.g. `"483920"`. |
| 5 | `save_otp(email, otp)` | Saves the signup OTP and 10-minute expiry to the user document. |
| 6 | `send_otp_email(email, otp)` | Calls `email_service.send_email()` with a friendly signup OTP message. |
| 7 | `verify_otp(email, otp_entered)` | Returns `"ok"`, `"expired"`, or `"invalid"` for signup OTP. |
| 8 | `mark_verified(email)` | Sets `is_verified=True` and clears the signup OTP fields. |
| 9 | `save_reset_otp(email, otp)` | Saves reset OTP + 10-min expiry + resets attempt counter to 0. |
| 10 | `send_reset_otp_email(email, otp)` | Calls `email_service.send_email()` with a friendly reset OTP message. |
| 11 | `verify_reset_otp(email, otp_entered)` | Returns `"ok"`, `"expired"`, `"invalid"`, or `"locked"` (after 5 wrong guesses). |
| 12 | `update_password(email, new_password)` | Hashes + saves the new password; clears reset OTP fields. |
| 13 | `find_user_by_email(email)` | Returns the user dictionary (no `_id`) or `None`. |
| 14 | `check_password(user, password)` | Returns `True` if password matches the hash, `False` if wrong. |
| 15 | `login_user(session, user)` | Saves `user_name` and `user_email` into the Flask session. |
| 16 | `logout_user(session)` | Clears the Flask session (logs the user out). |
| 17 | `get_logged_in_user(session)` | Returns the logged-in user's name, or `None` if not logged in. |

---

### Routes for auth (all active in app.py ✅)

| Route | Method | What it does |
|-------|--------|-------------|
| `/signup` | GET | Shows the signup form |
| `/signup` | POST | Validates input, creates user, sends OTP, redirects to `/verify` |
| `/verify` | GET | Shows the OTP entry form |
| `/verify` | POST | Checks OTP — if correct marks verified and redirects to `/login` |
| `/resend-otp` | POST | Generates a new signup OTP and resends it |
| `/login` | GET | Shows the login form with "Forgot password?" link |
| `/login` | POST | Checks email + password + `is_verified`, saves to session |
| `/logout` | GET | Clears session, redirects to `/login` |
| `/forgot-password` | GET | Shows "enter your email" form |
| `/forgot-password` | POST | Looks up email, generates reset OTP, emails it, redirects to `/reset-password` |
| `/reset-password` | GET | Shows OTP + new password form |
| `/reset-password` | POST | Validates OTP + password, updates hash, redirects to `/login` |
| `/resend-reset-otp` | POST | Generates a new reset OTP, resets attempt counter |
| `/` | GET | Main page — redirects to `/login` if not logged in |
| `/api/search?q=..` | GET | Returns places whose name, city or category contains q (login required) |

---

### Examiner Questions — Login, Verification, and Forgot Password

**Q: Why do you hash passwords instead of storing them as plain text?**
A: If the database is ever hacked, plain passwords would expose every user's account and every other site they use the same password on. A hash is a one-way scramble: `generate_password_hash("mypassword")` produces a long string that cannot be reversed. To check a login, we hash the entered password again and compare — we never need to un-hash.

**Q: What is an OTP and why do we use it?**
A: OTP stands for One Time Password. It is a random 6-digit code valid for only 10 minutes and usable only once. We use it to confirm the user owns the email address they registered with. After it is used or expires, it is cleared from the database.

**Q: What is a Flask session?**
A: A session is a small piece of data Flask stores in a cookie in the user's browser. It is signed with the `SECRET_KEY` from `.env`, so it cannot be tampered with. After login we store `user_name` and `user_email` in the session. Every route can then check who is logged in.

**Q: What is `SECRET_KEY` used for?**
A: Flask uses `SECRET_KEY` to sign session cookies. If anyone edits the cookie in their browser, the signature breaks and Flask rejects it. If the key is known to an attacker, they could forge sessions — so it must never appear in the code.

**Q: What is a unique index in MongoDB?**
A: An index makes lookups faster. A unique index also enforces a rule: no two documents can have the same value for that field. `create_index("email", unique=True)` means MongoDB automatically rejects a second user with the same email.

**Q: What is TEST MODE in `email_service.py`?**
A: If `EMAIL_ADDRESS` or `EMAIL_PASSWORD` are empty in `.env`, `send_email()` prints the full message in the terminal instead of sending it. This lets you demo signup, verification, and password reset without a real Gmail account.

**Q: Why do you always show the same message on /forgot-password regardless of whether the email exists?**
A: Security. If the message said "email not found" for unknown emails, an attacker could test millions of emails to discover which ones are registered. By always saying "If this email is registered, a code has been sent", the system gives no information away.

**Q: Why is there a limit of 5 wrong OTP attempts on /reset-password?**
A: An attacker could try all 1 000 000 possible 6-digit codes (000000 to 999999) if there was no limit. After 5 wrong guesses the user must click "Resend" which generates a fresh OTP and resets the counter. This makes brute-force guessing practically impossible.

**Q: Why do you use separate fields (reset_otp, reset_otp_expiry) instead of the same otp field?**
A: So the signup verification OTP and the password-reset OTP cannot interfere with each other. If a user is in the middle of verifying their email and also requests a password reset, each flow has its own independent OTP and expiry.

**Q: What is `starttls()` and why is it used?**
A: `starttls()` is a method on Python's SMTP object. It upgrades the connection from plain text to TLS encrypted. Without it, the email credentials (username and password) would be sent over the network in plain text and could be intercepted. Port 587 is the standard Gmail port for SMTP with TLS.

**Q: What does `update_password()` do?**
A: It hashes the new password with `generate_password_hash()` and saves it to the user's document in MongoDB. It also clears `reset_otp`, `reset_otp_expiry`, and resets `reset_attempts` to 0 so the old reset code cannot be reused.

**Q: What is `check_password_hash()` and how does it work?**
A: `check_password_hash(stored_hash, entered_password)` from `werkzeug.security` re-hashes `entered_password` using the same algorithm and salt, then compares. Returns `True` if they match. The plain password is never stored or compared directly.

---

*Last updated: Get Started landing page added — 226 tests pass.*

---

## System Diagrams — Understand How It Works

This project includes **5 black and white diagrams** as both JPG images and Markdown source files in the `diagrams/` folder.

### 🖼️ JPG Images (Ready to View)
All diagrams are available as high-quality JPG images — just open them in any image viewer or web browser:

1. **1_system_architecture.jpg** (28 KB) — System architecture: layers, components, data flow
2. **2_data_flow_1_search.jpg** (20 KB) — How location search works: user input → distance calculation → results
3. **3_data_flow_2_auth.jpg** (83 KB) — User authentication: signup → OTP → verification → login
4. **4_use_case_diagram.jpg** (19 KB) — All features: search, filter, map, trails, language
5. **5_system_working_flow.jpg** (63 KB) — Complete user journey: landing → auth → search → results → logout

### 📄 Markdown Source Files (Editable)
Each diagram also has a `.md` source file with Mermaid diagram code (for editing or re-rendering):

- `1_system_architecture.md` — System Architecture
- `2_data_flow_1_search.md` — Search Data Flow
- `3_data_flow_2_auth.md` — Authentication Data Flow
- `4_use_case_diagram.md` — Use Case Diagram
- `5_system_working_flow.md` — System Working Flow

### 🔍 How to View

**JPG Images:**
- Windows: Open in Photo Viewer or Preview
- Mac: Open in Preview
- Linux: Open in Image Viewer
- Web: Open in any browser

**Markdown Diagrams:**
- **GitHub:** Upload `.md` files to GitHub — they render automatically
- **VS Code:** Install Mermaid extension, then open `.md` file
- **Online:** Copy code into https://mermaid.live
- **Edit:** Open `.md` file in text editor to modify and re-generate

