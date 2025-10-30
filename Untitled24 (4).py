# europa_inventory_part1.py
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

# --- HELPER FUNCTIONS ---
def is_fuzzy_match(item_name_lower, search_term_lower):
    n = len(search_term_lower)
    m = len(item_name_lower)
    if n == 0: return True
    for i in range(m - n + 1):
        substring = item_name_lower[i:i+n]
        mismatches = sum(substring[j]!=search_term_lower[j] for j in range(n))
        if mismatches <= FUZZY_TOLERANCE:
            return True
    return False

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

def get_item_color(amount):
    if amount == 0: return "red"
    elif amount <= LOW_STOCK_THRESHOLD: return "orange"
    else: return "green"
# europa_inventory_part2.py
import streamlit as st

# --- PAGE NAVIGATION ---
def go_to_page(page_name):
    st.session_state.page = page_name

def go_back_to_inventory():
    st.session_state.page = "Inventory"
    st.session_state.edit_item_page = None
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0

# --- EDIT ITEM PAGE ---
def edit_item_page(category, item):
    st.header(f"EUROPA: Edit Item - {item}")
    data = st.session_state.inventory[category][item]
    current = data["current"]
    original = data["original"]

    st.write(f"Original Capacity: {original} units")
    st.write(f"Current Amount: {current} units")
    st.progress(current / original if original > 0 else 0)

    col1, col2 = st.columns(2)
    with col1:
        add_units = st.number_input("Add Units", min_value=0, value=st.session_state.add_units_edit, step=1)
    with col2:
        remove_units = st.number_input("Remove Units", min_value=0, value=st.session_state.remove_units_edit, step=1)

    # Disable simultaneous input
    if add_units > 0:
        remove_units = 0
    if remove_units > 0:
        add_units = 0

    apply_changes = st.button("Apply Changes")
    if apply_changes:
        if add_units > 0:
            new_amount = current + add_units
            if new_amount > original:
                st.error(f"Cannot exceed original capacity ({original}).")
            else:
                st.session_state.inventory[category][item]["current"] = new_amount
                record_change(category, item, current, new_amount, "add")
                st.success(f"Added {add_units} units. New amount: {new_amount}")
        elif remove_units > 0:
            new_amount = current - remove_units
            if new_amount < 0:
                st.error("Cannot remove more than current units.")
            else:
                st.session_state.inventory[category][item]["current"] = new_amount
                record_change(category, item, current, new_amount, "remove")
                if new_amount <= LOW_STOCK_THRESHOLD:
                    st.warning(f"Low Stock! Only {new_amount} units remaining.")
                if new_amount == 0:
                    st.error(f"{item} is now depleted!")
        st.experimental_rerun()

    st.button("Back", on_click=go_back_to_inventory)

# --- VERSION HISTORY PAGE ---
def version_history_page():
    st.header("EUROPA Inventory Version History")
    for entry in reversed(st.session_state.change_log):
        st.write(f"V{entry['version_id']} | {entry['timestamp']} | {entry['category']} -> {entry['item']} | {entry['action']} | {entry['old_amount']} -> {entry['new_amount']}")
    st.button("Back", on_click=go_back_to_inventory)

# --- MAIN INVENTORY PAGE ---
def main_inventory_page():
    st.header("EUROPA Inventory")
    for category, items in st.session_state.inventory.items():
        if st.button(category, key=category):
            st.session_state.open_category = category

    if st.session_state.open_category:
        cat = st.session_state.open_category
        st.subheader(f"{cat} Items")
        for item, data in st.session_state.inventory[cat].items():
            color = get_item_color(data["current"])
            item_button = st.button(f"{item} - {data['current']}/{data['original']} units", key=f"{cat}_{item}")
            if item_button:
                st.session_state.edit_item_page = (cat, item)
                st.session_state.page = "Edit Item"

# --- PAGE ROUTER ---
if st.session_state.page == "Inventory":
    main_inventory_page()
elif st.session_state.page == "Edit Item" and st.session_state.edit_item_page:
    category, item = st.session_state.edit_item_page
    edit_item_page(category, item)
elif st.session_state.page == "Version History":
    version_history_page()

# Sidebar
st.sidebar.title("EUROPA Sidebar")
if st.sidebar.button("Go to Version History"):
    st.session_state.page = "Version History"
if st.sidebar.button("Back to Inventory"):
    st.session_state.page = "Inventory"
