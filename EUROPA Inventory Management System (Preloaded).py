import streamlit as st
import copy
from datetime import datetime
import pandas as pd
import altair as alt
import numpy as np

# --- MISSION PARAMETERS ---
CREW_SIZE = 7
MISSION_DAYS = 1035
REDUNDANCY_FACTOR = 1.30

# --- MISSION START DATE ---
MISSION_START_DATE = datetime.strptime("2026-01-01", "%Y-%m-%d") #YYYY-MM-DD

# --- HELPER FUNCTIONS ---
def get_current_mission_day(reference_datetime=None):
    """
    Returns the mission day (1-based) counting from MISSION_START_DATE.
    If reference_datetime is provided, computes the mission day for that timestamp.
    Otherwise, uses 'now'.
    """
    if reference_datetime is None:
        reference_datetime = datetime.now()
    delta_days = (reference_datetime - MISSION_START_DATE).days + 1
    return max(1, min(MISSION_DAYS, delta_days))

DAYS_IN_MISSION = int(np.ceil(MISSION_DAYS * REDUNDANCY_FACTOR))

# --- LOW STOCK ---
LOW_STOCK_THRESHOLD = 100

# --- BARCODE MAPPING ---
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


# --- Interface Styling ---
def inject_button_styles(category=None, item_name=None, color=None):
    """Injects CSS to style specific buttons based on a key fragment."""
    if category and item_name and color:
        # Style for individual Item Buttons on Category Page
        css = f"""
        <style>
        /* Target the specific item button */
        [data-testid*="stButton"] > button[key*="item_{category}_{item_name}"] {{
            background-color: #112239 !important; /* Darker blue background */
            color: {color} !important; 
            border: 2px solid {color} !important;
            box-shadow: 0 0 8px {color};
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    elif category:
        # Style for Category Buttons on Inventory Page
        color_map = {
            "#FF4136": """ /* Critical Red */
                border: 2px solid #FF4136 !important;
                color: #FF4136 !important;
                box-shadow: 0 0 10px #FF4136;
                background-color: #451B1B !important;
            """,
            "#FFB703": """ /* Low Stock Amber/Orange/Yellow ALERT */
                border: 2px solid #FFB703 !important;
                color: #FFB703 !important;
                box-shadow: 0 0 8px #FFB703;
                background-color: #382A15 !important;
            """
        }
        # Style for the Inventory Page buttons
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

# --- THEME STYLES) ---
st.markdown("""
<style>
/* 1. Global Background, Text, and Font */
.stApp {
    background-color: #05101E; /* Deeper Navy/Space Blue */
    color: #F0F0F0; /* Slightly off-white for main text */
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 16px;
}

/* 2. Main Title/Header Styling */
h1 {
    color: #008CFF !important; /* Darker Electric Blue Accent */
    text-align: center;
    border-bottom: 3px solid #008CFF;
    /* ADJUSTMENT 1: Decreased padding to pull line closer to text */
    padding-bottom: 5px; 
    letter-spacing: 8px;
    text-shadow: 0 0 10px rgba(0, 140, 255, 0.7); /* Subtle Glow */
    margin-bottom: 0px; 
}

/* 3. Subheadings (h2, h3) */
h2, h3 {
    color: #F0F0F0 !important;
    border-left: 5px solid #008CFF;
    padding-left: 10px;
    margin-top: 25px;
    font-weight: 700;
}

/* 4. Streamlit Input Overrides */
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

/* New: Styling for Barcode Scanner Input - Make it blend but be prominent */
/* The key is the 'SCAN BARCODE' label and the border */
div[data-testid="stForm"] label {
    color: #008CFF !important;
    font-weight: bold;
    font-size: 18px;
    letter-spacing: 2px;
}
div[data-testid="stForm"] input {
    color: #A9D0F5; /* Light blue text for input */
    background-color: #0A192F; /* Very dark background for input field */
    border: 2px solid #008CFF; /* Bright blue border to highlight scanning area */
    box-shadow: 0 0 10px #008CFF;
    font-size: 20px;
    text-align: center;
}
/* Hide the 'Submit' button since the scanner hits 'Enter' */
div[data-testid="stForm"] button[type="submit"] {
    display: none !important;
}


/* 5. Generic Button Base Styling (Default/Return buttons) */
div.stButton > button {
    background-color: #112239; /* Darker Blue-Gray for button body */
    color: #F0F0F0 !important;
    border: 1px solid #2A3A54; 
    border-radius: 0px; 
    padding: 10px 20px;
    /* ADJUSTMENT 2: Increased top margin to create clear separation from the title line */
    margin: 30px 5px 5px 0px; 
    transition: background-color 0.2s, border-color 0.2s;
    font-weight: bold;
    cursor: pointer;
}
div.stButton > button:hover {
    background-color: #0A192F; 
    border-color: #008CFF; /* Blue hover */
}

/* 6. Alerts and Metrics*/
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

/* 7. Progress Bar (used on Edit page) */
.stProgress > div > div > div > div {
    background-color: #008CFF; /* Electric Blue bar color */
    box-shadow: 0 0 5px #008CFF;
}

/* 8. Horizontal Rules */
hr {
    border-top: 1px solid #2A3A54; /* Subtler divider */
    margin-top: 15px;
    margin-bottom: 15px;
}

/* 9. Metrics (New Style for Dashboard) */
div[data-testid="stMetric"] {
    background-color: #0A192F;
    padding: 15px;
    border-radius: 5px;
    border: 1px solid #008CFF;
    box-shadow: 0 0 5px rgba(0, 140, 255, 0.5);
    text-align: center;
}

/* 9a. Metric Label/Title */
div[data-testid="stMetric"] label {
    color: #A9D0F5 !important;
    font-size: 0.9em;
    text-transform: uppercase;
    font-weight: bold;
}

/* 9b. Metric Value */
div[data-testid="stMetricValue"] {
    color: #F0F0F0 !important;
    font-size: 2em;
    font-weight: bold;
}

/* 9c. Metric Delta (used for low/zero stock emphasis) */
div[data-testid="stMetricDelta"] {
    color: #FF4136 !important; /* Critical color for delta */
    font-weight: bold;
}


/* 10. Altair Chart Styling (Background/Axis) */
/* Altair uses Vega-Lite which can be hard to style via CSS, 
    but this helps ensure the container matches the dark theme */
.stDataFrame, .stPlotlyChart, .stAltairChart {
    background-color: #05101E; 
    border: 1px solid #008CFF;
    padding: 10px;
}


</style>
""", unsafe_allow_html=True)
# --- END OF STYLES ---

def get_initial_inventory():
    """
    Initialize inventory so that each item reflects predicted consumption for entire mission
    including redundancy.
    """
    inventory_data = {}

    # Predicted consumption totals for the crew
    total_meals = CREW_SIZE * 3 * MISSION_DAYS * REDUNDANCY_FACTOR  # Hydratable + Thermostabilized combined
    total_nf = CREW_SIZE * 1.5 * MISSION_DAYS * REDUNDANCY_FACTOR
    total_db = CREW_SIZE * 10 * MISSION_DAYS * REDUNDANCY_FACTOR

    # --- 1. Hydratable Meals ---
    hm_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Hydratable Meals"]
    hm_units_per_item = int(np.ceil((total_meals / 2) / len(hm_items)))  # divide by 2 for HM vs TM
    inventory_data["Hydratable Meals"] = {
        name: {"current": hm_units_per_item, "original": hm_units_per_item} for name in hm_items
    }

    # --- 2. Thermostabilized Meals ---
    tm_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Thermostabilized Meals"]
    tm_units_per_item = int(np.ceil((total_meals / 2) / len(tm_items)))  # divide by 2 for HM vs TM
    inventory_data["Thermostabilized Meals"] = {
        name: {"current": tm_units_per_item, "original": tm_units_per_item} for name in tm_items
    }

    # --- 3. Natural Form & Irradiated ---
    nf_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Natural Form & Irradiated"]
    nf_units_per_item = int(np.ceil(total_nf / len(nf_items)))
    inventory_data["Natural Form & Irradiated"] = {
        name: {"current": nf_units_per_item, "original": nf_units_per_item} for name in nf_items
    }

    # --- 4. Desserts & Beverages ---
    db_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Desserts & Beverages"]
    db_units_per_item = int(np.ceil(total_db / len(db_items)))
    inventory_data["Desserts & Beverages"] = {
        name: {"current": db_units_per_item, "original": db_units_per_item} for name in db_items
    }

    # --- 5. Condiments & Spreads ---
    # Roughly 1 per entrée/snack/dessert: base on Hydratable + Thermostabilized + NF + DB
    total_food_units = (
        sum(item["original"] for item in inventory_data["Hydratable Meals"].values()) +
        sum(item["original"] for item in inventory_data["Thermostabilized Meals"].values()) +
        sum(item["original"] for item in inventory_data["Natural Form & Irradiated"].values()) +
        sum(item["original"] for item in inventory_data["Desserts & Beverages"].values())
    )
    condiment_items = [v[1] for v in BARCODE_MAP.values() if v[0] == "Condiments & Spreads"]
    per_condiment = int(np.ceil(total_food_units / len(condiment_items)))

    inventory_data["Condiments & Spreads"] = {
        name: {"current": per_condiment, "original": per_condiment} for name in condiment_items
    }

    return inventory_data
    
def preload_realistic_changes(initial_inventory):
    """
    Generates realistic inventory changes only up to current mission day.
    Consumption is category-weighted: more meals consumed daily than condiments.
    """
    change_log = []
    version_id = 2  # 1 is reserved for INITIAL_LOAD
    current_state = copy.deepcopy(initial_inventory)

    category_daily_use = {
        "Hydratable Meals": CREW_SIZE * 3,
        "Thermostabilized Meals": CREW_SIZE * 3,
        "Natural Form & Irradiated": int(CREW_SIZE * 1.5),
        "Desserts & Beverages": CREW_SIZE * 10,
        "Condiments & Spreads": CREW_SIZE * 5
    }

    # Current mission day
    current_mission_day = get_current_mission_day()

    for day_offset in range(current_mission_day):
        for category, daily_total in category_daily_use.items():
            items = list(current_state[category].keys())
            for _ in range(random.randint(1, min(5, len(items)))):
                item = random.choice(items)
                old_amount = current_state[category][item]["current"]

                # Random consumption proportional to daily_total / items
                max_remove = max(1, daily_total // len(items))
                remove_units = random.randint(0, min(max_remove, old_amount))
                new_amount = old_amount - remove_units
                action = "remove" if remove_units > 0 else "none"

                if action != "none":
                    # Random timestamp in this day
                    ts = MISSION_START_DATE + timedelta(
                        days=day_offset,
                        hours=random.randint(6, 22),  # awake hours
                        minutes=random.randint(0,59),
                        seconds=random.randint(0,59)
                    )

                    current_state[category][item]["current"] = new_amount

                    change_log.append({
                        "version_id": version_id,
                        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "category": category,
                        "item": item,
                        "action": action,
                        "old_amount": old_amount,
                        "new_amount": new_amount,
                        "state_after_change": copy.deepcopy(current_state)
                    })
                    version_id += 1

    return change_log


# --- ICONS MAPPING ---
ICON_MAP = {
    "Hydratable Meals": "💧",
    "Thermostabilized Meals": "🔥",
    "Natural Form & Irradiated": "📦",
    "Desserts & Beverages": "🍹",
    "Condiments & Spreads": "🧂"
}

# --- SESSION STATE INIT ---
if "inventory" not in st.session_state:
    st.session_state.inventory = get_initial_inventory()
if "change_log" not in st.session_state:
    initial_inventory = get_initial_inventory()

    # INITIAL LOAD
    initial_entry = {
        "version_id": 1,
        "timestamp": MISSION_START_DATE.strftime("%Y-%m-%d %H:%M:%S"),
        "category": "SYSTEM",
        "item": "INITIAL_LOAD",
        "action": "INITIALIZATION",
        "old_amount": "N/A",
        "new_amount": "N/A",
        "state_after_change": copy.deepcopy(initial_inventory)
    }

    # PRELOAD REALISTIC PAST CHANGES
    preloaded_changes = preload_realistic_changes(initial_inventory)

    # MERGE
    st.session_state.change_log = [initial_entry] + preloaded_changes

    # Set current inventory to last known state
    st.session_state.inventory = (
        copy.deepcopy(preloaded_changes[-1]["state_after_change"])
        if preloaded_changes else initial_inventory
    )

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


# --- HELPER FUNCTIONS 2 ---
def get_item_color(amount):
    """Returns a specific hex code based on stock level for styling."""
    if amount == 0: return "#FF4136"  # Red (Danger)
    if amount <= LOW_STOCK_THRESHOLD: return "#FFB703"  # Amber/Orange (Low Stock Warning)
    return "#F0F0F0"  # White (Safe/Normal)

def get_category_color(category):
    """
    Returns the color code for the most critical item in a category.
    This determines the button color on the home page.
    """
    color = "#F0F0F0" # Default to White
    for item in st.session_state.inventory[category].values():
        if item["current"] == 0:
            return "#FF4136" # (Critical Alert)
        if item["current"] <= LOW_STOCK_THRESHOLD:
            color = "#FFB703" # (Low Stock Alert)
    return color

def record_change(category, item, old_amount, new_amount, action):
    """
    Records a change and stores the inventory **after** the change
    for proper restoration.
    """
    # Apply the change to the inventory
    st.session_state.inventory[category][item]["current"] = new_amount
    if action == "add" and new_amount > st.session_state.inventory[category][item]["original"]:
        st.session_state.inventory[category][item]["original"] = new_amount

    # Store the snapshot after applying the change 
    st.session_state.change_log.append({
        "version_id": len(st.session_state.change_log) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "item": item,
        "action": action,
        "old_amount": old_amount,
        "new_amount": new_amount,
        "state_after_change": copy.deepcopy(st.session_state.inventory)  # after change
    })

def revert_version(version_id):
    try:
        # Find the snapshot of the chosen version
        target_entry = next(entry for entry in st.session_state.change_log if entry["version_id"] == version_id)
        restored_state = copy.deepcopy(target_entry["state_after_change"])  # <- use AFTER snapshot

        # Record this restoration BEFORE applying it
        st.session_state.change_log.append({
            "version_id": len(st.session_state.change_log) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": "SYSTEM",
            "item": "INVENTORY_WIDE",
            "action": f"RESTORATION_TO_V{version_id}",
            "old_amount": "N/A",
            "new_amount": "N/A",
            "state_after_change": copy.deepcopy(restored_state)
        })

        # Apply restoration
        st.session_state.inventory = restored_state

    except StopIteration:
        st.error("Invalid version ID")
        
# --- PAGE NAVIGATION ---
def go_to_inventory():
    st.session_state.page = "Inventory"
    st.session_state.open_category = None
    st.session_state.edit_item_page = None
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0
    st.session_state.change_applied = False
    st.session_state.barcode_error = None # Clear any barcode error

def go_to_dashboard():
    st.session_state.page = "Dashboard"

def go_to_category(category):
    st.session_state.page = "Category"
    st.session_state.open_category = category
    st.session_state.change_applied = False
    st.session_state.barcode_error = None

def go_to_edit_item(category, item):
    st.session_state.page = "EditItem"
    st.session_state.edit_item_page = (category, item)
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0
    st.session_state.change_applied = False
    st.session_state.barcode_error = None

# --- BARCODE SCANNER LOGIC ---
def process_barcode_scan(barcode):
    """Checks the scanned barcode and navigates to the item edit page."""
    if barcode in BARCODE_MAP:
        category, item_name = BARCODE_MAP[barcode]
        go_to_edit_item(category, item_name)
        st.rerun()
    else:
        st.session_state.barcode_error = f"ERROR: Barcode '{barcode}' not found in manifest."
        st.rerun() # Rerun to display the error on the Inventory page

# --- DATA PREP FOR DASHBOARD ---
def create_inventory_dataframe():
    """Converts inventory data into a Pandas DataFrame for Altair plotting and calculates metrics."""
    data_list = []
    total_original = 0
    total_current = 0
    low_stock_count = 0
    zero_stock_count = 0

    for category, items in st.session_state.inventory.items():
        cat_current = sum(item['current'] for item in items.values())
        cat_original = sum(item['original'] for item in items.values())
        
        # Calculate individual item status 
        for item_name, item_data in items.items():
            if item_data['current'] == 0:
                zero_stock_count += 1
            elif item_data['current'] <= LOW_STOCK_THRESHOLD:
                low_stock_count += 1
                
        data_list.append({
            'Category': category,
            'Current Stock': cat_current,
            'Original Stock': cat_original,
            'Consumed Stock': cat_original - cat_current,
            # Days remaining calculation: Total stock / (Total original stock / Total mission days)
            'Days Remaining': np.floor(cat_current / (cat_original / DAYS_IN_MISSION)) if cat_original > 0 else np.inf,
            'Consumption Rate': (cat_original - cat_current) / cat_original if cat_original > 0 else 0
        })

        total_current += cat_current
        total_original += cat_original

    df = pd.DataFrame(data_list)
    return df, total_current, total_original, low_stock_count, zero_stock_count

def inventory_page():
    st.markdown("<h1>EUROPA INVENTORY</h1>", unsafe_allow_html=True)

    # --- Current Mission Day Indicator (Inventory page, no progress bar) ---
    current_day = get_current_mission_day()

    st.markdown(f"**Current Mission Day:** {current_day} / {MISSION_DAYS}")
    st.markdown("<hr>", unsafe_allow_html=True)

    # 1. BARCODE SCANNER FORM
    with st.form("barcode_scan_form", clear_on_submit=True):
        scanned_barcode = st.text_input(
            "SCAN BARCODE",
            key="barcode_input",
            help="Scan a product barcode here. The input field will automatically submit the code."
        )
        # Invisible submit button (enter)
        submitted = st.form_submit_button("Submit Scan", use_container_width=True)
        if submitted and scanned_barcode:
            process_barcode_scan(scanned_barcode.strip())

    # Display error if barcode not found
    if st.session_state.barcode_error:
        st.error(st.session_state.barcode_error)

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 2. NAVIGATION BUTTONS
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("📊 Inventory Dashboard", help="View visual stock summary", use_container_width=True):
            go_to_dashboard()
    with col_nav2:
        if st.button("📚 Consumption History", help="Review consumption edits over mission days", use_container_width=True):
            st.session_state.page = "History"
            
    st.markdown("<hr>", unsafe_allow_html=True)

    # 3. CATEGORY BUTTONS
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, category in enumerate(st.session_state.inventory.keys()):
        inject_button_styles(category=category) 
        button_label = f"{ICON_MAP.get(category, '•')} {category}"
        with cols[i % 3]: 
            if st.button(button_label, key=f"catbtn_{category}", help="Click to open category"):
                go_to_category(category)
    

def dashboard_page():
    st.markdown("<h2>// SYSTEM OVERVIEW: INVENTORY DASHBOARD</h2>", unsafe_allow_html=True)
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Mission Progress Bar ---
    current_day = get_current_mission_day()

    days_left = MISSION_DAYS - current_day
    st.markdown(f"**Mission Progress:** Day {current_day} / {MISSION_DAYS} | Days Left: {days_left}")
    st.progress(current_day / MISSION_DAYS)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Prepare Inventory Data ---
    df, total_current, total_original, low_stock_count, zero_stock_count = create_inventory_dataframe()

    # --- DAY CALCULATIONS ---
    overall_days_left = np.floor(total_current / (total_original / DAYS_IN_MISSION))

    # --- Metrics Section ---
    st.markdown("<h3>Mission-Wide Status</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Units (Current)", f"{total_current:,}", delta=f"Capacity: {total_original:,}")
    col2.metric("Low Stock Items (<=30)", low_stock_count, delta_color="inverse" if low_stock_count else "off")
    col3.metric("Zero Stock Items", zero_stock_count, delta_color="inverse" if zero_stock_count else "off")
    col4.metric("Total Days Left (All Crew)", f"{int(overall_days_left):,} days")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Status Indicators (By Category) ---
    st.markdown("<h3>Key Status Indicators (By Category)</h3>", unsafe_allow_html=True)

    for _, data in df.iterrows():
        category = data["Category"]
        days_rem = data["Days Remaining"]
        icon = ICON_MAP.get(category, '•')

        if days_rem <= 30:
            delta_color = "inverse"
            status_text = "CRITICAL"
        elif days_rem <= 60:
            delta_color = "off"
            status_text = "WARNING"
        else:
            delta_color = "normal"
            status_text = "NOMINAL"

        col_cat, col_units, col_days, col_status = st.columns([1.6, 1, 1, 1.4])

        col_cat.metric("Category", f"{icon} {category}")
        col_units.metric("Units Left", f"{data['Current Stock']:,}", delta=f"Max: {data['Original Stock']:,}")
        col_days.metric("Days Left (All Crew)", f"{int(days_rem):,}", delta=status_text, delta_color=delta_color)
        col_status.metric("Consumption %", f"{data['Consumption Rate']:.1%}", delta=f"Used: {data['Consumed Stock']:,}", delta_color="off")

        st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)

    # --- Charts and Tables ---
    st.markdown("<h3>Category Stock Levels (Units Remaining)</h3>", unsafe_allow_html=True)

    bar_chart = alt.Chart(df).mark_bar(opacity=0.8, color="#008CFF").encode(
        x=alt.X('Current Stock:Q', title="Current Units Remaining"),
        y=alt.Y('Category:N', sort='-x'),
        color=alt.Color(
            'Days Remaining:Q',
            scale=alt.Scale(
                domain=[0, 30, 60, DAYS_IN_MISSION],
                range=['#FF4136', '#FFB703', '#A9D0F5', '#008CFF']
            ),
            title="Days Remaining"
        ),
        tooltip=['Category', 'Current Stock', 'Original Stock', alt.Tooltip('Days Remaining', format='.0f')]
    ).properties(
        title='Inventory Breakdown by Category'
    ).interactive()

    st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3>Raw Data Table</h3>", unsafe_allow_html=True)
    st.dataframe(
        df.set_index('Category').sort_values('Days Remaining'),
        use_container_width=True,
        column_config={
            "Consumption Rate": st.column_config.ProgressColumn(
                "Consumption Rate", format="%.1f%%", min_value=0, max_value=1
            ),
            "Days Remaining": st.column_config.NumberColumn(format="%.0f days")
        }
    )

# --- CATEGORY PAGE ---
def category_page():
    category = st.session_state.open_category
    st.markdown(f"<h2>// CATEGORY: {category}</h2>", unsafe_allow_html=True) 
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    items = st.session_state.inventory[category]
    
    for item_name, data in items.items():
        color = get_item_color(data["current"])
        
        # Styling for the button BEFORE rendering it
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
        
        # Back to using st.button for functionality
        if st.button(display_text, key=f"item_{category}_{item_name}", help="Click to edit this item"):
            go_to_edit_item(category, item_name)

# --- ITEM EDIT PAGE ---
def edit_item_page():
    category, item = st.session_state.edit_item_page
    data = st.session_state.inventory[category][item]
    
    st.markdown(f"<h3>// ITEM: {item}</h3>", unsafe_allow_html=True) 
    
    if not st.session_state.change_applied:
        st.button("⬅ Back to Category", on_click=lambda: go_to_category(category))
    
    st.markdown(f"**Current Units:** {data['current']}  |  **Original Load:** {data['original']}")
    # Progress bar uses current/original
    st.progress(data["current"]/data["original"])
    
    # Keep the warning message here for the specific item page
    if data['current'] <= LOW_STOCK_THRESHOLD:
        st.warning(f"⚠️ **LOW STOCK WARNING!** Only **{data['current']}** units remaining. Replenishment required.")
        
    col1, col2 = st.columns(2)
    with col1:
        add_units = st.number_input(
            "Add Units (Resupply)",
            min_value=0,
            max_value=data["original"] * 2, 
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
        add_val = st.session_state.add_units_edit
        remove_val = st.session_state.remove_units_edit
        new_amount = old_amount + add_val - remove_val
        
        # Allow new_amount to exceed original capacity (resupply) but not go below zero
        if new_amount < 0:
            st.error("❌ **ERROR:** Value out of bounds. Cannot go below zero.")
        else:
            action = "add" if add_val > 0 else ("remove" if remove_val > 0 else "none")
            
            if action != "none":
                record_change(category, item, old_amount, new_amount, action)
                st.session_state.inventory[category][item]["current"] = new_amount
                
                # If added units, update the 'original' capacity to reflect the new maximum load
                if add_val > 0 and new_amount > data["original"]:
                    st.session_state.inventory[category][item]["original"] = new_amount
                
                st.session_state.change_applied = True 
                
                st.session_state.add_units_edit = 0
                st.session_state.remove_units_edit = 0
                
                st.rerun()
            else:
                st.warning("No units added or removed. Please specify a value.")

# --- CONSUMPTION HISTORY PAGE ---
def consumption_history_page():
    st.markdown("<h2>// SYSTEM LOG: CONSUMPTION HISTORY</h2>", unsafe_allow_html=True)
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- 1. Current Mission Day & Progress ---
    total_days_actual = MISSION_DAYS  # Use mission duration
    all_edits = st.session_state.change_log
    current_day = get_current_mission_day()

    st.markdown(f"**Current Mission Day:** {current_day} / {total_days_actual}")
    st.progress(current_day / total_days_actual)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. Range Selection Inputs ---
    col_start, col_end = st.columns(2)
    default_start = max(1, current_day - 6)
    default_end = current_day
    with col_start:
        start_day = st.number_input("Start Mission Day", min_value=1, max_value=total_days_actual, value=default_start, step=1)
    with col_end:
        end_day = st.number_input("End Mission Day", min_value=1, max_value=total_days_actual, value=default_end, step=1)

    if start_day > end_day:
        st.error("Start day cannot be greater than end day.")
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. Predicted Consumption Box ---
    st.info(f"""
**Predicted Consumption Per Day**  

- Meals (Hydratable + Thermostabilized): {CREW_SIZE * 3}  
- Natural Form + Irradiated: {int(CREW_SIZE * 1.5)}  
- Desserts + Beverages: {CREW_SIZE * 10}  
- Condiments & Spreads: Specific to Entrée/Snack/Dessert
""", icon="ℹ️")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 4. Edits by mission day ---
    def get_mission_day(ts_str):
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        return get_current_mission_day(ts)

    day_edits = {}
    for entry in all_edits:
        day_num = get_mission_day(entry["timestamp"])
        if start_day <= day_num <= end_day:
            day_edits.setdefault(day_num, []).append(entry)

    if not day_edits:
        st.info(f"No edits found in mission day range {start_day} to {end_day}.")
        return

    # --- 5. Display edits in each day
    for day_num in sorted(day_edits.keys(), reverse=True):
        st.markdown(f"### Mission Day {day_num}")
        for entry in reversed(day_edits[day_num]):  # Most recent edits on top
            timestamp = entry["timestamp"]
            category = entry["category"]
            item = entry["item"]
            action = entry["action"]
            old_amount = entry["old_amount"]
            new_amount = entry["new_amount"]

            # Versoin button with info
            if action.startswith("RESTORATION"):
                btn_label = f"V{entry['version_id']} | {timestamp} | SYSTEM RESTORE: {action}"
            elif action == "INITIALIZATION":
                btn_label = f"V{entry['version_id']} | {timestamp} | INITIAL INVENTORY LOADED"
            else:
                change_symbol = "+" if action == "add" else "-"
                change_amount = abs(new_amount - old_amount)
                btn_label = f"V{entry['version_id']} | {timestamp} | {category} > {item} | {change_symbol}{change_amount} ({old_amount} → {new_amount})"

            # Button restores the version
            if st.button(btn_label, key=f"restore_{entry['version_id']}"):
                revert_version(entry["version_id"])
                st.success(f"Inventory restored to V{entry['version_id']}")
                st.rerun()

        st.markdown("<hr style='margin-top:10px; margin-bottom:10px;'>", unsafe_allow_html=True)

# --- MAIN APP SWITCH ---
if "page" not in st.session_state:
    go_to_inventory()  # Initialize states if first opening

# Page selector / switcher
if st.session_state.page == "Inventory":
    inventory_page()
elif st.session_state.page == "Dashboard":
    dashboard_page()
elif st.session_state.page == "Category":
    category_page()
elif st.session_state.page == "EditItem":
    edit_item_page()
elif st.session_state.page == "History": 
    consumption_history_page()