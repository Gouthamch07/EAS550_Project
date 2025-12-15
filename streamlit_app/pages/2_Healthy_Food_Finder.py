import streamlit as st
import pandas as pd
from utils.queries import find_products_by_category_keyword

st.set_page_config(page_title="Healthy Food Finder", page_icon="🥗", layout="wide")

st.title("🥗 Healthy Food Finder")
st.markdown("### Find the healthiest (and avoid the worst) products in any category")

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
    # We don't need sort_by here anymore because we will show Best AND Worst automatically
    st.info("👇 We will analyze the top 100 matches")

if search_category:
    # Get top 100 matches sorted by Nutri-Score (Best first)
    # We fetch enough rows to show both top and bottom
    df = find_products_by_category_keyword(search_category, sort_order='ASC', limit=100)
    
    if df.empty:
        st.warning(f"No products found matching '{search_category}'. Try a different search term!")
    else:
        st.success(f"Found **{len(df):,}** products matching '{search_category}'")
        
        # Assign simple grades/emojis for display
        def assign_emoji(grade):
            g = str(grade).lower()
            if g == 'a': return '🟢'
            if g == 'b': return '🟡'
            if g == 'c': return '🟠'
            if g == 'd': return '🔴'
            if g == 'e': return '⛔'
            return '⚪'
        
        df['emoji'] = df['nutriscore_grade'].apply(assign_emoji)
        df['grade_display'] = df['nutriscore_grade'].str.upper()
        
        # === GRADE BREAKDOWN ===
        st.markdown("---")
        st.markdown(f"## 📊 Grade Breakdown for '{search_category.title()}'")
        
        grade_counts = df['nutriscore_grade'].value_counts()
        
        cols = st.columns(5)
        grades = ['a', 'b', 'c', 'd', 'e']
        labels = ['🟢 A', '🟡 B', '🟠 C', '🔴 D', '⛔ E']
        
        for i, grade in enumerate(grades):
            count = grade_counts.get(grade, 0)
            pct = (count / len(df) * 100)
            cols[i].metric(labels[i], f"{count}", f"{pct:.0f}%")

        # === BEST CHOICES ===
        st.markdown("---")
        st.markdown("## 🏆 BEST CHOICES (Top 10)")
        st.caption("Lowest Nutri-Score, Lowest Sugar, Highest Protein")
        
        best_products = df.head(10)
        
        st.dataframe(
            best_products,
            column_order=("product_name", "brand_name", "grade_display", "sugars_100g", "proteins_100g"),
            column_config={
                "product_name": st.column_config.TextColumn("Product"),
                "brand_name": st.column_config.TextColumn("Brand"),
                "grade_display": st.column_config.TextColumn("Grade", width="small"),
                "sugars_100g": st.column_config.ProgressColumn(
                    "Sugar", format="%.1f g", min_value=0, max_value=50
                ),
                "proteins_100g": st.column_config.ProgressColumn(
                    "Protein", format="%.1f g", min_value=0, max_value=30
                ),
            },
            hide_index=True,
            use_container_width=True
        )
        
        # === WORST CHOICES ===
        st.markdown("---")
        st.markdown("## ⚠️ AVOID THESE (Bottom 10)")
        st.caption("Highest Nutri-Score, High Sugar")
        
        # Get the tail (worst scores)
        worst_products = df.tail(10).sort_values('nutriscore_score', ascending=False)
        
        st.dataframe(
            worst_products,
            column_order=("product_name", "brand_name", "grade_display", "sugars_100g", "proteins_100g"),
            column_config={
                "product_name": st.column_config.TextColumn("Product"),
                "brand_name": st.column_config.TextColumn("Brand"),
                "grade_display": st.column_config.TextColumn("Grade", width="small"),
                "sugars_100g": st.column_config.ProgressColumn(
                    "Sugar", format="%.1f g", min_value=0, max_value=50
                ),
                "proteins_100g": st.column_config.ProgressColumn(
                    "Protein", format="%.1f g", min_value=0, max_value=30
                ),
            },
            hide_index=True,
            use_container_width=True
        )
        
        # === KEY INSIGHT ===
        st.markdown("---")
        good_count = grade_counts.get('a', 0) + grade_counts.get('b', 0)
        good_pct = (good_count / len(df) * 100)
        
        st.info(f"💡 **KEY INSIGHT**: Only **{good_pct:.0f}%** of these {search_category} products earned Grade A or B. Choose carefully!")

else:
    st.markdown("---")
    st.markdown("## 💡 Popular Searches:")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("- Chocolate\n- Cookies")
    with c2: st.markdown("- Soda\n- Juice")
    with c3: st.markdown("- Cereal\n- Yogurt")