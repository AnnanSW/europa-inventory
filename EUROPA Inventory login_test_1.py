import streamlit as st
import copy
from datetime import datetime
import pandas as pd
import altair as alt
import numpy as np

# ==============================
# CREW ACCOUNTS
# ==============================
CREW_ACCOUNTS = {
    "alex": {
        "password": "1234",
        "daily_needs": {"meals": 3, "snacks": 1.5, "desserts": 10},
        "notifications": []
    },
    "sam": {
        "password": "1234",
        "daily_needs": {"meals": 3, "snacks": 1.2, "desserts": 8},
        "notifications": []
    },
    "riley": {
        "password": "1234",
        "daily_needs": {"meals": 2.8, "snacks": 1.5, "desserts": 9},
        "notifications": []
    }
}

# ==============================
# CONFIG
# ==============================
MISSION_DAYS = 1035
REDUNDANCY_FACTOR = 1.3
MISSION_START_DATE = datetime.strptime("2026-01-01", "%Y-%m-%d")

# ==============================
# SESSION STATE
# ==============================
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "inventory" not in st.session_state:
    st.session_state.inventory = {}

if "page" not in st.session_state:
    st.session_state.page = "Login"

if "change_log" not in st.session_state:
    st.session_state.change_log = []

if "edit_item" not in st.session_state:
    st.session_state.edit_item = None

if "target_user" not in st.session_state:
    st.session_state.target_user = None

# ==============================
# INVENTORY INIT (BASED ON USERS)
# ==============================
def init_inventory():
    total_meals = sum(u["daily_needs"]["meals"] for u in CREW_ACCOUNTS.values()) * MISSION_DAYS * REDUNDANCY_FACTOR
    total_snacks = sum(u["daily_needs"]["snacks"] for u in CREW_ACCOUNTS.values()) * MISSION_DAYS * REDUNDANCY_FACTOR
    total_desserts = sum(u["daily_needs"]["desserts"] for u in CREW_ACCOUNTS.values()) * MISSION_DAYS * REDUNDANCY_FACTOR

    return {
        "Meals": {f"Meal {i}": {"current": int(total_meals/10), "original": int(total_meals/10)} for i in range(10)},
        "Snacks": {f"Snack {i}": {"current": int(total_snacks/10), "original": int(total_snacks/10)} for i in range(10)},
        "Desserts": {f"Dessert {i}": {"current": int(total_desserts/10), "original": int(total_desserts/10)} for i in range(10)},
    }

if not st.session_state.inventory:
    st.session_state.inventory = init_inventory()

# ==============================
# LOGIN
# ==============================
def login_page():
    st.title("🚀 Crew Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in CREW_ACCOUNTS and CREW_ACCOUNTS[u]["password"] == p:
            st.session_state.current_user = u
            st.session_state.page = "Inventory"
            st.rerun()
        else:
            st.error("Invalid login")

# ==============================
# SIDEBAR
# ==============================
def sidebar():
    if st.session_state.current_user:
        st.sidebar.write(f"👤 {st.session_state.current_user}")

        if st.sidebar.button("Inventory"):
            st.session_state.page = "Inventory"

        if st.sidebar.button("Dashboard"):
            st.session_state.page = "Dashboard"

        if st.sidebar.button("History"):
            st.session_state.page = "History"

        if st.sidebar.button("Logout"):
            st.session_state.current_user = None
            st.session_state.page = "Login"
            st.rerun()

# ==============================
# NOTIFICATIONS
# ==============================
def show_notifications():
    user = st.session_state.current_user
    notes = CREW_ACCOUNTS[user]["notifications"]

    if notes:
        st.warning("📩 Notifications")
        for n in notes:
            st.write("-", n)

        if st.button("Clear"):
            CREW_ACCOUNTS[user]["notifications"] = []

# ==============================
# RECORD CHANGE
# ==============================
def record_change(cat, item, old, new):
    user = st.session_state.current_user
    target = st.session_state.target_user or user

    st.session_state.inventory[cat][item]["current"] = new

    st.session_state.change_log.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cat": cat,
        "item": item,
        "old": old,
        "new": new,
        "by": user,
        "for": target
    })

    if target != user:
        CREW_ACCOUNTS[target]["notifications"].append(
            f"{user} took {item} for you"
        )

# ==============================
# INVENTORY PAGE
# ==============================
def inventory_page():
    st.title("📦 Inventory")

    if not st.session_state.current_user:
        st.warning("View only mode")

    for cat, items in st.session_state.inventory.items():
        st.subheader(cat)

        for name, data in items.items():
            if st.button(f"{name} ({data['current']})"):
                if st.session_state.current_user:
                    st.session_state.edit_item = (cat, name)
                    st.session_state.page = "Edit"
                    st.rerun()

# ==============================
# EDIT PAGE
# ==============================
def edit_page():
    if not st.session_state.current_user:
        st.error("Login required")
        return

    cat, item = st.session_state.edit_item
    data = st.session_state.inventory[cat][item]

    st.title(item)
    st.write("Current:", data["current"])

    target = st.selectbox("Who is this for?", list(CREW_ACCOUNTS.keys()))
    st.session_state.target_user = target

    add = st.number_input("Add", 0)
    remove = st.number_input("Remove", 0)

    if st.button("Apply"):
        new = data["current"] + add - remove

        if new >= 0:
            record_change(cat, item, data["current"], new)
            st.success("Updated")
            st.session_state.page = "Inventory"
            st.rerun()
        else:
            st.error("Cannot go below zero")

# ==============================
# DASHBOARD
# ==============================
def dashboard():
    st.title("📊 Dashboard")

    if st.session_state.current_user:
        mode = st.radio("Mode", ["Crew", "Personal"])
    else:
        mode = "Crew"

    if mode == "Crew":
        total = sum(
            item["current"]
            for cat in st.session_state.inventory.values()
            for item in cat.values()
        )
        st.metric("Total Units", total)

    else:
        user = st.session_state.current_user

        consumed = sum(
            (log["old"] - log["new"])
            for log in st.session_state.change_log
            if log["for"] == user
        )

        expected = CREW_ACCOUNTS[user]["daily_needs"]["meals"] * 30

        st.metric("Consumed", consumed)
        st.metric("Expected (30d)", expected)
        st.metric("Difference", consumed - expected)

# ==============================
# HISTORY
# ==============================
def history():
    st.title("📜 History")

    for log in reversed(st.session_state.change_log):
        st.write(
            f"{log['time']} | {log['by']} → {log['for']} | "
            f"{log['item']} ({log['old']} → {log['new']})"
        )

# ==============================
# MAIN ROUTER
# ==============================
sidebar()

if st.session_state.current_user:
    show_notifications()

if st.session_state.page == "Login":
    login_page()

elif st.session_state.page == "Inventory":
    inventory_page()

elif st.session_state.page == "Edit":
    edit_page()

elif st.session_state.page == "Dashboard":
    dashboard()

elif st.session_state.page == "History":
    history()