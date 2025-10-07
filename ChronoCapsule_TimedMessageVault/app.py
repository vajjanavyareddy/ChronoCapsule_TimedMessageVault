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
        st.warning("⚠️ No users found! Please create a user first.")
    else:
        user_map = {u['name']: u['id'] for u in users}
        creator = st.selectbox("Select User", list(user_map.keys()))
        title = st.text_input("Capsule Title")
        message = st.text_area("Capsule Message")
        # # scheduled_time = st.datetime_input("Schedule Time", value=datetime.now())
        # selected_date = st.date_input("Select Date", value=datetime.now().date())
        # selected_time = st.time_input("Select Time", value=datetime.now().time())
        # scheduled_time = datetime.combine(selected_date, selected_time)
        if "scheduled_time" not in st.session_state:
            st.session_state["scheduled_time"] = datetime.now()

    # Use datetime_input
        scheduled_time = st.datetime_input(
            "Schedule Time", 
            value=st.session_state["scheduled_time"], 
            key="scheduled_time_input"
        )

    st.write("Scheduled for:", scheduled_time)


        if st.button("Create Capsule ✅"):
            try:
                supabase.table("capsules").insert({
                    "title": title,
                    "message": message,
                    "creator_id": user_map[creator],
                    "scheduled_time": scheduled_time.isoformat(),
                    "is_delivered": False
                }).execute()
                st.success("🎉 Capsule created successfully!")
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


