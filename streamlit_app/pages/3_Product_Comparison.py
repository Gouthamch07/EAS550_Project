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
    st.header("📊 Head-to-Head Stats")
    
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
        
        winner = "Tie"
        if val1 != val2:
            if higher_is_better:
                winner = "Product 1" if val1 > val2 else "Product 2"
            else:
                winner = "Product 1" if val1 < val2 else "Product 2"
            
        if winner == "Product 1": wins1 += 1
        if winner == "Product 2": wins2 += 1
        
        # Formatting
        v1_str = f"{val1:.1f}"
        v2_str = f"{val2:.1f}"
        
        data.append({
            "Metric": label,
            f"{prod1_data['product_name'][:20]}...": v1_str,
            f"{prod2_data['product_name'][:20]}...": v2_str,
            "Winner": "👈" if winner == "Product 1" else ("👉" if winner == "Product 2" else "=")
        })
        
    st.table(pd.DataFrame(data))
    
    # === VERDICT ===
    st.markdown("---")
    st.markdown("## 🏆 THE VERDICT")
    
    if wins1 > wins2:
        st.success(f"🏆 **WINNER: {prod1_data['product_name']}** (Won {wins1} categories)")
    elif wins2 > wins1:
        st.success(f"🏆 **WINNER: {prod2_data['product_name']}** (Won {wins2} categories)")
    else:
        st.warning("🤝 **IT'S A TIE!** Both products have similar nutritional profiles.")

    # === SUGAR VISUAL ===
    st.markdown("---")
    st.markdown("### 🍬 Sugar Content Visualization (per 100g)")
    
    s1 = float(prod1_data.get('sugars_100g', 0) or 0)
    s2 = float(prod2_data.get('sugars_100g', 0) or 0)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{prod1_data['product_name']}**")
        cubes1 = int(s1 / 4) # 4g per cube
        st.write("🧊 " * min(cubes1, 20) + ("..." if cubes1 > 20 else ""))
        st.caption(f"{s1:.1f}g Sugar ≈ {cubes1} Cubes")
        
    with c2:
        st.markdown(f"**{prod2_data['product_name']}**")
        cubes2 = int(s2 / 4)
        st.write("🧊 " * min(cubes2, 20) + ("..." if cubes2 > 20 else ""))
        st.caption(f"{s2:.1f}g Sugar ≈ {cubes2} Cubes")

else:
    st.info("👆 Search and select two products above to compare them!")