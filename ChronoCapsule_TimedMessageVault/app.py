import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(page_title="ChronoCapsule", page_icon="⏳", layout="wide")

# Supabase client
supabase_url = st.secrets["supabase"]["url"]
supabase_key = st.secrets["supabase"]["key"]
supabase = create_client(supabase_url, supabase_key)

# Session state for active menu
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Create Capsule"

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
body {font-family:'Poppins',sans-serif; background:#f4f6f8;}
.main-header {text-align:center; font-size:2.2rem; font-weight:700; color:white; padding:1rem; border-radius:14px;
background: linear-gradient(90deg,#6a11cb,#2575fc); margin-bottom:2rem; box-shadow:0 4px 12px rgba(0,0,0,0.25);}
.section-header {font-size:1.6rem; font-weight:600; color:#283E51; margin-bottom:0.5rem;}
.divider {height:4px; width:100px; background: linear-gradient(90deg,#4B79A1,#283E51); border-radius:2px; margin-bottom:1.5rem;}
.capsule-card, .user-card {background:#fff; border-radius:16px; padding:1.8rem; margin-bottom:1rem; box-shadow:0 6px 20px rgba(0,0,0,0.1); transition:all 0.3s ease;}
.capsule-card:hover, .user-card:hover {transform:translateY(-4px); box-shadow:0 10px 25px rgba(0,0,0,0.15);}
.capsule-title, .user-name {font-weight:600; font-size:1.3rem; color:#2C3E50;}
.capsule-message, .user-info {color:#555; font-size:1rem; margin-top:6px;}
.status-pending {color:#E67E22; font-weight:600;}
.status-delivered {color:#27AE60; font-weight:600;}
.stButton>button {border-radius:16px; padding:20px; font-size:18px; font-weight:600; color:white; margin-bottom:10px; width:200px;}
.stButton>button:hover {transform:translateY(-3px); opacity:0.9;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">⏳ ChronoCapsule — Timed Messages</div>', unsafe_allow_html=True)

# ------------------- Sidebar Menu -------------------
with st.sidebar:
    st.markdown("<h4 style='text-align:center;'>📋 MENU</h4>", unsafe_allow_html=True)

    # Menu buttons with different classic colors
    if st.button("📝 Create Capsule", key="create_capsule"):
        st.session_state.active_menu = "Create Capsule"
    if st.button("📦 View Capsules", key="view_capsules"):
        st.session_state.active_menu = "View Capsules"
    if st.button("👥 Manage Users", key="manage_users"):
        st.session_state.active_menu = "Manage Users"

    # Custom button colors using JS trick
    st.markdown("""
    <style>
    button[kind='primary']:nth-of-type(1) {background:#3498DB;}
    button[kind='primary']:nth-of-type(2) {background:#2ECC71;}
    button[kind='primary']:nth-of-type(3) {background:#F39C12;}
    </style>
    """, unsafe_allow_html=True)

# ------------------- Active Menu -------------------
menu = st.session_state.active_menu

# ------------------- CREATE CAPSULE -------------------
if menu == "Create Capsule":
    st.markdown('<div class="section-header">📝 Create Capsule</div><div class="divider"></div>', unsafe_allow_html=True)
    try:
        users = supabase.table("users").select("*").execute().data
    except:
        users = []

    if not users:
        st.warning("⚠️ No users found! Enter email manually.")
        recipient_email = st.text_input("Recipient Email")
    else:
        user_map = {u['name']: u for u in users}
        selected_name = st.selectbox("Select User (optional)", ["-- None --"] + list(user_map.keys()))
        recipient_email = st.text_input("Or enter a custom email")
        if selected_name != "-- None --" and not recipient_email:
            recipient_email = user_map[selected_name]['email']

    title = st.text_input("Capsule Title")
    message = st.text_area("Capsule Message (HTML supported)")

    selected_date = st.date_input("Select Date", datetime.now().date())
    selected_time = st.time_input("Select Time", datetime.now().time())
    local_dt = datetime.combine(selected_date, selected_time)
    scheduled_utc = local_dt - timedelta(hours=5, minutes=30)
    st.info(f"🕒 Scheduled (IST): {local_dt.strftime('%Y-%m-%d %H:%M')} | 🌍 Stored (UTC): {scheduled_utc.strftime('%Y-%m-%d %H:%M')}")

    if st.button("Create Capsule ✅"):
        if not recipient_email or not title or not message:
            st.error("Fill all fields!")
        else:
            try:
                supabase.table("capsules").insert({
                    "title": title,
                    "message": message,
                    "recipient_email": recipient_email,
                    "scheduled_time": scheduled_utc.isoformat(),
                    "is_delivered": False
                }).execute()
                st.success("🎉 Capsule scheduled!")
            except Exception as e:
                st.error(f"Error: {e}")

# ------------------- VIEW CAPSULES -------------------
elif menu == "View Capsules":
    st.markdown('<div class="section-header">📦 View Capsules</div><div class="divider"></div>', unsafe_allow_html=True)
    filter_status = st.radio("Filter By", ["All", "Pending", "Delivered"], horizontal=True)

    try:
        data = supabase.table("capsules").select("*").execute().data
    except:
        data = []

    if data:
        df = pd.DataFrame(data)
        df["scheduled_time"] = pd.to_datetime(df["scheduled_time"], utc=True, errors="coerce")
        df["scheduled_ist"] = df["scheduled_time"] + timedelta(hours=5, minutes=30)
        if filter_status=="Pending": df = df[df["is_delivered"]==False]
        elif filter_status=="Delivered": df = df[df["is_delivered"]==True]

        if df.empty: st.info("No capsules match filter.")
        else:
            for _, row in df.iterrows():
                scheduled_str = row["scheduled_ist"].strftime('%Y-%m-%d %H:%M') if pd.notnull(row["scheduled_ist"]) else "N/A"
                st.markdown(f"""
                <div class="capsule-card">
                    <div class="capsule-title">🎯 {row['title']}</div>
                    <div class="capsule-message">{row['message']}</div>
                    <div class="capsule-message">
                        <b>Recipient:</b> {row['recipient_email']}<br>
                        <b>Scheduled (IST):</b> {scheduled_str}<br>
                        <b>Status:</b> {"<span class='status-delivered'>✅ Delivered</span>" if row['is_delivered'] else "<span class='status-pending'>⌛ Pending</span>"}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No capsules found.")

# ------------------- MANAGE USERS -------------------
elif menu == "Manage Users":
    st.markdown('<div class="section-header">👥 Manage Users</div><div class="divider"></div>', unsafe_allow_html=True)
    name = st.text_input("Name")
    email = st.text_input("Email")
    if st.button("Add User ➕"):
        if name and email:
            try: supabase.table("users").insert({"name": name,"email": email}).execute(); st.success("✅ User added!")
            except Exception as e: st.error(f"Error: {e}")
        else: st.error("Enter Name and Email!")

    try: users = supabase.table("users").select("*").execute().data
    except: users = []

    if users:
        df_users = pd.DataFrame(users)
        for _, row in df_users.iterrows():
            st.markdown(f"""
            <div class="user-card">
                <div class="user-name">👤 {row['name']}</div>
                <div class="user-info"><b>Email:</b> {row['email']}</div>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("No users found.")
