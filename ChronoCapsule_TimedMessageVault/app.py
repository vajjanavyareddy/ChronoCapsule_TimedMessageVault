st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

body {font-family: 'Poppins', sans-serif; background-color:#f0f2f6;}

.main-header {
    text-align:center; font-size:2.5rem; font-weight:700; 
    color:white; padding:1.5rem; border-radius:14px; 
    background: linear-gradient(90deg, #6A0DAD, #9B30FF);
    margin-bottom:2rem; box-shadow:0 4px 12px rgba(0,0,0,0.25);
}

/* Sidebar radio buttons as cards */
.stRadio>div>label {
    display:block; padding:20px; margin-bottom:15px; border-radius:16px;
    font-size:1.2rem; font-weight:600; text-align:center; cursor:pointer;
    color:white; transition: all 0.3s ease;
}

/* Individual radio button gradients (light) */
.stRadio>div>label:nth-child(1) { background: linear-gradient(135deg, #a7c957, #d3e27f); }  /* Create Capsule - light green */
.stRadio>div>label:nth-child(2) { background: linear-gradient(135deg, #3399ff, #99ccff); }  /* View Capsules - light blue */
.stRadio>div>label:nth-child(3) { background: linear-gradient(135deg, #ff7f50, #ffb690); }  /* Manage Users - light orange */

/* Hover effect for "card" buttons */
.stRadio>div>label:hover {
    transform: translateY(-3px); box-shadow:0 6px 18px rgba(0,0,0,0.2);
}

/* Capsule/User Cards */
.capsule-card, .user-card {
    border-radius:16px; padding:1.5rem; margin-bottom:1rem;
    box-shadow:0 4px 12px rgba(0,0,0,0.1); transition: all 0.3s ease;
}
.capsule-card:hover, .user-card:hover {transform:translateY(-4px); box-shadow:0 8px 18px rgba(0,0,0,0.15);}
.capsule-title, .user-name {font-weight:600; font-size:1.2rem; color:#2C3E50;}
.capsule-message, .user-info {color:#555; font-size:0.95rem; margin-top:4px;}
.status-pending {color:#E67E22; font-weight:600;}
.status-delivered {color:#27AE60; font-weight:600;}
</style>
""", unsafe_allow_html=True)
