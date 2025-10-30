# europa_inventory_streamlit_v2_part1.py
import streamlit as st
import copy
from datetime import datetime

# --- CONFIG ---
LOW_STOCK_THRESHOLD = 10

# --- INITIAL INVENTORY (only main 5 categories) ---
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

# --- HELPER FUNCTIONS ---
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

def get_item_color(amount):
    if amount == 0: return "red"
    elif amount <= LOW_STOCK_THRESHOLD: return "orange"
    return "green"

# --- STREAMLIT PAGE ---
st.set_page_config(page_title="EUROPA Inventory", layout="wide")
st.title("EUROPA INVENTORY")

# Sidebar: navigation
page = st.sidebar.selectbox("Menu", ["Inventory", "Version History"])
if page == "Inventory":
    st.header("EUROPA INVENTORY")
    
    for category_name, items in st.session_state.inventory.items():
        # Large category as a button/banner
        if st.button(f"📦 {category_name}"):
            with st.container():
                st.subheader(category_name)
                for item_name, data in items.items():
                    current = data["current"]
                    original = data["original"]
                    color = get_item_color(current)
                    progress = current / original if original > 0 else 0

                    # Each food item as expander
                    with st.expander(item_name):
                        st.markdown(f"**Current:** {current} / **Original:** {original}")
                        st.progress(progress)

                        col1, col2, col3 = st.columns([1,1,2])
                        # Mutually exclusive add/remove
                        add_key = f"add_{category_name}_{item_name}"
                        remove_key = f"remove_{category_name}_{item_name}"
                        add_amount = st.session_state.get(add_key, 0)
                        remove_amount = st.session_state.get(remove_key, 0)

                        with col1:
                            add_amount = st.number_input(
                                "Add", min_value=0, value=add_amount,
                                key=add_key,
                                disabled=remove_amount>0
                            )
                        with col2:
                            remove_amount = st.number_input(
                                "Remove", min_value=0, value=remove_amount,
                                key=remove_key,
                                disabled=add_amount>0
                            )
                        with col3:
                            if st.button("Apply Changes", key=f"apply_{category_name}_{item_name}"):
                                new_amount = current + add_amount - remove_amount
                                if new_amount > original:
                                    st.warning(f"Cannot exceed original amount ({original})!")
                                    new_amount = original
                                elif new_amount < 0:
                                    st.warning("Cannot go below 0!")
                                    new_amount = 0
                                if new_amount != current:
                                    record_change(category_name, item_name, current, new_amount, "update")
                                    st.session_state.inventory[category_name][item_name]["current"] = new_amount
                                    # Reset inputs
                                    st.session_state[add_key] = 0
                                    st.session_state[remove_key] = 0
                                    st.experimental_rerun()

                        # Alerts
                        if current == 0:
                            st.markdown(f"<span style='color:red;font-weight:bold'>⚠️ DEPLETED</span>", unsafe_allow_html=True)
                        elif current <= LOW_STOCK_THRESHOLD:
                            st.markdown(f"<span style='color:orange;font-weight:bold'>⚠️ LOW STOCK</span>", unsafe_allow_html=True)

elif page == "Version History":
    st.header("EUROPA VERSION HISTORY")
    if st.session_state.change_log:
        for entry in reversed(st.session_state.change_log):
            v_id = entry["version_id"]
            ts = entry["timestamp"]
            cat = entry["category"]
            item = entry["item"]
            action = entry["action"]
            old = entry["old_amount"]
            new = entry["new_amount"]
            direction = "➕" if new != "N/A" and new > old else "➖" if new != "N/A" and new < old else "ℹ️"
            st.markdown(f"**V{v_id} | {ts} | {cat} - {item}** | {direction} {old} → {new} | Action: {action}")
            if action != "RESTORATION":
                if st.button(f"Restore to V{v_id}", key=f"restore_{v_id}"):
                    restored_state = copy.deepcopy(st.session_state.change_log[v_id-1]["state_before_change"])
                    st.session_state.inventory = restored_state
                    st.session_state.change_log.append({
                        "version_id": len(st.session_state.change_log)+1,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "category": "SYSTEM",
                        "item": "INVENTORY_WIDE",
                        "action": f"RESTORATION_TO_V{v_id}",
                        "old_amount": "N/A",
                        "new_amount": "N/A",
                        "state_before_change": copy.deepcopy(st.session_state.inventory)
                    })
                    st.success(f"Restored to V{v_id}")
                    st.experimental_rerun()
    else:
        st.info("No changes recorded yet.")
