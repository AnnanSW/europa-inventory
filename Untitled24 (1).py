# europa_inventory_streamlit_hierarchical_part1.py
import streamlit as st
import copy
from datetime import datetime

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 10

# --- INITIAL INVENTORY ---
def get_initial_inventory():
    return {
        "HYDRATABLE MEALS": {
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
        "THERMOSTABILIZED MEALS": {
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
        "NATURAL FORM & IRRADIATED": {
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
        "DESSERTS & BEVERAGES (NON-MIX)": {
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
        "CONDIMENTS & SPREADS": {
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
def get_item_color(amount):
    if amount == 0:
        return "#FF4C4C"
    elif amount <= LOW_STOCK_THRESHOLD:
        return "#FFA500"
    else:
        return "#4CAF50"

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

# --- PAGE SETUP ---
st.set_page_config(page_title="EUROPA Inventory", layout="wide")
st.title("EUROPA Inventory Management")

# Sidebar summary
with st.sidebar:
    st.header("Inventory Summary")
    total_items = sum(len(items) for items in st.session_state.inventory.values())
    low_stock_items = sum(
        1 for category in st.session_state.inventory.values() 
        for item in category.values() if 0 < item['current'] <= LOW_STOCK_THRESHOLD
    )
    depleted_items = sum(
        1 for category in st.session_state.inventory.values() 
        for item in category.values() if item['current'] == 0
    )
    st.markdown(f"- Total items: {total_items}")
    st.markdown(f"- Low stock: {low_stock_items}")
    st.markdown(f"- Depleted: {depleted_items}")

# Version history expander
with st.sidebar.expander("Version History"):
    for entry in reversed(st.session_state.change_log):
        st.write(f"V{entry['version_id']}: {entry['timestamp']} | {entry['category']} | {entry['item']} | {entry['action']}")
    version_input = st.number_input("Restore Version ID", min_value=1, value=1, step=1)
    if st.button("Restore Version"):
        revert_version(version_input)
        st.experimental_rerun()

# --- DISPLAY CATEGORIES (collapsed) ---
for category, items in st.session_state.inventory.items():
    with st.expander(category, expanded=False):
        st.write(f"{len(items)} items")
# --- INTERACTIVE ITEM EXPANDERS ---
for category, items in st.session_state.inventory.items():
    with st.expander(category, expanded=False):
        for item_name, data in items.items():
            current = data["current"]
            original = data["original"]
            color = get_item_color(current)
            progress = current / original if original > 0 else 0

            with st.expander(item_name, expanded=False):
                st.markdown(f"**Current:** {current} / **Original:** {original}")
                st.progress(progress)

                col1, col2, col3 = st.columns([1,1,2])
                with col1:
                    add_amount = st.number_input(f"Add to {item_name}", min_value=0, value=0, key=f"add_{item_name}")
                with col2:
                    remove_amount = st.number_input(f"Remove from {item_name}", min_value=0, value=0, key=f"remove_{item_name}")
                with col3:
                    if st.button("Apply Changes", key=f"apply_{item_name}"):
                        new_amount = current + add_amount - remove_amount
                        if new_amount > original:
                            st.warning(f"Cannot exceed original amount ({original})!")
                            new_amount = original
                        elif new_amount < 0:
                            st.warning("Cannot go below 0!")
                            new_amount = 0
                        if new_amount != current:
                            record_change(category, item_name, current, new_amount, "update")
                            st.session_state.inventory[category][item_name]["current"] = new_amount
                            st.experimental_rerun()

                # Alert indicators
                if current == 0:
                    st.markdown(f"<span style='color:red;font-weight:bold'>⚠️ DEPLETED</span>", unsafe_allow_html=True)
                elif current <= LOW_STOCK_THRESHOLD:
                    st.markdown(f"<span style='color:orange;font-weight:bold'>⚠️ LOW STOCK</span>", unsafe_allow_html=True)

# --- SEARCH FUNCTIONALITY ---
search_term = st.text_input("Search Items")
if search_term:
    st.subheader(f"Search Results for '{search_term}'")
    for category, items in st.session_state.inventory.items():
        for item_name, data in items.items():
            if search_term.lower() in item_name.lower():
                current = data["current"]
                original = data["original"]
                color = get_item_color(current)
                progress = current / original if original > 0 else 0
                st.markdown(f"**{item_name}** ({category})")
                st.progress(progress)
                st.markdown(f"Current: {current} / Original: {original}")
