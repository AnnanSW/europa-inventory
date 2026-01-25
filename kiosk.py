import streamlit as st

# 1. Setup the Guest Data
the_waldicks = {
    "100101": {"name": "Scott Waldick", "seat": "A1", "drink": "Tea But You Have To Make It"},
    "100102": {"name": "Nikita Waldick", "seat": "A2", "drink": "Milk With A Red Cap"},
    "100103": {"name": "Jake Waldick", "seat": "A3", "drink": "Green Bottle That Looks Like A 40"},
    "100104": {"name": "Annan Waldick", "seat": "A5", "drink": "Water"},
    "100105": {"name": "Nima Waldick", "seat": "A6", "drink": "Tea"}
}

# 2. Page Configuration
st.set_page_config(page_title="Waldick Cinema Check-in", page_icon="🦖")

# Custom CSS for the "X" button and Theater Theme
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2 { color: #E50914 !important; text-align: center; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { width: 100%; border-radius: 20px; border: 1px solid #E50914; color: #E50914; }
    </style>
    """, unsafe_allow_html=True)

# 3. Initialize Session State
if 'current_guest' not in st.session_state:
    st.session_state.current_guest = None

# Function to reset the app
def reset_app():
    st.session_state.current_guest = None
    st.rerun()

# 4. App UI
st.title("🦖 JURASSIC PARK: REBORN")
st.subheader("Waldick Private Screening Check-in")
st.divider()

# Only show the input if no guest is currently "logged in"
if st.session_state.current_guest is None:
    barcode_input = st.text_input("PLEASE SCAN TICKET:", key="barcode_input")
    
    if barcode_input:
        if barcode_input in the_waldicks:
            st.session_state.current_guest = the_waldicks[barcode_input]
            st.rerun()
        else:
            st.error("⚠️ INVALID BARCODE")
else:
    # Display Guest Info Screen
    guest = st.session_state.current_guest
    
    # "X" Button to go back
    col_left, col_right = st.columns([0.85, 0.15])
    with col_right:
        if st.button("❌"):
            reset_app()

    st.balloons()
    st.success(f"ACCESS GRANTED: {guest['name']}")
    
    # Guest details layout
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🎫 Ticket")
        st.write(f"**Seat:** {guest['seat']}")
        st.write("**Popcorn:** Large + Refills")
        st.info("🔊 Premium Surround Sound")
        
    with c2:
        st.markdown("### 🥤 Order")
        st.write(f"**Drink:** {guest['drink']}")
    
    st.divider()
    if st.button("Next Guest"):
        reset_app()

# 5. Sidebar Operator View
with st.sidebar:
    st.markdown("**ID Cheat Sheet**")
    for bid, data in the_waldicks.items():
        st.caption(f"{data['name']}: `{bid}`")