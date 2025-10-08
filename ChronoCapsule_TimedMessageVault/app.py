# app.py
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from supabase import create_client
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import warnings

warnings.filterwarnings("ignore")

# -------------------
# PAGE CONFIG
# -------------------
st.set_page_config(page_title="ChronoCapsule", page_icon="⏳", layout="wide")

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
# HEADER
# -------------------
st.title("⏳ ChronoCapsule Dashboard")
st.markdown("Create, schedule, and deliver digital time capsules 📦")

# -------------------
# SIDEBAR MENU
# -------------------
menu = st.sidebar.radio("📌 Menu", ["Create Capsule", "View Capsules", "Manage Users"])

# -------------------
# CREATE CAPSULE
# -------------------
if menu == "Create Capsule":
    st.subheader("📝 Create a New Capsule")

    try:
        users = supabase.table("users").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        users = []

    if not users:
        st.warning("⚠️ No users found! You can still enter an email manually.")
        selected_user = None
        recipient_email = st.text_input("Enter Recipient Email")
    else:
        user_map = {u['name']: u for u in users}
        selected_name = st.selectbox("Select User (optional)", ["-- None --"] + list(user_map.keys()))
        recipient_email = st.text_input("Or enter a custom email")

        if selected_name != "-- None --" and not recipient_email:
            recipient_email = user_map[selected_name]['email']

    # Capsule details
    title = st.text_input("Capsule Title")
    message = st.text_area("Capsule Message (supports HTML formatting)")

    # Schedule inputs
    if "scheduled_date" not in st.session_state:
        st.session_state["scheduled_date"] = datetime.now().date()
    if "scheduled_time" not in st.session_state:
        st.session_state["scheduled_time"] = datetime.now().time()

    selected_date = st.date_input("Select Date", value=st.session_state["scheduled_date"])
    selected_time = st.time_input("Select Time", value=st.session_state["scheduled_time"])
    scheduled_time = datetime.combine(selected_date, selected_time)

    st.write("Scheduled for:", scheduled_time)

    # Save capsule
    if st.button("Create Capsule ✅"):
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
                    "scheduled_time": scheduled_time.isoformat(),
                    "is_delivered": False
                }).execute()
                st.success("🎉 Capsule created and scheduled!")

                # Optional: Send immediate confirmation email
                send_now = st.checkbox("Send confirmation email now?")
                if send_now:
                    sent = send_email(recipient_email, f"Capsule Scheduled: {title}",
                                      f"<p>Your capsule titled <b>{title}</b> has been scheduled for delivery at {scheduled_time}.</p>")
                    if sent:
                        st.info("📨 Confirmation email sent successfully!")

            except Exception as e:
                st.error(f"Error creating capsule: {e}")


# -------------------
# VIEW CAPSULES
# -------------------
elif menu == "View Capsules":
    st.subheader("📦 All Capsules")

    filter_status = st.radio("Filter by", ["All", "Pending", "Delivered"], horizontal=True)

    try:
        data = supabase.table("capsules").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching capsules: {e}")
        data = []

    if data:
        df = pd.DataFrame(data)

        if filter_status == "Pending":
            df = df[df["is_delivered"] == False]
        elif filter_status == "Delivered":
            df = df[df["is_delivered"] == True]

        if df.empty:
            st.info("No capsules match the selected filter.")
        else:
            for _, row in df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="padding:15px; margin:10px 0; border-radius:10px; 
                    box-shadow: 2px 2px 12px rgba(0,0,0,0.1); background-color:#f9f9f9;">
                    <h4>🎯 {row['title']}</h4>
                    <p>{row['message']}</p>
                    <p><b>Recipient:</b> {row['recipient_email']}<br>
                    <b>Scheduled:</b> {row['scheduled_time']}<br>
                    <b>Status:</b> {"✅ Delivered" if row['is_delivered'] else "⌛ Pending"}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No capsules found.")


# -------------------
# MANAGE USERS
# -------------------
elif menu == "Manage Users":
    st.subheader("👤 User Management")
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
        st.markdown("### Existing Users")
        df_users = pd.DataFrame(users)
        st.table(df_users)
    else:
        st.info("No users found.")
