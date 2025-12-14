import streamlit as st
from utils.queries import find_products_by_category_keyword

st.set_page_config(page_title="Healthy Food Finder", page_icon="🥗", layout="wide")
st.title("🥗 Healthy Food Finder")

col1, col2 = st.columns([2, 1])
with col1:
    search_category = st.text_input("What type of food?", placeholder="e.g., chocolate, yogurt")
with col2:
    sort_by = st.selectbox("Sort by:", ["Best Nutrition First", "Worst Nutrition First", "Alphabetical"])

if search_category:
    sort_map = {"Best Nutrition First": "ASC", "Worst Nutrition First": "DESC", "Alphabetical": "ALPHA"}
    # Use SQL Query
    df = find_products_by_category_keyword(search_category, sort_map[sort_by])
    
    if not df.empty:
        st.success(f"Found {len(df)} products")
        for idx, row in df.iterrows():
            grade = str(row['nutriscore_grade']).upper()
            emoji = {'A': '🟢', 'B': '🟡', 'C': '🟠', 'D': '🔴', 'E': '⛔'}.get(grade, '⚪')
            
            c1, c2, c3 = st.columns([3, 2, 2])
            c1.markdown(f"**{row['product_name']}**")
            c2.markdown(f"*{row['brand_name']}*")
            c3.markdown(f"{emoji} **{grade}** | 🍬 {row['sugars_100g']}g sugar")
    else:
        st.warning("No products found.")