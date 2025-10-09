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
st.markdown("""
    <style>
        h1 {
            text-align: center;
            color: #2C3E50;
            font-family: 'Poppins', sans-serif;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #555;
            font-size: 18px;
            margin-bottom: 40px;
            font-family: 'Poppins', sans-serif;
        }
        .capsule-card {
            padding: 18px;
            margin: 15px 0;
            border-radius: 12px;
            background: linear-gradient(135deg, #ffffff, #f9f9f9);
            box-shadow: 0px 4px 12px rgba(0,0,0,0.07);
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }
        .capsule-card:hover {
            transform: scale(1.01);
            box-shadow: 0px 6px 18px rgba(0,0,0,0.1);
        }
        .capsule-title {
            font-size: 20px;
            font-weight: 600;
            color: #2C3E50;
            margin-bottom: 5px;
        }
        .capsule-message {
            color: #555;
            margin-bottom: 12px;
        }
        .capsule-info {
            font-size: 14px;
            color: #444;
            background-color: #f1f3f4;
            border-radius: 8px;
            padding: 10px;
        }
        .status-pending {
            color: #E67E22;
            font-weight: 600;
        }
        .status-delivered {
            color: #27AE60;
            font-weight: 600;
        }
        .stButton>button {
            background: linear-gradient(90deg, #2C3E50, #4CA1AF);
            color: white;
            font-weight: 600;
            border-radius: 10px;
            padding: 8px 20px;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #4CA1AF, #2C3E50);
            transform: translateY(-2px);
        }
    </style>
""", unsafe_allow_html=True)

st.title("⏳ ChronoCapsule Dashboard")
st.markdown("<p class='subtitle'>Create, schedule, and deliver your memories in time — elegantly. 📦</p>", unsafe_allow_html=True)

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

    local_dt = datetime.combine(selected_date, selected_time)
    scheduled_time_utc = local_dt - timedelta(hours=5, minutes=30)

    st.info(f"🕒 Scheduled for (IST): {local_dt.strftime('%Y-%m-%d %H:%M')}  |  🌍 Stored as (UTC): {scheduled_time_utc.strftime('%Y-%m-%d %H:%M')}")

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
                    "scheduled_time": scheduled_time_utc.isoformat(),
                    "is_delivered": False
                }).execute()
                st.success("🎉 Capsule created and scheduled successfully!")
            except Exception as e:
                st.error(f"Error creating capsule: {e}")

# -------------------
# VIEW CAPSULES
# -------------------
elif menu == "View Capsules":
    st.subheader("📦 View Capsules")

    filter_status = st.radio("Filter by", ["All", "Pending", "Delivered"], horizontal=True)

    try:
        data = supabase.table("capsules").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching capsules: {e}")
        data = []

    if data:
        df = pd.DataFrame(data)
        df["scheduled_time"] = pd.to_datetime(df["scheduled_time"], utc=True, errors="coerce")
        df["scheduled_ist"] = df["scheduled_time"] + timedelta(hours=5, minutes=30)

        if filter_status == "Pending":
            df = df[df["is_delivered"] == False]
        elif filter_status == "Delivered":
            df = df[df["is_delivered"] == True]

        if df.empty:
            st.info("No capsules match the selected filter.")
        else:
            for _, row in df.iterrows():
                st.markdown(f"""
                <div class='capsule-card'>
                    <div class='capsule-title'>🎯 {row['title']}</div>
                    <div class='capsule-message'>{row['message']}</div>
                    <div class='capsule-info'>
                        <b>Recipient:</b> {row['recipient_email']}<br>
                        <b>Scheduled (IST):</b> {row['scheduled_ist'].strftime('%Y-%m-%d %H:%M')}<br>
                        <b>UTC Time:</b> {row['scheduled_time'].strftime('%Y-%m-%d %H:%M')}<br>
                        <b>Status:</b> {"<span class='status-delivered'>✅ Delivered</span>" if row['is_delivered'] else "<span class='status-pending'>⌛ Pending</span>"}
                    </div>
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
        st.dataframe(df_users.style.set_properties(**{
            'background-color': '#f9f9f9',
            'border-color': 'white',
            'color': '#2C3E50',
        }))
    else:
        st.info("No users found.")
