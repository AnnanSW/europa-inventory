# ===============================
# EUROPA INVENTORY — FLIGHT-GRADE
# ===============================

import streamlit as st
import copy
from datetime import datetime
import pandas as pd
import altair as alt
import numpy as np
from collections import defaultdict

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
LOW_STOCK_THRESHOLD = 30
WARNING_STOCK_THRESHOLD = 60

CREW_SIZE = 7
MISSION_DAYS = 1035
REDUNDANCY_FACTOR = 1.30
DAYS_IN_MISSION = int(np.ceil(MISSION_DAYS * REDUNDANCY_FACTOR))

OVER_TOLERANCE = 0.02     # +2%
UNDER_TOLERANCE = -0.15  # -15%

# -------------------------------------------------
# INITIAL INVENTORY (UNCHANGED)
# -------------------------------------------------
# Uses your existing get_initial_inventory()
# (function unchanged, omitted here for brevity)
# -------------------------------------------------

# ⚠️ KEEP YOUR EXISTING get_initial_inventory()
# ⚠️ KEEP BARCODE_MAP, ICON_MAP, CSS, DASHBOARD CODE
# Nothing above this point changes

# -------------------------------------------------
# SESSION STATE INIT (FIXED + CLEAN)
# -------------------------------------------------
if "inventory" not in st.session_state:
    st.session_state.inventory = get_initial_inventory()

if "change_log" not in st.session_state:
    st.session_state.change_log = [{
        "version_id": 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": "SYSTEM",
        "item": "INITIAL_LOAD",
        "delta": None,
        "snapshot": copy.deepcopy(st.session_state.inventory),
        "mission_day": 1
    }]

if "page" not in st.session_state:
    st.session_state.page = "Inventory"

# -------------------------------------------------
# VERSION / SNAPSHOT LOGIC (AUTHORITATIVE)
# -------------------------------------------------
def record_version(category, item, delta):
    st.session_state.change_log.append({
        "version_id": len(st.session_state.change_log) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "item": item,
        "delta": delta,
        "snapshot": copy.deepcopy(st.session_state.inventory),
        "mission_day": st.session_state.change_log[-1]["mission_day"]
    })

def restore_version(version_id):
    entry = next(v for v in st.session_state.change_log if v["version_id"] == version_id)
    st.session_state.inventory = copy.deepcopy(entry["snapshot"])
    record_version("SYSTEM", f"RESTORED → V{version_id}", None)

# -------------------------------------------------
# DAILY SNAPSHOT + CONSUMPTION MATH
# -------------------------------------------------
def daily_inventory_snapshots():
    snaps = {}
    for v in st.session_state.change_log:
        snaps[v["mission_day"]] = v["snapshot"]
    return snaps

def predicted_units_per_day_by_category():
    predicted = {}
    for cat, items in st.session_state.inventory.items():
        if cat == "Condiments & Spreads":
            continue
        original = sum(i["original"] for i in items.values())
        predicted[cat] = original / DAYS_IN_MISSION
    return predicted

def actual_daily_usage():
    snaps = daily_inventory_snapshots()
    days = sorted(snaps.keys())
    usage = {}

    for i in range(1, len(days)):
        prev = snaps[days[i - 1]]
        curr = snaps[days[i]]
        day_use = defaultdict(int)

        for cat in prev:
            for item in prev[cat]:
                delta = prev[cat][item]["current"] - curr[cat][item]["current"]
                if delta > 0:
                    day_use[cat] += delta

        usage[days[i]] = day_use
    return usage

# -------------------------------------------------
# HISTORY / CONSUMPTION PAGE (REPLACED)
# -------------------------------------------------
def history_page():
    st.markdown("<h1>📊 Consumption Rates & Change Log</h1>", unsafe_allow_html=True)
    st.button("⬅ Back to Inventory", on_click=lambda: setattr(st.session_state, "page", "Inventory"))
    st.markdown("<hr>", unsafe_allow_html=True)

    predicted = predicted_units_per_day_by_category()
    actual = actual_daily_usage()

    with st.expander("ℹ️ Predicted Units Per Day (Crew Total)", expanded=False):
        for cat, val in predicted.items():
            st.write(f"**{cat}:** {val:.1f} units/day")

    day_groups = defaultdict(list)
    for v in st.session_state.change_log:
        day_groups[v["mission_day"]].append(v)

    for day in sorted(day_groups.keys(), reverse=True):
        used = actual.get(day, {})
        st.markdown(f"<h3>Mission Day {day}</h3>", unsafe_allow_html=True)

        msgs = []
        flags = []

        for cat, pred in predicted.items():
            used_units = used.get(cat, 0)
            delta = used_units - pred
            pct = delta / pred if pred else 0

            msgs.append(f"{cat}: {delta:+.1f} units ({pct:+.1%})")

            if pct > OVER_TOLERANCE:
                flags.append("OVER")
            elif pct < UNDER_TOLERANCE:
                flags.append("UNDER")

        if "OVER" in flags:
            st.error("🚨 Rations exceeded\n" + "\n".join(msgs))
        elif "UNDER" in flags:
            st.warning("⚠️ Rations underused\n" + "\n".join(msgs))
        else:
            st.success("✅ Consumption within predicted range\n" + "\n".join(msgs))

        for v in reversed(day_groups[day]):
            delta = f"{v['delta']:+}" if isinstance(v["delta"], int) else ""
            label = f"V{v['version_id']} | {v['timestamp']} | {v['category']} > {v['item']} {delta}"
            if st.button(label, key=f"restore_{v['version_id']}"):
                restore_version(v["version_id"])
                st.experimental_rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

# -------------------------------------------------
# MAIN APP SWITCH
# -------------------------------------------------
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
