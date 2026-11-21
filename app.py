# app.py
# This file runs the Flask web server and defines ALL routes.
# It is a "waiter" — it takes requests and brings back answers.
# All real logic lives in recommender.py and auth.py.

import os
from flask import Flask, jsonify, request, render_template, session, redirect, url_for, flash
from dotenv import load_dotenv

from recommender import (load_places, get_cities, get_all_categories,
                        get_recommendations, get_city_centres, get_nearest_city,
                        search_places, apply_language, load_all_places, get_trail_route)
from database import get_trails_collection
from auth import (
    email_already_exists, create_user,
    generate_otp, save_otp, send_otp_email,
    verify_otp, mark_verified,
    find_user_by_email, check_password,
    login_user, logout_user, get_logged_in_user,
    save_reset_otp, send_reset_otp_email,
    verify_reset_otp, update_password,
    clean_email, is_valid_email,
    get_message,
)

# Load .env so os.environ can read SECRET_KEY, EMAIL_ADDRESS, etc.
load_dotenv()

app = Flask(__name__)

# SECRET_KEY is required for Flask sessions (login cookies).
# Flask signs every session cookie with this key so it cannot be faked.
# It is read from .env — never hardcoded here.
app.secret_key = os.environ.get("SECRET_KEY", "fallback-dev-key")
# Ensure Marathi/Unicode characters in JSON responses are sent as-is,
# not as \uXXXX escape sequences. This keeps JSON readable.
app.config["JSON_AS_ASCII"] = False


def get_lang():
    """
    Returns the current language code from the Flask session.
    Default is 'en' (English).
    Called inside every route that renders a template so the
    template knows which language to display.
    """
    return session.get("lang", "en")


# ── Inject 'lang' into every template automatically ──────────────────
# This is a "context processor" — it runs before every render_template()
# call and adds the 'lang' variable to the template context.
# This means every template can use {{ lang }} without us passing it
# manually in every render_template() call.
@app.context_processor
def inject_lang():
    return {"lang": get_lang()}


# ── GET / ────────────────────────────────────────────────────────────
# Landing page ("Get Started") for visitors who are not logged in.
# If the user is already logged in, skip the landing page and go
# straight to the main recommendations page.
@app.route("/")
def index():
    user_name = get_logged_in_user(session)
    if user_name:
        # Already logged in → main app
        return render_template("index.html", user_name=user_name)
    # Not logged in → show the landing / Get Started page
    return render_template("landing.html")


# ── GET /app ──────────────────────────────────────────────────────────
# The main recommendations page, reached after login.
# Kept as a separate URL so it is reachable directly (e.g. bookmarked).
@app.route("/app")
def main_app():
    user_name = get_logged_in_user(session)
    if not user_name:
        return redirect(url_for("login"))
    return render_template("index.html", user_name=user_name)


# ── GET /signup  — show the signup form ──────────────────────────────
# ── POST /signup — process the signup form ───────────────────────────
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # GET: just show the empty signup form
    if request.method == "GET":
        return render_template("signup.html")

    # POST: read the values the user typed into the form
    # request.form.get() reads a field by its HTML name attribute
    name             = request.form.get("fullname", "").strip()
    email            = clean_email(request.form.get("reg_email", ""))
    password         = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # ── Validation checks ────────────────────────────────────────────
    # flash() sends a one-time message to the template to show the user

    if not name or not email or not password:
        flash(get_message("signup.fields_required", get_lang()), "error")
        return render_template("signup.html")

    if not is_valid_email(email):
        flash(get_message("signup.invalid_email", get_lang()), "error")
        return render_template("signup.html")

    if len(password) < 8:
        flash(get_message("signup.password_short", get_lang()), "error")
        return render_template("signup.html")

    if password != confirm_password:
        flash(get_message("signup.passwords_mismatch", get_lang()), "error")
        return render_template("signup.html")

    if email_already_exists(email):
        flash(get_message("signup.email_exists", get_lang()), "error")
        return render_template("signup.html")

    create_user(name, email, password)
    otp = generate_otp()
    save_otp(email, otp)
    send_otp_email(email, otp)
    session["pending_email"] = email
    flash(get_message("signup.success", get_lang()), "success")
    return redirect(url_for("verify"))


# ── GET /verify  — show the OTP entry form ───────────────────────────
# ── POST /verify — check the OTP ─────────────────────────────────────
@app.route("/verify", methods=["GET", "POST"])
def verify():
    # pending_email is stored in session after signup
    email = session.get("pending_email")

    # If no email in session, user navigated here directly — send to signup
    if not email:
        return redirect(url_for("signup"))

    if request.method == "GET":
        return render_template("verify.html", email=email)

    # POST: read the OTP the user entered
    otp_entered = request.form.get("otp", "").strip()

    result = verify_otp(email, otp_entered)

    if result == "ok":
        mark_verified(email)
        session.pop("pending_email", None)
        flash(get_message("otp.verified", get_lang()), "success")
        return redirect(url_for("login"))

    elif result == "expired":
        flash(get_message("otp.expired", get_lang()), "error")
        return render_template("verify.html", email=email)

    else:
        flash(get_message("otp.incorrect", get_lang()), "error")
        return render_template("verify.html", email=email)


# ── POST /resend-otp — generate and resend a new OTP ─────────────────
@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    email = session.get("pending_email")

    if not email:
        return redirect(url_for("signup"))

    otp = generate_otp()
    save_otp(email, otp)
    send_otp_email(email, otp)
    flash(get_message("otp.sent", get_lang()), "success")
    return redirect(url_for("verify"))


# ── GET /login  — show the login form ────────────────────────────────
# ── POST /login — check credentials and log in ───────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, go straight to the main page
    if get_logged_in_user(session):
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("login.html")

    email    = clean_email(request.form.get("email", ""))
    password = request.form.get("password", "")

    if not is_valid_email(email):
        flash(get_message("login.invalid_email", get_lang()), "error")
        return render_template("login.html")

    user = find_user_by_email(email)

    if not user:
        flash(get_message("login.no_account", get_lang()), "error")
        return render_template("login.html")

    if not check_password(user, password):
        flash(get_message("login.wrong_password", get_lang()), "error")
        return render_template("login.html")

    if not user.get("is_verified"):
        session["pending_email"] = email
        flash(get_message("login.unverified", get_lang()), "error")
        return redirect(url_for("verify"))

    login_user(session, user)
    flash(get_message("login.welcome", get_lang()) + f", {user['name']}!", "success")
    return redirect(url_for("index"))


# ── GET /logout — clear session and redirect to login ────────────────
@app.route("/logout")
def logout():
    logout_user(session)
    flash(get_message("login.logged_out", get_lang()), "success")
    return redirect(url_for("login"))


# ── GET /trails — Trails listing page ───────────────────────────────────
# Shows all 4 themed trails as cards.
# Protected: must be logged in.
@app.route("/trails")
def trails_page():
    user_name = get_logged_in_user(session)
    if not user_name:
        return redirect(url_for("login"))
    collection = get_trails_collection()
    trails     = list(collection.find({}, {"_id": 0}))
    return render_template("trails.html", trails=trails, user_name=user_name)


# ── GET /trail/<trail_id> — Trail detail page ────────────────────────────
# Shows the ordered places on a map with a polyline and step distances.
@app.route("/trail/<int:trail_id>")
def trail_detail(trail_id):
    user_name = get_logged_in_user(session)
    if not user_name:
        return redirect(url_for("login"))

    collection = get_trails_collection()
    trail      = collection.find_one({"id": trail_id}, {"_id": 0})
    if not trail:
        return "Trail not found", 404

    lang       = get_lang()
    all_places = load_all_places()          # includes trail_only places
    route      = get_trail_route(trail, all_places)

    # Apply language to every place in the route
    route["places"] = [apply_language(p, lang) for p in route["places"]]

    # Estimated driving time: total_km ÷ 40 km/h (approximate)
    driving_hours = round(route["total_km"] / 40, 1)

    return render_template("trail_detail.html",
                           trail=trail,
                           route=route,
                           driving_hours=driving_hours,
                           user_name=user_name,
                           lang=lang)


# ── GET /api/trails — All trails as JSON ─────────────────────────────────
@app.route("/api/trails")
def api_trails():
    lang       = request.args.get("lang", get_lang())
    collection = get_trails_collection()
    all_places = load_all_places()
    trails     = list(collection.find({}, {"_id": 0}))

    result = []
    for trail in trails:
        route = get_trail_route(trail, all_places)
        result.append({
            "id":           trail["id"],
            "name":         trail["name_mr"] if lang == "mr" else trail["name"],
            "description":  trail["description_mr"] if lang == "mr" else trail["description"],
            "place_count":  len(route["places"]),
            "total_km":     route["total_km"],
        })
    return jsonify(result)


# ── GET /api/trail/<trail_id> — Single trail detail as JSON ──────────────
@app.route("/api/trail/<int:trail_id>")
def api_trail_detail(trail_id):
    lang       = request.args.get("lang", get_lang())
    collection = get_trails_collection()
    trail      = collection.find_one({"id": trail_id}, {"_id": 0})
    if not trail:
        return jsonify({"error": "Trail not found"}), 404

    all_places = load_all_places()
    route      = get_trail_route(trail, all_places)
    route["places"] = [apply_language(p, lang) for p in route["places"]]

    driving_hours = round(route["total_km"] / 40, 1)

    return jsonify({
        "id":            trail["id"],
        "name":          trail["name_mr"] if lang == "mr" else trail["name"],
        "description":   trail["description_mr"] if lang == "mr" else trail["description"],
        "places":        route["places"],
        "steps":         route["steps"],
        "total_km":      route["total_km"],
        "driving_hours": driving_hours,
    })


# ── POST /set-language — save the chosen language in the session ──────
# Called by JavaScript on every page when the user clicks the toggle.
# Accepts JSON body: {"lang": "en"} or {"lang": "mr"}
# Stores it in session["lang"] so Flask templates can read it.
# Returns {"ok": true} so the JS knows the save worked.
@app.route("/set-language", methods=["POST"])
def set_language():
    data = request.get_json(silent=True) or {}
    lang = data.get("lang", "en")
    # Only allow "en" or "mr" — ignore anything else
    if lang not in ("en", "mr"):
        lang = "en"
    session["lang"] = lang
    return jsonify({"ok": True, "lang": lang})


# ── GET  /forgot-password — show "enter your email" form ─────────────
# ── POST /forgot-password — look up email, send reset OTP ────────────
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    email = clean_email(request.form.get("email", ""))

    if not is_valid_email(email):
        flash(get_message("forgot.invalid_email", get_lang()), "error")
        return render_template("forgot_password.html")

    if email_already_exists(email):
        otp = generate_otp()
        save_reset_otp(email, otp)
        sent = send_reset_otp_email(email, otp)
        if not sent:
            flash(get_message("forgot.safe_message_test", get_lang()), "success")
        else:
            flash(get_message("forgot.safe_message", get_lang()), "success")
        session["reset_email"] = email
        return redirect(url_for("reset_password"))

    flash(get_message("forgot.safe_message", get_lang()), "success")
    return render_template("forgot_password.html")


# ── GET  /reset-password — show reset form ───────────────────────────
# ── POST /reset-password — verify OTP and save new password ──────────
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = session.get("reset_email")

    # If no email in session, user navigated here directly
    if not email:
        return redirect(url_for("forgot_password"))

    if request.method == "GET":
        return render_template("reset_password.html", email=email)

    otp_entered  = request.form.get("otp", "").strip()
    new_password = request.form.get("password", "")
    confirm      = request.form.get("confirm_password", "")

    if len(new_password) < 8:
        flash(get_message("reset.password_short", get_lang()), "error")
        return render_template("reset_password.html", email=email)

    if new_password != confirm:
        flash(get_message("reset.passwords_mismatch", get_lang()), "error")
        return render_template("reset_password.html", email=email)

    result = verify_reset_otp(email, otp_entered)

    if result == "locked":
        flash(get_message("reset.locked", get_lang()), "error")
        return render_template("reset_password.html", email=email)

    if result == "expired":
        flash(get_message("reset.expired", get_lang()), "error")
        return render_template("reset_password.html", email=email)

    if result == "invalid":
        flash(get_message("reset.incorrect", get_lang()), "error")
        return render_template("reset_password.html", email=email)

    update_password(email, new_password)
    session.pop("reset_email", None)
    flash(get_message("reset.success", get_lang()), "success")
    return redirect(url_for("login"))


# ── POST /resend-reset-otp — generate and resend a new reset OTP ─────
@app.route("/resend-reset-otp", methods=["POST"])
def resend_reset_otp():
    email = session.get("reset_email")

    if not email:
        return redirect(url_for("forgot_password"))

    otp = generate_otp()
    save_reset_otp(email, otp)
    send_reset_otp_email(email, otp)
    flash(get_message("reset.otp_sent", get_lang()), "success")
    return redirect(url_for("reset_password"))


# ── GET /api/search ──────────────────────────────────────────────────
# Searches places by name, city or category.
# The search is NOT case-sensitive.
# Query parameter: q -- the search text, e.g. /api/search?q=fort
# Returns a JSON list of matching places (no distance_km — just raw data).
# Returns ALL 53 places if q is empty or missing.
#
# This route is protected: the user must be logged in.
@app.route("/api/search")
def api_search():
    if not get_logged_in_user(session):
        return jsonify({"error": "Login required"}), 401

    query  = request.args.get("q",    "").strip()
    lang   = request.args.get("lang", get_lang())  # new: en or mr

    places  = load_places()
    results = search_places(places, query)
    # Translate text fields before returning
    return jsonify([apply_language(p, lang) for p in results])


# ── GET /api/cities ──────────────────────────────────────────────────
@app.route("/api/cities")
def api_cities():
    cities = get_cities()
    return jsonify(cities)


# ── GET /api/city-centres ─────────────────────────────────────────────
# Returns the GPS centre coordinates for each of the 6 cities.
# Used by the web page to search by city and to find the nearest city.
# Example response: {"Mumbai": {"lat": 19.076, "lon": 72.877}, ...}
@app.route("/api/city-centres")
def api_city_centres():
    return jsonify(get_city_centres())


# ── GET /api/nearest-city ─────────────────────────────────────────────
# Given lat and lon, returns the name of the nearest of the 6 cities.
# Example: /api/nearest-city?lat=19.14&lon=77.32 -> {"nearest_city": "Nanded"}
@app.route("/api/nearest-city")
def api_nearest_city():
    lat_str = request.args.get("lat", "")
    lon_str = request.args.get("lon", "")

    if not lat_str or not lon_str:
        return jsonify({"error": "lat and lon are required"}), 400

    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except ValueError:
        return jsonify({"error": "lat and lon must be numbers"}), 400

    city = get_nearest_city(lat, lon)
    return jsonify({"nearest_city": city})


# ── GET /api/nearest-places ───────────────────────────────────────────
# Fallback endpoint: returns the 5 nearest places to a location,
# ignoring radius — used when /api/recommend returns zero results.
# Example: /api/nearest-places?lat=19.14&lon=77.32
@app.route("/api/nearest-places")
def api_nearest_places():
    lat_str = request.args.get("lat", "")
    lon_str = request.args.get("lon", "")
    lang    = request.args.get("lang", get_lang())

    if not lat_str or not lon_str:
        return jsonify({"error": "lat and lon are required"}), 400

    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except ValueError:
        return jsonify({"error": "lat and lon must be numbers"}), 400

    from recommender import find_nearby_places
    all_places    = load_places()
    all_with_dist = find_nearby_places(all_places, lat, lon, 9999)
    sorted_by_dist = sorted(all_with_dist, key=lambda p: p["distance_km"])
    nearest        = sorted_by_dist[:5]
    return jsonify([apply_language(p, lang) for p in nearest])


# ── GET /api/places ──────────────────────────────────────────────────
@app.route("/api/places")
def api_places():
    # Optional lang parameter: ?lang=mr returns Marathi text, default is English
    lang   = request.args.get("lang", get_lang())
    places = load_places()
    # Translate text fields for every place before returning
    return jsonify([apply_language(p, lang) for p in places])


# ── GET /api/categories ──────────────────────────────────────────────
@app.route("/api/categories")
def api_categories():
    places = load_places()
    categories = get_all_categories(places)
    return jsonify(categories)


# ── GET /api/recommend ───────────────────────────────────────────────
@app.route("/api/recommend")
def api_recommend():
    lat_str    = request.args.get("lat",      "")
    lon_str    = request.args.get("lon",      "")
    radius_str = request.args.get("radius",   "50")
    category   = request.args.get("category", "")
    season     = request.args.get("season",   "")
    lang       = request.args.get("lang",     get_lang())  # new: en or mr

    if not lat_str or not lon_str:
        return jsonify({"error": "lat and lon are required. Example: ?lat=18.52&lon=73.85&radius=50"}), 400

    try:
        lat    = float(lat_str)
        lon    = float(lon_str)
        radius = float(radius_str)
    except ValueError:
        return jsonify({"error": "lat, lon and radius must be numbers."}), 400

    results = get_recommendations(lat, lon, radius, category, season)
    # Translate text fields before returning
    return jsonify([apply_language(p, lang) for p in results])


if __name__ == "__main__":
    app.run(debug=True)
