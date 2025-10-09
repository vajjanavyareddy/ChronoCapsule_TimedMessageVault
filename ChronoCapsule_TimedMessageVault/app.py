import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import warnings

warnings.filterwarnings("ignore")

# -------------------
# PAGE CONFIG
# -------------------
st.set_page_config(page_title="ChronoCapsule ⏳", page_icon="⏳", layout="wide")

# -------------------
# SUPABASE CLIENT
# -------------------
supabase_url = st.secrets["supabase"]["url"]
supabase_key = st.secrets["supabase"]["key"]
supabase = create_client(supabase_url, supabase_key)

# -------------------
# EMAIL FUNCTION
# -------------------
def send_email(recipient, subject, message):
    try:
        sender_email = st.secrets["email"]["address"]
        sender_password = st.secrets["email"]["password"]

        msg = MIMEText(message, "html")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
        return False


# -------------------
# MAIN MENU CARDS
# -------------------
def home_page():
    st.markdown("""
    <h1 style='text-align:center; color:#333;'>⏳ ChronoCapsule Dashboard</h1>
    <p style='text-align:center; color:gray;'>Create, schedule, and deliver digital time capsules with ease.</p>
    <br><br>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        if st.button("📝 Create Capsule", use_container_width=True):
            st.session_state["page"] = "create"

    with col2:
        if st.button("📦 View Capsules", use_container_width=True):
            st.session_state["page"] = "view"

    with col3:
        if st.button("👤 Manage Users", use_container_width=True):
            st.session_state["page"] = "users"

    # Custom CSS for card styling
    st.markdown("""
        <style>
        div.stButton > button {
            background: linear-gradient(135deg, #89f7fe, #66a6ff);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 15px;
            padding: 20px;
            height: 130px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
            transition: 0.3s;
            font-size: 18px;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #66a6ff, #89f7fe);
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)


# -------------------
# CREATE CAPSULE
# -------------------
def create_capsule():
    st.markdown("<h2>📝 Create a New Capsule</h2>", unsafe_allow_html=True)

    try:
        users = supabase.table("users").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        users = []

    if not users:
        st.warning("⚠️ No users found! You can still enter an email manually.")
        recipient_email = st.text_input("Enter Recipient Email")
    else:
        user_map = {u['name']: u for u in users}
        selected_name = st.selectbox("Select User (optional)", ["-- None --"] + list(user_map.keys()))
        recipient_email = st.text_input("Or enter a custom email")

        if selected_name != "-- None --" and not recipient_email:
            recipient_email = user_map[selected_name]['email']

    title = st.text_input("Capsule Title")
    message = st.text_area("Capsule Message (supports HTML formatting)")

    selected_date = st.date_input("Select Date", value=datetime.now().date())
    selected_time = st.time_input("Select Time", value=datetime.now().time())

    local_dt = datetime.combine(selected_date, selected_time)
    scheduled_time_utc = local_dt - timedelta(hours=5, minutes=30)

    st.write(f"🕒 Scheduled for (IST): {local_dt.strftime('%Y-%m-%d %H:%M')}")
    st.write(f"🌍 Stored as (UTC): {scheduled_time_utc.strftime('%Y-%m-%d %H:%M')}")

    if st.button("✅ Create Capsule"):
        if not recipient_email:
            st.error("Please provide a recipient email.")
        elif not title or not message:
            st.error("Please fill in all required fields.")
        else:
            try:
                supabase.table("capsules").insert({
                    "title": title,
                    "message": message,
                    "recipient_email": recipient_email,
                    "scheduled_time": scheduled_time_utc.isoformat(),
                    "is_delivered": False
                }).execute()
                st.success("🎉 Capsule created and scheduled!")

                send_now = st.checkbox("Send confirmation email now?")
                if send_now:
                    sent = send_email(
                        recipient_email,
                        f"Capsule Scheduled: {title}",
                        f"<p>Your capsule titled <b>{title}</b> has been scheduled for delivery at {local_dt.strftime('%Y-%m-%d %H:%M %p IST')}.</p>"
                    )
                    if sent:
                        st.info("📨 Confirmation email sent successfully!")
            except Exception as e:
                st.error(f"Error creating capsule: {e}")


# -------------------
# VIEW CAPSULES
# -------------------
def view_capsules():
    st.markdown("<h2>📦 All Capsules</h2>", unsafe_allow_html=True)

    filter_status = st.radio("Filter by", ["All", "Pending", "Delivered"], horizontal=True)

    try:
        data = supabase.table("capsules").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching capsules: {e}")
        data = []

    if data:
        df = pd.DataFrame(data)
        df['scheduled_time'] = pd.to_datetime(df['scheduled_time'], utc=True, errors='coerce')
        df['scheduled_ist'] = df['scheduled_time'] + timedelta(hours=5, minutes=30)

        if filter_status == "Pending":
            df = df[df["is_delivered"] == False]
        elif filter_status == "Delivered":
            df = df[df["is_delivered"] == True]

        if df.empty:
            st.info("No capsules match the selected filter.")
        else:
            for _, row in df.iterrows():
                scheduled_display = (
                    row['scheduled_ist'].strftime('%Y-%m-%d %H:%M')
                    if pd.notnull(row['scheduled_ist'])
                    else "Invalid / Missing Time"
                )

                st.markdown(f"""
                <div style="padding:20px; margin:10px 0; border-radius:15px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.1); background-color:#ffffff;">
                <h4 style="color:#2E86C1;">🎯 {row['title']}</h4>
                <p>{row['message']}</p>
                <p><b>Recipient:</b> {row['recipient_email']}<br>
                <b>Scheduled (IST):</b> {scheduled_display}<br>
                <b>Status:</b> {"✅ Delivered" if row['is_delivered'] else "⌛ Pending"}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No capsules found.")


# -------------------
# MANAGE USERS
# -------------------
def manage_users():
    st.markdown("<h2>👤 User Management</h2>", unsafe_allow_html=True)
    name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")

    if st.button("Create User"):
        try:
            supabase.table("users").insert({"name": name, "email": email}).execute()
            st.success("✅ User created successfully!")
        except Exception as e:
            st.error(f"Error creating user: {e}")

    try:
        users = supabase.table("users").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        users = []

    if users:
        df_users = pd.DataFrame(users)
        st.table(df_users)
    else:
        st.info("No users found.")


# -------------------
# PAGE NAVIGATION
# -------------------
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if st.session_state["page"] == "home":
    home_page()
elif st.session_state["page"] == "create":
    create_capsule()
elif st.session_state["page"] == "view":
    view_capsules()
elif st.session_state["page"] == "users":
    manage_users()

# Back button for navigation
if st.session_state["page"] != "home":
    if st.button("⬅️ Back to Home"):
        st.session_state["page"] = "home"
