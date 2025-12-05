# 🥫 FRESH Smart Pantry
GitHub Repository: https://github.com/sherryxie2025/TEAM-15-FRESH

---

# Table of Contents
- Introduction
- Features
- Installation
- Configuration (API Keys)
- Usage
- Dataset
- Project Structure
- API Services Used
- Key Variables Used in Code
- Limitations & Free-Tier Notes
- License
- Acknowledgements

---

# Introduction
**FRESH** is a web-based Streamlit application that allows users to:

- Track household food inventory  
- Monitor expiration dates  
- Automatically fetch nutrition data  
- Receive personalized recipe recommendations  
- Visualize calorie and protein statistics by category  

---

# Features

### Analytics Dashboard
- Soon-to-expire items  
- Key summary metrics (average calories, low stock, etc.)  
- Calories by category  
- Protein by category  

### Recipe Recommendations
- Uses Spoonacular API  
- Recommend top 3 recipes based on available ingredients  

### Inventory Management
- Add and remove pantry items  
- Auto-calculate *days left* before expiration  
- Export inventory to CSV  
- Search and filter by category 

### Nutrition Auto-Fetch
- Retrieves calories and protein from the USDA FoodData Central API  

---

# Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/sherryxie2025/TEAM-15-FRESH
```

### **2. Make Sure Python Is Installed**
```bash
python --version
```

### **3. Install Required Python Libraries**
Required libraries:
- io  
- pandas  
- streamlit  
- requests  
- altair  

Windows:
```bash
pip install streamlit pandas requests altair
```

macOS:
```bash
pip3 install streamlit pandas requests altair
```

### **4. Launch the Application**
```bash
streamlit run fresh.py
```

---

# Configuration (API Keys)

## USDA FoodData Central API
Used to fetch calories and protein.  
We included a free key. You can also sign up:
https://fdc.nal.usda.gov/api-key-signup.html

## Spoonacular Recipe API
Used to generate top 3 recipe recommendations.

Free tier limits:
- 50 points/day  
- 1 request per second  
- 2 concurrent requests  
- Requires backlink  

We included two free keys. You can also sign up:
https://spoonacular.com/food-api

---

# Usage

## Login
Use the built-in demo account:

| Username | Password |
|----------|----------|
| fresh    | fresh2025 |

---

## Dashboard
- Highlights expiring items  
- Shows nutrition charts  
- Displays KPIs  

---

## Recipes
- Uses Spoonacular  
- Click **Refresh Recommendations** after updating inventory  

---

## Add Food
- Enter details  
- Auto-fetch nutrition  
- Save to inventory  

---

## Take Items From Inventory
- Reduce quantity  
- Removes item automatically when quantity reaches zero  

---

# Dataset

## Example Dataset Used in the Application

FRESH system includes a built-in example dataset that can be loaded when:

- The user checks **“Use example dataset”** on the homepage  
- No CSV is uploaded  
- No public CSV URL is provided  

This dataset is embedded directly in the code and represents a small sample pantry for demonstration and testing.
You can also find this CSV file in our GitHub Repository.

### **Example Dataset (Hard-coded in `fresh.py`)**

| Food_Name       | Expiration_Date | Calories | Protein | Weight_g | Quantity | Category  |
|-----------------|------------------|----------|---------|----------|----------|-----------|
| Milk            | 2025-12-08       | 120      | 8       | 240      | 1        | Dairy     |
| Apple           | 2025-12-10       | 95       | 0.5     | 182      | 3        | Fruit     |
| Yogurt          | 2025-12-12       | 80       | 5       | 150      | 2        | Dairy     |
| Spinach         | 2025-12-05       | 23       | 3       | 85       | 1        | Vegetable |
| Chicken Breast  | 2025-12-07       | 165      | 31      | 120      | 2        | Meat      |
| Tofu            | 2025-12-06       | 76       | 8       | 100      | 1        | Protein   |
| Eggs            | 2025-12-11       | 70       | 6       | 50       | 12       | Protein   |
| Bread           | 2025-12-09       | 250      | 9       | 500      | 1        | Grain     |

These rows come directly from the following code block in `fresh.py`:

```python
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
```

---

## Required Dataset Columns
You can also upload datasets. The required dataset columns:

| Column Name | Description |
|-------------|-------------|
| Food_Name | Name of item |
| Expiration_Date | Date item expires |
| Calories | Calories per serving |
| Protein | Protein in grams |
| Weight_g | Serving weight |
| Quantity | Number of units |
| Category | Category label |
| Days_Left | Computed days until expiration |

---

# Project Structure
```
TEAM-15-FRESH/
│
├── fresh.py
├── example_dataset.csv              
├── README.md                
└── images/
      ├── add_food.png
      ├── dashboard.png
      ├── login.png
      └── recipes.png
```

---

# API Services Used

## USDA FoodData Central API
- Fetches nutrition info  
- Free tier  

## Spoonacular Recipe API
- Provides recipe suggestions  
- Matches ingredients from the inventory  

---

# Key Variables Used in Code

## API Keys
```python
SPOONACULAR_API_KEY = "..."
USDA_API_KEY = "..."
```

## Required Dataset Columns
```python
REQUIRED_COLS = ["Food_Name", "Expiration_Date", "Calories", "Protein", "Weight_g", "Quantity", "Category"]
```

## Main Inventory DataFrame
```python
st.session_state["inventory_df"]
```

## Computed Expiration Days
```python
df["Days_Left"]
```

## Recipe Ingredient Matching
```python
ingredient_keywords
```
Used to determine which recipes use the most ingredients from the inventory.

## Core Functions
```python
fetch_recipes_safe()
fetch_nutrition()
load_csv()
pretty_bar_chart()
```

## UI Filter Variables
```python
search
cat
```

---

# Limitations & Free-Tier Notes

## Spoonacular
- 50 calls/day  
- No SLA  
- Can throttle  

## USDA
- May fail for certain items  
- Rate limits  

---

# License
MIT License — free for academic use.

---

# Acknowledgements
- USDA FoodData Central  
- Spoonacular API  
- Streamlit  
- Course Instructor & Teaching Team
