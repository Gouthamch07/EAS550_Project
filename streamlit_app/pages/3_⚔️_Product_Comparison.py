import streamlit as st
import pandas as pd
from utils.connector import get_data

st.set_page_config(page_title="Product Comparison", page_icon="⚔️", layout="wide")

# Load data
df_fact = get_data("fact_nutrition", schema="analytics")

st.title("⚔️ Product Comparison Battle")
st.markdown("### Compare products side-by-side to see which is healthier")

# === PRODUCT SELECTION ===
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🥊 Product 1")
    search_1 = st.text_input("Search for first product:", placeholder="e.g., Coca Cola", key="search1")
    
    if search_1:
        results_1 = df_fact[df_fact['product_name'].str.contains(search_1, case=False, na=False)]
        if len(results_1) > 0:
            product_1 = st.selectbox(
                "Select product:",
                results_1['product_name'].tolist(),
                key="product1"
            )
        else:
            st.warning("No products found!")
            product_1 = None
    else:
        product_1 = None

with col2:
    st.markdown("#### 🥊 Product 2")
    search_2 = st.text_input("Search for second product:", placeholder="e.g., Sprite", key="search2")
    
    if search_2:
        results_2 = df_fact[df_fact['product_name'].str.contains(search_2, case=False, na=False)]
        if len(results_2) > 0:
            product_2 = st.selectbox(
                "Select product:",
                results_2['product_name'].tolist(),
                key="product2"
            )
        else:
            st.warning("No products found!")
            product_2 = None
    else:
        product_2 = None

# === COMPARISON ===
if product_1 and product_2:
    st.markdown("---")
    st.markdown("## 📊 Head-to-Head Comparison")
    
    # Get product data
    data_1 = df_fact[df_fact['product_name'] == product_1].iloc[0]
    data_2 = df_fact[df_fact['product_name'] == product_2].iloc[0]
    
    # Helper function to determine winner
    def get_winner(val1, val2, lower_is_better=True):
        if pd.isna(val1) or pd.isna(val2):
            return "—"
        if lower_is_better:
            return "✓" if val1 < val2 else ("✓" if val2 < val1 else "=")
        else:
            return "✓" if val1 > val2 else ("✓" if val2 > val1 else "=")
    
    # Create comparison table
    comparison_data = {
        "Metric": [],
        product_1[:30]: [],
        product_2[:30]: [],
        "Winner": []
    }
    
    # Energy
    energy_1 = data_1.get('energy_kcal_100g', 0)
    energy_2 = data_2.get('energy_kcal_100g', 0)
    comparison_data["Metric"].append("⚡ Energy (kcal/100g)")
    comparison_data[product_1[:30]].append(f"{energy_1:.0f}")
    comparison_data[product_2[:30]].append(f"{energy_2:.0f}")
    comparison_data["Winner"].append("← Lower" if energy_1 < energy_2 else ("Lower →" if energy_2 < energy_1 else "Tie"))
    
    # Sugar
    sugar_1 = data_1.get('sugars_100g', 0)
    sugar_2 = data_2.get('sugars_100g', 0)
    comparison_data["Metric"].append("🍬 Sugar (g/100g)")
    comparison_data[product_1[:30]].append(f"{sugar_1:.1f}g")
    comparison_data[product_2[:30]].append(f"{sugar_2:.1f}g")
    comparison_data["Winner"].append("← Lower" if sugar_1 < sugar_2 else ("Lower →" if sugar_2 < sugar_1 else "Tie"))
    
    # Fat
    fat_1 = data_1.get('fat_100g', 0)
    fat_2 = data_2.get('fat_100g', 0)
    comparison_data["Metric"].append("🧈 Fat (g/100g)")
    comparison_data[product_1[:30]].append(f"{fat_1:.1f}g")
    comparison_data[product_2[:30]].append(f"{fat_2:.1f}g")
    comparison_data["Winner"].append("← Lower" if fat_1 < fat_2 else ("Lower →" if fat_2 < fat_1 else "Tie"))
    
    # Protein
    protein_1 = data_1.get('proteins_100g', 0)
    protein_2 = data_2.get('proteins_100g', 0)
    comparison_data["Metric"].append("💪 Protein (g/100g)")
    comparison_data[product_1[:30]].append(f"{protein_1:.1f}g")
    comparison_data[product_2[:30]].append(f"{protein_2:.1f}g")
    comparison_data["Winner"].append("← Higher" if protein_1 > protein_2 else ("Higher →" if protein_2 > protein_1 else "Tie"))
    
    # Display table
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
    
    # === VERDICT ===
    st.markdown("---")
    st.markdown("## 🏆 THE VERDICT")
    
    # Simple scoring: count wins
    wins_1 = 0
    wins_2 = 0
    
    if energy_1 < energy_2: wins_1 += 1
    elif energy_2 < energy_1: wins_2 += 1
    
    if sugar_1 < sugar_2: wins_1 += 1
    elif sugar_2 < sugar_1: wins_2 += 1
    
    if fat_1 < fat_2: wins_1 += 1
    elif fat_2 < fat_1: wins_2 += 1
    
    if protein_1 > protein_2: wins_1 += 1
    elif protein_2 > protein_1: wins_2 += 1
    
    if wins_1 > wins_2:
        st.success(f"🏆 **WINNER: {product_1}** (Won {wins_1} out of 4 metrics)")
        st.info(f"💡 **Why?** {product_1} has better nutrition scores in more categories")
    elif wins_2 > wins_1:
        st.success(f"🏆 **WINNER: {product_2}** (Won {wins_2} out of 4 metrics)")
        st.info(f"💡 **Why?** {product_2} has better nutrition scores in more categories")
    else:
        st.warning(f"🤝 **IT'S A TIE!** Both products are equally (un)healthy")
    
    # === SUGAR VISUAL ===
    if sugar_1 > 0 or sugar_2 > 0:
        st.markdown("---")
        st.markdown("### 🍬 Sugar Content Visualization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{product_1[:30]}**")
            sugar_cubes_1 = int(sugar_1 / 4)  # 4g per sugar cube
            st.markdown("🧊 " * min(sugar_cubes_1, 20))
            st.caption(f"= {sugar_cubes_1} sugar cubes")
        
        with col2:
            st.markdown(f"**{product_2[:30]}**")
            sugar_cubes_2 = int(sugar_2 / 4)
            st.markdown("🧊 " * min(sugar_cubes_2, 20))
            st.caption(f"= {sugar_cubes_2} sugar cubes")

else:
    st.info("👆 Search and select two products above to compare them!")

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Product Comparison Tool | Battle your favorite products</p>
</div>
""", unsafe_allow_html=True)