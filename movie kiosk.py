import streamlit as st

# 1. Setup the Guest Data
the_waldicks = {
    "100101": {
        "name": "Scott Waldick", 
        "seat": "A1", 
        "drink": "Tea But You Have To Make It"
    },
    "100102": {
        "name": "Nikita Waldick", 
        "seat": "A2", 
        "drink": "Milk With A Red Cap"
    },
    "100103": {
        "name": "Jake Waldick", 
        "seat": "A3", 
        "drink": "Green Bottle That Looks Like A 40"
    },
    "100104": {
        "name": "Annan Waldick", 
        "seat": "A5", 
        "drink": "Water"
    },
    "100105": {
        "name": "Nima Waldick", 
        "seat": "A6", 
        "drink": "Tea"
    }
}

# 2. Page Configuration & Theme
st.set_page_config(page_title="Waldick Cinema Check-in", page_icon="🦖", layout="centered")

# Custom CSS for a dark theater vibe
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #E50914 !important; /* Cinematic Red */
        text-align: center;
    }
    .stAlert {
        background-color: #1f2937;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header Section
st.title("🦖 JURASSIC PARK: REBORN")
st.subheader("Waldick Private Screening - Guest Check-in")
st.divider()

# 4. Scanning Input
# Using a text input to act as the barcode receiver
barcode_input = st.text_input("PLEASE SCAN TICKET OR ENTER ID NUMBER:", placeholder="e.g. 100101")

# 5. Logic to Display Guest Info
if barcode_input:
    if barcode_input in the_waldicks:
        guest = the_waldicks[barcode_input]
        
        # Success Greeting
        st.balloons()
        st.success(f"ACCESS GRANTED: Welcome, {guest['name']}!")
        
        # Display Information Layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎫 Ticket Details")
            st.write(f"**Movie:** Jurassic Park: Reborn")
            st.write(f"**Seat Number:** `{guest['seat']}`")
            st.write(f"**Audio Package:** Premium Surround Sound")
        
        with col2:
            st.markdown("### 🍿 Concessions")
            st.write(f"**Popcorn:** Large (Unlimited Refills)")
            st.write(f"**Drink Choice:** {guest['drink']}")

        st.divider()
        st.info("🔊 **Notice:** This screening is optimized for 7.1 Surround Sound. Please take your seat.")
        
    else:
        st.error("⚠️ INVALID BARCODE: Please contact theater management.")

# 6. Sidebar (Admin view to see IDs if you forget them)
with st.sidebar:
    st.image("https://www.freeiconspng.com/uploads/jurassic-park-reborn-logo-1.png", use_container_width=True)
    st.markdown("---")
    st.markdown("**Operator Reference:**")
    for bid, data in the_waldicks.items():
        st.caption(f"{data['name']}: {bid}")