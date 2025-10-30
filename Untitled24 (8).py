# europa_inventory_nasa_part2_fixed.py (continuation)

# --- PAGE NAVIGATION ---
def go_to_inventory():
    st.session_state.page = "Inventory"
    st.session_state.open_category = None
    st.session_state.edit_item_page = None
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0
    # Reset all clicked flags
    for key in list(st.session_state.keys()):
        if key.startswith("clicked_"):
            st.session_state[key] = False

def go_to_category(category):
    st.session_state.page = "Category"
    st.session_state.open_category = category

def go_to_item(category, item):
    st.session_state.page = "Item"
    st.session_state.edit_item_page = (category, item)
    st.session_state.add_units_edit = 0
    st.session_state.remove_units_edit = 0

def go_to_history():
    st.session_state.page = "History"

# --- DISPLAY FUNCTIONS ---
def display_inventory_page():
    st.title("EUROPA INVENTORY CONTROL PANEL")
    st.subheader("Select a category to view items")
    for category in st.session_state.inventory:
        clicked_key = f"clicked_{category}"
        if st.session_state.get(clicked_key, False) is False:
            if st.button(category):
                st.session_state[clicked_key] = True
                go_to_category(category)
                st.experimental_rerun()
    st.markdown("---")
    if st.session_state.get("clicked_history", False) is False:
        if st.button("View Version History"):
            st.session_state["clicked_history"] = True
            go_to_history()
            st.experimental_rerun()

def display_category_page():
    category = st.session_state.open_category
    st.title(f"EUROPA: {category.upper()}")
    if st.button("Back", on_click=go_to_inventory):
        st.experimental_rerun()
    st.markdown("---")
    items = st.session_state.inventory[category]
    for item_name, data in items.items():
        color = get_item_color(data["current"])
        st.markdown(f"**{item_name}**  —  Current: {data['current']} / Original: {data['original']}")
        st.progress(data["current"] / data["original"])
        clicked_key = f"clicked_{category}_{item_name}"
        if st.session_state.get(clicked_key, False) is False:
            if st.button(f"Edit {item_name}", key=item_name):
                st.session_state[clicked_key] = True
                go_to_item(category, item_name)
                st.experimental_rerun()

def display_item_page():
    category, item = st.session_state.edit_item_page
    data = st.session_state.inventory[category][item]
    st.title(f"{item.upper()}")
    if st.button("Back", on_click=lambda: go_to_category(category)):
        st.experimental_rerun()
    st.markdown(f"Original: {data['original']}  |  Current: {data['current']}")
    st.progress(data["current"] / data["original"])
    st.markdown("---")
    add_col, remove_col, apply_col = st.columns([1,1,1])
    with add_col:
        add_val = st.number_input("Add Units", min_value=0, value=st.session_state.add_units_edit, key="add_input")
        if add_val > 0:
            st.session_state.remove_units_edit = 0
    with remove_col:
        remove_val = st.number_input("Remove Units", min_value=0, value=st.session_state.remove_units_edit, key="remove_input")
        if remove_val > 0:
            st.session_state.add_units_edit = 0
    with apply_col:
        if st.button("Apply Changes"):
            new_amount = data["current"] + add_val - remove_val
            if new_amount > data["original"]:
                st.error("Cannot exceed original capacity!")
            elif new_amount < 0:
                st.error("Cannot go below zero!")
            else:
                old = data["current"]
                data["current"] = new_amount
                if add_val > 0:
                    record_change(category, item, old, new_amount, "add")
                elif remove_val > 0:
                    record_change(category, item, old, new_amount, "remove")
                st.session_state.add_units_edit = 0
                st.session_state.remove_units_edit = 0
                st.experimental_rerun()

def display_history_page():
    st.title("EUROPA: VERSION HISTORY")
    if st.button("Back", on_click=go_to_inventory):
        st.experimental_rerun()
    st.markdown("---")
    log = st.session_state.change_log
    if not log:
        st.info("No changes recorded yet.")
        return
    for entry in reversed(log):
        st.markdown(f"**V{entry['version_id']}** | {entry['timestamp']} | {entry['category']} | {entry['item']} | {entry['action']} | {entry['old_amount']} → {entry['new_amount']}")
        clicked_key = f"clicked_restore_{entry['version_id']}"
        if st.session_state.get(clicked_key, False) is False:
            if "RESTORATION" not in entry["action"]:
                if st.button(f"Restore to V{entry['version_id']}", key=f"restore{entry['version_id']}"):
                    st.session_state[clicked_key] = True
                    revert_version(entry['version_id'])
                    st.experimental_rerun()
# europa_inventory_nasa_part2_fixed_cont.py

# --- MAIN APP RENDERING ---
page = st.session_state.get("page", "Inventory")

if page == "Inventory":
    display_inventory_page()

elif page == "Category":
    display_category_page()

elif page == "Item":
    display_item_page()

elif page == "History":
    display_history_page()

# --- THEMING & VISUALS ---
st.markdown(
    """
    <style>
    body {
        background-color: #0B1D51; /* NASA dark blue background */
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }
    .stButton>button {
        background-color: #1C3FAA;
        color: #fff;
        font-weight: bold;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #3B63D3;
        color: #ffffff;
    }
    .stProgress>div>div>div>div {
        background-color: #0cf;
    }
    .stNumberInput>div>input {
        background-color: #001f3f;
        color: #0cf;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)
