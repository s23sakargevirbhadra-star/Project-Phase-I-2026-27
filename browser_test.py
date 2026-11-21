# browser_test.py
# Simulates what a real browser does: visits pages, checks redirects,
# submits forms, reads responses. Uses Flask's test client so no real
# server port is needed — but this tests the EXACT same code path.

import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database import get_users_collection

app.config["TESTING"] = True
client = app.test_client()

results = []
errors  = []

def check(label, passed, detail=""):
    sym = "PASS" if passed else "FAIL"
    line = f"  [{sym}]  {label}"
    if detail:
        line += f"  →  {detail}"
    results.append(line)
    if not passed:
        errors.append(label)

# ══════════════════════════════════════════════════════════════
# FLOW 1:  Visit / without login  →  should redirect to /login
# ══════════════════════════════════════════════════════════════
r = client.get("/")
check("GET / (no login) → redirect to /login",
      r.status_code == 302 and "/login" in r.headers.get("Location",""),
      f"status={r.status_code} location={r.headers.get('Location','')}")

# ══════════════════════════════════════════════════════════════
# FLOW 2:  /login page loads correctly
# ══════════════════════════════════════════════════════════════
r = client.get("/login")
check("GET /login → 200", r.status_code == 200)
check("GET /login → shows login form", b"Log In" in r.data)
check("GET /login → has email input", b'name="email"' in r.data)
check("GET /login → has Forgot password link",
      b"forgot" in r.data.lower())

# ══════════════════════════════════════════════════════════════
# FLOW 3:  /signup page loads correctly
# ══════════════════════════════════════════════════════════════
r = client.get("/signup")
check("GET /signup → 200", r.status_code == 200)
check("GET /signup → shows signup form", b"Create Account" in r.data)

# ══════════════════════════════════════════════════════════════
# FLOW 4:  Signup with INVALID email → rejected, no DB write
# ══════════════════════════════════════════════════════════════
bad_emails = ["1234", "abc", "abc@", "@gmail.com", "abc@gmail", "abc @gmail.com"]
for bad in bad_emails:
    get_users_collection().delete_many({"email": bad})
    r = client.post("/signup", data={
        "name":"Test","email":bad,"password":"test1234","confirm_password":"test1234"
    })
    check(f"POST /signup invalid email '{bad}' → stays on page (200)",
          r.status_code == 200, f"got {r.status_code}")
    check(f"POST /signup invalid email '{bad}' → shows error message",
          b"valid email" in r.data)
    user = get_users_collection().find_one({"email": bad})
    check(f"POST /signup invalid email '{bad}' → NOT saved to MongoDB",
          user is None)

# ══════════════════════════════════════════════════════════════
# FLOW 5:  Signup with valid email → creates user, redirects to /verify
# ══════════════════════════════════════════════════════════════
TEST_EMAIL = "browser_test_user@example.com"
get_users_collection().delete_many({"email": TEST_EMAIL})
r = client.post("/signup", data={
    "name":"Browser Test","email":TEST_EMAIL,
    "password":"testpass99","confirm_password":"testpass99"
})
check("POST /signup valid → 302 redirect",        r.status_code == 302)
check("POST /signup valid → redirects to /verify", "/verify" in r.headers.get("Location",""))

user = get_users_collection().find_one({"email": TEST_EMAIL})
check("POST /signup valid → user saved in MongoDB", user is not None)
check("POST /signup valid → is_verified = False",  user and user.get("is_verified") == False)
check("POST /signup valid → password is hashed",
      user and ":" in user.get("password_hash",""))
check("POST /signup valid → OTP generated",        user and user.get("otp") is not None)

# ══════════════════════════════════════════════════════════════
# FLOW 6:  /verify page loads (requires pending_email in session)
# ══════════════════════════════════════════════════════════════
# After signup the session has pending_email — the client keeps sessions automatically
r = client.get("/verify")
check("GET /verify after signup → 200", r.status_code == 200)
check("GET /verify → shows OTP form", b"6-digit" in r.data or b"Verify" in r.data)
check("GET /verify → shows email address", TEST_EMAIL.encode() in r.data)
check("GET /verify → has Resend button", b"Resend" in r.data)

# ══════════════════════════════════════════════════════════════
# FLOW 7:  Wrong OTP → rejected, stays on verify page
# ══════════════════════════════════════════════════════════════
r = client.post("/verify", data={"otp": "000000"})
check("POST /verify wrong OTP → stays on verify (200)", r.status_code == 200)
check("POST /verify wrong OTP → shows error", b"Incorrect" in r.data)

# ══════════════════════════════════════════════════════════════
# FLOW 8:  Correct OTP → verified, redirect to /login
# ══════════════════════════════════════════════════════════════
real_otp = get_users_collection().find_one({"email": TEST_EMAIL})["otp"]
r = client.post("/verify", data={"otp": real_otp})
check("POST /verify correct OTP → 302 redirect", r.status_code == 302)
check("POST /verify correct OTP → redirects to /login",
      "/login" in r.headers.get("Location",""))
user = get_users_collection().find_one({"email": TEST_EMAIL})
check("POST /verify correct OTP → is_verified = True",  user.get("is_verified") == True)
check("POST /verify correct OTP → OTP cleared",          user.get("otp") is None)

# ══════════════════════════════════════════════════════════════
# FLOW 9:  Unverified user tries to login → redirect to /verify
# ══════════════════════════════════════════════════════════════
UNVERIFIED_EMAIL = "unverified_browser@example.com"
get_users_collection().delete_many({"email": UNVERIFIED_EMAIL})
c2 = app.test_client()  # fresh client = no session
c2.post("/signup", data={
    "name":"UV","email":UNVERIFIED_EMAIL,
    "password":"testpass99","confirm_password":"testpass99"
})
r = c2.post("/login", data={"email": UNVERIFIED_EMAIL, "password": "testpass99"})
check("POST /login unverified → 302 redirect",       r.status_code == 302)
check("POST /login unverified → redirects to /verify",
      "/verify" in r.headers.get("Location",""))
get_users_collection().delete_many({"email": UNVERIFIED_EMAIL})

# ══════════════════════════════════════════════════════════════
# FLOW 10:  Verified user logs in → session set, redirect to /
# ══════════════════════════════════════════════════════════════
# Create a new client to reset session
c3 = app.test_client()
r = c3.post("/login", data={"email": TEST_EMAIL, "password": "testpass99"})
check("POST /login verified → 302 redirect",          r.status_code == 302)
check("POST /login verified → redirects to /",
      r.headers.get("Location","") in ["/", "http://localhost/"])

# ══════════════════════════════════════════════════════════════
# FLOW 11:  Logged-in user visits / → gets the main page
# ══════════════════════════════════════════════════════════════
r = c3.get("/")
check("GET / (logged in) → 200", r.status_code == 200)
check("GET / (logged in) → shows map", b"leaflet" in r.data.lower() or b"map" in r.data.lower())
check("GET / (logged in) → shows user name", b"Browser Test" in r.data)
check("GET / (logged in) → shows Logout button", b"Logout" in r.data)
check("GET / (logged in) → shows search box",    b"search-input" in r.data)
check("GET / (logged in) → shows season dropdown", b"season-select" in r.data)
check("GET / (logged in) → shows city dropdown",  b"city-select" in r.data)

# ══════════════════════════════════════════════════════════════
# FLOW 12:  Logged-in user visits /logout → session cleared
# ══════════════════════════════════════════════════════════════
r = c3.get("/logout")
check("GET /logout → 302 redirect",                r.status_code == 302)
check("GET /logout → redirects to /login",
      "/login" in r.headers.get("Location",""))
r = c3.get("/")
check("GET / after logout → redirect to /login",   r.status_code == 302)

# ══════════════════════════════════════════════════════════════
# FLOW 13:  Forgot password page
# ══════════════════════════════════════════════════════════════
r = client.get("/forgot-password")
check("GET /forgot-password → 200", r.status_code == 200)
check("GET /forgot-password → shows form", b"Reset Code" in r.data or b"Forgot" in r.data)

r = client.post("/forgot-password", data={"email": "notreal@example.com"})
check("POST /forgot-password unknown email → shows safe message",
      b"If this email is registered" in r.data)

r = client.post("/forgot-password", data={"email": "invalid-no-at"})
check("POST /forgot-password invalid email → shows validation error",
      b"valid email" in r.data)

# ══════════════════════════════════════════════════════════════
# FLOW 14:  API endpoints (no login required for recommend/places/etc.)
# ══════════════════════════════════════════════════════════════
r = client.get("/api/cities")
check("GET /api/cities → 200 with 6 cities",
      r.status_code == 200 and len(r.get_json()) == 6)

r = client.get("/api/categories")
check("GET /api/categories → 200 with 8 categories",
      r.status_code == 200 and len(r.get_json()) == 8)

r = client.get("/api/places")
check("GET /api/places → 200 with 53 places",
      r.status_code == 200 and len(r.get_json()) == 53)

r = client.get("/api/recommend?lat=18.5204&lon=73.8567&radius=50")
data = r.get_json()
check("GET /api/recommend Pune 50km → 200 with results",
      r.status_code == 200 and len(data) > 0,
      f"{len(data)} results, top: {data[0]['name'] if data else 'none'}")

r = client.get("/api/recommend?lat=18.5204&lon=73.8567&radius=500&season=monsoon")
data = r.get_json()
check("GET /api/recommend season=monsoon → all have monsoon",
      all("monsoon" in p.get("seasons","") for p in data),
      f"{len(data)} results")

r = client.get("/api/recommend?lat=18.5204&lon=73.8567&radius=500&season=winter&category=Fort")
data = r.get_json()
check("GET /api/recommend season+category combined",
      all(p["category"]=="Fort" and "winter" in p.get("seasons","") for p in data),
      f"{len(data)} fort+winter results")

r = client.get("/api/recommend")
check("GET /api/recommend (no lat/lon) → 400",
      r.status_code == 400 and "error" in r.get_json())

r = client.get("/api/search?q=fort")
check("GET /api/search (no login) → 401",   r.status_code == 401)

# Logged-in search
with client.session_transaction() as sess:
    sess["user_name"] = "Test"; sess["user_email"] = "t@t.com"
r = client.get("/api/search?q=Mumbai")
data = r.get_json()
check("GET /api/search?q=Mumbai (logged in) → 200 with results",
      r.status_code == 200 and len(data) > 0,
      f"{len(data)} results")

r = client.get("/api/nearest-city?lat=19.1383&lon=77.3210")
check("GET /api/nearest-city Nanded coords",
      r.get_json().get("nearest_city") == "Nanded")

r = client.get("/api/nearest-places?lat=19.1383&lon=77.3210")
check("GET /api/nearest-places → 5 results", len(r.get_json()) == 5)

r = client.get("/api/city-centres")
check("GET /api/city-centres → 6 entries", len(r.get_json()) == 6)

# ── Cleanup ──────────────────────────────────────────────────────
get_users_collection().delete_many({"email": TEST_EMAIL})

# ── Summary ──────────────────────────────────────────────────────
passed = sum(1 for x in results if "[PASS]" in x)
failed = sum(1 for x in results if "[FAIL]" in x)

lines = ["=" * 60, "BROWSER / FLOW TEST RESULTS", "=" * 60, ""]
lines += results
lines += ["", "=" * 60,
          f"PASSED : {passed}",
          f"FAILED : {failed}",
          "OVERALL: ALL PASSED" if failed == 0 else "OVERALL: SOME FAILED",
          "=" * 60]
if errors:
    lines += ["", "FAILING CHECKS:"]
    for e in errors:
        lines.append(f"  ✗ {e}")

with open("browser_test_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
