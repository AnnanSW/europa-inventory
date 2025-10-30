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
def get_item_color(amount):
    if amount == 0: return "red"
    elif amount <= LOW_STOCK_THRESHOLD: return "orange"
    else: return "green"

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

# --- PAGE NAVIGATION FUNCTIONS ---
def go_to_page(page_name):
    st.session_state.page = page_name

def go_back_to_inventory():
    st.session_state.page = "Inventory"
    st.session_state.open_category = None
    st.session_state.edit_item_page = None
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0

def go_to_category_page(category):
    st.session_state.page = "Category"
    st.session_state.open_category = category

def go_to_item_page(category, item):
    st.session_state.page = "Item"
    st.session_state.edit_item_page = (category, item)
# europa_inventory_part2.py (continuation)

st.set_page_config(page_title="EUROPA Inventory", layout="wide")

# --- PAGE RENDERING FUNCTIONS ---
def render_inventory_page():
    st.title("EUROPA INVENTORY")
    st.subheader("Select a Category to View Items")
    for category in st.session_state.inventory.keys():
        if st.button(category):
            go_to_category_page(category)

def render_category_page():
    category = st.session_state.open_category
    st.header(f"{category}")
    st.button("← Back", on_click=go_back_to_inventory)
    st.write("---")
    items = st.session_state.inventory[category]
    for item, data in items.items():
        color = get_item_color(data["current"])
        st.markdown(f"**{item}**")
        st.progress(data["current"]/data["original"])
        st.markdown(f"Current: {data['current']} | Original: {data['original']}")
        if st.button(f"Edit {item}", key=f"edit_{item}"):
            go_to_item_page(category, item)
        st.write("---")

def render_item_page():
    category, item = st.session_state.edit_item_page
    st.header(f"{item} ({category})")
    st.button("← Back", on_click=lambda: go_to_category_page(category))
    data = st.session_state.inventory[category][item]
    st.markdown(f"Original: {data['original']} | Current: {data['current']}")
    st.progress(data["current"]/data["original"])
    
    # Inputs with mutual exclusion
    col1, col2 = st.columns(2)
    with col1:
        add = st.number_input("Add Units", min_value=0, value=st.session_state.add_units_edit, key="add_units")
        if add > 0:
            st.session_state.remove_units_edit = 0
    with col2:
        remove = st.number_input("Remove Units", min_value=0, value=st.session_state.remove_units_edit, key="remove_units")
        if remove > 0:
            st.session_state.add_units_edit = 0
    
    if st.button("Apply Changes"):
        new_amount = data["current"] + add - remove
        if new_amount > data["original"]:
            st.error(f"Cannot exceed original amount ({data['original']})")
        elif new_amount < 0:
            st.error("Cannot go below zero")
        else:
            if add > 0:
                record_change(category, item, data["current"], new_amount, "add")
            elif remove > 0:
                record_change(category, item, data["current"], new_amount, "remove")
            data["current"] = new_amount
            st.success("Updated successfully")
            st.session_state.add_units_edit = 0
            st.session_state.remove_units_edit = 0

def render_version_history():
    st.title("Version History")
    st.button("← Back", on_click=go_back_to_inventory)
    st.write("---")
    log = st.session_state.change_log
    for entry in reversed(log):
        direction = "+" if entry["action"]=="add" else "-" if entry["action"]=="remove" else ""
        st.markdown(f"**V{entry['version_id']}** | {entry['timestamp']} | {entry['category']} - {entry['item']} | {direction}{abs(entry.get('new_amount',0)-entry.get('old_amount',0))}")

# --- SIDEBAR ---
page_option = st.sidebar.selectbox("Navigation", ["Inventory","Version History"])
if page_option == "Version History":
    st.session_state.page = "VersionHistory"

# --- PAGE ROUTING ---
if st.session_state.page == "Inventory":
    render_inventory_page()
elif st.session_state.page == "Category":
    render_category_page()
elif st.session_state.page == "Item":
    render_item_page()
elif st.session_state.page == "VersionHistory":
    render_version_history()
