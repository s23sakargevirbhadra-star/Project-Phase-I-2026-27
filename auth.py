# auth.py
# All authentication logic: signup, OTP verification, login, logout,
# forgot password, and reset password.
#
# Each function does exactly ONE thing and is under 15 lines.
# No heavy libraries — only Python built-ins + what we already have.
#
# New in this version:
#   - send_otp_email() now uses email_service.send_email() instead of raw smtplib.
#   - Four new functions for forgot/reset password:
#       save_reset_otp(), verify_reset_otp(), increment_reset_attempts(), update_password()

import re      # built-in module for regular expressions (pattern matching)
import random
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash

from database import get_users_collection
from email_service import send_email   # our dedicated email module


# ─────────────────────────────────────────────
# MESSAGE TRANSLATIONS
# ─────────────────────────────────────────────

# MESSAGES is a plain dictionary with every server-generated flash message
# in both English ("en") and Marathi ("mr").
#
# How to use:
#   flash(get_message("signup.invalid_email", lang), "error")
#
# How to add a new message:
#   1. Add a new key inside both "en" and "mr" blocks.
#   2. Use get_message(key, lang) wherever you need it.

MESSAGES = {
    "en": {
        # Signup
        "signup.fields_required":    "All fields are required.",
        "signup.invalid_email":      "Please enter a valid email address (example: name@gmail.com).",
        "signup.password_short":     "Password must be at least 8 characters.",
        "signup.passwords_mismatch": "Passwords do not match.",
        "signup.email_exists":       "An account with this email already exists.",
        "signup.success":            "Account created! Enter the 6-digit code sent to your email.",
        # OTP / verify
        "otp.sent":                  "A new code has been sent.",
        "otp.expired":               "Your code has expired. Please request a new one.",
        "otp.incorrect":             "Incorrect code. Please try again.",
        "otp.verified":              "Email verified! You can now log in.",
        # Login
        "login.invalid_email":       "Please enter a valid email address (example: name@gmail.com).",
        "login.no_account":          "No account found with that email.",
        "login.wrong_password":      "Incorrect password.",
        "login.unverified":          "Please verify your email before logging in.",
        "login.welcome":             "Welcome back",   # + ", <name>!" appended
        "login.logged_out":          "You have been logged out.",
        # Forgot / reset password
        "forgot.safe_message":       "If this email is registered, a reset code has been sent.",
        "forgot.safe_message_test":  "If this email is registered, a reset code has been sent. (Check your terminal — TEST MODE is active.)",
        "forgot.invalid_email":      "Please enter a valid email address (example: name@gmail.com).",
        "reset.locked":              "Too many wrong attempts. Please request a new reset code.",
        "reset.expired":             "Your reset code has expired. Please request a new one.",
        "reset.incorrect":           "Incorrect code. Please try again.",
        "reset.password_short":      "New password must be at least 8 characters.",
        "reset.passwords_mismatch":  "Passwords do not match.",
        "reset.success":             "Password changed successfully. Please log in.",
        "reset.otp_sent":            "A new reset code has been sent.",
    },
    "mr": {
        # Signup
        "signup.fields_required":    "सर्व फील्ड आवश्यक आहेत.",
        "signup.invalid_email":      "कृपया वैध ईमेल पत्ता टाका (उदाहरण: name@gmail.com).",
        "signup.password_short":     "पासवर्ड किमान ८ अक्षरांचा असावा.",
        "signup.passwords_mismatch": "पासवर्ड जुळत नाहीत.",
        "signup.email_exists":       "या ईमेलसह खाते आधीच अस्तित्वात आहे.",
        "signup.success":            "खाते तयार झाले! तुमच्या ईमेलवर पाठवलेला ६-अंकी कोड टाका.",
        # OTP / verify
        "otp.sent":                  "नवीन कोड पाठवला गेला.",
        "otp.expired":               "तुमचा कोड कालबाह्य झाला. कृपया नवीन विनंती करा.",
        "otp.incorrect":             "चुकीचा कोड. कृपया पुन्हा प्रयत्न करा.",
        "otp.verified":              "ईमेल सत्यापित झाला! आता तुम्ही लॉग इन करू शकता.",
        # Login
        "login.invalid_email":       "कृपया वैध ईमेल पत्ता टाका (उदाहरण: name@gmail.com).",
        "login.no_account":          "या ईमेलसह कोणतेही खाते सापडले नाही.",
        "login.wrong_password":      "चुकीचा पासवर्ड.",
        "login.unverified":          "लॉग इन करण्यापूर्वी कृपया तुमचा ईमेल सत्यापित करा.",
        "login.welcome":             "परत स्वागत आहे",   # + ", <name>!" appended
        "login.logged_out":          "तुम्ही लॉग आउट झालात.",
        # Forgot / reset password
        "forgot.safe_message":       "हा ईमेल नोंदणीकृत असल्यास, रीसेट कोड पाठवला गेला आहे.",
        "forgot.safe_message_test":  "हा ईमेल नोंदणीकृत असल्यास, रीसेट कोड पाठवला गेला आहे. (टर्मिनल तपासा — TEST MODE सुरू आहे.)",
        "forgot.invalid_email":      "कृपया वैध ईमेल पत्ता टाका (उदाहरण: name@gmail.com).",
        "reset.locked":              "खूप जास्त चुकीचे प्रयत्न. कृपया नवीन रीसेट कोड विनंती करा.",
        "reset.expired":             "तुमचा रीसेट कोड कालबाह्य झाला. कृपया नवीन विनंती करा.",
        "reset.incorrect":           "चुकीचा कोड. कृपया पुन्हा प्रयत्न करा.",
        "reset.password_short":      "नवीन पासवर्ड किमान ८ अक्षरांचा असावा.",
        "reset.passwords_mismatch":  "पासवर्ड जुळत नाहीत.",
        "reset.success":             "पासवर्ड यशस्वीरित्या बदलला. कृपया लॉग इन करा.",
        "reset.otp_sent":            "नवीन रीसेट कोड पाठवला गेला.",
    }
}


def get_message(key, lang="en"):
    """
    Returns the translated flash message for the given key and language.

    How it works:
      1. Look up MESSAGES[lang][key].
      2. If not found, fall back to MESSAGES["en"][key].
      3. If still not found, return the key itself (easy to spot missing keys).

    Parameters:
      key  -- message key, e.g. "signup.invalid_email"
      lang -- "en" or "mr" (default "en")

    Example:
      get_message("otp.incorrect", "mr")
      -> "चुकीचा कोड. कृपया पुन्हा प्रयत्न करा."
    """
    lang_msgs = MESSAGES.get(lang, MESSAGES["en"])
    return lang_msgs.get(key) or MESSAGES["en"].get(key) or key


# ─────────────────────────────────────────────
# EMAIL VALIDATION HELPERS
# ─────────────────────────────────────────────

def clean_email(email):
    """
    Removes spaces from both ends of the email and converts it to lowercase.
    Always call this before doing anything with an email address.

    Why: users sometimes accidentally type a space before or after,
    and email addresses are case-insensitive by standard.

    Example:
      clean_email("  Alice@Gmail.COM  ") -> "alice@gmail.com"
      clean_email("bob@example.com")     -> "bob@example.com"
    """
    if not email:
        return ""
    return email.strip().lower()


def is_valid_email(email):
    """
    Returns True if the email address looks real, False if it does not.

    The rule in plain English:
      1. One or more letters, numbers, dots, *, %, + or - characters  (the username part)
      2. Then an @ symbol
      3. Then a domain name (letters, numbers, dots or dashes)
      4. Then a dot
      5. Then at least 2 letters  (like .com, .in, .edu)

    Also rejects emails longer than 100 characters.

    Examples that pass:  name@gmail.com   a.b@college.edu.in   user+tag@domain.org   user_name@domain.com
    Examples that fail:  1234   abc   abc@   @gmail.com   abc@gmail   abc @gmail.com

    How it works:
      re.match() tries to match the pattern against the full string.
      ^ means "start of string", $ means "end of string".
      + means "one or more of the previous character".
      {2,} means "2 or more of the previous character".
    """
    if not email or len(email) > 100:
        return False

    # The pattern broken into parts so it is easy to explain:
    #   ^                      start of string
    #   [A-Za-z0-9._*%+-]+    one or more allowed username characters
    #                          (underscore _ is valid in email usernames by the standard)
    #   @                      the @ symbol
    #   [A-Za-z0-9.-]+         domain name (e.g. "gmail" or "college.edu")
    #   \.                     a literal dot (backslash escapes the dot)
    #   [A-Za-z]{2,}           at least 2 letters (e.g. "com", "in", "edu")
    #   $                      end of string
    pattern = r"^[A-Za-z0-9._*%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    # re.match() returns a Match object if the pattern fits, or None if it does not
    return re.match(pattern, email) is not None


# ─────────────────────────────────────────────
# USERS COLLECTION SETUP
# ─────────────────────────────────────────────

def create_users_index():
    """
    Creates a unique index on the 'email' field of the 'users' collection.
    MongoDB will then refuse to insert two users with the same email.
    Safe to run more than once — MongoDB ignores it if it already exists.
    """
    collection = get_users_collection()
    collection.create_index("email", unique=True)
    print("Unique index on 'email' created (or already exists).")


# ─────────────────────────────────────────────
# SIGNUP HELPERS
# ─────────────────────────────────────────────

def email_already_exists(email):
    """
    Returns True if the email is already registered, False if it is free.
    Uses find_one() — returns the document if found, None if not found.
    """
    collection = get_users_collection()
    return collection.find_one({"email": email}) is not None


def create_user(name, email, password):
    """
    Saves a new user to MongoDB.
    Stores only the hashed password — never the plain text.
    is_verified starts as False until the user confirms their email with OTP.
    reset_attempts tracks wrong reset-OTP guesses (used in forgot password).
    """
    collection = get_users_collection()
    user = {
        "name":             name,
        "email":            email,
        "password_hash":    generate_password_hash(password),
        "is_verified":      False,
        "otp":              None,
        "otp_expiry":       None,
        "reset_otp":        None,    # separate field for password-reset OTP
        "reset_otp_expiry": None,
        "reset_attempts":   0,       # counts wrong reset OTP guesses
    }
    result = collection.insert_one(user)
    return result.inserted_id


# ─────────────────────────────────────────────
# OTP HELPERS (signup verification)
# ─────────────────────────────────────────────

def generate_otp():
    """
    Returns a random 6-digit string, e.g. "483920".
    random.randint(100000, 999999) always gives exactly 6 digits.
    """
    return str(random.randint(100000, 999999))


def save_otp(email, otp):
    """
    Saves the signup OTP and a 10-minute expiry into the user's document.
    Uses MongoDB $set so only these two fields change — nothing else.
    """
    collection = get_users_collection()
    expiry = datetime.utcnow() + timedelta(minutes=10)
    collection.update_one(
        {"email": email},
        {"$set": {"otp": otp, "otp_expiry": expiry}}
    )


def send_otp_email(email, otp):
    """
    Emails the signup verification OTP to the user.
    Uses email_service.send_email() which handles Gmail SMTP and TEST MODE.
    Returns True if the email was sent, False if it fell back to terminal.
    """
    subject = "Your Maharashtra Places verification code"
    body = (
        f"Hello,\n\n"
        f"Your Maharashtra Places verification code is: {otp}\n\n"
        f"It is valid for 10 minutes.\n\n"
        f"If you did not sign up, please ignore this email.\n\n"
        f"— Maharashtra Places Team"
    )
    return send_email(email, subject, body)


def verify_otp(email, otp_entered):
    """
    Checks the signup OTP entered by the user.
    Returns "ok", "expired", or "invalid".
      "ok"      — OTP matches and is still within 10 minutes
      "expired" — OTP matches but time has run out
      "invalid" — OTP does not match what is stored
    """
    collection = get_users_collection()
    user = collection.find_one({"email": email})
    if not user or user.get("otp") != otp_entered:
        return "invalid"
    if datetime.utcnow() > user.get("otp_expiry"):
        return "expired"
    return "ok"


def mark_verified(email):
    """
    Sets is_verified=True and clears the signup OTP fields.
    Called after verify_otp() returns "ok".
    Clearing the OTP means it cannot be used a second time.
    """
    collection = get_users_collection()
    collection.update_one(
        {"email": email},
        {"$set": {"is_verified": True, "otp": None, "otp_expiry": None}}
    )


# ─────────────────────────────────────────────
# FORGOT PASSWORD HELPERS
# ─────────────────────────────────────────────

def save_reset_otp(email, otp):
    """
    Saves a password-reset OTP into the user's document with a 10-minute expiry.
    Also resets the wrong-attempt counter to 0 so the user gets 5 fresh tries.
    Uses separate fields (reset_otp, reset_otp_expiry) so signup OTP is untouched.
    """
    collection = get_users_collection()
    expiry = datetime.utcnow() + timedelta(minutes=10)
    collection.update_one(
        {"email": email},
        {"$set": {
            "reset_otp":        otp,
            "reset_otp_expiry": expiry,
            "reset_attempts":   0,     # fresh start — 5 attempts allowed
        }}
    )


def send_reset_otp_email(email, otp):
    """
    Emails the password-reset OTP to the user.
    Uses the same email_service.send_email() so TEST MODE works here too.
    Returns True if sent, False if it fell back to terminal.
    """
    subject = "Maharashtra Places — password reset code"
    body = (
        f"Hello,\n\n"
        f"Your password reset code is: {otp}\n\n"
        f"It is valid for 10 minutes.\n\n"
        f"If you did not request a password reset, please ignore this email.\n\n"
        f"— Maharashtra Places Team"
    )
    return send_email(email, subject, body)


def verify_reset_otp(email, otp_entered):
    """
    Checks the password-reset OTP.
    Returns "ok", "expired", "invalid", or "locked".
      "ok"      — OTP matches and is within 10 minutes
      "expired" — OTP matches but time is up
      "locked"  — too many wrong attempts (5 or more); must request a new OTP
      "invalid" — OTP does not match
    The attempt counter is incremented on every wrong guess.
    """
    collection = get_users_collection()
    user = collection.find_one({"email": email})

    if not user or not user.get("reset_otp"):
        return "invalid"

    # If already 5+ wrong attempts, lock further guesses
    if user.get("reset_attempts", 0) >= 5:
        return "locked"

    if user.get("reset_otp") != otp_entered:
        # Wrong guess — increment the attempt counter
        collection.update_one(
            {"email": email},
            {"$inc": {"reset_attempts": 1}}   # $inc adds 1 to the counter
        )
        return "invalid"

    if datetime.utcnow() > user.get("reset_otp_expiry"):
        return "expired"

    return "ok"


def update_password(email, new_password):
    """
    Hashes the new password and saves it.
    Clears reset_otp and reset_otp_expiry so the code cannot be reused.
    Resets the attempt counter.
    """
    collection = get_users_collection()
    collection.update_one(
        {"email": email},
        {"$set": {
            "password_hash":    generate_password_hash(new_password),
            "reset_otp":        None,
            "reset_otp_expiry": None,
            "reset_attempts":   0,
        }}
    )


# ─────────────────────────────────────────────
# LOGIN HELPERS
# ─────────────────────────────────────────────

def find_user_by_email(email):
    """
    Returns the user document for that email (without _id), or None if not found.
    {"_id": 0} tells MongoDB to leave out its internal _id field.
    """
    collection = get_users_collection()
    return collection.find_one({"email": email}, {"_id": 0})


def check_password(user, password_entered):
    """
    Returns True if the entered password matches the stored hash, False otherwise.
    check_password_hash() re-hashes the input and compares — no plain text stored.
    """
    return check_password_hash(user["password_hash"], password_entered)


# ─────────────────────────────────────────────
# SESSION HELPERS
# ─────────────────────────────────────────────

def login_user(session, user):
    """
    Saves the user's name and email into the Flask session cookie.
    The session is signed with SECRET_KEY so it cannot be tampered with.
    """
    session["user_name"]  = user["name"]
    session["user_email"] = user["email"]


def logout_user(session):
    """
    Clears all data from the Flask session, logging the user out.
    The next request will find no user data and treat them as a guest.
    """
    session.clear()


def get_logged_in_user(session):
    """
    Returns the name of the logged-in user, or None if not logged in.
    Routes use this to decide whether to show the page or redirect to /login.
    """
    return session.get("user_name")


# ─────────────────────────────────────────────
# Run once to create the unique email index
# ─────────────────────────────────────────────
if __name__ == "__main__":
    create_users_index()
