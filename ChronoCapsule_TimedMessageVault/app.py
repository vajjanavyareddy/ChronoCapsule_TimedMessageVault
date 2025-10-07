# app.py
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from supabase import create_client
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# -------------------
# PAGE CONFIG
# -------------------
st.set_page_config(page_title="ChronoCapsule", page_icon="⏳", layout="wide")

# -------------------
# SUPABASE CLIENT (using Streamlit Secrets)
# -------------------
supabase_url = st.secrets["supabase"]["url"]
supabase_key = st.secrets["supabase"]["key"]
supabase = create_client(supabase_url, supabase_key)

# Debug: check connection (optional)
# st.write("✅ Connected to Supabase!")

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
        # Use email from selected user
            recipient_email = user_map[selected_name]['email']

# Other inputs
    title = st.text_input("Capsule Title")
    message = st.text_area("Capsule Message")

# Scheduled time inputs (with session_state as before)
    if "scheduled_date" not in st.session_state:
        st.session_state["scheduled_date"] = datetime.now().date()
    if "scheduled_time" not in st.session_state:
        st.session_state["scheduled_time"] = datetime.now().time()

    selected_date = st.date_input("Select Date", value=st.session_state["scheduled_date"])
    selected_time = st.time_input("Select Time", value=st.session_state["scheduled_time"])
    scheduled_time = datetime.combine(selected_date, selected_time)

    st.write("Scheduled for:", scheduled_time)

# Validation
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
            # Show nice cards
            for _, row in df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="padding:15px; margin:10px 0; border-radius:10px; 
                    box-shadow: 2px 2px 12px rgba(0,0,0,0.1); background-color:#f9f9f9;">
                    <h4>🎯 {row['title']}</h4>
                    <p>{row['message']}</p>
                    <p><b>Scheduled:</b> {row['scheduled_time']}<br>
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







