# europa_inventory_app_part1.py
import streamlit as st
import copy
import time
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

# --- HELPER FUNCTIONS ---
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

def get_item_class(amount):
    if amount == 0: return "color:red;font-weight:bold;"
    elif amount <= LOW_STOCK_THRESHOLD: return "color:orange;font-weight:bold;"
    else: return "color:#66fcf1;"
# europa_inventory_app_part2.py
import streamlit as st

# --- PAGE NAVIGATION ---
if "page" not in st.session_state:
    st.session_state.page = "MAIN_MENU"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None

# --- NAVIGATION FUNCTIONS ---
def go_to_main_menu():
    st.session_state.page = "MAIN_MENU"
    st.session_state.selected_category = None
    st.session_state.selected_item = None

def go_to_category(category):
    st.session_state.selected_category = category
    st.session_state.page = "CATEGORY_PAGE"

def go_to_item(item):
    st.session_state.selected_item = item
    st.session_state.page = "ITEM_PAGE"

# --- MAIN MENU ---
def render_main_menu():
    st.markdown("<h1 style='color:#66fcf1;'>EUROPA INVENTORY</h1>", unsafe_allow_html=True)
    st.markdown("### Select a category to view:")
    for cat in st.session_state.inventory.keys():
        if st.button(cat):
            go_to_category(cat)
            st.experimental_rerun()
    if st.button("Version History"):
        st.session_state.page = "VERSION_HISTORY"
        st.experimental_rerun()

# --- CATEGORY PAGE ---
def render_category_page():
    cat = st.session_state.selected_category
    st.markdown(f"<h2 style='color:#45a29e;'>{cat}</h2>", unsafe_allow_html=True)
    st.button("Back to Main Menu", on_click=go_to_main_menu)
    items = st.session_state.inventory[cat]
    for item_name, data in items.items():
        current = data["current"]
        original = data["original"]
        color = "orange" if current <= LOW_STOCK_THRESHOLD else "#66fcf1"
        color = "red" if current==0 else color
        st.markdown(f"<div style='padding:5px; border:1px solid #0b0c10; margin-bottom:5px;'>"
                    f"<span style='color:{color}; font-weight:bold;'>{item_name}</span> "
                    f"({current}/{original}) units"
                    f"</div>", unsafe_allow_html=True)
        if st.button(f"Edit {item_name}"):
            go_to_item(item_name)
            st.experimental_rerun()

# --- ITEM PAGE ---
def render_item_page():
    cat = st.session_state.selected_category
    item = st.session_state.selected_item
    data = st.session_state.inventory[cat][item]
    st.markdown(f"<h2 style='color:#45a29e;'>{item}</h2>", unsafe_allow_html=True)
    st.button("Back to Main Menu", on_click=go_to_main_menu)
    current = data["current"]
    original = data["original"]
    st.markdown(f"Current: {current} / Original: {original}")
    add_val = st.number_input("Add Units", min_value=0, value=0)
    remove_val = st.number_input("Remove Units", min_value=0, value=0)
    
    # Ensure only one input is used
    if add_val>0:
        remove_val=0
    if remove_val>0:
        add_val=0

    if st.button("Apply Change"):
        new_amount = current + add_val - remove_val
        if new_amount > original:
            st.error("Cannot exceed original stock!")
        elif new_amount <0:
            st.error("Cannot go below 0!")
        else:
            action = "add" if add_val>0 else "remove"
            record_change(cat, item, current, new_amount, action)
            st.session_state.inventory[cat][item]["current"] = new_amount
            st.success(f"Updated {item} to {new_amount} units")
            st.experimental_rerun()
# europa_inventory_app_part3.py
import streamlit as st

# --- VERSION HISTORY PAGE ---
def render_version_history():
    st.markdown("<h1 style='color:#66fcf1;'>Version History</h1>", unsafe_allow_html=True)
    st.button("Back to Main Menu", on_click=go_to_main_menu)
    if not st.session_state.change_log:
        st.info("No changes have been recorded yet.")
        return
    for entry in reversed(st.session_state.change_log):
        version = entry["version_id"]
        timestamp = entry["timestamp"]
        category = entry["category"]
        item = entry["item"]
        action = entry["action"]
        old = entry["old_amount"]
        new = entry["new_amount"]
        st.markdown(f"<div style='padding:5px; border:1px solid #0b0c10; margin-bottom:5px;'>"
                    f"<strong>V{version}</strong> | {timestamp} | {category} - {item} | "
                    f"{action} | {old} → {new}</div>", unsafe_allow_html=True)

# --- PAGE ROUTER ---
if st.session_state.page == "MAIN_MENU":
    render_main_menu()
elif st.session_state.page == "CATEGORY_PAGE":
    render_category_page()
elif st.session_state.page == "ITEM_PAGE":
    render_item_page()
elif st.session_state.page == "VERSION_HISTORY":
    render_version_history()
else:
    st.error("Unknown page, returning to main menu")
    go_to_main_menu()
    st.experimental_rerun()
