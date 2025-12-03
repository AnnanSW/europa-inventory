import streamlit as st
import copy
from datetime import datetime
import pandas as pd
import altair as alt

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 10
WARNING_STOCK_THRESHOLD = 20

# --- BARCODE MAPPING (NEW ADDITION) ---
# A dictionary to map a simulated, authentic-looking barcode to the item name
BARCODE_MAP = {
    "931301018901": ("Hydratable Meals", "Beef Stroganoff (Pouch)"),
    "931301018902": ("Hydratable Meals", "Scrambled Eggs (Powder)"),
    "931301018903": ("Hydratable Meals", "Cream of Mushroom Soup (Mix)"),
    "931301018904": ("Hydratable Meals", "Macaroni and Cheese (Dry)"),
    "931301018905": ("Hydratable Meals", "Asparagus Tips (Dried)"),
    "931301018906": ("Hydratable Meals", "Grape Drink (Mix)"),
    "931301018907": ("Hydratable Meals", "Coffee (Mix)"),
    "931301018908": ("Hydratable Meals", "Chili (Dried)"),
    "931301018909": ("Hydratable Meals", "Chicken and Rice (Dried)"),
    "931301018910": ("Hydratable Meals", "Oatmeal with Applesauce (Dry)"),

    "931301018911": ("Thermostabilized Meals", "Lemon Pepper Tuna (Pouch)"),
    "931301018912": ("Thermostabilized Meals", "Spicy Green Beans (Pouch)"),
    "931301018913": ("Thermostabilized Meals", "Pork Chop (Pouch)"),
    "931301018914": ("Thermostabilized Meals", "Chicken Tacos (Pouch)"),
    "931301018915": ("Thermostabilized Meals", "Turkey (Pouch)"),
    "931301018916": ("Thermostabilized Meals", "Brownie (Pouch)"),
    "931301018917": ("Thermostabilized Meals", "Raspberry Yogurt (Pouch)"),
    "931301018918": ("Thermostabilized Meals", "Ham Steak (Pouch)"),
    "931301018919": ("Thermostabilized Meals", "Sausage Patty (Pouch)"),
    "931301018920": ("Thermostabilized Meals", "Fruit Cocktail (Pouch)"),

    "931301018921": ("Natural Form & Irradiated", "Pecans (Irradiated)"),
    "931301018922": ("Natural Form & Irradiated", "Shortbread Cookies"),
    "931301018923": ("Natural Form & Irradiated", "Crackers"),
    "931301018924": ("Natural Form & Irradiated", "M&Ms (Candy)"),
    "931301018925": ("Natural Form & Irradiated", "Tortillas (Packages)"),
    "931301018926": ("Natural Form & Irradiated", "Dried Apricots"),
    "931301018927": ("Natural Form & Irradiated", "Dry Roasted Peanuts"),
    "931301018928": ("Natural Form & Irradiated", "Beef Jerky (Strips)"),
    "931301018929": ("Natural Form & Irradiated", "Fruit Bar"),
    "931301018930": ("Natural Form & Irradiated", "Cheese Spread (Tube)"),

    "931301018931": ("Desserts & Beverages (Non-Mix)", "Space Ice Cream (Freeze-dried)"),
    "931301018932": ("Desserts & Beverages (Non-Mix)", "Banana Pudding (Pouch)"),
    "931301018933": ("Desserts & Beverages (Non-Mix)", "Chocolate Pudding (Pouch)"),
    "931301018934": ("Desserts & Beverages (Non-Mix)", "Apple Sauce (Pouch)"),
    "931301018935": ("Desserts & Beverages (Non-Mix)", "Orange Juice (Carton)"),
    "931301018936": ("Desserts & Beverages (Non-Mix)", "Tea Bags (Box)"),
    "931301018937": ("Desserts & Beverages (Non-Mix)", "Hot Cocoa (Mix)"),
    "931301018938": ("Desserts & Beverages (Non-Mix)", "Cranberry Sauce (Pouch)"),
    "931301018939": ("Desserts & Beverages (Non-Mix)", "Strawberry Shake (Mix)"),
    "931301018940": ("Desserts & Beverages (Non-Mix)", "Dried Peaches"),

    "931301018941": ("Condiments & Spreads", "Ketchup (Packet)"),
    "931301018942": ("Condiments & Spreads", "Mustard (Packet)"),
    "931301018943": ("Condiments & Spreads", "Salt (Packet)"),
    "931301018944": ("Condiments & Spreads", "Pepper (Packet)"),
    "931301018945": ("Condiments & Spreads", "Jelly (Packet)"),
    "931301018946": ("Condiments & Spreads", "Honey (Tube)"),
    "931301018947": ("Condiments & Spreads", "Hot Sauce (Bottle)"),
    "931301018948": ("Condiments & Spreads", "Mayonnaise (Packet)"),
    "931301018949": ("Condiments & Spreads", "Sugar (Packet)"),
    "931301018950": ("Condiments & Spreads", "Taco Sauce (Packet)"),
}


# --- DYNAMIC STYLING INJECTION ---
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
        # Apply special style for the Inventory Page buttons
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

# --- CUSTOM PROFESSIONAL HUD THEME STYLES (Finalized Spacing) ---
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
# --- END OF CUSTOM NASA THEME STYLES ---

# --- INITIAL INVENTORY (FULLY STOCKED) ---
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

# --- ICONS MAPPING ---
ICON_MAP = {
    "Hydratable Meals": "💧",
    "Thermostabilized Meals": "🔥",
    "Natural Form & Irradiated": "📦",
    "Desserts & Beverages (Non-Mix)": "🍹",
    "Condiments & Spreads": "🧂"
}

# --- SESSION STATE INIT (Standard setup) ---
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
# New: State for Barcode Scanning
if "barcode_error" not in st.session_state:
    st.session_state.barcode_error = None


# --- HELPER FUNCTIONS ---
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
            return "#FF4136" # Red trumps all (Critical Alert)
        if item["current"] <= LOW_STOCK_THRESHOLD:
            color = "#FFB703" # Amber is the warning (Low Stock Alert)
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
        # State before change V{id} is actually the state *before* it was recorded
        restored_state = copy.deepcopy(st.session_state.change_log[version_id-1]["state_before_change"])
        st.session_state.inventory = restored_state
        # Record the restoration action
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
        
# --- PAGE NAVIGATION (Standard setup) ---
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

# --- BARCODE SCANNER LOGIC (NEW FUNCTION) ---
def process_barcode_scan(barcode):
    """Checks the scanned barcode and navigates to the item edit page."""
    if barcode in BARCODE_MAP:
        category, item_name = BARCODE_MAP[barcode]
        go_to_edit_item(category, item_name)
        st.rerun()
    else:
        st.session_state.barcode_error = f"ERROR: Barcode '{barcode}' not found in manifest."
        st.rerun() # Rerun to display the error on the Inventory page

# --- DATA PREP FOR DASHBOARD (NEW FUNCTION) ---
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
        
        # Calculate individual item status for the metrics
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
            'Consumption Rate': (cat_original - cat_current) / cat_original if cat_original > 0 else 0
        })

        total_current += cat_current
        total_original += cat_original

    df = pd.DataFrame(data_list)
    return df, total_current, total_original, low_stock_count, zero_stock_count

# --- MAIN INVENTORY PAGE (MODIFIED) ---
def inventory_page():
    st.markdown("<h1>EUROPA INVENTORY</h1>", unsafe_allow_html=True)

    # 1. BARCODE SCANNER FORM
    with st.form("barcode_scan_form", clear_on_submit=True):
        scanned_barcode = st.text_input(
            "SCAN BARCODE",
            key="barcode_input",
            help="Scan a product barcode here. The input field will automatically submit the code."
        )
        # This invisible submit button is necessary for the form submission
        submitted = st.form_submit_button("Submit Scan", use_container_width=True)

        if submitted and scanned_barcode:
            # When the scanner hits Enter, it submits the form and we process the barcode
            process_barcode_scan(scanned_barcode.strip())

    # Display error message if applicable
    if st.session_state.barcode_error:
        st.error(st.session_state.barcode_error)

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 2. NAVIGATION BUTTONS
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("📊 Inventory Dashboard", help="View visual stock summary", use_container_width=True):
            go_to_dashboard()
    with col_nav2:
        if st.button("📚 Version History / Restore", help="Review and revert changes", use_container_width=True):
            st.session_state.page = "History"
            
    st.markdown("<hr>", unsafe_allow_html=True)

    # 3. CATEGORY BUTTONS (Existing Logic)
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, category in enumerate(st.session_state.inventory.keys()):
        # Inject CSS styling for the button BEFORE rendering it
        inject_button_styles(category=category) 
        
        button_label = f"{ICON_MAP.get(category, '•')} {category}"
        
        with cols[i % 3]: 
            if st.button(button_label, key=f"catbtn_{category}", help="Click to open category"):
                go_to_category(category)
    

# --- DASHBOARD PAGE (NEW) ---
def dashboard_page():
    st.markdown("<h2>// SYSTEM OVERVIEW: INVENTORY DASHBOARD</h2>", unsafe_allow_html=True)
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr>", unsafe_allow_html=True)

    df, total_current, total_original, low_stock_count, zero_stock_count = create_inventory_dataframe()

    # --- Metrics Section ---
    st.markdown("<h3>Key Status Indicators</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    # Total Units Metric
    col1.metric("Total Units (Current)", f"{total_current:,}", delta=f"Capacity: {total_original:,}")
    # Low Stock Warning Metric (The inverse color changes the number color)
    low_stock_delta = low_stock_count - 0
    col2.metric("Low Stock Items (<=10)", low_stock_count, delta=f"{low_stock_delta} low items", delta_color="off" if low_stock_delta == 0 else "inverse")
    # Zero Stock Critical Metric
    zero_stock_delta = zero_stock_count - 0
    col3.metric("Zero Stock Items (Critical)", zero_stock_count, delta=f"{zero_stock_delta} critical items", delta_color="off" if zero_stock_delta == 0 else "inverse")
    # Consumption Rate
    consumption_rate = (total_original - total_current) / total_original
    col4.metric("Overall Consumption", f"{consumption_rate:.1%}", delta=f"{total_original - total_current:,} units used")

    st.markdown("<br>", unsafe_allow_html=True) 

    # --- Chart 1: Category Stock Levels (Bar Chart) ---
    st.markdown("<h3>Category Stock Levels (Units Remaining)</h3>", unsafe_allow_html=True)

    # Altair Theming for the HUD feel
    hud_colors = ["#008CFF", "#A9D0F5", "#FFB703", "#FF4136", "#2A3A54"]

    # Define the Altair chart
    bar_chart = alt.Chart(df).mark_bar(opacity=0.8, color="#008CFF").encode(
        # X-axis for stock count
        x=alt.X('Current Stock:Q', title="Current Units Remaining"),
        # Y-axis for category names, sorted by current stock (descending)
        y=alt.Y('Category:N', title="Category", sort='-x'),
        # Color based on consumption rate
        color=alt.Color('Consumption Rate:Q', scale=alt.Scale(range=hud_colors), title="Consumption Rate"),
        # Tooltip for interaction
        tooltip=['Category', 'Current Stock', 'Original Stock', alt.Tooltip('Consumption Rate', format='.1%')]
    ).properties(
        title='Inventory Breakdown by Category (Consumption Highlight)'
    ).interactive()

    st.altair_chart(bar_chart, use_container_width=True)

    # --- Chart 2: Overall Stock Status (Donut Chart) ---
    st.markdown("<h3>Overall Stock Status</h3>", unsafe_allow_html=True)

    stock_status_data = pd.DataFrame({
        'Status': ['Available', 'Consumed'],
        'Units': [total_current, total_original - total_current]
    })
    
    # Define the colors: Available (Bright Blue) and Consumed (Dark Blue)
    stock_colors = alt.Scale(domain=['Available', 'Consumed'], range=['#008CFF', '#112239'])

    pie_chart = alt.Chart(stock_status_data).encode(
        theta=alt.Theta("Units", stack=True)
    ).properties(
        title='Total Units: Available vs. Consumed'
    )

    # The arcs representing the data (Donut)
    base = pie_chart.mark_arc(outerRadius=120, innerRadius=80).encode(
        color=alt.Color("Status:N", scale=stock_colors),
        order=alt.Order("Units", sort="descending"),
        tooltip=["Status", "Units"]
    )
    
    # Add text labels inside the donut
    text = base.mark_text(radius=100).encode(
        text=alt.Text("Units:Q", format=","),
        order=alt.Order("Units", sort="descending"),
        color=alt.value("white")
    )
    
    st.altair_chart(base, use_container_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3>Raw Data Table</h3>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True) # Display raw data


# --- CATEGORY PAGE (UNCHANGED) ---
def category_page():
    category = st.session_state.open_category
    st.markdown(f"<h2>// CATEGORY: {category}</h2>", unsafe_allow_html=True) 
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    items = st.session_state.inventory[category]
    
    for item_name, data in items.items():
        color = get_item_color(data["current"])
        
        # Inject CSS styling for the button BEFORE rendering it
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
        
        # Revert back to using st.button for functionality
        if st.button(display_text, key=f"item_{category}_{item_name}", help="Click to edit this item"):
            go_to_edit_item(category, item_name)

# --- ITEM EDIT PAGE (UNCHANGED) ---
def edit_item_page():
    category, item = st.session_state.edit_item_page
    data = st.session_state.inventory[category][item]
    
    st.markdown(f"<h3>// ITEM: {item}</h3>", unsafe_allow_html=True) 
    
    if not st.session_state.change_applied:
        st.button("⬅ Back to Category", on_click=lambda: go_to_category(category))
    
    st.markdown(f"**Current Units:** {data['current']}  |  **Original Load:** {data['original']}")
    st.progress(data["current"]/data["original"])
    
    # Keep the warning message here, as it's the specific item page
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
        st.success(f"✅ **UPDATE SUCCESS** | {item} is now at **{data['current']}** units. Data hash accepted.")
        st.button("🚀 Return to Inventory Home", on_click=go_to_inventory)
    elif st.button("Apply Changes"):
        old_amount = data["current"]
        add_val = st.session_state.add_units_edit
        remove_val = st.session_state.remove_units_edit
        new_amount = old_amount + add_val - remove_val
        
        if new_amount > data["original"] or new_amount < 0:
            st.error("❌ **ERROR:** Value out of bounds. Cannot exceed original capacity or go below zero.")
        else:
            action = "add" if add_val > 0 else ("remove" if remove_val > 0 else "none")
            
            if action != "none":
                record_change(category, item, old_amount, new_amount, action)
                st.session_state.inventory[category][item]["current"] = new_amount
                
                st.session_state.change_applied = True 
                
                st.session_state.add_units_edit = 0
                st.session_state.remove_units_edit = 0
                
                st.rerun()
            else:
                st.warning("No units added or removed. Please specify a value.")

# --- VERSION HISTORY PAGE (UNCHANGED) ---
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
            # Calculate the absolute difference for display
            change_amount = abs(new_amount - old_amount)
            if change_amount > 0:
                st.markdown(f"**V{version_id}** | {timestamp} | {category} > {item} | {change_symbol}{change_amount} ({old_amount}→{new_amount})", unsafe_allow_html=True)
                if st.button(f"Restore to state before V{version_id}", key=f"restore_{version_id}"):
                    revert_version(version_id)
                    st.success(f"Inventory restored to state before V{version_id}")
                    st.rerun() # Rerun to show the restored state
            

# --- MAIN APP SWITCH ---
# Ensure session state is initialized on the first run
if "page" not in st.session_state:
    go_to_inventory() # Use the function to initialize all states

# Page selector
if st.session_state.page == "Inventory":
    inventory_page()
elif st.session_state.page == "Dashboard":
    dashboard_page()
elif st.session_state.page == "Category":
    category_page()
elif st.session_state.page == "EditItem":
    edit_item_page()
elif st.session_state.page == "History":
    history_page()