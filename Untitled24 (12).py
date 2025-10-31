# europa_inventory_nasa_part1.py
import streamlit as st
import copy
from datetime import datetime
import time

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
if "page" not in st.session_state:
    st.session_state.page = "Inventory"
if "open_category" not in st.session_state:
    st.session_state.open_category = None
if "edit_item_page" not in st.session_state:
    st.session_state.edit_item_page = None

# --- STYLING ---
st.markdown("""
    <style>
        .stApp {
            background-color:#050505;
            color:#c5c6c7;
            font-family: 'Orbitron', sans-serif;
        }
        .stButton>button {
            background: linear-gradient(135deg, #0b3d91, #1f2833);
            color: #66fcf1;
            border-radius: 8px;
            border: 2px solid #45a29e;
            padding: 0.4rem 0.8rem;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #45a29e;
            color: #0b0c10;
            transform: scale(1.05);
        }
        .stProgress>div>div>div>div {
            background: linear-gradient(90deg, #45a29e, #66fcf1);
        }
        @keyframes pulseRed {
            0% {color: #ff4c4c;}
            50% {color: #ff0000;}
            100% {color: #ff4c4c;}
        }
        @keyframes pulseOrange {
            0% {color: #ffae42;}
            50% {color: #ff7f00;}
            100% {color: #ffae42;}
        }
        .low-stock {
            animation: pulseOrange 1s infinite;
            font-weight: bold;
        }
        .critical {
            animation: pulseRed 1s infinite;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def record_change(category, item, old_amount, new_amount, action):
    st.session_state.change_log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "item": item,
        "action": action,
        "old_amount": old_amount,
        "new_amount": new_amount
    })
# --- NAVIGATION FUNCTIONS ---
def go_to_inventory():
    st.session_state.page = "Inventory"
    st.session_state.open_category = None
    st.session_state.edit_item_page = None

def go_to_category(category):
    st.session_state.page = "Category"
    st.session_state.open_category = category
    st.session_state.edit_item_page = None

def go_to_edit_item(category, item):
    st.session_state.page = "Item"
    st.session_state.open_category = category
    st.session_state.edit_item_page = item


# --- PAGE RENDERING ---
page = st.session_state.get("page", "Inventory")

# --- SIDEBAR ---
st.sidebar.title("🛰️ EUROPA CONTROL PANEL")
if st.sidebar.button("🏠 Home"):
    go_to_inventory()
if st.sidebar.button("🧾 Version History"):
    st.session_state.page = "History"

st.sidebar.markdown("---")
st.sidebar.caption("System Status: ✅ Nominal")
st.sidebar.caption("Operator: **Automated Inventory AI**")
st.sidebar.caption(datetime.now().strftime("Mission Time: %Y-%m-%d %H:%M:%S"))

# --- INVENTORY PAGE ---
if page == "Inventory":
    st.title("🪐 EUROPA INVENTORY SYSTEM")

    for category, items in st.session_state.inventory.items():
        with st.container():
            st.markdown(f"### ⚙️ {category}")
            if st.button(f"Open {category}"):
                go_to_category(category)
                st.rerun()

# --- CATEGORY PAGE ---
elif page == "Category":
    category = st.session_state.open_category
    if not category:
        go_to_inventory()
        st.rerun()

    st.title(f"📦 {category}")
    if st.button("⬅ Back to Main Menu"):
        go_to_inventory()
        st.rerun()

    for item, data in st.session_state.inventory[category].items():
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            status_class = get_item_class(data["current"])
            st.markdown(
                f"<span class='{status_class}'>{item}</span>", unsafe_allow_html=True
            )
        with col2:
            progress = data["current"] / data["original"]
            st.progress(progress)
            st.caption(f"{data['current']} / {data['original']}")
        with col3:
            if st.button(f"Edit {item}"):
                go_to_edit_item(category, item)
                st.rerun()

# --- ITEM EDIT PAGE ---
elif page == "Item":
    category = st.session_state.open_category
    item = st.session_state.edit_item_page

    if not category or not item:
        go_to_inventory()
        st.rerun()

    st.title(f"🔧 Edit: {item}")
    st.caption(f"Category: {category}")

    current = st.session_state.inventory[category][item]["current"]
    original = st.session_state.inventory[category][item]["original"]
    st.markdown(f"**Current stock:** {current} / {original}")

    col1, col2 = st.columns(2)
    with col1:
        add_val = st.number_input("Add units", min_value=0, step=1, key=f"add_{item}")
    with col2:
        remove_val = st.number_input("Remove units", min_value=0, step=1, key=f"remove_{item}")

    # Make sure only one input is active at a time
    if add_val > 0 and remove_val > 0:
        st.warning("You can only add OR remove at a time.")
    elif add_val > 0:
        st.session_state[f"remove_{item}"] = 0
    elif remove_val > 0:
        st.session_state[f"add_{item}"] = 0

    if st.button("✅ Apply Changes"):
        old = current
        if add_val > 0:
            new = min(original, current + add_val)
            action = f"Added {add_val}"
        elif remove_val > 0:
            new = max(0, current - remove_val)
            action = f"Removed {remove_val}"
        else:
            new = current
            action = "No Change"

        st.session_state.inventory[category][item]["current"] = new
        record_change(category, item, old, new, action)

        st.success(f"✔️ {item} updated: {action} | New stock: {new}/{original}")

        # Automatically return to home page
        time.sleep(1.5)
        go_to_inventory()
        st.rerun()

    if st.button("⬅ Cancel"):
        go_to_inventory()
        st.rerun()
# --- VERSION HISTORY PAGE ---
elif page == "History":
    st.title("📜 VERSION HISTORY LOG")

    if st.button("⬅ Back to Main Menu"):
        go_to_inventory()
        st.rerun()

    if not st.session_state.change_log:
        st.info("No changes have been made yet.")
    else:
        for idx, log in enumerate(reversed(st.session_state.change_log), start=1):
            with st.container():
                st.markdown("---")
                st.markdown(
                    f"""
                    <div style='background-color:#0b0c10; padding:1rem; border-radius:10px; border:1px solid #45a29e;'>
                        <h4 style='color:#66fcf1;'>🧾 Log Entry {len(st.session_state.change_log) - idx + 1}</h4>
                        <p><b>Time:</b> {log['timestamp']}</p>
                        <p><b>Category:</b> {log['category']}</p>
                        <p><b>Item:</b> {log['item']}</p>
                        <p><b>Action:</b> {log['action']}</p>
                        <p><b>Old Amount:</b> {log['old_amount']} → <b>New Amount:</b> {log['new_amount']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")
        st.markdown("### ⚙️ Restore Previous State")
        st.caption("Select a log entry number to restore the inventory state before that change.")

        options = list(range(1, len(st.session_state.change_log) + 1))
        restore_index = st.selectbox("Select log entry to restore", options)

        if st.button("♻️ Restore"):
            try:
                # Reverse calculate up to the restore point
                target = len(st.session_state.change_log) - restore_index
                restored_inventory = get_initial_inventory()
                for log in st.session_state.change_log[:target]:
                    cat, item = log["category"], log["item"]
                    if cat in restored_inventory and item in restored_inventory[cat]:
                        restored_inventory[cat][item]["current"] = log["new_amount"]
                st.session_state.inventory = copy.deepcopy(restored_inventory)
                st.success("✅ Inventory restored successfully.")
                time.sleep(1)
                go_to_inventory()
                st.rerun()
            except Exception as e:
                st.error(f"Restoration failed: {e}")

def get_item_class(amount):
    if amount == 0:
        return "critical"
    elif amount <= LOW_STOCK_THRESHOLD:
        return "low-stock"
    return ""
