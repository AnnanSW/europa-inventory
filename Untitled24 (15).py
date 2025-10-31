import streamlit as st
import copy
from datetime import datetime
import fuzzywuzzy.fuzz
import pandas as pd

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 10
SEARCH_THRESHOLD = 80 # Fuzzy match score threshold

# --- INITIAL INVENTORY ---
def get_initial_inventory():
    return {
        "Hydratable Meals": {
            "Beef Stroganoff (Pouch)": {"current": 50, "original": 50},
            "Scrambled Eggs (Powder)": {"current": 75, "original": 75},
            "Cream of Mushroom Soup (Mix)": {"current": 60, "original": 60},
            "Macaroni and Cheese (Dry)": {"current": 45, "original": 45},
            "Asparagus Tips (Dried)": {"current": 30, "original": 30},
            "Grape Drink (Mix)": {"current": 9, "original": 90}, # Low Stock Example
            "Coffee (Mix)": {"current": 110, "original": 110},
            "Chili (Dried)": {"current": 0, "original": 40}, # Depleted Example
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

# --- HELPER FUNCTIONS ---
def get_item_color(amount):
    if amount == 0: return "#FF4136"  # red
    if amount <= LOW_STOCK_THRESHOLD: return "#FF851B"  # orange
    return "#2ECC40"  # green

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
        # Check if version_id is valid and not a system log (which contains the current state)
        if 1 <= version_id <= len(st.session_state.change_log):
            # We restore to the state *before* the action of version_id
            restored_state = copy.deepcopy(st.session_state.change_log[version_id-1]["state_before_change"])
            st.session_state.inventory = restored_state
            
            # Log the restoration
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
            st.success(f"Inventory restored to state *before* V{version_id}")
            go_to_inventory()
        else:
            st.error("Invalid version ID for restoration.")
    except Exception as e:
        st.error(f"Error during restoration: {e}")

# --- PAGE NAVIGATION ---
def go_to_inventory():
    st.session_state.page = "Inventory"
    st.session_state.open_category = None
    st.session_state.edit_item_page = None
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0
    # Rerunning Streamlit to ensure immediate redirect
    st.experimental_rerun()

def go_to_category(category):
    st.session_state.page = "Category"
    st.session_state.open_category = category

def go_to_edit_item(category, item):
    st.session_state.page = "EditItem"
    st.session_state.edit_item_page = (category, item)
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0

# --- MAIN INVENTORY PAGE (Refactored for 6-Box Layout and Search) ---
def inventory_page():
    st.markdown("<h1 style='color:#7FDBFF; text-align:center'>🛰️ EUROPA INVENTORY MANAGEMENT</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border:2px solid #7FDBFF'>", unsafe_allow_html=True)
    
    # --- Search Bar ---
    search_query = st.text_input("🔍 Search Inventory (e.g., Tuna, Coffee, Nuts)", key="search_bar")
    if search_query:
        display_search_results(search_query)
        st.markdown("<hr style='border:1px solid #7FDBFF'>", unsafe_allow_html=True)
        return # Stop processing the main menu if search results are displayed
    
    # --- Menu Boxes (6-Column Layout) ---
    categories = list(st.session_state.inventory.keys())
    
    # Create a list of all 6 items: 5 categories + Version History
    menu_items = categories + ["Version History / Restore"]
    
    # Use 3 columns, repeating twice for 6 items in a 2x3 grid
    cols = st.columns(3)
    
    for i, item_name in enumerate(menu_items):
        with cols[i % 3].container(height=120):
            if item_name != "Version History / Restore":
                # Category Button
                if st.button(f"📦 {item_name}", key=f"catbtn_{item_name}", use_container_width=True):
                    go_to_category(item_name)
            else:
                # Version History Button
                st.markdown(f"### ⚙️ {item_name}")
                if st.button("Open History Log", use_container_width=True):
                    st.session_state.page = "History"
                
    st.markdown("<hr style='border:1px solid #7FDBFF'>", unsafe_allow_html=True)

# --- SEARCH RESULTS PAGE ---
def display_search_results(query):
    st.markdown(f"### Results for: '**{query}**'")
    found_items = []
    
    # Iterate through all categories and items for fuzzy matching
    for category, items in st.session_state.inventory.items():
        for item_name, data in items.items():
            # Calculate fuzzy match score
            score = fuzzywuzzy.fuzz.partial_ratio(query.lower(), item_name.lower())
            if score >= SEARCH_THRESHOLD:
                found_items.append((category, item_name, data, score))

    if not found_items:
        st.info(f"No items found matching '{query}'. Try a different keyword.")
        return

    # Sort results by match score (best match first)
    found_items.sort(key=lambda x: x[3], reverse=True)
    
    # Display results
    for category, item_name, data, score in found_items:
        color = get_item_color(data["current"])
        
        # Display alerts if applicable
        if data["current"] == 0:
            st.error(f"🔴 **DEPLETED STOCK**: {item_name} (0 units)")
        elif data["current"] <= LOW_STOCK_THRESHOLD:
            st.warning(f"⚠️ **LOW STOCK**: {item_name} ({data['current']} units)")
            
        display_text = f"**{item_name}** ({category}) | Current: **{data['current']}** | Original: {data['original']}"
        
        # Use a container for a nicer clickable area and style
        with st.container(border=True):
            st.markdown(display_text, unsafe_allow_html=True)
            if st.button(f"Edit {item_name}", key=f"search_edit_{category}_{item_name}"):
                go_to_edit_item(category, item_name)


# --- CATEGORY PAGE (Added Stock Alerts) ---
def category_page():
    category = st.session_state.open_category
    st.markdown(f"<h2 style='color:#7FDBFF'>📦 {category}</h2>", unsafe_allow_html=True)
    
    # Use a back button with the lambda function inline for convenience
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr style='border:1px solid #7FDBFF'>", unsafe_allow_html=True)
    
    items = st.session_state.inventory[category]
    
    # Create columns for item layout
    num_cols = 2
    cols = st.columns(num_cols)
    col_index = 0
    
    for item_name, data in items.items():
        with cols[col_index % num_cols]:
            # Use container with border for the "app window" feel
            with st.container(border=True):
                current_amount = data["current"]
                original_amount = data["original"]
                
                # Low/Depleted Stock Alerts
                if current_amount == 0:
                    st.error(f"🔴 **DEPLETED STOCK**")
                elif current_amount <= LOW_STOCK_THRESHOLD:
                    st.warning(f"⚠️ **LOW STOCK**")
                    
                st.markdown(f"**{item_name}**")
                st.markdown(f"Current: **{current_amount}** | Original: {original_amount}")
                st.progress(current_amount / original_amount)

                # The button to go to edit page
                if st.button("Edit Units", key=f"item_{category}_{item_name}", use_container_width=True):
                    go_to_edit_item(category, item_name)
                    
        col_index += 1

# --- ITEM EDIT PAGE (Added Feedback & Auto-Redirect) ---
def edit_item_page():
    category, item = st.session_state.edit_item_page
    data = st.session_state.inventory[category][item]
    
    current_amount = data["current"]
    original_amount = data["original"]
    
    st.markdown(f"<h3 style='color:#7FDBFF'>🔧 Editing: {item}</h3>", unsafe_allow_html=True)
    st.button("⬅ Back to Category", on_click=lambda: go_to_category(category))
    st.markdown("<hr style='border:1px solid #7FDBFF'>", unsafe_allow_html=True)
    
    # Low/Depleted Stock Alerts
    if current_amount == 0:
        st.error(f"🔴 **CRITICAL ALERT**: This item is **DEPLETED**.")
    elif current_amount <= LOW_STOCK_THRESHOLD:
        st.warning(f"⚠️ **LOW STOCK ALERT**: Only **{current_amount}** units remaining.")
        
    st.markdown(f"**Current Units:** **{current_amount}** | **Original Load:** {original_amount}")
    st.progress(current_amount / original_amount)
    
    col1, col2 = st.columns(2)
    with col1:
        # Maximum for 'Add Units' is limited by the 'original' load
        add_units = st.number_input(
            "Add Units (Resupply/Correction)",
            min_value=0,
            max_value=original_amount - current_amount,
            value=st.session_state.add_units_edit,
            key="add_units_input",
            help="Units to add, max is the difference to original load."
        )
        if add_units > 0:
            st.session_state.remove_units_edit = 0
            st.session_state.add_units_edit = add_units
    
    with col2:
        # Maximum for 'Remove Units' is limited by the 'current' amount
        remove_units = st.number_input(
            "Remove Units (Consumption/Loss)",
            min_value=0,
            max_value=current_amount,
            value=st.session_state.remove_units_edit,
            key="remove_units_input",
            help="Units to remove, max is the current amount."
        )
        if remove_units > 0:
            st.session_state.add_units_edit = 0
            st.session_state.remove_units_edit = remove_units
    
    # Consolidated Apply Button
    if st.button("Apply Inventory Change", type="primary", use_container_width=True):
        units_to_change = st.session_state.add_units_edit - st.session_state.remove_units_edit
        
        if units_to_change == 0:
            st.warning("No change was made. Please enter a value to add or remove.")
            return

        old_amount = current_amount
        new_amount = old_amount + units_to_change
        
        # Check against capacity and zero (though number_input should prevent this)
        if new_amount > original_amount:
            st.error(f"❌ **ERROR**: Change of {units_to_change} units exceeds the original capacity of {original_amount}.")
        elif new_amount < 0:
            st.error(f"❌ **ERROR**: Change of {units_to_change} units would result in a negative stock.")
        else:
            action = "add" if units_to_change > 0 else "remove"
            record_change(category, item, old_amount, new_amount, action)
            st.session_state.inventory[category][item]["current"] = new_amount
            
            # Detailed success message
            change_str = f"**+ {units_to_change}**" if units_to_change > 0 else f"**- {abs(units_to_change)}**"
            st.success(f"✅ Success: {item} updated. Change: {change_str}. New Total: **{new_amount}** units.")
            
            # Redirect to the main page as requested
            st.balloons()
            st.info("Redirecting to main Inventory page...")
            go_to_inventory()

# --- VERSION HISTORY PAGE ---
def history_page():
    st.markdown("<h2 style='color:#7FDBFF'>📜 VERSION HISTORY & RESTORE</h2>", unsafe_allow_html=True)
    st.button("⬅ Back to Inventory", on_click=go_to_inventory)
    st.markdown("<hr style='border:1px solid #7FDBFF'>", unsafe_allow_html=True)

    if not st.session_state.change_log:
        st.info("No changes have been recorded yet.")
        return

    # Create a simple DataFrame for better display
    log_data = []
    for entry in reversed(st.session_state.change_log):
        version_id = entry["version_id"]
        timestamp = entry["timestamp"]
        category = entry["category"]
        item = entry["item"]
        action = entry["action"]
        old_amount = entry["old_amount"]
        new_amount = entry["new_amount"]
        
        # Format the description
        description = ""
        if action.startswith("RESTORATION"):
            description = f"SYSTEM RESTORE: {action}"
            log_type = "SYSTEM"
        else:
            change_amount = abs(new_amount - old_amount)
            change_symbol = "+" if action == "add" else "-"
            description = f"{change_symbol}{change_amount} ({old_amount} → {new_amount})"
            log_type = "UPDATE"
            
        log_data.append({
            "V": version_id,
            "Timestamp": timestamp,
            "Type": log_type,
            "Location": f"{category} > {item}",
            "Change": description,
            "Restore": version_id # Hidden column for button reference
        })

    # Display using st.dataframe with custom styling for clarity
    df = pd.DataFrame(log_data)
    
    # Hide the 'Restore' column for display, use it only for the button logic
    display_df = df.drop(columns=["Restore"]) 
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
             "V": st.column_config.NumberColumn("V", width="small"),
             "Timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
             "Type": st.column_config.Column("Type", width="small"),
        }
    )

    st.markdown("---")
    st.markdown("#### Restore to a Previous State")
    
    # The restore button should allow restoring to *any* version's state before change
    restore_v = st.number_input(
        "Enter Version ID (V) to Restore *before*:",
        min_value=1,
        max_value=len(st.session_state.change_log),
        value=len(st.session_state.change_log) if len(st.session_state.change_log) > 0 else 1,
        step=1
    )

    if st.button(f"↩️ RESTORE Inventory to state before V{restore_v}", type="secondary"):
        revert_version(restore_v)
        st.experimental_rerun() # Rerun to show the effect immediately


# --- MAIN APP SWITCH ---
# Initialization is handled at the top, this is the final page routing logic
if st.session_state.page == "Inventory":
    inventory_page()
elif st.session_state.page == "Category":
    category_page()
elif st.session_state.page == "EditItem":
    edit_item_page()
elif st.session_state.page == "History":
    history_page()