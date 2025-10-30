# europa_inventory_nasa_part1.py
import streamlit as st
import copy
from datetime import datetime

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 10
FUZZY_TOLERANCE = 2

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

# --- SESSION STATE INIT ---
if "inventory" not in st.session_state:
    st.session_state.inventory = get_initial_inventory()
if "change_log" not in st.session_state:
    st.session_state.change_log = []
if "page" not in st.session_state:
    st.session_state.page = "Inventory"
if "open_category" not in st.session_state:
    st.session_state.open_category = None
if "edit_item_page" not in st.session_state:
    st.session_state.edit_item_page = None
if "add_units_edit" not in st.session_state:
    st.session_state.add_units_edit = 0
if "remove_units_edit" not in st.session_state:
    st.session_state.remove_units_edit = 0

# --- HELPER FUNCTIONS ---
def get_item_color(amount):
    if amount == 0: return "#FF4136"  # red
    if amount <= LOW_STOCK_THRESHOLD: return "#FF851B"  # orange
    return "#2ECC40"  # green

def record_change(category, item, old_amount, new_amount, action):
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
    except:
        st.error("Invalid version ID")
# europa_inventory_nasa_part2.py
# --- PAGE RENDERING FUNCTIONS ---

def display_inventory_page():
    st.title("EUROPA INVENTORY CONTROL PANEL")
    for category_name in st.session_state.inventory:
        if st.button(category_name):
            st.session_state.page = "Category"
            st.session_state.open_category = category_name

def display_category_page():
    category = st.session_state.open_category
    st.subheader(f"Category: {category}")
    for item in st.session_state.inventory[category]:
        if st.button(item):
            st.session_state.page = "Item"
            st.session_state.edit_item_page = (category, item)
    if st.button("Back"):
        st.session_state.page = "Inventory"
        st.session_state.open_category = None

def display_item_page():
    category, item = st.session_state.edit_item_page
    data = st.session_state.inventory[category][item]
    st.subheader(f"{item} (Category: {category})")
    st.write(f"Current: {data['current']} / Original: {data['original']}")

    add_val = st.number_input("Add Units", min_value=0, value=0, key="add_units_edit")
    remove_val = st.number_input("Remove Units", min_value=0, value=0, key="remove_units_edit")
    if add_val > 0:
        st.session_state.remove_units_edit = 0
    if remove_val > 0:
        st.session_state.add_units_edit = 0

    if st.button("Apply Change"):
        new_amount = data["current"] + add_val - remove_val
        if new_amount < 0:
            st.error("Cannot remove more than current units!")
        elif new_amount > data["original"]:
            st.error("Cannot add more than original amount!")
        else:
            record_change(category, item, data["current"], new_amount,
                          "add" if add_val else "remove")
            st.session_state.inventory[category][item]["current"] = new_amount
            st.success(f"Updated {item} to {new_amount} units")
            st.session_state.add_units_edit = 0
            st.session_state.remove_units_edit = 0

    if st.button("Back"):
        st.session_state.page = "Category"
        st.session_state.edit_item_page = None

def display_history_page():
    st.title("Version History")
    for entry in reversed(st.session_state.change_log):
        st.write(f"V{entry['version_id']} | {entry['timestamp']} | {entry['category']}:{entry['item']} | {entry['action']} | {entry['old_amount']} -> {entry['new_amount']}")
        if st.button(f"Restore V{entry['version_id']}"):
            revert_version(entry['version_id'])
            st.success(f"Restored to version {entry['version_id']}")

# --- THEMING ---
st.set_page_config(page_title="EUROPA Inventory", layout="wide")
st.markdown("""
<style>
body { background-color: #0B1D51; color: #ffffff; font-family: 'Orbitron', sans-serif; }
.stButton>button { background-color: #1C3FAA; color:#fff; font-weight:bold; border-radius:10px; height:3em; width:100%; }
.stButton>button:hover { background-color:#3B63D3; color:#ffffff; }
.stNumberInput>div>input { background-color: #001f3f; color:#0cf; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# --- PAGE LOGIC ---
page = st.session_state.page
if page == "Inventory":
    display_inventory_page()
elif page == "Category":
    display_category_page()
elif page == "Item":
    display_item_page()
elif page == "History":
    display_history_page()
