"""
alert.py
--------
Everything related to notifying a human that a violation happened.
Two channels are implemented:
  1. A local sound/console alert (always safe to leave on, works offline).
  2. An email alert (optional — needs real SMTP credentials in config.py).

Keeping alerting in its own file means you can swap in SMS (Twilio) or
a Telegram/WhatsApp bot later without touching the detection code.
"""

import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import (
    ENABLE_SOUND_ALERT,
    ENABLE_EMAIL_ALERT,
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    EMAIL_RECEIVER,
    EMAIL_SMTP_SERVER,
    EMAIL_SMTP_PORT,
)


def sound_alert():
    """Play a guaranteed audible system alert on Windows."""
    print("🚨 ALERT: Safety violation detected!")
    
    if sys.platform == "win32":
        try:
            import winsound
            # Plays standard Windows exclamation sound through normal speakers
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            # Backup frequency beep
            winsound.Beep(1200, 400)
            return
        except Exception as e:
            print(f"[SOUND ERROR] {e}")

    print("\a", end="", flush=True)


def email_alert(zone: str, violation_type: str):
    """Send an email notification. Requires EMAIL_* values to be filled in
    config.py and ENABLE_EMAIL_ALERT = True."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = f"SafeSite AI Alert: {violation_type} in {zone}"

        body = (
            f"A safety violation was detected.\n\n"
            f"Zone: {zone}\n"
            f"Violation type: {violation_type}\n\n"
            f"Please check the live dashboard for details and the snapshot image."
        )
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print(f"Email alert sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"Email alert failed (check config.py credentials): {e}")


def trigger_alert(zone: str, violation_type: str):
    """Single entry point called from the detection loop — fires whichever
    alert channels are enabled in config.py."""
    if ENABLE_SOUND_ALERT:
        sound_alert()
    if ENABLE_EMAIL_ALERT:
        email_alert(zone, violation_type)