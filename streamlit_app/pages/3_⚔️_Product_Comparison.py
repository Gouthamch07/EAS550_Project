import streamlit as st
import pandas as pd
from utils.queries import search_products, get_product_details

st.set_page_config(page_title="Product Comparison", page_icon="⚔️", layout="wide")
st.title("⚔️ Product Comparison Battle")

col1, col2 = st.columns(2)

# Product 1 Selection
with col1:
    st.markdown("#### 🥊 Product 1")
    search_1 = st.text_input("Search Product 1:", placeholder="e.g. Coca Cola", key="s1")
    prod1_data = None
    if search_1:
        res1 = search_products(search_1)
        if not res1.empty:
            sel1 = st.selectbox("Select:", res1['product_name'].tolist(), key="sel1")
            prod1_data = get_product_details(sel1).iloc[0]

# Product 2 Selection
with col2:
    st.markdown("#### 🥊 Product 2")
    search_2 = st.text_input("Search Product 2:", placeholder="e.g. Pepsi", key="s2")
    prod2_data = None
    if search_2:
        res2 = search_products(search_2)
        if not res2.empty:
            sel2 = st.selectbox("Select:", res2['product_name'].tolist(), key="sel2")
            prod2_data = get_product_details(sel2).iloc[0]

# Comparison Logic
if prod1_data is not None and prod2_data is not None:
    st.markdown("---")
    st.header("📊 Head-to-Head")
    
    metrics = [
        ('Energy (kcal)', 'energy_kcal_100g', False), # False = lower is better
        ('Sugar (g)', 'sugars_100g', False),
        ('Fat (g)', 'fat_100g', False),
        ('Protein (g)', 'proteins_100g', True) # True = higher is better
    ]
    
    data = []
    wins1, wins2 = 0, 0
    
    for label, col, higher_is_better in metrics:
        val1 = float(prod1_data.get(col, 0) or 0)
        val2 = float(prod2_data.get(col, 0) or 0)
        
        if val1 == val2:
            winner = "Tie"
        elif higher_is_better:
            winner = "Product 1" if val1 > val2 else "Product 2"
        else:
            winner = "Product 1" if val1 < val2 else "Product 2"
            
        if winner == "Product 1": wins1 += 1
        if winner == "Product 2": wins2 += 1
        
        data.append({
            "Metric": label,
            f"{prod1_data['product_name'][:20]}...": val1,
            f"{prod2_data['product_name'][:20]}...": val2,
            "Winner": winner
        })
        
    st.table(pd.DataFrame(data))
    
    if wins1 > wins2:
        st.success(f"🏆 WINNER: {prod1_data['product_name']}")
    elif wins2 > wins1:
        st.success(f"🏆 WINNER: {prod2_data['product_name']}")
    else:
        st.warning("🤝 It's a Tie!")