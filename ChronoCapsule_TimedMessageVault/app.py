import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, timedelta
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
# GLOBAL CSS — Elegant, Modern, and Smooth
# -------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        .main {
            background: linear-gradient(135deg, #E8F0FF, #F7FAFC);
            padding: 1.5rem;
            border-radius: 15px;
        }

        h1 {
            text-align: center;
            background: linear-gradient(90deg, #283E51, #4B79A1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 44px;
            margin-bottom: 5px;
        }

        .subtitle {
            text-align: center;
            color: #444;
            font-size: 18px;
            margin-bottom: 40px;
            opacity: 0.8;
        }

        .capsule-card {
            padding: 25px;
            margin: 22px 0;
            border-radius: 16px;
            background: linear-gradient(145deg, #ffffff, #f3f6fa);
            box-shadow: 0 6px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease-in-out;
        }

        .capsule-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.12);
        }

        .capsule-title {
            font-size: 22px;
            font-weight: 600;
            color: #243B55;
            margin-bottom: 10px;
        }

        .capsule-message {
            color: #333;
            font-size: 15.5px;
            margin-bottom: 14px;
            line-height: 1.5;
        }

        .capsule-info {
            font-size: 14px;
            background-color: #F8FAFC;
            padding: 12px;
            border-left: 5px solid #4B79A1;
            border-radius: 8px;
            margin-top: 10px;
            color: #333;
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
            background: linear-gradient(90deg, #4B79A1, #283E51);
            color: white;
            font-weight: 600;
            border-radius: 12px;
            padding: 10px 24px;
            border: none;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background: linear-gradient(90deg, #283E51, #4B79A1);
            transform: translateY(-2px);
        }

        .stTextInput>div>div>input, textarea, select {
            border-radius: 10px !important;
            border: 1px solid #dce1e7 !important;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
        }

        .stRadio>div {
            background: white;
            padding: 10px 15px;
            border-radius: 10px;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
        }

        .section-header {
            color: #283E51;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .divider {
            height: 3px;
            background: linear-gradient(90deg, #4B79A1, #283E51);
            border-radius: 2px;
            margin-bottom: 25px;
            width: 100px;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------
# HEADER
# -------------------
st.title("ChronoCapsule ⏳")
st.markdown("<p class='subtitle'>Timeless messages, delivered perfectly on time.</p>", unsafe_allow_html=True)

# -------------------
# SIDEBAR MENU
# -------------------
menu = st.sidebar.radio("📋 Menu", ["Create Capsule", "View Capsules", "Manage Users"])

# -------------------
# CREATE CAPSULE
# -------------------
if menu == "Create Capsule":
    st.markdown("<div class='section-header'>📝 Create a New Capsule</div><div class='divider'></div>", unsafe_allow_html=True)

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
    message = st.text_area("Capsule Message (supports HTML)")

    # Schedule Inputs
    selected_date = st.date_input("Select Date", value=datetime.now().date())
    selected_time = st.time_input("Select Time", value=datetime.now().time())
    local_dt = datetime.combine(selected_date, selected_time)
    scheduled_time_utc = local_dt - timedelta(hours=5, minutes=30)

    st.info(f"🕒 Scheduled (IST): {local_dt.strftime('%Y-%m-%d %H:%M')} | 🌍 Stored (UTC): {scheduled_time_utc.strftime('%Y-%m-%d %H:%M')}")

    if st.button("Create Capsule ✅"):
        if not recipient_email or not title or not message:
            st.error("Please fill in all fields!")
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
    st.markdown("<div class='section-header'>📦 View Capsules</div><div class='divider'></div>", unsafe_allow_html=True)

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
                # ✅ Safe date formatting fix
                scheduled_display = "Invalid Time"
                if pd.notna(row["scheduled_ist"]):
                    scheduled_display = row["scheduled_ist"].strftime('%Y-%m-%d %H:%M')

                st.markdown(f"""
                <div class="capsule-card">
                    <div class="capsule-title">🎯 {row['title']}</div>
                    <div class="capsule-message">{row['message']}</div>
                    <div class="capsule-info">
                        <b>Recipient:</b> {row['recipient_email']}<br>
                        <b>Scheduled (IST):</b> {scheduled_display}<br>
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
    st.markdown("<div class='section-header'>👤 Manage Users</div><div class='divider'></div>", unsafe_allow_html=True)

    name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")

    if st.button("Add User ➕"):
        try:
            supabase.table("users").insert({"name": name, "email": email}).execute()
            st.success("✅ User added successfully!")
        except Exception as e:
            st.error(f"Error adding user: {e}")

    try:
        users = supabase.table("users").select("*").execute().data
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        users = []

    if users:
        df_users = pd.DataFrame(users)
        st.dataframe(df_users.style.set_properties(**{
            'background-color': '#f9f9f9',
            'color': '#2C3E50',
        }))
    else:
        st.info("No users found.")
