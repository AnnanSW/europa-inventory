# europa_inventory_streamlit_full.py
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

# --- HELPER FUNCTIONS ---
def get_item_color(amount):
    if amount == 0: return "#FF4C4C"
    elif amount <= LOW_STOCK_THRESHOLD: return "#FFA500"
    else: return "#4CAF50"

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

def modify_item(category, item):
    data = st.session_state.inventory[category][item]
    col1, col2, col3 = st.columns([3,2,2])
    with col1:
        st.markdown(f"**{item}**")
        st.progress(data['current']/data['original'], text=f"{data['current']} / {data['original']}")
    with col2:
        add = st.number_input("Add units", min_value=0, max_value=data['original']-data['current'], value=0, key=f"add_{category}_{item}")
        if st.button("Add", key=f"add_btn_{category}_{item}") and add > 0:
            old = data['current']
            data['current'] += add
            record_change(category, item, old, data['current'], "add")
            if data['current'] <= LOW_STOCK_THRESHOLD:
                st.warning(f"⚠️ Low stock for {item}: {data['current']} units remaining")
    with col3:
        remove = st.number_input("Remove units", min_value=0, max_value=data['current'], value=0, key=f"remove_{category}_{item}")
        if st.button("Remove", key=f"remove_btn_{category}_{item}") and remove > 0:
            old = data['current']
            data['current'] -= remove
            record_change(category, item, old, data['current'], "remove")
            if data['current'] == 0:
                st.error(f"❌ {item} is now depleted")
            elif data['current'] <= LOW_STOCK_THRESHOLD:
                st.warning(f"⚠️ Low stock for {item}: {data['current']} units remaining")

# --- UI ---
st.set_page_config(page_title="Europa Inventory", layout="wide")
st.title("Europa Inventory Management")

theme = st.sidebar.selectbox("Select Theme", ["Professional", "Sci-Fi Europa"])

for category, items in st.session_state.inventory.items():
    with st.expander(category, expanded=True):
        for item in items:
            modify_item(category, item)

with st.sidebar:
    st.header("Inventory Summary")
    total_items = sum(len(items) for items in st.session_state.inventory.values())
    low_stock = sum(1 for cat in st.session_state.inventory.values() for i in cat.values() if 0 < i['current'] <= LOW_STOCK_THRESHOLD)
    depleted = sum(1 for cat in st.session_state.inventory.values() for i in cat.values() if i['current']==0)
    st.write(f"Total items: {total_items}")
    st.write(f"Low stock: {low_stock}")
    st.write(f"Depleted: {depleted}")
    if st.button("View Change Log"):
        for log in reversed(st.session_state.change_log):
            st.text(f"V{log['version_id']}: {log['item']} {log['old_amount']} -> {log['new_amount']} [{log['action']}] @ {log['timestamp']}")