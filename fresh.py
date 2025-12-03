import io
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

import requests
from datetime import datetime, timedelta

import json
import altair as alt

# =========================
# Basic page config
# =========================
st.set_page_config(
    page_title="FRESH Smart Pantry",
    page_icon="🥫",
    layout="wide",
)

# =========================
# login system 
# =========================

# Hard-coded demo users 
VALID_USERS = {
    "fresh": "fresh2025",
    "demo": "demo123",
}

# Initialize login state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# If not logged in, show login page and stop
if not st.session_state["logged_in"]:
    st.markdown(
        "<h1 style='text-align:center; margin-top:40px;'>FRESH Login</h1>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Sign In")

        if login_btn:
            if username in VALID_USERS and password == VALID_USERS[username]:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.stop() 

# =========================
# CSS: Theme & components
# =========================
FRESH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Poppins:wght@500;600;700;800&display=swap');

/* === Global app background & base font === */
.stApp {
  font-family: "Inter", sans-serif !important;
  background: radial-gradient(circle at top left, #e0f7fa 0%, #e8fff3 45%, #ffffff 100%) !important;
  color: #0a3d3f !important;
}

/* === Login card container === */
.login-card {
  background: rgba(255,255,255,0.96);
  border-radius: 20px;
  padding: 24px 28px;
  border: 1px solid rgba(148, 163, 184, 0.4);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.10);
}

/* === Top summary header card === */
.top-card {
  background: linear-gradient(120deg, #ecfdf5 0%, #e0f2fe 55%, #ffffff 100%);
  border-radius: 24px;
  padding: 18px 22px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(56, 189, 248, 0.35);
  box-shadow: 0 4px 14px rgba(15, 118, 110, 0.08);
}

/* FRESH logo text */
.fresh-logo {
  font-family: "Poppins", sans-serif !important;
  font-size: 52px !important;
  font-weight: 800 !important;
  letter-spacing: 1px;
  background: linear-gradient(92deg, #16a34a 0%, #22c55e 35%, #0ea5e9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow:
    0 2px 6px rgba(16, 185, 129, 0.2),
    0 4px 12px rgba(59, 130, 246, 0.15);
  padding-bottom: 4px;
}

/* Subtitle under FRESH logo */
.top-subtitle {
  margin-top: 4px;
  font-size: 14px;
  color: #3b5756;
}

/* Right side of header: date & pills */
.top-right {
  text-align: right;
  font-size: 14px;
  color: #0f172a;
}

.top-pill-row {
  margin-top: 6px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.top-pill {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.1);
  color: #047857;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(52, 211, 153, 0.5);
}

/* === Page- and section-level titles === */
.page-title {
  font-family: "Poppins", sans-serif !important;
  font-size: 2.4rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.04em;
  color: #0f3d3e !important;
  margin-top: 24px !important;
  margin-bottom: 10px !important;
  text-shadow: 0 1px 3px rgba(15, 23, 42, 0.10);
}

.section-title {
  font-family: "Poppins", sans-serif !important;
  font-size: 1.6rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em;
  color: #0f3d3e !important;
  margin-top: 22px !important;
  margin-bottom: 8px !important;
}

/* Subtle helper text */
.subtle {
  color: #3b5756 !important;
  font-size: 0.9rem;
}

/* === Generic content cards (highlights / recipes) === */
.block {
  background: rgba(255, 255, 255, 0.96);
  border-radius: 18px;
  padding: 18px 20px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.06);
  transition: 0.18s ease-out;
}

.block:hover {
  border-color: rgba(16, 185, 129, 0.8);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.10);
  transform: translateY(-1px);
}

/* Card headline text (Milk / Apple / recipe title) */
.card-title {
  font-family: "Poppins", sans-serif !important;
  font-size: 1.7rem;
  font-weight: 700;
  color: #0f3d3e;
}

/* Small badges / chips */
.badge {
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(209, 250, 229, 0.9);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #05603a;
  font-size: 11px;
  font-weight: 500;
}

/* === Gradient button style (for .btn links) === */
.btn {
  padding: 10px 14px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(90deg, #34d399 0%, #22c55e 100%);
  color: #ffffff;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 3px 8px rgba(22, 163, 74, 0.35);
  transition: 0.2s;
}

.btn:hover {
  background: linear-gradient(90deg, #16a34a 0%, #059669 100%);
  box-shadow: 0 5px 14px rgba(21, 128, 61, 0.5);
  transform: translateY(-1px);
}

/* === DataFrame table shell === */
[data-testid="stDataFrame"] {
  background-color: #ffffff !important;
  border-radius: 14px !important;
}

/* Stronger header background for AG Grid */
[data-testid="stDataFrame"] .st-ag-theme-streamlit .ag-header {
  background-color: #e0f2fe !important;
}

/* Header text style for AG Grid */
[data-testid="stDataFrame"] .st-ag-theme-streamlit .ag-header-cell-text {
  color: #0f3d3e !important;
  font-weight: 600 !important;
}

/* Rounder table container */
[data-testid="stDataFrame"] .st-ag-theme-streamlit {
  border-radius: 14px !important;
  overflow: hidden !important;
}

/* Slightly tighter number input padding */
.stNumberInput > div > input {
  padding-top: 4px !important;
  padding-bottom: 4px !important;
}

</style>
"""
st.markdown(FRESH_CSS, unsafe_allow_html=True)

SPOONACULAR_API_KEY = "f6fe73660fae4273ba25c44ec8c126be"

@st.cache_data(ttl=60 * 60 * 12)
def fetch_recipes_safe(ingredients, n=3):
    """Safe Recipe Fetching with Free Tier Limits."""
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "ingredients": ",".join(ingredients),
        "number": n,
        "ranking": 1,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

USDA_API_KEY = "hlInVRCOG7dXLKYyJVJ6h9lODdrT6QSUyJDXcQrA"

def fetch_nutrition(food_name: str):
    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={USDA_API_KEY}&query={food_name}"
    search_res = requests.get(search_url, timeout=10)
    if search_res.status_code != 200:
        return None

    search_data = search_res.json()
    if "foods" not in search_data or len(search_data["foods"]) == 0:
        return None

    fdc_id = search_data["foods"][0]["fdcId"]
    detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={USDA_API_KEY}"
    detail_res = requests.get(detail_url, timeout=10)
    if detail_res.status_code != 200:
        return None

    detail_data = detail_res.json()

    calories = 0
    protein = 0
    weight_g = detail_data.get("servingSize", 100)

    for nutrient in detail_data.get("foodNutrients", []):
        name = nutrient.get("nutrient", {}).get("name", "")
        amount = nutrient.get("amount", 0)
        if "Energy" in name and nutrient["nutrient"]["unitName"].lower() == "kcal":
            calories = amount
        if "Protein" in name:
            protein = amount

    return {
        "calories": calories,
        "protein": protein,
        "weight_g": weight_g,
    }

# =========================
# Data helpers
# =========================
REQUIRED_COLS = ["Food_Name", "Expiration_Date", "Calories", "Protein", "Weight_g", "Quantity", "Category"]

@st.cache_data(show_spinner=False)
def load_csv(source: str | io.BytesIO) -> pd.DataFrame:
    """Load and clean a CSV from path/URL or uploaded file."""
    if isinstance(source, io.BytesIO):
        df = pd.read_csv(source)
    else:
        df = pd.read_csv(source)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()
    df["Food_Name"] = df["Food_Name"].astype(str).str.strip()
    df["Category"] = df["Category"].astype(str).str.strip()

    df["Expiration_Date"] = pd.to_datetime(df["Expiration_Date"], errors="coerce")
    df = df.dropna(subset=["Expiration_Date"])

    for col in ["Calories", "Protein", "Weight_g", "Quantity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    today = pd.Timestamp(datetime.now().date())
    df["Days_Left"] = (df["Expiration_Date"] - today).dt.days

    return df

@st.cache_data(show_spinner=False)
def example_df() -> pd.DataFrame:
    csv = io.StringIO(
    """Food_Name,Expiration_Date,Calories,Protein,Weight_g,Quantity,Category
Milk,2025-12-08,120,8,240,1,Dairy
Apple,2025-12-10,95,0.5,182,3,Fruit
Yogurt,2025-12-12,80,5,150,2,Dairy
Spinach,2025-12-05,23,3,85,1,Vegetable
Chicken Breast,2025-12-07,165,31,120,2,Meat
Tofu,2025-12-06,76,8,100,1,Protein
Eggs,2025-12-11,70,6,50,12,Protein
Bread,2025-12-09,250,9,500,1,Grain
"""
)
    return load_csv(io.BytesIO(csv.getvalue().encode()))

# =========================
# Charts with Altair
# =========================
def pretty_bar_chart(df, x_col, y_col, title, y_title, color):
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X(x_col, sort="-y", axis=alt.Axis(labelAngle=0, title="Category")),
            y=alt.Y(y_col, axis=alt.Axis(title=y_title)),
            tooltip=[x_col, y_col],
            color=alt.value(color),
        )
        .properties(title=title, height=260)
        .configure_title(fontSize=18, anchor="start", color="#065f46", font="Helvetica Neue")
        .configure_axis(labelColor="#4b5563", titleColor="#4b5563", grid=False)
        .configure_view(strokeWidth=0)
    )
    return chart

# =========================
# Sidebar: navigation + data source + logout
# =========================
with st.sidebar:
    st.markdown("### 🥫 FRESH")
    st.markdown(f"👤 **User:** {st.session_state['username']}")
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

    mode = st.radio(
        "Navigation",
        ["Dashboard", "Recipes", "Add Food"],
        index=0,
    )

    st.markdown("---")
    st.markdown("#### Data source")

    use_example = st.checkbox("Use example dataset", value=True)

    url = st.text_input(
        "CSV URL (optional)",
        placeholder="https://raw.githubusercontent.com/<user>/<repo>/<branch>/data.csv",
    )

    uploaded = st.file_uploader("Upload CSV", type=["csv"])

try:
    if uploaded is not None:
        df = load_csv(uploaded)
        source_label = f"Uploaded: {uploaded.name}"
    elif url and urlparse(url).scheme in {"http", "https"}:
        df = load_csv(url)
        source_label = "Loaded from URL"
    elif use_example:
        df = example_df()
        source_label = "Example dataset"
    else:
        df = example_df()
        source_label = "Example dataset (default)"
except Exception as e:
    st.sidebar.error(f"Failed to load data: {e}")
    df = example_df()
    source_label = "Example dataset (fallback)"

st.sidebar.markdown(f"**Loaded:** {source_label}")

# Ensure df is not empty
if df.empty:
    st.error("No valid data loaded. Please check your CSV.")
    st.stop()

# =========================
# Initialize session inventory
# =========================
if "inventory_df" not in st.session_state:
    st.session_state["inventory_df"] = df.copy()

# Use the session-level inventory
df = st.session_state["inventory_df"]

# =========================
# Top header summary
# =========================
total_items = len(df)
expiring_3 = int((df["Days_Left"] <= 3).sum())

st.markdown(
    f"""
<div class="top-card" style="margin-bottom: 16px;">
  <div>
    <div class="fresh-logo">FRESH</div>
    <div class="top-subtitle">
      Smart fridge inventory manager · Track freshness, reduce waste, save what you love
    </div>
  </div>
  <div class="top-right">
    <div>Today: {datetime.now().date()}</div>
    <div class="top-pill-row">
      <span class="top-pill">{total_items} items</span>
      <span class="top-pill">{expiring_3} expiring ≤ 3 days</span>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
# =========================
# Mode: Dashboard
# =========================
if mode == "Dashboard":
    st.markdown('<h2 class="page-title">Dashboard</h2>', unsafe_allow_html=True)

    # Highlight the top 3 items with least days left
    soon_items = (
      df.sort_values("Days_Left", ascending=True)
        .head(3)       # ⬅️ 只取前三名
     )

    for _, row in soon_items.iterrows():
      name = row["Food_Name"]
      days = int(row["Days_Left"])

      st.markdown(
        f"""
    <div class="block" style="margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
     <div class="card-title" style="font-size:20px;">{name}</div>
     <div class="subtle">{days} days left</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    # KPI metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items", f"{total_items:,}")
    col2.metric("Expiring ≤ 3 days", f"{expiring_3:,}")
    avg_cal = round(df["Calories"].mean(), 1) if not df.empty else 0
    col3.metric("Avg Calories", f"{avg_cal}")
    low_stock = int((df["Quantity"] <= 1).sum())
    col4.metric("Low stock (≤ 1)", f"{low_stock:,}")

    # Nutrition overview charts
    st.markdown("### Nutrition Overview")

    # Aggregate data for charts
    cat_agg = (
        df.groupby("Category", as_index=False)["Calories"]
        .sum()
        .sort_values("Calories", ascending=False)
    )

    protein_agg = (
        df.groupby("Category", as_index=False)["Protein"]
        .sum()
        .sort_values("Protein", ascending=False)
    )

    col_cal, col_pro = st.columns(2)

    with col_cal:
        if not cat_agg.empty:
            cal_chart = pretty_bar_chart(
                cat_agg,
                x_col="Category",
                y_col="Calories",
                title="Calories by Category",
                y_title="Calories (kcal)",
                color="#38bdf8",  # 蓝色
            )
            st.altair_chart(cal_chart, use_container_width=True)
        else:
            st.info("No data for calories chart.")

    with col_pro:
        if not protein_agg.empty:
            pro_chart = pretty_bar_chart(
                protein_agg,
                x_col="Category",
                y_col="Protein",
                title="Protein by Category",
                y_title="Protein (g)",
                color="#22c55e",  # 绿色
            )
            st.altair_chart(pro_chart, use_container_width=True)
        else:
            st.info("No data for protein chart.")

# =========================
# Mode: Recipes (API + Caching + Free Plan Safe)
# =========================
if mode == "Recipes":
    st.markdown(
        "<h2 class='page-title'>Recommended Recipes</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtle">Generated once per day using Spoonacular API (free tier).</div>',
        unsafe_allow_html=True
    )

    # Manual refresh button 
    refresh = st.button("🔄 Refresh Recommendations (uses 1 point)")

    # Get ingredient list from pantry data
    ingredient_keywords = (
        df["Food_Name"]
        .str.replace(r"[^a-zA-Z ]", "", regex=True)
        .str.lower()
        .str.split()
        .explode()
        .unique()
        .tolist()
    )

    # Limit number of ingredients for consistent results
    ingredient_keywords = ingredient_keywords[:5]

    # Call API only if user presses refresh
    if refresh:
        recipes = fetch_recipes_safe(ingredient_keywords, n=3)
        st.success("Recommendations updated!")
    else:
        # Load cached results if available
        recipes = fetch_recipes_safe(ingredient_keywords, n=3)

    # If error, show fallback
    if isinstance(recipes, dict) and "error" in recipes:
        st.error(f"API Error: {recipes['error']}")
        st.info("Using fallback sample recipes instead.")
        recipes = []
    # Display recipe cards
    if recipes:
        c1, c2, c3 = st.columns(3)
        for col, r in zip([c1, c2, c3], recipes):
            title = r.get("title", "Recipe")
            image = r.get("image", "")
            used = ", ".join([i["name"] for i in r.get("usedIngredients", [])])
            missed = ", ".join([i["name"] for i in r.get("missedIngredients", [])])

            with col:
                st.markdown("<div class='block'>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='heading' style='font-size:18px;font-weight:600'>{title}</div>",
                    unsafe_allow_html=True,
                )

                if image:
                    st.image(image, use_container_width=True)

                st.markdown(f"<div class='subtle'>Uses: {used}</div>", unsafe_allow_html=True)
                if missed:
                    st.markdown(f"<div class='subtle'>Missing: {missed}</div>",
                                unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No recipes yet. Click 'Refresh Recommendations' to generate.")

    
# =========================
# Mode: Add Food
# =========================
if mode == "Add Food":
    st.markdown('<h2 class="page-title">Add Food Item</h2>', unsafe_allow_html=True)

    # nutrition cache for live preview
    if "nutri_preview" not in st.session_state:
        st.session_state["nutri_preview"] = None

    with st.form("add_form", clear_on_submit=False):
        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input("Name")
            qty = st.number_input("Quantity", min_value=0.0, value=1.0, step=1.0)
            cat = st.selectbox("Category",["Dairy", "Fruit", "Vegetable", "Meat", "Protein", "Grain", "Other"],)
            
            

        with c2:
            purchase = st.date_input("Purchase Date")
            weight_g = st.number_input("Weight (g)", min_value=0.0, value=100.0, step=10.0)
            exp = st.date_input("Expiration Date")

        
        fetch_btn = st.form_submit_button("Auto-fetch Nutrition Data")

        # Save button submits the form
        save_btn = st.form_submit_button("Save")

        # Handle Auto-fetch Nutrition
        if fetch_btn:
            if not name:
                st.error("Enter a food name first.")
            else:
                nutri = fetch_nutrition(name)
                if nutri is None:
                    st.warning("No nutrition data found.")
                elif "error" in nutri:
                    st.error(f"API error: {nutri['error']}")
                else:
                    st.session_state["nutri_preview"] = nutri

        # Show preview if exists
        if st.session_state["nutri_preview"]:
            nut = st.session_state["nutri_preview"]
            st.info(
                f"Calories: {nut['calories']} kcal  |  "
                f"Protein: {nut['protein']} g  |  "
                f"Weight (serving): {nut['weight_g']} g"
            )

               # Handle Save
        if save_btn:
            if not name:
                st.error("Name is required.")
            else:
                # Use nutrition preview if available
                nut = st.session_state["nutri_preview"]

                new_row = {
                    "Food_Name": name,
                    "Expiration_Date": pd.to_datetime(exp),
                    "Calories": nut["calories"] if nut else 0,
                    "Protein": nut["protein"] if nut else 0,
                    "Weight_g": nut["weight_g"] if nut else weight_g,
                    "Quantity": qty,
                    "Category": cat,
                }

                # Compute Days_Left
                today = pd.Timestamp(datetime.now().date())
                new_row["Days_Left"] = (new_row["Expiration_Date"] - today).days

                # Append new row to inventory in session state
                st.session_state["inventory_df"] = pd.concat(
                    [st.session_state["inventory_df"], pd.DataFrame([new_row])],
                    ignore_index=True,
                )

                # Clear nutrition preview for next entry
                st.session_state["nutri_preview"] = None

                # Visual feedback
                st.success(f"Added: {name}")

               
                try:
                    st.toast(f"Added {name} to inventory.", icon="🥫")
                except Exception:
                    pass


# =========================
# Take items from inventory (reduce quantity) — Add Food page only
# =========================
if mode == "Add Food":
    st.markdown(
    '<h2 class="page-title">Take Items From Inventory</h2>',
    unsafe_allow_html=True,
)

    inv_all = st.session_state["inventory_df"]

    if inv_all.empty:
        st.info("Inventory is empty.")
    else:
        # Build labels showing item and quantity
        option_labels = [
            f"{row['Food_Name']} (Qty: {row['Quantity']})"
            for _, row in inv_all.iterrows()
        ]

        # Map label → Food_Name
        label_to_name = {
            f"{row['Food_Name']} (Qty: {row['Quantity']})": row["Food_Name"]
            for _, row in inv_all.iterrows()
        }

        # Select one item
        selected_label = st.selectbox(
            "Select item:",
            [""] + option_labels,
            key="take_item_select",
        )

        if selected_label:
            food_name = label_to_name[selected_label]

            # Current quantity of this item
            current_qty = int(
                inv_all[inv_all["Food_Name"] == food_name]["Quantity"].iloc[0]
            )

            reduce_n = st.number_input(
                "How many do you want to take?",
                min_value=1,
                max_value=current_qty,
                value=1,
                step=1,
                key="take_item_n",
            )

            # Confirm button
            if st.button("Confirm", key="take_item_confirm"):
                new_qty = current_qty - reduce_n

                if new_qty > 0:
                    # Update remaining quantity
                    st.session_state["inventory_df"].loc[
                        st.session_state["inventory_df"]["Food_Name"] == food_name,
                        "Quantity"
                    ] = new_qty

                    st.success(
                        f"Took {reduce_n} {food_name}. New quantity: {new_qty}"
                    )
                else:
                    # Remove the item if quantity reaches zero
                    st.session_state["inventory_df"] = (
                        st.session_state["inventory_df"][
                            st.session_state["inventory_df"]["Food_Name"] != food_name
                        ]
                    )

                    st.success(f"All {food_name} taken. Item removed.")
# =========================
# Inventory table (Dashboard + Add Food)
# =========================
if mode in ["Dashboard", "Add Food"]:
    st.markdown(
    '<h2 class="page-title" style="margin-top:18px;">Inventory</h2>',
    unsafe_allow_html=True,
)

    search = st.text_input("Search food name", key="inv_search")
    cat = st.selectbox(
        "Filter by category",
        options=["All"] + sorted(df["Category"].unique().tolist()),
        key="inv_cat",
    )

    inv = st.session_state["inventory_df"].copy()
    if search:
        inv = inv[inv["Food_Name"].str.contains(search, case=False, na=False)]
    if cat != "All":
        inv = inv[inv["Category"] == cat]

    inv = inv[
        ["Food_Name", "Category", "Expiration_Date", "Days_Left",
         "Calories", "Protein", "Weight_g", "Quantity"]
    ].sort_values(["Days_Left", "Food_Name"])

    st.dataframe(inv, use_container_width=True, height=360)

    # Download filtered CSV
    csv_bytes = inv.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv_bytes,
        file_name="fresh_filtered.csv",
        mime="text/csv",
    )