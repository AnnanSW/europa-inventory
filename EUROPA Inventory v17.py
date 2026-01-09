
# EUROPA INVENTORY SYSTEM — FINALIZED MARS MISSION BUILD
# Crew: 7 | Mission: 650 days | NASA portion sizing | Unified Days Remaining Display

import streamlit as st
import copy
from datetime import datetime
import pandas as pd
import altair as alt
import numpy as np

# --- CONFIGURATION ---
LOW_STOCK_THRESHOLD = 30
WARNING_STOCK_THRESHOLD = 60

# --- MISSION PARAMETERS ---
CREW_SIZE = 7
MISSION_DAYS = 650
REDUNDANCY_FACTOR = 1.30
DAYS_IN_MISSION = int(np.ceil(MISSION_DAYS * REDUNDANCY_FACTOR))

# --- BARCODE MAP (UNCHANGED) ---
BARCODE_MAP = {
    "9313010189018": ("Hydratable Meals", "Beef Stroganoff (Pouch)"),
    "9313010189025": ("Hydratable Meals", "Scrambled Eggs (Powder)"),
    "9313010189032": ("Hydratable Meals", "Cream of Mushroom Soup (Mix)"),
    "9313010189049": ("Hydratable Meals", "Macaroni and Cheese (Dry)"),
    "9313010189056": ("Hydratable Meals", "Asparagus Tips (Dried)"),
    "9313010189063": ("Hydratable Meals", "Grape Drink (Mix)"),
    "9313010189070": ("Hydratable Meals", "Coffee (Mix)"),
    "9313010189087": ("Hydratable Meals", "Chili (Dried)"),
    "9313010189094": ("Hydratable Meals", "Chicken and Rice (Dried)"),
    "9313010189100": ("Hydratable Meals", "Oatmeal with Applesauce (Dry)"),

    "9313010189117": ("Thermostabilized Meals", "Lemon Pepper Tuna (Pouch)"),
    "9313010189124": ("Thermostabilized Meals", "Spicy Green Beans (Pouch)"),
    "9313010189131": ("Thermostabilized Meals", "Pork Chop (Pouch)"),
    "9313010189148": ("Thermostabilized Meals", "Chicken Tacos (Pouch)"),
    "9313010189155": ("Thermostabilized Meals", "Turkey (Pouch)"),
    "9313010189162": ("Thermostabilized Meals", "Brownie (Pouch)"),
    "9313010189179": ("Thermostabilized Meals", "Raspberry Yogurt (Pouch)"),
    "9313010189186": ("Thermostabilized Meals", "Ham Steak (Pouch)"),
    "9313010189193": ("Thermostabilized Meals", "Sausage Patty (Pouch)"),
    "9313010189209": ("Thermostabilized Meals", "Fruit Cocktail (Pouch)"),

    "9313010189216": ("Natural Form & Irradiated", "Pecans (Irradiated)"),
    "9313010189223": ("Natural Form & Irradiated", "Shortbread Cookies"),
    "9313010189230": ("Natural Form & Irradiated", "Crackers"),
    "9313010189247": ("Natural Form & Irradiated", "M&Ms (Candy)"),
    "9313010189254": ("Natural Form & Irradiated", "Tortillas (Packages)"),
    "9313010189261": ("Natural Form & Irradiated", "Dried Apricots"),
    "9313010189278": ("Natural Form & Irradiated", "Dry Roasted Peanuts"),
    "9313010189285": ("Natural Form & Irradiated", "Beef Jerky (Strips)"),
    "9313010189292": ("Natural Form & Irradiated", "Fruit Bar"),
    "9313010189308": ("Natural Form & Irradiated", "Cheese Spread (Tube)"),

    "9313010189315": ("Desserts & Beverages (Non-Mix)", "Space Ice Cream (Freeze-dried)"),
    "9313010189322": ("Desserts & Beverages (Non-Mix)", "Banana Pudding (Pouch)"),
    "9313010189339": ("Desserts & Beverages (Non-Mix)", "Chocolate Pudding (Pouch)"),
    "9313010189346": ("Desserts & Beverages (Non-Mix)", "Apple Sauce (Pouch)"),
    "9313010189353": ("Desserts & Beverages (Non-Mix)", "Orange Juice (Carton)"),
    "9313010189360": ("Desserts & Beverages (Non-Mix)", "Tea Bags (Box)"),
    "9313010189377": ("Desserts & Beverages (Non-Mix)", "Hot Cocoa (Mix)"),
    "9313010189384": ("Desserts & Beverages (Non-Mix)", "Cranberry Sauce (Pouch)"),
    "9313010189391": ("Desserts & Beverages (Non-Mix)", "Strawberry Shake (Mix)"),
    "9313010189407": ("Desserts & Beverages (Non-Mix)", "Dried Peaches"),

    "9313010189414": ("Condiments & Spreads", "Ketchup (Packet)"),
    "9313010189421": ("Condiments & Spreads", "Mustard (Packet)"),
    "9313010189438": ("Condiments & Spreads", "Salt (Packet)"),
    "9313010189445": ("Condiments & Spreads", "Pepper (Packet)"),
    "9313010189452": ("Condiments & Spreads", "Jelly (Packet)"),
    "9313010189469": ("Condiments & Spreads", "Honey (Tube)"),
    "9313010189476": ("Condiments & Spreads", "Hot Sauce (Bottle)"),
    "9313010189483": ("Condiments & Spreads", "Mayonnaise (Packet)"),
    "9313010189490": ("Condiments & Spreads", "Sugar (Packet)"),
    "9313010189506": ("Condiments & Spreads", "Taco Sauce (Packet)"),
}

# --- INVENTORY INITIALIZATION (NASA PORTIONS) ---
def get_initial_inventory():
    MEALS_PER_PERSON_PER_DAY = 3
    total_meals = int(np.ceil(CREW_SIZE * MEALS_PER_PERSON_PER_DAY * MISSION_DAYS * REDUNDANCY_FACTOR))

    MEAL_WEIGHTS = {
        "Hydratable Meals": 1.0,
        "Thermostabilized Meals": 1.0,
        "Natural Form & Irradiated": 0.5,
        "Desserts & Beverages (Non-Mix)": 0.25
    }

    category_multipliers = {
        "Hydratable Meals": [1.2,0.9,1.1,1.0,0.8,1.5,1.8,0.9,1.3,1.0],
        "Thermostabilized Meals": [1.5,1.0,0.9,1.2,0.8,1.4,1.6,0.7,0.6,1.3],
        "Natural Form & Irradiated": [0.8,1.1,2.0,2.5,3.0,1.0,0.9,0.6,1.2,0.7],
        "Desserts & Beverages (Non-Mix)": [0.7,0.8,0.9,1.0,1.5,1.8,1.3,0.6,1.1,0.5]
    }

    category_items = {
        cat: [v[1] for v in BARCODE_MAP.values() if v[0] == cat]
        for cat in category_multipliers
    }

    total_weight = sum(len(items) * MEAL_WEIGHTS[cat] for cat, items in category_items.items())
    base_unit = total_meals / total_weight

    inventory = {}
    for cat, items in category_items.items():
        inventory[cat] = {}
        for name, mult in zip(items, category_multipliers[cat]):
            units = int(np.ceil(base_unit * MEAL_WEIGHTS[cat] * mult))
            inventory[cat][name] = {"current": units, "original": units}

    # Condiments (1 per entrée)
    entree_count = sum(
        inventory[c][i]["original"]
        for c in ["Hydratable Meals", "Thermostabilized Meals"]
        for i in inventory[c]
    )
    condiments = [v[1] for v in BARCODE_MAP.values() if v[0] == "Condiments & Spreads"]
    per_cond = int(np.ceil(entree_count / len(condiments)))

    inventory["Condiments & Spreads"] = {
        name: {"current": per_cond, "original": per_cond} for name in condiments
    }

    return inventory

# --- DASHBOARD DATA (UNIFIED DAYS REMAINING) ---
def create_inventory_dataframe():
    data = []
    total_current = total_original = 0

    for category, items in st.session_state.inventory.items():
        cat_current = sum(i["current"] for i in items.values())
        cat_original = sum(i["original"] for i in items.values())
        total_current += cat_current
        total_original += cat_original

        data.append({
            "Category": category,
            "Current Stock": cat_current,
            "Original Stock": cat_original
        })

    overall_days = int(np.floor(total_current / (total_original / DAYS_IN_MISSION)))
    overall_days_per_crew = overall_days * CREW_SIZE

    for row in data:
        row["Days Remaining"] = overall_days
        row["Days Per Crew Member"] = overall_days_per_crew

    return pd.DataFrame(data), overall_days, overall_days_per_crew

