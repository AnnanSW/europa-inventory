import streamlit as st
import copy
from datetime import datetime
import pandas as pd
import io

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 10
WARNING_STOCK_THRESHOLD = 20

# --- DYNAMIC STYLING INJECTION ---
def inject_button_styles(category=None, item_name=None, color=None):
    if category and item_name and color:
        css = f"""
        <style>
        [data-testid*="stButton"] > button[key*="item_{category}_{item_name}"] {{
            background-color: #112239 !important;
            color: {color} !important; 
            border: 2px solid {color} !important;
            box-shadow: 0 0 8px {color};
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    elif category:
        color_map = {
            "#FF4136": """ 
                border: 2px solid #FF4136 !important;
                color: #FF4136 !important;
                box-shadow: 0 0 10px #FF4136;
                background-color: #451B1B !important;
            """,
            "#FFB703": """ 
                border: 2px solid #FFB703 !important;
                color: #FFB703 !important;
                box-shadow: 0 0 8px #FFB703;
                background-color: #382A15 !important;
            """
        }
        style = color_map.get(get_category_color(category), '')
        if style:
             css = f"""
            <style>
            [data-testid*="stButton"] > button[key*="catbtn_{category}"] {{
                {style}
            }}
            </style>
            """
             st.markdown(css, unsafe_allow_html=True)

# --- THEME STYLES ---
st.markdown("""
<style>
.stApp {
    background-color: #05101E;
    color: #F0F0F0;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 16px;
}
h1 {
    color: #008CFF !important;
    text-align: center;
    border-bottom: 3px solid #008CFF;
    padding-bottom: 5px; 
    letter-spacing: 8px;
    text-shadow: 0 0 10px rgba(0, 140, 255, 0.7);
    margin-bottom: 0px; 
}
h2, h3 {
    color: #F0F0F0 !important;
    border-left: 5px solid #008CFF;
    padding-left: 10px;
    margin-top: 25px;
    font-weight: 700;
}
div[data-testid="stNumberInput"] label {
    color: #008CFF !important;
}
div[data-testid="stNumberInput"] input {
    color: #F0F0F0; 
    background-color: #05101E; 
    border: 1px solid #008CFF;
    padding: 5px;
    border-radius: 3px;
}
div.stButton > button {
    background-color: #112239;
    color: #F0F0F0 !important;
    border: 1px solid #2A3A54; 
    border-radius: 0px; 
    padding: 10px 20px;
    margin: 30px 5px 5px 0px; 
    transition: background-color 0.2s, border-color 0.2s;
    font-weight: bold;
    cursor: pointer;
}
div.stButton > button:hover {
    background-color: #0A192F; 
    border-color: #008CFF;
}
div[data-testid="stAlert"].stAlert-success {
    background-color: #002244; 
    border-color: #008CFF;
    box-shadow: 0 0 8px #008CFF; 
}
div[data-testid="stAlert"].stAlert-error {
    background-color: #451B1B; 
    border-color: #FF4136;
    box-shadow: 0 0 8px #FF4136;
}
div[data-testid="stAlert"].stAlert-warning {
    background-color: #382A15; 
    border-color: #FFB703; 
}
.stProgress > div > div > div > div {
    background-color: #008CFF;
    box-shadow: 0 0 5px #008CFF;
}
hr {
    border-top: 1px solid #2A3A54;
    margin-top: 15px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

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

ICON_MAP = {
    "Hydratable Meals": "💧",
    "Thermostabilized Meals": "🔥",
    "Natural Form & Irradiated": "📦",
    "Desserts & Beverages (Non-Mix)": "🍹",
    "Condiments & Spreads": "🧂"
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
if "change_applied" not in st.session_state:
    st.session_state.change_applied = False

# barcode mapping stored in session_state as dict: barcode -> (category, item)
if "barcode_mapping" not in st.session_state:
    st.session_state.barcode_mapping = {}  # user will upload or edit

if "last_scanned" not in st.session_state:
    st.session_state.last_scanned = ""

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

# --- NAVIGATION ---
def go_to_inventory():
    st.session_state.page = "Inventory"
    st.session_state.open_category = None
    st.session_state.edit_item_page = None
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0
    st.session_state.change_applied = False

def go_to_category(category):
    st.session_state.page = "Category"
    st.session_state.open_category = category
    st.session_state.change_applied = False

def go_to_edit_item(category, item):
    st.session_state.page = "EditItem"
    st.session_state.edit_item_page = (category, item)
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0
    st.session_state.change_applied = False

# --- BARCODE MAPPING UI ---
def barcode_management_panel():
    st.sidebar.header("Barcode Mapping")
    st.sidebar.write("Upload a CSV file with columns: `barcode,category,item` to map real barcodes to inventory items.")
    uploaded = st.sidebar.file_uploader("Upload barcode CSV", type=["csv"], key="barcode_csv_uploader")
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            # Expect columns: barcode, category, item
            required = {"barcode","category","item"}
            if not required.issubset(set(df.columns.str.lower())):
                st.sidebar.error("CSV must contain columns: barcode,category,item (case-insensitive).")
            else:
                # normalize columns
                df.columns = [c.lower() for c in df.columns]
                count = 0
                for _, row in df.iterrows():
                    code = str(row["barcode"]).strip()
                    cat = str(row["category"]).strip()
                    itm = str(row["item"]).strip()
                    if code and cat and itm:
                        st.session_state.barcode_mapping[code] = (cat, itm)
                        count += 1
                st.sidebar.success(f"Imported {count} barcode mappings.")
        except Exception as e:
            st.sidebar.error(f"Failed to parse CSV: {e}")

    st.sidebar.write("Current mappings: ")
    if st.session_state.barcode_mapping:
        df_map = pd.DataFrame(
            [(k, v[0], v[1]) for k, v in st.session_state.barcode_mapping.items()],
            columns=["barcode","category","item"]
        )
        st.sidebar.dataframe(df_map)
        if st.sidebar.button("Export mapping to CSV"):
            buffer = io.StringIO()
            df_map.to_csv(buffer, index=False)
            st.sidebar.download_button("Download CSV", buffer.getvalue(), file_name="barcode_mapping_export.csv")
    else:
        st.sidebar.info("No barcode mappings loaded. App will fallback to item-name matching.")

    st.sidebar.markdown("---")
    st.sidebar.write("Quick-add mapping (for small edits):")
    c1, c2 = st.sidebar.columns([2,1])
    with c1:
        new_code = st.text_input("Barcode", key="new_code_input")
    with c2:
        if st.button("Add mapping"):
            # We need category and item fields below
            st.sidebar.info("Please select a category and item from the main UI, then click 'Add mapping' again.")
    st.sidebar.caption("Tip: Click an item in the main UI, then add its barcode here and press 'Add mapping' to bind it.")

# --- MAIN INVENTORY PAGE ---
def inventory_page():
    st.markdown("<h1>EUROPA INVENTORY</h1>", unsafe_allow_html=True)

    # display small status about barcode mapping
    if st.session_state.barcode_mapping:
        st.info(f"{len(st.session_state.barcode_mapping)} barcode mappings loaded.")
    else:
        st.info("No barcode mappings loaded — scanning will match item names (case-insensitive).")

    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for i, category in enumerate(st.session_state.inventory.keys()):
        inject_button_styles(category=category)
        button_label = f"{ICON_MAP.get(category, '•')} {category}"
        with cols[i % 3]:
            if st.button(button_label, key=f"catbtn_{category}", help="Click to open category"):
                go_to_category(category)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Version History / Restore"):
        st.session_state.page = "History"

# --- CATEGORY PAGE ---
def category_page():
    category = st.session_state.open_category
    st.markdown(f"<h2>// CATEGORY: {category}</h2>", unsafe_allow_html=True)
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr>", unsafe_allow_html=True)

    items = st.session_state.inventory[category]
    for item_name, data in items.items():
        color = get_item_color(data["current"])
        inject_button_styles(category=category, item_name=item_name, color=color)

        if data["current"] == 0:
            status_emoji = "🚨"
            status_text = "ZERO STOCK"
        elif data["current"] <= LOW_STOCK_THRESHOLD:
            status_emoji = "⚠️"
            status_text = "LOW STOCK (REPLENISH)"
        else:
            status_emoji = "✅"
            status_text = "NOMINAL"

        display_text = f"{status_emoji} **{item_name}** | CURRENT: **{data['current']}** / MAX: {data['original']} | STATUS: {status_text}"

        if st.button(display_text, key=f"item_{category}_{item_name}", help="Click to edit this item"):
            # If user clicked to open this item, optionally allow quick binding to barcode input
            st.session_state.selected_for_mapping = (category, item_name)
            go_to_edit_item(category, item_name)

# --- ITEM EDIT PAGE ---
def edit_item_page():
    category, item = st.session_state.edit_item_page
    data = st.session_state.inventory[category][item]

    st.markdown(f"<h3>// ITEM: {item}</h3>", unsafe_allow_html=True)

    if not st.session_state.change_applied:
        st.button("⬅ Back to Category", on_click=lambda: go_to_category(category))

    st.markdown(f"**Current Units:** {data['current']}  |  **Original Load:** {data['original']}")
    st.progress(data["current"]/data["original"])

    if data['current'] <= LOW_STOCK_THRESHOLD:
        st.warning(f"⚠️ **LOW STOCK WARNING!** Only **{data['current']}** units remaining. Replenishment required.")

    # Show quick-bind UI if the user selected this item from the inventory
    if "selected_for_mapping" in st.session_state and st.session_state.selected_for_mapping == (category, item):
        st.info("This item is selected for quick barcode mapping. Use the sidebar to paste the barcode and press 'Add mapping' there.")
        # Provide a simple input for immediate mapping
        new_code = st.text_input("Enter barcode to bind to this item (quick bind)", key="quick_bind_input")
        if new_code:
            st.session_state.barcode_mapping[str(new_code)] = (category, item)
            st.success(f"Bound barcode {new_code} → {category} > {item}")
            # clear selection
            st.session_state.selected_for_mapping = None
            st.experimental_rerun()

    col1, col2 = st.columns(2)
    with col1:
        add_units = st.number_input(
            "Add Units (Resupply)",
            min_value=0,
            max_value=data["original"]-data["current"],
            value=st.session_state.add_units_edit,
            key="add_units_input",
            disabled=st.session_state.change_applied
        )
        if add_units > 0 and not st.session_state.change_applied:
            st.session_state.remove_units_edit = 0
            st.session_state.add_units_edit = add_units
    with col2:
        remove_units = st.number_input(
            "Remove Units (Consumption)",
            min_value=0,
            max_value=data["current"],
            value=st.session_state.remove_units_edit,
            key="remove_units_input",
            disabled=st.session_state.change_applied
        )
        if remove_units > 0 and not st.session_state.change_applied:
            st.session_state.add_units_edit = 0
            st.session_state.remove_units_edit = remove_units

    if st.session_state.change_applied:
        st.success(f"✅ **UPDATE SUCCESS** | {item} is now at **{data['current']}** units. Data hash accepted.")
        st.button("🚀 Return to Inventory Home", on_click=go_to_inventory)
    elif st.button("Apply Changes"):
        old_amount = data["current"]
        new_amount = old_amount + st.session_state.add_units_edit - st.session_state.remove_units_edit

        if new_amount > data["original"] or new_amount < 0:
            st.error("❌ **ERROR:** Value out of bounds. Cannot exceed original capacity or go below zero.")
        else:
            action = "add" if st.session_state.add_units_edit > 0 else "remove"
            record_change(category, item, old_amount, new_amount, action)
            st.session_state.inventory[category][item]["current"] = new_amount

            st.session_state.change_applied = True

            st.session_state.add_units_edit = 0
            st.session_state.remove_units_edit = 0

            st.rerun()

# --- HISTORY PAGE ---
def history_page():
    st.markdown("<h2>// SYSTEM LOG: VERSION HISTORY</h2>", unsafe_allow_html=True)
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr>", unsafe_allow_html=True)

    if not st.session_state.change_log:
        st.info("No changes have been recorded yet.")
        return

    for entry in reversed(st.session_state.change_log):
        version_id = entry["version_id"]
        timestamp = entry["timestamp"]
        category = entry["category"]
        item = entry["item"]
        action = entry["action"]
        old_amount = entry["old_amount"]
        new_amount = entry["new_amount"]

        if action.startswith("RESTORATION"):
            st.markdown(f"<p style='color:#FF4136;'>**V{version_id}** | {timestamp} | SYSTEM RESTORE: {action}</p>", unsafe_allow_html=True)
        else:
            change_symbol = "+" if action == "add" else "-"
            st.markdown(f"**V{version_id}** | {timestamp} | {category} > {item} | {change_symbol}{abs(new_amount - old_amount)} ({old_amount}→{new_amount})", unsafe_allow_html=True)
            if st.button(f"Restore to V{version_id}", key=f"restore_{version_id}"):
                revert_version(version_id)
                st.success(f"Inventory restored to state before V{version_id}")

# --- BARCODE ROUTING (invisible input) ---
def barcode_router():
    # Small UI note (collapsed) to allow manual tests
    with st.expander("🔎 Barcode Scanner (click to test / view)"):
        st.write("Scan a barcode with your scanner. If mappings are loaded, they will be used. Otherwise, item-name matching will be attempted.")
        st.write("You can also manually type a barcode and press Enter to test routing.")

    # Invisible input that captures scanner keystrokes
    barcode = st.text_input(
        "", 
        key="barcode_input_hidden",
        label_visibility="collapsed",
        placeholder="Scan barcode here..."
    )

    if barcode:
        code = str(barcode).strip()
        # First try explicit mapping
        if code in st.session_state.barcode_mapping:
            category, item = st.session_state.barcode_mapping[code]
            # Validate that category/item exist
            if category in st.session_state.inventory and item in st.session_state.inventory[category]:
                st.session_state.page = "EditItem"
                st.session_state.edit_item_page = (category, item)
                st.session_state.add_units_edit = 0
                st.session_state.remove_units_edit = 0
                st.session_state.change_applied = False
                st.session_state.last_scanned = code
                st.session_state.barcode_input_hidden = ""
                st.experimental_rerun()
            else:
                st.warning(f"Mapping found for barcode {code}, but category/item not in current inventory: {category} > {item}")
                st.session_state.barcode_input_hidden = ""
                st.experimental_rerun()
        else:
            # Fallback: try to match by item name (case-insensitive)
            matched = False
            low = code.lower()
            for cat, items in st.session_state.inventory.items():
                for itm in items.keys():
                    if itm.lower() == low:
                        st.session_state.page = "EditItem"
                        st.session_state.edit_item_page = (cat, itm)
                        st.session_state.add_units_edit = 0
                        st.session_state.remove_units_edit = 0
                        st.session_state.change_applied = False
                        st.session_state.last_scanned = code
                        st.session_state.barcode_input_hidden = ""
                        st.experimental_rerun()
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                st.warning(f"Scanned barcode '{code}' not recognized.")
                st.session_state.barcode_input_hidden = ""
                st.experimental_rerun()

# --- MAIN APP SWITCH ---
def main():
    st.set_page_config(page_title="EUROPA Inventory (Barcode-enabled)", layout="centered")
    barcode_management_panel()

    # show last scanned for debugging
    if st.session_state.last_scanned:
        st.sidebar.markdown(f"**Last scanned:** `{st.session_state.last_scanned}`")

    # run barcode router in the background (renders hidden input)
    barcode_router()

    if st.session_state.page == "Inventory":
        inventory_page()
    elif st.session_state.page == "Category":
        category_page()
    elif st.session_state.page == "EditItem":
        # Protect against invalid edit_item_page tuple
        if st.session_state.edit_item_page and len(st.session_state.edit_item_page) == 2:
            edit_item_page()
        else:
            st.error("Invalid edit item target — returning to inventory.")
            go_to_inventory()
            inventory_page()
    elif st.session_state.page == "History":
        history_page()

if __name__ == "__main__":
    main()
'''

# write file
file_path = "/mnt/data/EUROPA_Inventory_v2_with_barcodes.py"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(app_code)

file_path