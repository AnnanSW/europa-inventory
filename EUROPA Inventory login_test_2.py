import streamlit as st
import copy
from datetime import datetime
import pandas as pd
import altair as alt
import numpy as np
import hashlib

# --- MISSION PARAMETERS ---
CREW_SIZE = 7
MISSION_DAYS = 1035
REDUNDANCY_FACTOR = 1.30

# --- MISSION START DATE ---
MISSION_START_DATE = datetime.strptime("2026-01-01", "%Y-%m-%d") #YYYY-MM-DD

# --- LOW STOCK ---
LOW_STOCK_THRESHOLD = 100  # Adjusted for larger mission

# --- DAYS IN MISSION including redundancy ---
DAYS_IN_MISSION = int(np.ceil(MISSION_DAYS * REDUNDANCY_FACTOR))

# --- BARCODE MAP (Existing mapping) ---
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

    "9313010189315": ("Desserts & Beverages", "Space Ice Cream (Freeze-dried)"),
    "9313010189322": ("Desserts & Beverages", "Banana Pudding (Pouch)"),
    "9313010189339": ("Desserts & Beverages", "Chocolate Pudding (Pouch)"),
    "9313010189346": ("Desserts & Beverages", "Apple Sauce (Pouch)"),
    "9313010189353": ("Desserts & Beverages", "Orange Juice (Carton)"),
    "9313010189360": ("Desserts & Beverages", "Tea Bags (Box)"),
    "9313010189377": ("Desserts & Beverages", "Hot Cocoa (Mix)"),
    "9313010189384": ("Desserts & Beverages", "Cranberry Sauce (Pouch)"),
    "9313010189391": ("Desserts & Beverages", "Strawberry Shake (Mix)"),
    "9313010189407": ("Desserts & Beverages", "Dried Peaches"),

    "9313010189414": ("Condiments & Spreads", "Ketchup (Packet)"),
    "9313010189421": ("Condiments & Spreads", "Mustard (Packet)"),
    "9313010189438": ("Condiments & Spreads", "Salt (Packet)"),
    "9313010189445": ("Condiments & Spreads", "Pepper (Packet)"),
    "9313010189452": ("Condiments & Spreads", "Jelly (Packet)"),
    "9313010189469": ("Condiments & Spreads", "Honey (Tube)"),
    "9313010189476": ("Condiments & Spreads", "Hot Sauce (Bottle)"),
    "9313010189483": ("Condiments & Spreads", "Mayonnaise (Packet)"),
    "9313010189490": ("Condiments & Spreads", "Sugar (Packet)"),
    "9313010189506": ("Condiments & Spreads", "Taco Sauce (Packet)"),
}

# --- ICONS MAPPING ---
ICON_MAP = {
    "Hydratable Meals": "💧",
    "Thermostabilized Meals": "🔥",
    "Natural Form & Irradiated": "📦",
    "Desserts & Beverages": "🍹",
    "Condiments & Spreads": "🧂"
}

# --- LOGIN / CREW CREDENTIALS ---
# NASA-like usernames + PINs
CREW_CREDENTIALS = {
    "astro_johnson": "1234",
    "astro_lee": "2345",
    "astro_singh": "3456",
    "astro_martinez": "4567",
    "astro_nguyen": "5678",
    "astro_petrov": "6789",
    "astro_kim": "7890"
}

# --- SESSION STATE INIT ---
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "change_log" not in st.session_state:
    st.session_state.change_log = []
if "page" not in st.session_state:
    st.session_state.page = "Login"
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
def get_current_mission_day(reference_datetime=None):
    if reference_datetime is None:
        reference_datetime = datetime.now()
    delta_days = (reference_datetime - MISSION_START_DATE).days + 1
    return max(1, min(MISSION_DAYS, delta_days))

def get_initial_inventory():
    inventory_data = {}
    total_meals = CREW_SIZE * 3 * MISSION_DAYS * REDUNDANCY_FACTOR
    total_nf = CREW_SIZE * 1.5 * MISSION_DAYS * REDUNDANCY_FACTOR
    total_db = CREW_SIZE * 10 * MISSION_DAYS * REDUNDANCY_FACTOR

    # Hydratable Meals
    hm_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Hydratable Meals"]
    hm_units = int(np.ceil((total_meals/2)/len(hm_items)))
    inventory_data["Hydratable Meals"] = {name: {"current": hm_units, "original": hm_units} for name in hm_items}

    # Thermostabilized Meals
    tm_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Thermostabilized Meals"]
    tm_units = int(np.ceil((total_meals/2)/len(tm_items)))
    inventory_data["Thermostabilized Meals"] = {name: {"current": tm_units, "original": tm_units} for name in tm_items}

    # Natural Form & Irradiated
    nf_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Natural Form & Irradiated"]
    nf_units = int(np.ceil(total_nf / len(nf_items)))
    inventory_data["Natural Form & Irradiated"] = {name: {"current": nf_units, "original": nf_units} for name in nf_items}

    # Desserts & Beverages
    db_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Desserts & Beverages"]
    db_units = int(np.ceil(total_db / len(db_items)))
    inventory_data["Desserts & Beverages"] = {name: {"current": db_units, "original": db_units} for name in db_items}

    # Condiments & Spreads
    total_food_units = sum(item["original"] for category in inventory_data.values() for item in category.values())
    condiment_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Condiments & Spreads"]
    per_condiment = int(np.ceil(total_food_units / len(condiment_items)))
    inventory_data["Condiments & Spreads"] = {name: {"current": per_condiment, "original": per_condiment} for name in condiment_items}

    return inventory_data

if not st.session_state.inventory:
    st.session_state.inventory = get_initial_inventory()
    st.session_state.change_log.append({
        "version_id": 1,
        "timestamp": MISSION_START_DATE.strftime("%Y-%m-%d %H:%M:%S"),
        "category": "SYSTEM",
        "item": "INITIAL_LOAD",
        "action": "INITIALIZATION",
        "old_amount": "N/A",
        "new_amount": "N/A",
        "state_after_change": copy.deepcopy(st.session_state.inventory)
    })
# -------------------
# --- LOGIN PAGE ---
# -------------------
def login_page():
    st.title("🚀 Mission Inventory System - Login")
    st.write("Enter your NASA-style credentials to continue:")

    username = st.text_input("Username")
    pin = st.text_input("PIN", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in CREW_CREDENTIALS and CREW_CREDENTIALS[username] == pin:
            st.session_state.logged_in_user = username
            st.session_state.page = "Dashboard"
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid username or PIN. Please try again.")


# ------------------------
# --- DASHBOARD PAGE ---
# ------------------------
def dashboard_page():
    st.title("🛰️ Mission Dashboard")
    st.write(f"Crew Member: **{st.session_state.logged_in_user}**")
    current_day = get_current_mission_day()
    st.write(f"Mission Day: **{current_day} / {MISSION_DAYS}**")
    st.progress(current_day / MISSION_DAYS)

    st.markdown("---")
    st.subheader("Navigation")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Inventory"):
            st.session_state.page = "Inventory"
    with col2:
        if st.button("Edit Items"):
            st.session_state.page = "EditItem"
    with col3:
        if st.button("Consumption History"):
            st.session_state.page = "History"

    st.markdown("---")
    st.subheader("Inventory Overview")
    overview_data = []
    for cat, items in st.session_state.inventory.items():
        total_cat = sum(v["current"] for v in items.values())
        original_cat = sum(v["original"] for v in items.values())
        overview_data.append({"Category": cat, "Current Units": total_cat, "Original Units": original_cat})

    df_overview = pd.DataFrame(overview_data)
    st.table(df_overview)

    chart = alt.Chart(df_overview).mark_bar().encode(
        x=alt.X("Category", sort=None),
        y="Current Units",
        tooltip=["Category", "Current Units", "Original Units"]
    )
    st.altair_chart(chart, use_container_width=True)


# --------------------------
# --- INVENTORY PAGE ---
# --------------------------
def inventory_page():
    st.title("📦 Inventory Management")
    st.write("Scan a barcode or select a category to view items:")

    barcode_input = st.text_input("Scan or enter barcode")
    scan_button = st.button("Scan Barcode")

    if scan_button and barcode_input:
        if barcode_input in BARCODE_MAP:
            cat, name = BARCODE_MAP[barcode_input]
            st.success(f"Item found: {ICON_MAP[cat]} **{name}** in **{cat}**")
            st.session_state.open_category = cat
        else:
            st.session_state.barcode_error = barcode_input
            st.error(f"Barcode {barcode_input} not recognized.")

    st.markdown("---")
    st.subheader("Categories")
    for cat in st.session_state.inventory.keys():
        if st.button(f"{ICON_MAP[cat]} {cat}"):
            st.session_state.open_category = cat

    if st.session_state.open_category:
        cat_name = st.session_state.open_category
        st.markdown(f"### {ICON_MAP[cat_name]} {cat_name}")
        items = st.session_state.inventory[cat_name]
        for item_name, values in items.items():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(item_name)
            with col2:
                st.write(f"{values['current']} units")
            with col3:
                edit_button = st.button(f"Edit {item_name}", key=f"edit_{cat_name}_{item_name}")
                if edit_button:
                    st.session_state.edit_item_page = (cat_name, item_name)
                    st.session_state.page = "EditItem"


# --------------------------
# --- EDIT ITEM PAGE ---
# --------------------------
def edit_item_page():
    if not st.session_state.edit_item_page:
        st.info("Select an item from the Inventory page to edit.")
        return

    cat_name, item_name = st.session_state.edit_item_page
    st.title(f"✏️ Edit Item: {item_name} ({cat_name})")
    item_data = st.session_state.inventory[cat_name][item_name]

    st.write(f"Current Units: {item_data['current']}")
    add_units = st.number_input("Add Units", min_value=0, value=0, step=1)
    remove_units = st.number_input("Remove Units", min_value=0, value=0, step=1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply Changes"):
            old_value = item_data["current"]
            item_data["current"] = max(0, old_value + add_units - remove_units)
            st.session_state.change_applied = True
            st.session_state.change_log.append({
                "version_id": len(st.session_state.change_log) + 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "category": cat_name,
                "item": item_name,
                "action": f"ADD {add_units} / REMOVE {remove_units}",
                "old_amount": old_value,
                "new_amount": item_data["current"],
                "state_after_change": copy.deepcopy(st.session_state.inventory)
            })
            st.success(f"Updated {item_name}: {old_value} → {item_data['current']} units")
    with col2:
        if st.button("Cancel"):
            st.session_state.page = "Inventory"
            st.session_state.edit_item_page = None
# -----------------------------
# --- CONSUMPTION HISTORY PAGE ---
# -----------------------------
def history_page():
    st.title("📊 Consumption History")
    if not st.session_state.change_log:
        st.info("No consumption or edits recorded yet.")
        return

    df_log = pd.DataFrame(st.session_state.change_log)
    st.dataframe(df_log[["version_id", "timestamp", "category", "item", "action", "old_amount", "new_amount"]])

    st.markdown("---")
    st.subheader("Restore Previous Version")
    version_to_restore = st.number_input("Enter Version ID to Restore", min_value=1, max_value=len(st.session_state.change_log), step=1)
    if st.button("Restore Version"):
        selected_version = next((v for v in st.session_state.change_log if v["version_id"] == version_to_restore), None)
        if selected_version:
            st.session_state.inventory = copy.deepcopy(selected_version["state_after_change"])
            st.success(f"Inventory restored to version {version_to_restore}")
        else:
            st.error(f"Version {version_to_restore} not found.")


# -----------------------------
# --- LOW STOCK ALERTS ---
# -----------------------------
def low_stock_alerts():
    st.subheader("⚠️ Low Stock Alerts")
    low_stock_items = []
    for cat, items in st.session_state.inventory.items():
        for item_name, data in items.items():
            if data["current"] <= max(1, int(data["original"] * 0.1)):
                low_stock_items.append(f"{item_name} ({cat}) - {data['current']} units left")
    if low_stock_items:
        for alert in low_stock_items:
            st.warning(alert)
    else:
        st.success("All items are above low-stock threshold.")


# -----------------------------
# --- MAIN APP FUNCTION ---
# -----------------------------
def main_app():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "Login"
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    if "inventory" not in st.session_state:
        st.session_state.inventory = copy.deepcopy(INVENTORY)
    if "edit_item_page" not in st.session_state:
        st.session_state.edit_item_page = None
    if "open_category" not in st.session_state:
        st.session_state.open_category = None
    if "change_log" not in st.session_state:
        st.session_state.change_log = []

    if st.session_state.page == "Login":
        login_page()
    elif st.session_state.page == "Dashboard":
        dashboard_page()
        low_stock_alerts()
    elif st.session_state.page == "Inventory":
        inventory_page()
    elif st.session_state.page == "EditItem":
        edit_item_page()
    elif st.session_state.page == "History":
        history_page()
    else:
        st.error("Unknown page. Resetting to Login.")
        st.session_state.page = "Login"


# -----------------------------
# --- RUN APP ---
# -----------------------------
if __name__ == "__main__":
    main_app()