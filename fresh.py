import io
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

import requests
from datetime import datetime, timedelta

import json

SPOONACULAR_API_KEY = "f6fe73660fae4273ba25c44ec8c126be"

@st.cache_data(ttl=60 * 60 * 12)  # cache 12 hours to minimize API usage
def fetch_recipes_safe(ingredients, n=3):
    """Safe Recipe Fetching with Free Tier Limits."""
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "ingredients": ",".join(ingredients),
        "number": n,
        "ranking": 1,  # maximize used ingredients
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
        st.error("USDA API search failed.")
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
    weight_g = detail_data.get("servingSize", 100)  # default 100g if missing

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
# Basic page config
# =========================
st.set_page_config(
    page_title="FRESH Smart Pantry",
    page_icon="🥫",
    layout="wide",
)

# =========================
# CSS: 深色背景 + 卡片风格
# =========================
FRESH_CSS = """
<style>
/* 🌿 主背景：清爽渐变蓝绿 */
.stApp {
  background: linear-gradient(135deg, #e0f7fa 0%, #e8fdf5 50%, #ffffff 100%) !important;
  color: #0f172a !important;
  font-family: "Helvetica Neue", system-ui, -apple-system, sans-serif;
}

/* 🌱 卡片风格 */
.block {
  background: rgba(255,255,255,0.9);
  border-radius: 18px;
  padding: 18px 20px;
  border: 1px solid rgba(56,189,248,0.3); /* 淡蓝边框 */
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.block:hover {
  border-color: rgba(16,185,129,0.6); /* hover 变成绿色边 */
}

/* 🌿 标题与文字 */
.heading { color: #065f46; }       /* 深绿色标题 */
.subtle { color: #4b5563; }        /* 灰蓝说明文字 */

/* 🍋 标签小圆角 */
.badge {
  padding:4px 10px;
  border-radius:999px;
  background:rgba(209,250,229,0.8);
  border:1px solid rgba(16,185,129,0.3);
  color:#047857;
  font-size:11px;
}

/* 🫐 按钮 */
.btn {
  padding:14px 16px;
  border-radius:14px;
  border:1px solid rgba(56,189,248,0.3);
  background:linear-gradient(90deg,#22d3ee,#34d399);
  color:#ffffff;
  text-decoration:none;
  display:block;
  text-align:center;
  font-size:14px;
  font-weight:500;
}
.btn:hover {
  background:linear-gradient(90deg,#2dd4bf,#38bdf8);
  border-color:rgba(16,185,129,0.5);
}

/* 🍃 Tag 区块 */
.chips span {
  margin-right:8px;
  margin-bottom:8px;
  display:inline-block;
}

/* 📊 数据表格微调 */
[data-testid="stDataFrame"] {
  background-color: #ffffff !important;
  border-radius: 12px;
}

/* 📈 顶部标题容器 */
.block-header {
  background:linear-gradient(90deg,rgba(16,185,129,0.15),rgba(56,189,248,0.15));
  border-radius: 14px;
  padding:12px 16px;
}
</style>
"""
st.markdown(FRESH_CSS, unsafe_allow_html=True)

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

    # Parse date
    df["Expiration_Date"] = pd.to_datetime(df["Expiration_Date"], errors="coerce")
    df = df.dropna(subset=["Expiration_Date"])

    # Ensure numeric
    for col in ["Calories", "Protein", "Weight_g", "Quantity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)


    # Days left
    today = pd.Timestamp(datetime.now().date())
    df["Days_Left"] = (df["Expiration_Date"] - today).dt.days

    return df



@st.cache_data(show_spinner=False)
def example_df() -> pd.DataFrame:
    csv = io.StringIO(
        """Food_Name,Expiration_Date,Calories,Protein,Weight_g,Quantity,Category
Milk,2026-01-15,120,8,240,1,Dairy
Apple,2026-01-20,95,0.5,182,3,Fruit
Yogurt,2026-01-25,80,5,150,2,Dairy
Spinach,2026-01-12,23,3,85,1,Vegetable
Chicken Breast,2026-01-18,165,31,120,2,Meat
Tofu,2026-01-10,76,8,100,1,Protein
Eggs,2026-01-22,70,6,50,12,Protein
Bread,2026-01-14,250,9,500,1,Grain
"""
    )
    return load_csv(io.BytesIO(csv.getvalue().encode()))


# =========================
# Sidebar: navigation + data source
# =========================
with st.sidebar:
    st.markdown("### 🥫 FRESH")
    mode = st.radio(
        "Navigation",
        ["Dashboard", "Recipes", "Add Food", "Account"],
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

# Data loading precedence: upload > URL > example
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
<div class="block" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
  <div>
    <div class="heading" style="font-size:26px;font-weight:700;">FRESH</div>
    <div class="subtle">Smart Pantry · Track what you eat, save what you love</div>
  </div>
  <div style="text-align:right;">
    <div class="subtle">Today: {datetime.now().date()}</div>
    <div class="subtle">{total_items} items · {expiring_3} expiring ≤ 3 days</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================
# Mode: Dashboard
# =========================
if mode == "Dashboard":
    st.markdown('<h2 class="heading">Dashboard</h2>', unsafe_allow_html=True)

    # Highlight a couple of key items (demo)
    highlight_names = ["Milk", "Apple"]
    for name in highlight_names:
        sub = df[df["Food_Name"].str.contains(name, case=False, na=False)]
        if not sub.empty:
            days = int(sub["Days_Left"].min())
            soon10 = int((df["Days_Left"] <= 10).sum())
            st.markdown(
                f"""
<div class="block" style="margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
  <div class="heading" style="font-weight:600;font-size:16px;">{name.title()}</div>
  <div class="subtle">{days} days left</div>
  <div class="subtle">{soon10} items ≤ 10 days</div>
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

    # Simple calories chart by category
    st.markdown("### Calories by Category")
    cat_agg = (
        df.groupby("Category", as_index=False)["Calories"]
        .sum()
        .sort_values("Calories", ascending=False)
    )
    if not cat_agg.empty:
        st.bar_chart(cat_agg, x="Category", y="Calories", height=260)
    else:
        st.info("No data for chart.")

    # Simple protein chart by category
    st.markdown("### Protein by Category")
    protein_agg = (
        df.groupby("Category", as_index=False)["Protein"]
        .sum()
        .sort_values("Protein", ascending=False)
    )

    if not protein_agg.empty:
        st.bar_chart(protein_agg, x="Category", y="Protein", height=260)
    else:
        st.info("No data for protein chart.")


    




# =========================
# Mode: Recipes (API + Caching + Free Plan Safe)
# =========================
if mode == "Recipes":
    st.markdown('<h2 class="heading">Recommended Recipes</h2>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Generated once per day using Spoonacular API (free tier).</div>',
                unsafe_allow_html=True)

    # Manual refresh button to avoid burning API points
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

    # Limit to 5 ingredients to keep results stable & cheap
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
    st.markdown('<h2 class="heading">Add Food Item</h2>', unsafe_allow_html=True)

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


        # This button does NOT submit the form
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
                calories = (
                    st.session_state["nutri_preview"]["calories"]
                    if st.session_state["nutri_preview"]
                    else 0
                )

                nut = st.session_state["nutri_preview"]

                new_row = {
                    "Food_Name": name,
                    "Expiration_Date": pd.to_datetime(exp),
                    "Calories": nut["calories"] if nut else 0,
                    "Protein": nut["protein"] if nut else 0,
                    "Weight_g": nut["weight_g"] if nut else 0,
                    "Quantity": qty,
                    "Category": cat,
                }

                today = pd.Timestamp(datetime.now().date())
                new_row["Days_Left"] = (new_row["Expiration_Date"] - today).days

                st.session_state["inventory_df"] = pd.concat(
                    [st.session_state["inventory_df"], pd.DataFrame([new_row])],
                    ignore_index=True,
                )

                # Clear nutrition preview for next entry
                st.session_state["nutri_preview"] = None

                st.success(f"Added: {name}")




# =========================
# Mode: Account
# =========================
if mode == "Account":
    st.markdown(
        '<h2 class="heading" style="text-align:center;">Welcome to FRESH</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtle" style="text-align:center;">Minimal auth mockup for UI demonstration.</div>',
        unsafe_allow_html=True,
    )

    colA, colB, colC = st.columns([1, 1, 1])
    with colB:
        with st.form("auth_form"):
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            login = st.form_submit_button("Sign In")
            if login:
                if email and pwd:
                    st.success("Signed in (demo only, no real auth).")
                else:
                    st.error("Please enter email and password.")
        st.markdown(
            '<div class="subtle" style="margin-top:10px;">No account? In real system, this goes to sign-up.</div>',
            unsafe_allow_html=True,
        )

# =========================
# Inventory table (all modes)
# =========================
st.markdown('<h3 class="heading" style="margin-top:18px;">Inventory</h3>', unsafe_allow_html=True)

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

inv = inv[["Food_Name", "Category", "Expiration_Date", "Days_Left", "Calories", "Protein", "Weight_g", "Quantity"]].sort_values(
    ["Days_Left", "Food_Name"]
)

st.dataframe(inv, use_container_width=True, height=360)

# ------------------------
# Delete item from Inventory
# ------------------------
st.markdown("### Delete an Item")

# Let user pick which food to delete
delete_choice = st.selectbox(
    "Select a food to delete:",
    options=[""] + inv["Food_Name"].tolist()
)

# Delete button
if st.button("Delete Selected Item"):
    if delete_choice == "":
        st.warning("Please select a food to delete.")
    else:
        # Remove from session-state inventory
        st.session_state["inventory_df"] = st.session_state["inventory_df"][
            st.session_state["inventory_df"]["Food_Name"] != delete_choice
        ]

        st.success(f"Deleted: {delete_choice}")
        st.rerun()


# Download filtered CSV
csv_bytes = inv.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered CSV",
    data=csv_bytes,
    file_name="fresh_filtered.csv",
    mime="text/csv",
)

# Footer
st.markdown(
    '<div class="subtle" style="margin-top:10px;font-size:11px;">FRESH Demo · Streamlit · Frontend-style UI for course project</div>',
    unsafe_allow_html=True,
)