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
            "Macaroni and Cheese (Dry)": {"current": 45, "original": 45}
        },
        "Thermostabilized Meals": {
            "Lemon Pepper Tuna (Pouch)": {"current": 120, "original": 120},
            "Spicy Green Beans (Pouch)": {"current": 85, "original": 85}
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
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown(f"**{item}**")
        st.progress(data['current']/data['original'], text=f"{data['current']} / {data['original']}")
    with col2:
        change = st.number_input("Adjust units", min_value=0, value=data['current'], key=f"{category}_{item}")
        if st.button("Apply", key=f"apply_{category}_{item}"):
            old = data['current']
            data['current'] = change
            record_change(category, item, old, change, "modify")
            if change <= LOW_STOCK_THRESHOLD and change > 0:
                st.warning(f"⚠️ Low stock for {item}: {change} units remaining")
            elif change == 0:
                st.error(f"❌ {item} is now depleted")

# --- UI ---
st.set_page_config(page_title="Europa Inventory", layout="wide")
st.title("Europa Inventory Management")

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