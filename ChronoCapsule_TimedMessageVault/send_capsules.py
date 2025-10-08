import os
from supabase import create_client
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Load environment variables ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if not all([SUPABASE_URL, SUPABASE_KEY, EMAIL_ADDRESS, EMAIL_PASSWORD]):
    print("❌ Error: Missing environment variables. Please set SUPABASE_URL, SUPABASE_KEY, EMAIL_ADDRESS, EMAIL_PASSWORD.")
    exit(1)

# --- Initialize Supabase client ---
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Email sending function ---
def send_email(to_email, subject, body):
    """Send an email using Gmail SMTP"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False

# --- Capsule delivery logic ---
def main():
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc + timedelta(hours=5, minutes=30)

    print(f"Checking for capsules to send at (IST): {now_ist}")

    # Convert IST back to UTC for comparison with stored UTC time
    now_iso = now_ist.astimezone(timezone.utc).isoformat()

    response = supabase.table("capsules").select("*").filter("is_delivered", "eq", False).filter("scheduled_time", "lte", now_iso).execute()
    capsules = response.data

    if not capsules:
        print("No capsules to send.")
        return

    for capsule in capsules:
        recipient = capsule.get("recipient_email")
        if not recipient:
            print(f"Skipping capsule {capsule['id']}: No recipient email.")
            continue

        title = capsule.get("title", "No Subject")
        message = capsule.get("message", "")

        sent = send_email(recipient, f"ChronoCapsule: {title}", message)

        if sent:
            supabase.table("capsules").update({"is_delivered": True}).eq("id", capsule["id"]).execute()
            print(f"✅ Marked capsule {capsule['id']} as delivered.")

if __name__ == "__main__":
    main()

