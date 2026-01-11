import streamlit as st
import copy
from datetime import datetime
import pandas as pd
import altair as alt
import numpy as np
from collections import defaultdict

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 30
WARNING_STOCK_THRESHOLD = 60
CREW_SIZE = 7
MISSION_DAYS = 1035
REDUNDANCY_FACTOR = 1.30
DAYS_IN_MISSION = int(np.ceil(MISSION_DAYS * REDUNDANCY_FACTOR))

# --- BARCODE MAP ---
BARCODE_MAP = {
    "9313010189018": ("Hydratable Meals", "Beef Stroganoff (Pouch)"),
    "9313010189025": ("Hydratable Meals", "Scrambled Eggs (Powder)"),
    "9313010189032": ("Hydratable Meals", "Cream of Mushroom Soup (Mix)"),
    "9313010189049": ("Hydratable Meals", "Macaroni and Cheese (Dry)"),
    "9313010189056": ("Hydratable Meals", "Asparagus Tips (Dried)"),
    "9313010189063": ("Hydratable Meals", "Grape Drink (Mix)"),
    "9313010189070": ("Hydratable Meals", "Coffee (Mix)"),
    "9313010189087": ("Hydratable Meals", "Chili (Dried)"),
    "9313010189094": ("Hydratable Meals", "Chicken and Rice (Dried)"),
    "9313010189100": ("Hydratable Meals", "Oatmeal with Applesauce (Dry)"),
    "9313010189117": ("Thermostabilized Meals", "Lemon Pepper Tuna (Pouch)"),
    "9313010189124": ("Thermostabilized Meals", "Spicy Green Beans (Pouch)"),
    "9313010189131": ("Thermostabilized Meals", "Pork Chop (Pouch)"),
    "9313010189148": ("Thermostabilized Meals", "Chicken Tacos (Pouch)"),
    "9313010189155": ("Thermostabilized Meals", "Turkey (Pouch)"),
    "9313010189162": ("Thermostabilized Meals", "Brownie (Pouch)"),
    "9313010189179": ("Thermostabilized Meals", "Raspberry Yogurt (Pouch)"),
    "9313010189186": ("Thermostabilized Meals", "Ham Steak (Pouch)"),
    "9313010189193": ("Thermostabilized Meals", "Sausage Patty (Pouch)"),
    "9313010189209": ("Thermostabilized Meals", "Fruit Cocktail (Pouch)"),
    "9313010189216": ("Natural Form & Irradiated", "Pecans (Irradiated)"),
    "9313010189223": ("Natural Form & Irradiated", "Shortbread Cookies"),
    "9313010189230": ("Natural Form & Irradiated", "Crackers"),
    "9313010189247": ("Natural Form & Irradiated", "M&Ms (Candy)"),
    "9313010189254": ("Natural Form & Irradiated", "Tortillas (Packages)"),
    "9313010189261": ("Natural Form & Irradiated", "Dried Apricots"),
    "9313010189278": ("Natural Form & Irradiated", "Dry Roasted Peanuts"),
    "9313010189285": ("Natural Form & Irradiated", "Beef Jerky (Strips)"),
    "9313010189292": ("Natural Form & Irradiated", "Fruit Bar"),
    "9313010189308": ("Natural Form & Irradiated", "Cheese Spread (Tube)"),
    "9313010189315": ("Desserts & Beverages (Non-Mix)", "Space Ice Cream (Freeze-dried)"),
    "9313010189322": ("Desserts & Beverages (Non-Mix)", "Banana Pudding (Pouch)"),
    "9313010189339": ("Desserts & Beverages (Non-Mix)", "Chocolate Pudding (Pouch)"),
    "9313010189346": ("Desserts & Beverages (Non-Mix)", "Apple Sauce (Pouch)"),
    "9313010189353": ("Desserts & Beverages (Non-Mix)", "Orange Juice (Carton)"),
    "9313010189360": ("Desserts & Beverages (Non-Mix)", "Tea Bags (Box)"),
    "9313010189377": ("Desserts & Beverages (Non-Mix)", "Hot Cocoa (Mix)"),
    "9313010189384": ("Desserts & Beverages (Non-Mix)", "Cranberry Sauce (Pouch)"),
    "9313010189391": ("Desserts & Beverages (Non-Mix)", "Strawberry Shake (Mix)"),
    "9313010189407": ("Desserts & Beverages (Non-Mix)", "Dried Peaches"),
    "9313010189414": ("Condiments & Spreads", "Ketchup (Packet)"),
    "9313010189421": ("Condiments & Spreads", "Mustard (Packet)"),
    "9313010189438": ("Condiments & Spreads", "Salt (Packet)"),
    "9313010189445": ("Condiments & Spreads", "Pepper (Packet)"),
    "9313010189452": ("Condiments & Spreads", "Jelly (Packet)"),
    "9313010189469": ("Condiments & Spreads", "Honey (Tube)"),
    "9313010189476": ("Condiments & Spreads", "Hot Sauce (Bottle)"),
    "9313010189483": ("Condiments & Spreads", "Mayonnaise (Packet)"),
    "9313010189490": ("Condiments & Spreads", "Sugar (Packet)"),
    "9313010189506": ("Condiments & Spreads", "Taco Sauce (Packet)")
}

# --- ICONS ---
ICON_MAP = {
    "Hydratable Meals": "💧",
    "Thermostabilized Meals": "🔥",
    "Natural Form & Irradiated": "📦",
    "Desserts & Beverages (Non-Mix)": "🍹",
    "Condiments & Spreads": "🧂"
}

# --- INITIAL INVENTORY ---
def get_initial_inventory():
    MEALS_PER_PERSON_PER_DAY = 3
    total_meals_required = int(np.ceil(CREW_SIZE * MEALS_PER_PERSON_PER_DAY * DAYS_IN_MISSION * REDUNDANCY_FACTOR))
    MEAL_WEIGHTS = {
        "Hydratable Meals": 1.0,
        "Thermostabilized Meals": 1.0,
        "Natural Form & Irradiated": 0.5,
        "Desserts & Beverages (Non-Mix)": 0.25
    }

    stock_hm = [1.2,0.9,1.1,1.0,0.8,1.5,1.8,0.9,1.3,1.0]
    stock_tm = [1.5,1.0,0.9,1.2,0.8,1.4,1.6,0.7,0.6,1.3]
    stock_nf = [0.8,1.1,2.0,2.5,3.0,1.0,0.9,0.6,1.2,0.7]
    stock_db = [0.7,0.8,0.9,1.0,1.5,1.8,1.3,0.6,1.1,0.5]

    category_items = {
        "Hydratable Meals": ([v[1] for v in BARCODE_MAP.values() if v[0]=="Hydratable Meals"], stock_hm),
        "Thermostabilized Meals": ([v[1] for v in BARCODE_MAP.values() if v[0]=="Thermostabilized Meals"], stock_tm),
        "Natural Form & Irradiated": ([v[1] for v in BARCODE_MAP.values() if v[0]=="Natural Form & Irradiated"], stock_nf),
        "Desserts & Beverages (Non-Mix)": ([v[1] for v in BARCODE_MAP.values() if v[0]=="Desserts & Beverages (Non-Mix)"], stock_db)
    }

    total_weighted_units = sum(len(items)*MEAL_WEIGHTS[cat] for cat,(items,_) in category_items.items())
    base_units_per_weight = total_meals_required / total_weighted_units

    inventory_data = {}
    for category, (items, multipliers) in category_items.items():
        meal_weight = MEAL_WEIGHTS[category]
        calculated_units = [base_units_per_weight*meal_weight*mult for mult in multipliers]
        uniform_units = int(np.ceil(np.mean(calculated_units)))
        inventory_data[category] = {name: {"current": uniform_units, "original": uniform_units} for name in items}

    # Condiments
    total_entrees = sum(item["original"] for cat in ["Hydratable Meals","Thermostabilized Meals"] for item in inventory_data[cat].values())
    condiment_items = [v[1] for v in BARCODE_MAP.values() if v[0]=="Condiments & Spreads"]
    per_condiment = int(np.ceil(total_entrees / len(condiment_items)))
    inventory_data["Condiments & Spreads"] = {name: {"current": per_condiment, "original": per_condiment} for name in condiment_items}

    return inventory_data

# --- SESSION STATE INIT ---
if "inventory" not in st.session_state:
    st.session_state.inventory = get_initial_inventory()
if "change_log" not in st.session_state:
    st.session_state.change_log = []
    initial_inventory_snapshot = copy.deepcopy(st.session_state.inventory)
    st.session_state.change_log.append({
        "version_id": 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": "SYSTEM",
        "item": "INITIAL_LOAD",
        "action": "initial",
        "old_amount": "N/A",
        "new_amount": "N/A",
        "state_before_change": initial_inventory_snapshot,
        "mission_day": 1,
        "used_predicted": True
    })
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
if "change_applied" not in st.session_state:
    st.session_state.change_applied = False
if "barcode_error" not in st.session_state:
    st.session_state.barcode_error = None

# --- HELPER FUNCTIONS ---
def get_item_color(amount):
    if amount == 0: return "#FF4136"
    if amount <= LOW_STOCK_THRESHOLD: return "#FFB703"
    return "#F0F0F0"

def get_category_color(category):
    color = "#F0F0F0"
    for item in st.session_state.inventory[category].values():
        if item["current"] == 0:
            return "#FF4136"
        if item["current"] <= LOW_STOCK_THRESHOLD:
            color = "#FFB703"
    return color

def record_change(category, item, old_amount, new_amount, action, used_predicted=False, predicted_units_per_day=None):
    current_mission_day = st.session_state.change_log[-1].get("mission_day",1) if st.session_state.change_log else 1
    if predicted_units_per_day is None:
        predicted_units_per_day = old_amount - new_amount if action in ("add","remove") else 0
    st.session_state.change_log.append({
        "version_id": len(st.session_state.change_log)+1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "item": item,
        "action": action,
        "old_amount": old_amount,
        "new_amount": new_amount,
        "state_before_change": copy.deepcopy(st.session_state.inventory),
        "mission_day": current_mission_day,
        "used_predicted": used_predicted,
        "predicted_units": predicted_units_per_day
    })

def revert_version(version_id):
    try:
        restored_state = copy.deepcopy(next(entry for entry in st.session_state.change_log if entry["version_id"]==version_id)["state_before_change"])
        st.session_state.inventory = restored_state
        st.session_state.change_log.append({
            "version_id": len(st.session_state.change_log)+1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": "SYSTEM",
            "item": "RESTORE",
            "action": f"RESTORATION_TO_V{version_id}",
            "old_amount": "N/A",
            "new_amount": "N/A",
            "state_before_change": copy.deepcopy(st.session_state.inventory),
            "mission_day": st.session_state.change_log[-1].get("mission_day",1)
        })
    except StopIteration:
        st.error("Invalid version ID")

# --- PAGE NAVIGATION ---
def go_to_inventory():
    st.session_state.page="Inventory"
    st.session_state.open_category=None
    st.session_state.edit_item_page=None
    st.session_state.add_units_edit=0
    st.session_state.remove_units_edit=0
    st.session_state.change_applied=False
    st.session_state.barcode_error=None

def go_to_dashboard():
    st.session_state.page="Dashboard"

def go_to_category(category):
    st.session_state.page="Category"
    st.session_state.open_category=category
    st.session_state.change_applied=False
    st.session_state.barcode_error=None

def go_to_edit_item(category,item):
    st.session_state.page="EditItem"
    st.session_state.edit_item_page=(category,item)
    st.session_state.add_units_edit=0
    st.session_state.remove_units_edit=0
    st.session_state.change_applied=False
    st.session_state.barcode_error=None

def process_barcode_scan(barcode):
    if barcode in BARCODE_MAP:
        category,item_name = BARCODE_MAP[barcode]
        go_to_edit_item(category,item_name)
        st.rerun()
    else:
        st.session_state.barcode_error=f"ERROR: Barcode '{barcode}' not found in manifest."
        st.rerun()
# --- DASHBOARD PAGE ---
def render_dashboard():
    st.title("Mission Inventory Dashboard 🚀")

    # Summary Metrics
    total_items = sum(item["current"] for cat in st.session_state.inventory for item in st.session_state.inventory[cat].values())
    zero_stock_items = sum(1 for cat in st.session_state.inventory for item in st.session_state.inventory[cat].values() if item["current"]==0)
    low_stock_items = sum(1 for cat in st.session_state.inventory for item in st.session_state.inventory[cat].values() if 0<item["current"]<=LOW_STOCK_THRESHOLD)

    st.metric("Total Units Remaining", total_items)
    st.metric("Items Out of Stock", zero_stock_items)
    st.metric("Low Stock Items", low_stock_items)

    # Category Overview
    st.subheader("Category Status")
    for category in st.session_state.inventory:
        color = get_category_color(category)
        units_remaining = sum(item["current"] for item in st.session_state.inventory[category].values())
        st.button(f"{ICON_MAP.get(category,'📦')} {category} — {units_remaining} units", key=f"cat_{category}", on_click=go_to_category, args=(category,), help=f"Click to view {category} items")

# --- INVENTORY PAGE ---
def render_inventory():
    st.title("Mission Inventory 📦")
    st.write("Click a category to view details.")

    for category in st.session_state.inventory:
        color = get_category_color(category)
        units_remaining = sum(item["current"] for item in st.session_state.inventory[category].values())
        if st.button(f"{ICON_MAP.get(category,'📦')} {category} — {units_remaining} units", key=f"inv_{category}", on_click=go_to_category, args=(category,)):
            pass

# --- CATEGORY PAGE ---
def render_category_page():
    category = st.session_state.open_category
    if category is None:
        st.error("No category selected.")
        return

    st.title(f"{ICON_MAP.get(category,'📦')} {category} Items")
    st.button("Back to Inventory", on_click=go_to_inventory)

    inventory_table = []
    for item_name, item_data in st.session_state.inventory[category].items():
        color = get_item_color(item_data["current"])
        inventory_table.append({
            "Item": item_name,
            "Current Units": item_data["current"],
            "Color": color
        })

    for entry in inventory_table:
        item_name = entry["Item"]
        units = entry["Current Units"]
        color = entry["Color"]
        st.markdown(f"<div style='background-color:{color};padding:6px;margin:2px;border-radius:4px;'>"
                    f"{item_name} — {units} units "
                    f"<button onclick='window.location.href=\"#\"'>{'Edit'}</button></div>", unsafe_allow_html=True)
        if st.button(f"Edit {item_name}", key=f"edit_{item_name}", on_click=go_to_edit_item, args=(category,item_name)):
            pass

# --- EDIT ITEM PAGE ---
def render_edit_item_page():
    category,item_name = st.session_state.edit_item_page
    if category is None or item_name is None:
        st.error("No item selected for editing.")
        return

    st.title(f"Edit Item — {item_name}")
    st.button("Back to Category", on_click=go_to_category, args=(category,))

    current_units = st.session_state.inventory[category][item_name]["current"]
    st.write(f"Current Units: {current_units}")

    st.session_state.add_units_edit = st.number_input("Add Units", min_value=0, value=st.session_state.add_units_edit, step=1)
    st.session_state.remove_units_edit = st.number_input("Remove Units", min_value=0, value=st.session_state.remove_units_edit, step=1)

    col1,col2 = st.columns(2)
    with col1:
        if st.button("Apply Add"):
            if st.session_state.add_units_edit > 0:
                old = st.session_state.inventory[category][item_name]["current"]
                st.session_state.inventory[category][item_name]["current"] += st.session_state.add_units_edit
                record_change(category,item_name,old,st.session_state.inventory[category][item_name]["current"],action="add")
                st.session_state.change_applied = True
                st.session_state.add_units_edit = 0
                st.experimental_rerun()
    with col2:
        if st.button("Apply Remove"):
            if st.session_state.remove_units_edit > 0:
                old = st.session_state.inventory[category][item_name]["current"]
                new_units = max(0, old - st.session_state.remove_units_edit)
                st.session_state.inventory[category][item_name]["current"] = new_units
                record_change(category,item_name,old,new_units,action="remove")
                st.session_state.change_applied = True
                st.session_state.remove_units_edit = 0
                st.experimental_rerun()

    # Hardcoded predicted usage display
    predicted_usage_per_day = 3  # Hardcoded example
    st.write(f"Predicted usage per day (hardcoded): {predicted_usage_per_day} units")

# --- CHANGE LOG PAGE ---
def render_change_log():
    st.title("Change Log 📝")
    if not st.session_state.change_log:
        st.write("No changes recorded yet.")
        return

    df_log = pd.DataFrame(st.session_state.change_log)
    st.dataframe(df_log[["version_id","timestamp","category","item","action","old_amount","new_amount","mission_day","used_predicted"]])

    st.subheader("Revert to Previous Version")
    version_to_revert = st.number_input("Version ID to revert", min_value=1, max_value=len(st.session_state.change_log), value=1, step=1)
    if st.button("Revert"):
        revert_version(version_to_revert)
        st.success(f"Restored to version {version_to_revert}")
        st.experimental_rerun()
# --- BARCODE SCANNER ---
def render_barcode_scanner():
    st.title("📡 Barcode Scanner")
    st.write("Scan a product barcode to jump to its item page.")

    with st.form("barcode_form", clear_on_submit=True):
        barcode_input = st.text_input("Enter or scan barcode:")
        submitted = st.form_submit_button("Submit")

        if submitted and barcode_input:
            barcode_input = barcode_input.strip()
            if barcode_input in BARCODE_MAP:
                category, item_name = BARCODE_MAP[barcode_input]
                go_to_edit_item(category,item_name)
                st.experimental_rerun()
            else:
                st.error(f"Barcode '{barcode_input}' not found.")

# --- MAIN APP NAVIGATION ---
def main_app():
    # Ensure session state initialized
    if "page" not in st.session_state:
        st.session_state.page = "Inventory"
    if "open_category" not in st.session_state:
        st.session_state.open_category = None
    if "edit_item_page" not in st.session_state:
        st.session_state.edit_item_page = (None,None)
    if "add_units_edit" not in st.session_state:
        st.session_state.add_units_edit = 0
    if "remove_units_edit" not in st.session_state:
        st.session_state.remove_units_edit = 0
    if "change_applied" not in st.session_state:
        st.session_state.change_applied = False
    if "barcode_error" not in st.session_state:
        st.session_state.barcode_error = None
    if "inventory" not in st.session_state:
        st.session_state.inventory = get_initial_inventory()
    if "change_log" not in st.session_state:
        st.session_state.change_log = []

    # Navigation Menu
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to page", ["Inventory","Dashboard","Barcode Scanner","Change Log"])

    if page == "Inventory":
        st.session_state.page = "Inventory"
    elif page == "Dashboard":
        st.session_state.page = "Dashboard"
    elif page == "Barcode Scanner":
        st.session_state.page = "Barcode Scanner"
    elif page == "Change Log":
        st.session_state.page = "Change Log"

    # Render current page
    if st.session_state.page == "Inventory":
        render_inventory()
    elif st.session_state.page == "Dashboard":
        render_dashboard()
    elif st.session_state.page == "Category":
        render_category_page()
    elif st.session_state.page == "EditItem":
        render_edit_item_page()
    elif st.session_state.page == "Change Log":
        render_change_log()
    elif st.session_state.page == "Barcode Scanner":
        render_barcode_scanner()

# --- RUN APP ---
if __name__ == "__main__":
    main_app()

