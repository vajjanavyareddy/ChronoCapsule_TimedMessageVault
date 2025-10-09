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
# CUSTOM CSS
# -------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #101820, #243447);
    color: #EDEDED;
    font-family: 'Poppins', sans-serif;
}

h1, h2, h3, h4 {
    color: #E3F2FD !important;
}

[data-testid="stSidebar"] {display: none;}
.block-container {
    padding-top: 2rem;
}

.card {
    backdrop-filter: blur(12px);
    background: rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    padding: 40px;
    text-align: center;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.15);
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.35);
    background: rgba(255, 255, 255, 0.12);
}

.card button {
    width: 100%;
    background: linear-gradient(135deg, #00B4DB, #0083B0);
    border: none;
    padding: 15px;
    font-weight: 600;
    border-radius: 10px;
    color: white;
    transition: 0.3s;
}

.card button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #0083B0, #00B4DB);
}

.container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 50px;
    margin-top: 100px;
}

.content-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.15);
}

</style>
""", unsafe_allow_html=True)


# -------------------
# HOME PAGE
# -------------------
def home_page():
    st.markdown("<h1 style='text-align:center;'>⏳ ChronoCapsule Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#B0BEC5;'>Create, schedule, and deliver digital time capsules elegantly.</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if st.button("📝 Create Capsule"):
            st.session_state["page"] = "create"
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if st.button("📦 View Capsules"):
            st.session_state["page"] = "view"
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if st.button("👤 Manage Users"):
            st.session_state["page"] = "users"
        st.markdown("</div>", unsafe_allow_html=True)


# -------------------
# CREATE CAPSULE
# -------------------
def create_capsule():
    st.markdown("<h2>📝 Create a New Capsule</h2>", unsafe_allow_html=True)
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    try:
        users = supabase.table("users").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        users = []

    if not users:
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

    if st.button("✅ Create Capsule"):
        if not recipient_email or not title or not message:
            st.error("⚠️ Please fill in all required fields.")
        else:
            try:
                supabase.table("capsules").insert({
                    "title": title,
                    "message": message,
                    "recipient_email": recipient_email,
                    "scheduled_time": scheduled_time_utc.isoformat(),
                    "is_delivered": False
                }).execute()
                st.success("🎉 Capsule created successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------
# VIEW CAPSULES
# -------------------
def view_capsules():
    st.markdown("<h2>📦 All Capsules</h2>", unsafe_allow_html=True)
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    try:
        data = supabase.table("capsules").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching capsules: {e}")
        data = []

    if data:
        df = pd.DataFrame(data)
        df['scheduled_time'] = pd.to_datetime(df['scheduled_time'], utc=True, errors='coerce')
        df['scheduled_ist'] = df['scheduled_time'] + timedelta(hours=5, minutes=30)

        for _, row in df.iterrows():
            scheduled_display = (
                row['scheduled_ist'].strftime('%Y-%m-%d %H:%M')
                if pd.notnull(row['scheduled_ist'])
                else "Invalid Time"
            )
            st.markdown(f"""
            <div class='content-card'>
            <h4>🎯 {row['title']}</h4>
            <p>{row['message']}</p>
            <p><b>Recipient:</b> {row['recipient_email']}<br>
            <b>Scheduled (IST):</b> {scheduled_display}<br>
            <b>Status:</b> {"✅ Delivered" if row['is_delivered'] else "⌛ Pending"}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No capsules found.")
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------
# MANAGE USERS
# -------------------
def manage_users():
    st.markdown("<h2>👤 Manage Users</h2>", unsafe_allow_html=True)
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")

    if st.button("Create User"):
        try:
            supabase.table("users").insert({"name": name, "email": email}).execute()
            st.success("✅ User added successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

    try:
        users = supabase.table("users").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        users = []

    if users:
        st.table(pd.DataFrame(users))
    else:
        st.info("No users found.")
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------
# PAGE CONTROL
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

if st.session_state["page"] != "home":
    if st.button("⬅️ Back to Dashboard"):
        st.session_state["page"] = "home"
