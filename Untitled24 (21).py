# europa_inventory_nasa_part1.py
import streamlit as st
import copy
from datetime import datetime

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 10
WARNING_STOCK_THRESHOLD = 20 # New threshold for yellow warning

# --- CUSTOM NASA THEME STYLES (Refined for Polished Look) ---
st.markdown("""
<style>
/* 1. Global Background, Text, and Font */
.stApp {
    background-color: #0A192F; /* Deep Navy/Space Blue */
    color: #CCD6F6; /* Light Blue-Gray for main text */
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 16px;
}

/* 2. Main Title/Header Styling */
h1 {
    color: #64FFDA !important; /* Neon Cyan for accent */
    text-align: center;
    border-bottom: 3px solid #64FFDA;
    padding-bottom: 10px;
    letter-spacing: 5px;
    text-shadow: 0 0 8px rgba(100, 255, 218, 0.7); /* Subtle glow */
    margin-bottom: 20px;
}

/* 3. Subheadings (h2, h3) */
h2, h3 {
    color: #FFEA00 !important; /* Yellow for prominence */
    border-left: 5px solid #FFEA00;
    padding-left: 10px;
    margin-top: 25px;
    font-weight: 600;
}

/* 4. Streamlit Input Overrides (for professional look) */
div[data-testid="stTextInput"], div[data-testid="stNumberInput"] {
    background-color: #172A45;
    border: 1px solid #172A45;
    border-radius: 4px;
    padding: 10px;
}
div[data-testid="stNumberInput"] input {
    color: #CCD6F6; /* Input text color */
    background-color: #0A192F; /* Dark background for input box itself */
    border: 1px solid #303C54;
    padding: 5px;
    border-radius: 3px;
}

/* 5. Generic Button Base Styling (The cool foundation) */
div.stButton > button {
    background-color: #172A45; 
    color: #64FFDA !important;
    border: 1px solid #64FFDA;
    border-radius: 5px;
    padding: 10px 20px;
    margin: 5px 5px 5px 0px;
    transition: background-color 0.2s, border-color 0.2s;
    font-weight: bold;
    cursor: pointer;
}
div.stButton > button:hover {
    background-color: #0F375F; 
    border-color: #CCD6F6;
}

/* --- ITEM-SPECIFIC COLOR ALERTS (OVERRIDING GENERIC BUTTONS) --- */
/* A. Category Buttons on Inventory Page (Uses st.session_state) */
/* B. Item Buttons on Category Page (Uses CSS logic based on key/state) */

/* Item Button: Danger (Red - At Zero) */
div[data-testid^="stBlock"] > div > div > div > button[data-testid^="item_"][style*="border-color: #FF4136"] {
    background-color: #451B1B !important;
    color: #FF4136 !important; 
    border: 2px solid #FF4136 !important;
    box-shadow: 0 0 10px #FF4136;
}
/* Item Button: Warning (Yellow - Low Stock) */
div[data-testid^="stBlock"] > div > div > div > button[data-testid^="item_"][style*="border-color: #FFD700"] {
    background-color: #383315 !important;
    color: #FFD700 !important; 
    border: 2px solid #FFD700 !important;
    box-shadow: 0 0 10px #FFD700;
}

/* 6. Alerts */
div[data-testid="stAlert"].stAlert-success {background-color: #1A342B; border-color: #2ECC40;}
div[data-testid="stAlert"].stAlert-error {background-color: #451B1B; border-color: #FF4136;}
div[data-testid="stAlert"].stAlert-info {background-color: #172A45; border-color: #7FDBFF;}

/* 7. Progress Bar */
.stProgress > div > div > div > div {
    background-color: #64FFDA; 
    box-shadow: 0 0 5px #64FFDA;
}

/* 8. Horizontal Rules */
hr {
    border-top: 2px solid #172A45; /* Subtle separation */
    margin-top: 15px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)
# --- END OF CUSTOM NASA THEME STYLES ---

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
            "Fruit Cocktail (Pouch)": {"current": 5, "original": 75} # Low stock example
        },
        "Natural Form & Irradiated": {
            "Pecans (Irradiated)": {"current": 60, "original": 60},
            "Shortbread Cookies": {"current": 90, "original": 90},
            "Crackers": {"current": 150, "original": 150},
            "M&Ms (Candy)": {"current": 180, "original": 180},
            "Tortillas (Packages)": {"current": 200, "original": 200},
            "Dried Apricots": {"current": 80, "original": 80},
            "Dry Roasted Peanuts": {"current": 0, "original": 70}, # Zero stock example
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
if "change_applied" not in st.session_state:
    st.session_state.change_applied = False

# --- HELPER FUNCTIONS ---
def get_item_color(amount):
    """Returns a specific hex code based on stock level for item buttons."""
    if amount == 0: return "#FF4136"  # Red (Danger)
    if amount <= LOW_STOCK_THRESHOLD: return "#FFD700"  # Yellow (Warning)
    return "#64FFDA"  # Cyan (Safe/Normal)

def get_category_style(category):
    """Checks if any item in a category is low and returns a CSS style."""
    for item in st.session_state.inventory[category].values():
        if item["current"] == 0:
            return f'style="border: 2px solid #FF4136; color: #FF4136; box-shadow: 0 0 10px #FF4136;"'
        if item["current"] <= LOW_STOCK_THRESHOLD:
            return f'style="border: 2px solid #FFD700; color: #FFD700; box-shadow: 0 0 10px #FFD700;"'
        if item["current"] <= WARNING_STOCK_THRESHOLD:
            return f'style="border: 1px solid #FFD700; color: #FFD700;"'
    return '' # Default style (handled by main CSS)

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
# --- PAGE NAVIGATION ---
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

# --- MAIN INVENTORY PAGE ---
def inventory_page():
    st.markdown("<h1>EUROPA INVENTORY</h1>", unsafe_allow_html=True)
    
    # Check for categories with low stock and display a general warning
    low_stock_categories = [
        cat for cat in st.session_state.inventory 
        if any(item["current"] <= LOW_STOCK_THRESHOLD for item in st.session_state.inventory[cat].values())
    ]
    if low_stock_categories:
        st.warning(f"⚠️ **CRITICAL ALERT:** Low stock detected in: {', '.join(low_stock_categories)}")

    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, category in enumerate(st.session_state.inventory.keys()):
        with cols[i % 3]: # Distribute buttons across columns
            # Apply dynamic styling to the button
            style_str = get_category_style(category)
            if st.markdown(
                f'<button {style_str} key="catbtn_{category}">{category}</button>',
                unsafe_allow_html=True
            ):
                go_to_category(category)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Version History / Restore"):
        st.session_state.page = "History"

# --- CATEGORY PAGE ---
def category_page():
    category = st.session_state.open_category
    st.markdown(f"<h2>{category}</h2>", unsafe_allow_html=True)
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    items = st.session_state.inventory[category]
    
    for item_name, data in items.items():
        color = get_item_color(data["current"])
        
        # Apply the color to the button's border/color using inline style
        # The CSS above targets this specific inline style for special effects
        style_str = f'style="border-color: {color}; color: {color};"'
        
        if data["current"] == 0:
            status_emoji = "🚨"
            status_text = "ZERO STOCK"
        elif data["current"] <= LOW_STOCK_THRESHOLD:
            status_emoji = "⚠️"
            status_text = "LOW STOCK"
        elif data["current"] <= WARNING_STOCK_THRESHOLD:
            status_emoji = "🟡"
            status_text = "CHECK STOCK"
        else:
            status_emoji = "🟢"
            status_text = "OK"

        display_text = f"{status_emoji} **{item_name}** | Current: {data['current']} | Status: {status_text}"
        
        # Use HTML markdown to create the button with dynamic styling
        if st.markdown(
            f'<button key="item_{category}_{item_name}" {style_str}>{display_text}</button>',
            unsafe_allow_html=True
        ):
            go_to_edit_item(category, item_name)

# --- ITEM EDIT PAGE ---
def edit_item_page():
    category, item = st.session_state.edit_item_page
    data = st.session_state.inventory[category][item]
    
    st.markdown(f"<h3>{item}</h3>", unsafe_allow_html=True) 
    
    if not st.session_state.change_applied:
        st.button("⬅ Back to Category", on_click=lambda: go_to_category(category))
    
    st.markdown(f"**Current Units:** {data['current']}  |  **Original Load:** {data['original']}")
    st.progress(data["current"]/data["original"])
    
    if data['current'] <= LOW_STOCK_THRESHOLD:
        st.warning(f"⚠️ **LOW STOCK WARNING!** Only **{data['current']}** units remaining. Replenishment required.")
        
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
        st.success(f"✅ **Update Complete!** {item} is now at **{data['current']}** units.")
        st.button("🚀 Return to Inventory Home", on_click=go_to_inventory)
    elif st.button("Apply Changes"):
        old_amount = data["current"]
        new_amount = old_amount + st.session_state.add_units_edit - st.session_state.remove_units_edit
        
        if new_amount > data["original"] or new_amount < 0:
            st.error("❌ **Error:** Cannot exceed original capacity or go below zero.")
        else:
            action = "add" if st.session_state.add_units_edit > 0 else "remove"
            record_change(category, item, old_amount, new_amount, action)
            st.session_state.inventory[category][item]["current"] = new_amount
            
            st.session_state.change_applied = True 
            
            st.session_state.add_units_edit = 0
            st.session_state.remove_units_edit = 0
            
            st.rerun()

# --- VERSION HISTORY PAGE ---
def history_page():
    st.markdown("<h2>VERSION HISTORY</h2>", unsafe_allow_html=True)
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
            st.markdown(f"**V{version_id}** | {timestamp} | SYSTEM RESTORE: {action}")
        else:
            change_symbol = "+" if action == "add" else "-"
            st.markdown(f"**V{version_id}** | {timestamp} | {category} > {item} | {change_symbol}{abs(new_amount - old_amount)} ({old_amount}→{new_amount})")
            if st.button(f"Restore to V{version_id}", key=f"restore_{version_id}"):
                revert_version(version_id)
                st.success(f"Inventory restored to state before V{version_id}")

# --- MAIN APP SWITCH ---
if "page" not in st.session_state:
    st.session_state.page = "Inventory"
    st.session_state.open_category = None
    st.session_state.edit_item_page = None
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0
    st.session_state.change_applied = False

# Page selector
if st.session_state.page == "Inventory":
    inventory_page()
elif st.session_state.page == "Category":
    category_page()
elif st.session_state.page == "EditItem":
    edit_item_page()
elif st.session_state.page == "History":
    history_page()