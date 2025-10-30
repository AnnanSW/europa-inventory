# europa_inventory_app_part1.py
import streamlit as st
import copy
from datetime import datetime

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 10

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
if "open_category" not in st.session_state:
    st.session_state.open_category = None
if "open_item" not in st.session_state:
    st.session_state.open_item = None

# --- HELPER FUNCTIONS ---
def get_item_color(amount):
    if amount == 0:
        return "red"
    elif amount <= LOW_STOCK_THRESHOLD:
        return "orange"
    else:
        return "green"

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

# --- PAGE SELECTION ---
page = st.sidebar.selectbox("Page", ["Inventory", "Version History"])

# --- SIDEBAR SUMMARY ---
inventory_flat = [(cat, item, data) for cat, items in st.session_state.inventory.items() for item, data in items.items()]
st.sidebar.markdown("## Summary")
st.sidebar.markdown(f"- Total items: {len(inventory_flat)}")
low_stock_count = sum(1 for _, _, d in inventory_flat if 0 < d["current"] <= LOW_STOCK_THRESHOLD)
depleted_count = sum(1 for _, _, d in inventory_flat if d["current"] == 0)
st.sidebar.markdown(f"- Low stock (<{LOW_STOCK_THRESHOLD}): {low_stock_count}")
st.sidebar.markdown(f"- Depleted: {depleted_count}")
# --- PART 2: INVENTORY DISPLAY, EDIT WINDOWS, AND VERSION HISTORY ---

if page == "Inventory":
    st.title("EUROPA INVENTORY")

    for category_name, items in st.session_state.inventory.items():
        # Category button
        cat_key = f"cat_{category_name}"
        if st.button(f"📦 {category_name}", key=cat_key):
            st.session_state.open_category = category_name
            st.session_state.open_item = None  # Close any open item window

        if st.session_state.open_category == category_name:
            st.markdown("---")
            for item_name, data in items.items():
                item_key = f"item_{category_name}_{item_name}"
                # Item display with color and progress bar
                current = data["current"]
                original = data["original"]
                color = get_item_color(current)
                st.markdown(f"**{item_name}** ({current}/{original})")
                st.progress(current/original)

                if st.button(f"✏️ Edit {item_name}", key=item_key):
                    st.session_state.open_item = (category_name, item_name)

    # Item edit window
    if st.session_state.open_item:
        cat, item = st.session_state.open_item
        st.subheader(f"Editing: {item} in {cat}")
        current = st.session_state.inventory[cat][item]["current"]
        original = st.session_state.inventory[cat][item]["original"]

        col1, col2 = st.columns(2)
        with col1:
            add_amount = st.number_input("Add Units", min_value=0, step=1, key="add_units")
        with col2:
            remove_amount = st.number_input("Remove Units", min_value=0, step=1, key="remove_units")

        # Disable one input if the other is used
        if add_amount > 0:
            st.session_state.remove_units = 0
        if remove_amount > 0:
            st.session_state.add_units = 0

        if st.button("Apply Changes"):
            new_amount = current + add_amount - remove_amount
            if new_amount > original:
                st.error(f"Cannot exceed original amount ({original}).")
            elif new_amount < 0:
                st.error("Cannot go below 0.")
            else:
                if add_amount > 0:
                    action = "add"
                    record_change(cat, item, current, new_amount, action)
                elif remove_amount > 0:
                    action = "remove"
                    record_change(cat, item, current, new_amount, action)
                st.session_state.inventory[cat][item]["current"] = new_amount
                st.success(f"Updated {item} to {new_amount} units.")
                # Reset inputs
                st.session_state.add_units = 0
                st.session_state.remove_units = 0

if page == "Version History":
    st.title("Version History")
    if not st.session_state.change_log:
        st.info("No changes recorded yet.")
    else:
        for entry in reversed(st.session_state.change_log):
            vid = entry["version_id"]
            ts = entry["timestamp"]
            cat = entry["category"]
            item = entry["item"]
            action = entry["action"]
            old = entry["old_amount"]
            new = entry["new_amount"]
            st.markdown(f"**V{vid}** | {ts} | {cat} | {item} | {action} | {old} → {new}")
            if action != "RESTORATION":
                if st.button(f"Restore to V{vid}", key=f"restore_{vid}"):
                    # Revert logic
                    try:
                        restored_state = copy.deepcopy(st.session_state.change_log[vid-1]["state_before_change"])
                        st.session_state.inventory = restored_state
                        st.session_state.change_log.append({
                            "version_id": len(st.session_state.change_log)+1,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "category": "SYSTEM",
                            "item": "INVENTORY_WIDE",
                            "action": f"RESTORATION_TO_V{vid}",
                            "old_amount": "N/A",
                            "new_amount": "N/A",
                            "state_before_change": copy.deepcopy(st.session_state.inventory)
                        })
                        st.success(f"Restored inventory to state before V{vid}")
                    except Exception as e:
                        st.error(f"Restore failed: {e}")
