
import streamlit as st
from datetime import datetime
import copy

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 10
FUZZY_TOLERANCE = 2

# --- Initial Data ---
def _get_initial_data():
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

# --- Session State Setup ---
if "inventory" not in st.session_state:
    st.session_state.inventory = _get_initial_data()
if "change_log" not in st.session_state:
    st.session_state.change_log = []

# --- Utility functions ---
def is_fuzzy_match(item_name_lower, search_term_lower):
    n = len(search_term_lower)
    m = len(item_name_lower)
    if n == 0:
        return True
    for i in range(m - n + 1):
        substring = item_name_lower[i : i + n]
        mismatches = sum(1 for j in range(n) if substring[j] != search_term_lower[j])
        if mismatches <= FUZZY_TOLERANCE:
            return True
    return False

def record_change(category, item, old_amount, new_amount, action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state_before_change = copy.deepcopy(st.session_state.inventory)
    entry = {
        "version_id": len(st.session_state.change_log) + 1,
        "timestamp": timestamp,
        "category": category,
        "item": item,
        "action": action,
        "change_amount": abs(new_amount - old_amount),
        "old_amount": old_amount,
        "new_amount": new_amount,
        "state_before_change": state_before_change
    }
    st.session_state.change_log.append(entry)

def record_reversion(reverted_to_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state_before_change = copy.deepcopy(st.session_state.inventory)
    entry = {
        "version_id": len(st.session_state.change_log) + 1,
        "timestamp": timestamp,
        "category": "SYSTEM",
        "item": "INVENTORY_WIDE",
        "action": f"RESTORATION_TO_V{reverted_to_id}",
        "change_amount": 0,
        "old_amount": "N/A",
        "new_amount": "N/A",
        "state_before_change": state_before_change
    }
    st.session_state.change_log.append(entry)

def revert_version(version_id):
    try:
        restored_state = copy.deepcopy(st.session_state.change_log[version_id - 1]["state_before_change"])
        st.session_state.inventory = restored_state
        record_reversion(version_id)
        return True
    except Exception as e:
        return False

# --- Streamlit App Layout ---
st.set_page_config(page_title="Europa Inventory", layout="wide")
st.title("EUROPA Inventory System")
st.markdown("Web conversion of the CLI inventory manager with fuzzy search and versioned change log.")

col1, col2 = st.columns([1,3])

with col1:
    st.header("Navigation")
    nav = st.radio("Choose view:", ("Categories", "Search", "Change Log / Restore"), index=0)
    st.markdown("---")
    st.write("Low stock threshold:", LOW_STOCK_THRESHOLD)
    if st.button("Reset Session (fresh inventory)"):
        st.session_state.inventory = _get_initial_data()
        st.session_state.change_log = []
        st.success("Session reset. Inventory restored to initial values.")

# --- Categories view ---
if nav == "Categories":
    st.subheader("Categories")
    inventory = st.session_state.inventory
    for cat in inventory:
        items = inventory[cat]
        total_current = sum(d["current"] for d in items.values())
        depleted = total_current == 0
        low = any(0 < d["current"] <= LOW_STOCK_THRESHOLD for d in items.values())
        badge = "✅" if not low and not depleted else ("⚠️ Low" if low else "🛑 Depleted")
        with st.expander(f"{cat} — {badge}", expanded=False):
            for item_name, d in items.items():
                cols = st.columns([3,1,1])
                cols[0].write(item_name)
                cols[1].write(f"{d['current']} units")
                modify = cols[2].radio("Action", ("-", "Add", "Remove"), key=f"{cat}_{item_name}_action")
                if modify != "-":
                    amount = cols[2].number_input("Qty", min_value=1, value=1, key=f"{cat}_{item_name}_amt")
                    if cols[2].button("Apply", key=f"{cat}_{item_name}_apply"):
                        old = d["current"]
                        if modify == "Add":
                            new = old + amount
                            if new > d["original"]:
                                st.warning(f"Cannot exceed original amount ({d['original']}). Change ignored.")
                            else:
                                record_change(cat, item_name, old, new, "add")
                                st.session_state.inventory[cat][item_name]["current"] = new
                                st.success(f"Added {amount} to {item_name}. New: {new}")
                        else:
                            new = old - amount
                            if new < 0:
                                st.warning("Cannot go below zero. Change ignored.")
                            else:
                                record_change(cat, item_name, old, new, "remove")
                                st.session_state.inventory[cat][item_name]["current"] = new
                                if new > 0 and new <= LOW_STOCK_THRESHOLD:
                                    st.warning(f"Low stock: {new} units remaining (threshold {LOW_STOCK_THRESHOLD}).")
                                if new == 0:
                                    st.error(f"{item_name} is now depleted.")
                                st.success(f"Removed {amount} from {item_name}. New: {new}")

# --- Search view ---
elif nav == "Search":
    st.subheader("Typo-tolerant Search")
    term = st.text_input("Search term (leave empty to show all)", value="")
    results = []
    for cat, items in st.session_state.inventory.items():
        for item_name, d in items.items():
            if is_fuzzy_match(item_name.lower(), term.lower()):
                results.append((cat, item_name, d))
    st.write(f"{len(results)} results")
    for i, (cat, item_name, d) in enumerate(results, start=1):
        cols = st.columns([3,1,1])
        cols[0].write(f"{i}. {item_name} ({cat})")
        cols[1].write(f"{d['current']}")
        if cols[2].button("Modify", key=f"search_mod_{i}"):
            st.session_state["_modify_target"] = (cat, item_name)
            st.experimental_rerun()

    if "_modify_target" in st.session_state:
        cat, item_name = st.session_state["_modify_target"]
        st.info(f"Modifying {item_name} in {cat}")
        d = st.session_state.inventory[cat][item_name]
        colA, colB = st.columns(2)
        with colA:
            amt = st.number_input("Amount", min_value=1, value=1, key="search_amt")
            act = st.selectbox("Action", ("Add", "Remove"), key="search_act")
            if st.button("Apply change (search view)"):
                old = d["current"]
                if act == "Add":
                    new = old + amt
                    if new > d["original"]:
                        st.warning("Cannot exceed original amount.")
                    else:
                        record_change(cat, item_name, old, new, "add")
                        st.session_state.inventory[cat][item_name]["current"] = new
                        st.success("Change applied.")
                        del st.session_state["_modify_target"]
                        st.experimental_rerun()
                else:
                    new = old - amt
                    if new < 0:
                        st.warning("Cannot go below zero.")
                    else:
                        record_change(cat, item_name, old, new, "remove")
                        st.session_state.inventory[cat][item_name]["current"] = new
                        st.success("Change applied.")
                        del st.session_state["_modify_target"]
                        st.experimental_rerun()

# --- Change Log / Restore view ---
else:
    st.subheader("Change Log / Restore")
    log = st.session_state.change_log
    if not log:
        st.info("No changes recorded in this session yet.")
    else:
        for entry in reversed(log):
            if entry["action"].startswith("RESTORATION"):
                st.write(f"V{entry['version_id']} | {entry['timestamp']} | SYSTEM: {entry['action']}")
            else:
                sign = "-" if entry["action"]=="remove" else "+"
                st.write(f"V{entry['version_id']} | {entry['timestamp']} | {entry['item']} | {sign}{entry['change_amount']} ({entry['old_amount']} -> {entry['new_amount']})")
        st.markdown("---")
        st.write("Restore: select a version ID to restore to the state *before* that version was applied.")
        vid = st.number_input("Version ID to restore to (e.g., 5)", min_value=1, max_value=max(1, len(log)), value=1, step=1)
        if st.button("Restore to selected version"):
            if 1 <= vid <= len(log):
                if revert_version(vid):
                    st.success(f"Restored to state before V{vid}. Restoration recorded.")
                else:
                    st.error("Restore failed. Check version ID.")
    st.markdown("---")
    if st.button("Export current inventory to clipboard (CSV)"):
        import pandas as pd
        rows = []
        for cat, items in st.session_state.inventory.items():
            for name, d in items.items():
                rows.append({"category":cat, "item":name, "current":d["current"], "original":d["original"]})
        df = pd.DataFrame(rows)
        st.experimental_set_query_params()  # placeholder to allow clipboard in some environments
        st.write(df)

st.sidebar.write("Session changes:", len(st.session_state.change_log))
