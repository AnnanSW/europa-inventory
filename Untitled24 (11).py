# europa_inventory_part1.py
import streamlit as st
import copy
from datetime import datetime

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 10

# --- INITIAL INVENTORY ---
def get_initial_inventory():
    return {
        "Hydratable Meals": {
            "Beef Stroganoff (Pouch)": {"current": 50, "original": 50},
            "Scrambled Eggs (Powder)": {"current": 75, "original": 75},
            "Cream of Mushroom Soup (Mix)": {"current": 60, "original": 60},
            "Macaroni and Cheese (Dry)": {"current": 45, "original": 45},
            "Asparagus Tips (Dried)": {"current": 30, "original": 30},
            "Grape Drink (Mix)": {"current": 90, "original": 90},
            "Coffee (Mix)": {"current": 110, "original": 110},
            "Chili (Dried)": {"current": 40, "original": 40},
            "Chicken and Rice (Dried)": {"current": 55, "original": 55},
            "Oatmeal with Applesauce (Dry)": {"current": 80, "original": 80}
        },
        "Thermostabilized Meals": {
            "Lemon Pepper Tuna (Pouch)": {"current": 120, "original": 120},
            "Spicy Green Beans (Pouch)": {"current": 85, "original": 85},
            "Pork Chop (Pouch)": {"current": 70, "original": 70},
            "Chicken Tacos (Pouch)": {"current": 95, "original": 95},
            "Turkey (Pouch)": {"current": 65, "original": 65},
            "Brownie (Pouch)": {"current": 100, "original": 100},
            "Raspberry Yogurt (Pouch)": {"current": 130, "original": 130},
            "Ham Steak (Pouch)": {"current": 55, "original": 55},
            "Sausage Patty (Pouch)": {"current": 40, "original": 40},
            "Fruit Cocktail (Pouch)": {"current": 75, "original": 75}
        },
        "Natural Form & Irradiated": {
            "Pecans (Irradiated)": {"current": 60, "original": 60},
            "Shortbread Cookies": {"current": 90, "original": 90},
            "Crackers": {"current": 150, "original": 150},
            "M&Ms (Candy)": {"current": 180, "original": 180},
            "Tortillas (Packages)": {"current": 200, "original": 200},
            "Dried Apricots": {"current": 80, "original": 80},
            "Dry Roasted Peanuts": {"current": 70, "original": 70},
            "Beef Jerky (Strips)": {"current": 45, "original": 45},
            "Fruit Bar": {"current": 110, "original": 110},
            "Cheese Spread (Tube)": {"current": 65, "original": 65}
        },
        "Desserts & Beverages (Non-Mix)": {
            "Space Ice Cream (Freeze-dried)": {"current": 40, "original": 40},
            "Banana Pudding (Pouch)": {"current": 50, "original": 50},
            "Chocolate Pudding (Pouch)": {"current": 55, "original": 55},
            "Apple Sauce (Pouch)": {"current": 70, "original": 70},
            "Orange Juice (Carton)": {"current": 85, "original": 85},
            "Tea Bags (Box)": {"current": 100, "original": 100},
            "Hot Cocoa (Mix)": {"current": 90, "original": 90},
            "Cranberry Sauce (Pouch)": {"current": 45, "original": 45},
            "Strawberry Shake (Mix)": {"current": 60, "original": 60},
            "Dried Peaches": {"current": 35, "original": 35}
        },
        "Condiments & Spreads": {
            "Ketchup (Packet)": {"current": 300, "original": 300},
            "Mustard (Packet)": {"current": 250, "original": 250},
            "Salt (Packet)": {"current": 400, "original": 400},
            "Pepper (Packet)": {"current": 400, "original": 400},
            "Jelly (Packet)": {"current": 150, "original": 150},
            "Honey (Tube)": {"current": 100, "original": 100},
            "Hot Sauce (Bottle)": {"current": 50, "original": 50},
            "Mayonnaise (Packet)": {"current": 200, "original": 200},
            "Sugar (Packet)": {"current": 350, "original": 350},
            "Taco Sauce (Packet)": {"current": 120, "original": 120}
        }
    }

# --- SESSION STATE ---
if "inventory" not in st.session_state:
    st.session_state.inventory = get_initial_inventory()
if "change_log" not in st.session_state:
    st.session_state.change_log = []

# --- HELPER FUNCTIONS ---
def get_item_color(amount):
    if amount == 0:
        return "red"
    elif amount <= LOW_STOCK_THRESHOLD:
        return "orange"
    else:
        return "green"

def go_to_category(category):
    st.session_state.page = "Category"
    st.session_state.open_category = category

def go_to_inventory():
    st.session_state.page = "Inventory"
    st.session_state.open_category = None
    st.session_state.edit_item_page = None
# --- PAGE FUNCTIONS ---

def inventory_page():
    st.markdown("<h1 style='text-align:center; color:cyan;'>EUROPA INVENTORY</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("## NAVIGATION")
    for category in st.session_state.inventory.keys():
        if st.sidebar.button(category):
            go_to_category(category)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Version History"):
        st.session_state.page = "History"

    # Display category overview with progress bars
    for category, items in st.session_state.inventory.items():
        with st.expander(category, expanded=False):
            for item_name, data in items.items():
                col1, col2, col3 = st.columns([4,2,2])
                with col1:
                    st.markdown(f"**{item_name}**")
                with col2:
                    progress = data["current"] / data["original"]
                    st.progress(progress)
                with col3:
                    color = get_item_color(data["current"])
                    st.markdown(f"<span style='color:{color}'>{data['current']} / {data['original']}</span>", unsafe_allow_html=True)
                    if st.button(f"Edit {item_name}", key=f"edit_{item_name}"):
                        st.session_state.page = "EditItem"
                        st.session_state.edit_item_page = (category, item_name)

def edit_item_page():
    category, item_name = st.session_state.edit_item_page
    data = st.session_state.inventory[category][item_name]
    
    st.markdown(f"<h2 style='color:cyan;'>{item_name} (EUROPA)</h2>", unsafe_allow_html=True)
    st.markdown(f"Original: {data['original']} units  |  Current: {data['current']} units")
    
    col1, col2 = st.columns(2)
    with col1:
        add_val = st.number_input("Add Units", min_value=0, value=0, key="add_input")
    with col2:
        remove_val = st.number_input("Remove Units", min_value=0, value=0, key="remove_input")
    
    # Ensure mutual exclusion
    if add_val > 0:
        st.session_state["remove_input"] = 0
    if remove_val > 0:
        st.session_state["add_input"] = 0
    
    if st.button("Apply Changes"):
        if add_val > 0:
            new_amount = min(data["current"] + add_val, data["original"])
            if new_amount == data["current"]:
                st.warning("Cannot exceed original capacity.")
            else:
                record_change(category, item_name, data["current"], new_amount, "add")
                data["current"] = new_amount
                st.success(f"Added {add_val} units to {item_name}.")
                st.session_state.page = "Inventory"
        elif remove_val > 0:
            new_amount = max(data["current"] - remove_val, 0)
            record_change(category, item_name, data["current"], new_amount, "remove")
            data["current"] = new_amount
            st.success(f"Removed {remove_val} units from {item_name}.")
            st.session_state.page = "Inventory"
        else:
            st.warning("No change applied.")
    
    if st.button("Back"):
        st.session_state.page = "Inventory"

def version_history_page():
    st.markdown("<h2 style='color:cyan;'>Version History</h2>", unsafe_allow_html=True)
    for entry in reversed(st.session_state.change_log):
        st.markdown(f"{entry['timestamp']} | {entry['action']} | {entry['item']} | {entry['old_amount']} -> {entry['new_amount']}")
    if st.button("Back"):
        st.session_state.page = "Inventory"

# --- MAIN APP ---
if "page" not in st.session_state:
    st.session_state.page = "Inventory"
if "open_category" not in st.session_state:
    st.session_state.open_category = None
if "edit_item_page" not in st.session_state:
    st.session_state.edit_item_page = None

if st.session_state.page == "Inventory":
    inventory_page()
elif st.session_state.page == "EditItem":
    edit_item_page()
elif st.session_state.page == "History":
    version_history_page()
# --- ADDITIONAL STYLING & ALERTS ---

def get_item_color(amount):
    """Returns color based on current inventory level."""
    if amount == 0:
        return "red"
    elif amount <= LOW_STOCK_THRESHOLD:
        return "orange"
    else:
        return "green"

# Apply NASA-style theme using Streamlit markdown
st.markdown("""
    <style>
        .stApp {
            background-color: #0b0c10;
            color: #c5c6c7;
        }
        .css-1d391kg {padding:1rem 1rem 1rem 1rem;}
        .stButton>button {
            background-color: #1f2833;
            color: #66fcf1;
            border-radius: 10px;
            border: 2px solid #45a29e;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #45a29e;
            color: #0b0c10;
        }
        .stProgress>div>div>div>div {
            background-color: #45a29e;
        }
        .stTextInput>div>input {
            background-color: #1f2833;
            color: #66fcf1;
        }
    </style>
""", unsafe_allow_html=True)

# --- VERSION HISTORY RECORD FUNCTION ---
def record_change(category, item, old_amount, new_amount, action):
    """Records any add/remove action to the change log."""
    st.session_state.change_log.append({
        "version_id": len(st.session_state.change_log)+1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "item": item,
        "action": action,
        "old_amount": old_amount,
        "new_amount": new_amount,
        "state_before_change": copy.deepcopy(st.session_state.inventory)
    })

def revert_version(version_id):
    """Restores inventory to a previous version."""
    try:
        restored_state = copy.deepcopy(st.session_state.change_log[version_id-1]["state_before_change"])
        st.session_state.inventory = restored_state
        st.session_state.change_log.append({
            "version_id": len(st.session_state.change_log)+1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": "SYSTEM",
            "item": "INVENTORY_WIDE",
            "action": f"RESTORATION_TO_V{version_id}",
            "old_amount": "N/A",
            "new_amount": "N/A",
            "state_before_change": copy.deepcopy(st.session_state.inventory)
        })
        st.success(f"Inventory restored to version {version_id}.")
    except:
        st.error("Invalid version ID")
