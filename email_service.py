# email_service.py
# This file has ONE job: send an email.
# It is a separate file so any part of the project can import it easily.
#
# How it works:
#   1. Read EMAIL_ADDRESS and EMAIL_PASSWORD from the .env file.
#   2. Connect to Gmail's SMTP server (smtp.gmail.com, port 587).
#   3. Upgrade the connection to encrypted (starttls).
#   4. Log in and send the email.
#
# TEST MODE:
#   If EMAIL_ADDRESS or EMAIL_PASSWORD are missing in .env,
#   the email is NOT sent. Instead the message is printed in the terminal.
#   This lets you demo the project without a real Gmail account.

import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load .env so os.environ can read EMAIL_ADDRESS and EMAIL_PASSWORD
load_dotenv()


def send_email(to_email, subject, body):
    """
    Sends a plain-text email using Gmail SMTP.

    Parameters:
      to_email -- the recipient's email address  e.g. "alice@gmail.com"
      subject  -- the email subject line          e.g. "Your verification code"
      body     -- the email body text             e.g. "Your code is 483920..."

    Returns:
      True  -- email was sent successfully
      False -- sending failed (credentials missing or network error)

    In both failure cases the message is printed in the terminal so the
    developer can still read the OTP during testing.
    """
    sender   = os.environ.get("EMAIL_ADDRESS", "").strip()
    password = os.environ.get("EMAIL_PASSWORD", "").strip()

    # ── TEST MODE ────────────────────────────────────────────────────
    # If credentials are not set, fall back to printing in terminal
    if not sender or not password:
        print(f"\n[TEST MODE — no email sent]")
        print(f"  To     : {to_email}")
        print(f"  Subject: {subject}")
        print(f"  Body   : {body}\n")
        return False   # return False so the caller can show a fallback message

    # ── Build the email message ──────────────────────────────────────
    # MIMEText creates a properly formatted email object
    message = MIMEText(body, "plain")          # "plain" = plain text, not HTML
    message["Subject"] = subject
    message["From"]    = sender
    message["To"]      = to_email

    # ── Connect and send ─────────────────────────────────────────────
    try:
        # port 587 is the standard Gmail port for sending email with TLS
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()                  # upgrade to encrypted connection
            server.login(sender, password)     # log in to Gmail
            server.sendmail(sender, to_email, message.as_string())
        return True    # email sent successfully

    except Exception as error:
        # If sending fails for any reason (wrong password, network issue, etc.)
        # print in terminal so the developer can still read the OTP
        print(f"\n[EMAIL FAILED — printing here instead]")
        print(f"  To     : {to_email}")
        print(f"  Subject: {subject}")
        print(f"  Body   : {body}")
        print(f"  Error  : {error}\n")
        return False   # let the caller know the email was not delivered
