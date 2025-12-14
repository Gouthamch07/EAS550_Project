import streamlit as st
import pandas as pd
import plotly.express as px
from utils.connector import get_data

st.set_page_config(page_title="Healthy Food Finder", page_icon="🥗", layout="wide")

# Load data
df_fact = get_data("fact_nutrition", schema="analytics")

st.title("🥗 Healthy Food Finder")
st.markdown("### Find the healthiest products in any category")

# === CATEGORY INPUT ===
st.markdown("---")
col1, col2 = st.columns([2, 1])

with col1:
    search_category = st.text_input(
        "What type of food are you looking for?",
        placeholder="e.g., chocolate, yogurt, cereal, bread, chips",
        help="We'll search product names for this keyword"
    )

with col2:
    sort_by = st.selectbox(
        "Sort by:",
        ["Best Nutrition First", "Worst Nutrition First", "Alphabetical"]
    )

if search_category:
    # Filter products
    filtered_df = df_fact[
        df_fact['product_name'].str.contains(search_category, case=False, na=False)
    ].copy()
    
    if len(filtered_df) == 0:
        st.warning(f"No products found matching '{search_category}'. Try a different search term!")
    else:
        st.success(f"Found **{len(filtered_df):,}** products matching '{search_category}'")
        
        # Calculate health score (lower sugar + higher protein = better)
        filtered_df['health_score'] = (
            -filtered_df['sugars_100g'].fillna(50) +  # Lower sugar is better
            filtered_df['proteins_100g'].fillna(0)     # Higher protein is better
        )
        
        # Sort based on selection
        if sort_by == "Best Nutrition First":
            filtered_df = filtered_df.sort_values('health_score', ascending=False)
        elif sort_by == "Worst Nutrition First":
            filtered_df = filtered_df.sort_values('health_score', ascending=True)
        else:
            filtered_df = filtered_df.sort_values('product_name')
        
        # Assign simple grades based on health score
        def assign_grade(score):
            if score >= 10:
                return 'a', '🟢'
            elif score >= 5:
                return 'b', '🟡'
            elif score >= 0:
                return 'c', '🟠'
            elif score >= -10:
                return 'd', '🔴'
            else:
                return 'e', '⛔'
        
        filtered_df['grade'], filtered_df['emoji'] = zip(*filtered_df['health_score'].apply(assign_grade))
        
        # === GRADE BREAKDOWN ===
        st.markdown("---")
        st.markdown(f"## 📊 Grade Breakdown for '{search_category.title()}'")
        
        grade_counts = filtered_df['grade'].value_counts()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            count_a = grade_counts.get('a', 0)
            pct_a = (count_a / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.metric("🟢 Grade A", f"{count_a}", f"{pct_a:.1f}%")
        
        with col2:
            count_b = grade_counts.get('b', 0)
            pct_b = (count_b / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.metric("🟡 Grade B", f"{count_b}", f"{pct_b:.1f}%")
        
        with col3:
            count_c = grade_counts.get('c', 0)
            pct_c = (count_c / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.metric("🟠 Grade C", f"{count_c}", f"{pct_c:.1f}%")
        
        with col4:
            count_d = grade_counts.get('d', 0)
            pct_d = (count_d / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.metric("🔴 Grade D", f"{count_d}", f"{pct_d:.1f}%")
        
        with col5:
            count_e = grade_counts.get('e', 0)
            pct_e = (count_e / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.metric("⛔ Grade E", f"{count_e}", f"{pct_e:.1f}%")
        
        # === BEST CHOICES ===
        st.markdown("---")
        st.markdown("## 🏆 BEST CHOICES (Top 10)")
        
        best_products = filtered_df.head(10) if sort_by == "Best Nutrition First" else filtered_df.nlargest(10, 'health_score')
        
        for idx, row in best_products.iterrows():
            col_name, col_brand, col_score, col_nutrients = st.columns([3, 2, 1, 2])
            
            with col_name:
                st.markdown(f"**{row['product_name'][:50]}**")
            
            with col_brand:
                brand = row.get('brand_name', 'Unknown')
                st.markdown(f"*{brand}*")
            
            with col_score:
                st.markdown(f"{row['emoji']} **{row['grade'].upper()}**")
            
            with col_nutrients:
                sugar = row.get('sugars_100g', 0)
                protein = row.get('proteins_100g', 0)
                st.markdown(f"🍬 {sugar:.1f}g sugar | 💪 {protein:.1f}g protein")
        
        # === WORST CHOICES ===
        st.markdown("---")
        st.markdown("## ⚠️ AVOID THESE (Bottom 10)")
        
        worst_products = filtered_df.tail(10) if sort_by == "Best Nutrition First" else filtered_df.nsmallest(10, 'health_score')
        
        for idx, row in worst_products.iterrows():
            col_name, col_brand, col_score, col_nutrients = st.columns([3, 2, 1, 2])
            
            with col_name:
                st.markdown(f"**{row['product_name'][:50]}**")
            
            with col_brand:
                brand = row.get('brand_name', 'Unknown')
                st.markdown(f"*{brand}*")
            
            with col_score:
                st.markdown(f"{row['emoji']} **{row['grade'].upper()}**")
            
            with col_nutrients:
                sugar = row.get('sugars_100g', 0)
                protein = row.get('proteins_100g', 0)
                st.markdown(f"🍬 {sugar:.1f}g sugar | 💪 {protein:.1f}g protein")
        
        # === KEY INSIGHT ===
        st.markdown("---")
        good_count = count_a + count_b
        good_pct = (good_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        
        st.info(f"💡 **KEY INSIGHT**: Only **{good_pct:.0f}%** of {search_category} products earned Grade A or B")
        
        # === DOWNLOAD OPTION ===
        csv = filtered_df[['product_name', 'brand_name', 'health_score', 'sugars_100g', 'proteins_100g']].to_csv(index=False)
        st.download_button(
            label=f"📥 Download Full {search_category.title()} List",
            data=csv,
            file_name=f"{search_category}_products.csv",
            mime="text/csv"
        )

else:
    # === SHOW EXAMPLES ===
    st.markdown("---")
    st.markdown("## 💡 Popular Searches:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🍫 Sweet Treats
        - chocolate
        - cookies
        - ice cream
        - candy
        """)
    
    with col2:
        st.markdown("""
        ### 🥤 Beverages
        - soda
        - juice
        - energy drinks
        - coffee
        """)
    
    with col3:
        st.markdown("""
        ### 🥣 Breakfast
        - cereal
        - yogurt
        - bread
        - granola
        """)

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Healthy Food Finder | Making better choices easier</p>
</div>
""", unsafe_allow_html=True)