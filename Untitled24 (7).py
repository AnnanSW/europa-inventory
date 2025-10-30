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

# --- SESSION STATE ---
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

# --- STYLING FOR NASA THEME ---
st.markdown(
    """
    <style>
    body {
        background-color: #0b0c10;
        color: #c5c6c7;
        font-family: 'Orbitron', sans-serif;
    }
    .stButton>button {
        background-color: #1f2833;
        color: #66fcf1;
        border-radius: 5px;
        height: 3em;
        width: 100%;
        font-weight: bold;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a29e;
        color: #0b0c10;
    }
    .stProgress>div>div>div {
        background-color: #66fcf1 !important;
    }
    .stNumberInput>div>input {
        background-color: #1f2833;
        color: #c5c6c7;
        border: 1px solid #45a29e;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True
)

# --- HELPER FUNCTIONS ---
def get_item_color(amount):
    if amount == 0: return "#ff4d4d"
    elif amount <= LOW_STOCK_THRESHOLD: return "#ffd11a"
    else: return "#66fcf1"

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
# europa_inventory_nasa_part2.py (continuation)

# --- PAGE NAVIGATION ---
def go_to_inventory():
    st.session_state.page = "Inventory"
    st.session_state.open_category = None
    st.session_state.edit_item_page = None
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0

def go_to_category(category):
    st.session_state.page = "Category"
    st.session_state.open_category = category

def go_to_item(category, item):
    st.session_state.page = "Item"
    st.session_state.edit_item_page = (category, item)
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0

def go_to_history():
    st.session_state.page = "History"

# --- DISPLAY FUNCTIONS ---
def display_inventory_page():
    st.title("EUROPA INVENTORY CONTROL PANEL")
    st.subheader("Select a category to view items")
    for category in st.session_state.inventory:
        if st.button(category):
            go_to_category(category)
            st.experimental_rerun()
    st.markdown("---")
    if st.button("View Version History"):
        go_to_history()
        st.experimental_rerun()

def display_category_page():
    category = st.session_state.open_category
    st.title(f"EUROPA: {category.upper()}")
    st.button("Back", on_click=go_to_inventory)
    st.markdown("---")
    items = st.session_state.inventory[category]
    for item_name, data in items.items():
        color = get_item_color(data["current"])
        st.markdown(f"**{item_name}**  —  Current: {data['current']} / Original: {data['original']}")
        st.progress(data["current"] / data["original"])
        if st.button(f"Edit {item_name}", key=item_name):
            go_to_item(category, item_name)
            st.experimental_rerun()

def display_item_page():
    category, item = st.session_state.edit_item_page
    data = st.session_state.inventory[category][item]
    st.title(f"{item.upper()}")
    st.button("Back", on_click=lambda: go_to_category(category))
    st.markdown(f"Original: {data['original']}  |  Current: {data['current']}")
    st.progress(data["current"] / data["original"])
    st.markdown("---")
    # Add / Remove inputs
    add_col, remove_col, apply_col = st.columns([1,1,1])
    with add_col:
        add_val = st.number_input("Add Units", min_value=0, value=st.session_state.add_units_edit, key="add_input")
        if add_val > 0:
            st.session_state.remove_units_edit = 0
    with remove_col:
        remove_val = st.number_input("Remove Units", min_value=0, value=st.session_state.remove_units_edit, key="remove_input")
        if remove_val > 0:
            st.session_state.add_units_edit = 0
    with apply_col:
        if st.button("Apply Changes"):
            new_amount = data["current"] + add_val - remove_val
            if new_amount > data["original"]:
                st.error("Cannot exceed original capacity!")
            elif new_amount < 0:
                st.error("Cannot go below zero!")
            else:
                old = data["current"]
                data["current"] = new_amount
                if add_val > 0:
                    record_change(category, item, old, new_amount, "add")
                elif remove_val > 0:
                    record_change(category, item, old, new_amount, "remove")
                st.session_state.add_units_edit = 0
                st.session_state.remove_units_edit = 0
                st.experimental_rerun()

def display_history_page():
    st.title("EUROPA: VERSION HISTORY")
    st.button("Back", on_click=go_to_inventory)
    st.markdown("---")
    log = st.session_state.change_log
    if not log:
        st.info("No changes recorded yet.")
        return
    for entry in reversed(log):
        st.markdown(f"**V{entry['version_id']}** | {entry['timestamp']} | {entry['category']} | {entry['item']} | {entry['action']} | {entry['old_amount']} → {entry['new_amount']}")
        if "RESTORATION" not in entry["action"]:
            if st.button(f"Restore to V{entry['version_id']}", key=f"restore{entry['version_id']}"):
                revert_version(entry['version_id'])
                st.experimental_rerun()

# --- MAIN PAGE LOGIC ---
if st.session_state.page == "Inventory":
    display_inventory_page()
elif st.session_state.page == "Category":
    display_category_page()
elif st.session_state.page == "Item":
    display_item_page()
elif st.session_state.page == "History":
    display_history_page()
