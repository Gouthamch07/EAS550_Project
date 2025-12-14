import streamlit as st
from utils.connector import get_data
import pandas as pd

st.set_page_config(
    page_title="Global Food & Nutrition Explorer",
    page_icon="🥗",
    layout="wide"
)

# Load data
df_dim = get_data("dim_products", schema="analytics")
df_fact = get_data("fact_nutrition", schema="analytics")
df = df_dim.merge(df_fact, on='product_id', how='inner', suffixes=('', '_fact'))

# === HERO SECTION ===
st.title("🥗 Global Food & Nutrition Explorer")
st.markdown("### Discover the truth about what you eat")

# === SEARCH BAR (PROMINENT) ===
st.markdown("---")
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("## 🔍 What food are you curious about?")
    search_query = st.text_input(
        "",
        placeholder="Try: chocolate, yogurt, cereal, chips...",
        label_visibility="collapsed"
    )
    
    if search_query:
        # Search in product names
        results = df[df['product_name'].str.contains(search_query, case=False, na=False)]
        
        if len(results) > 0:
            st.success(f"Found {len(results):,} products matching '{search_query}'")
            
            # Show top 5 results with grades
            top_results = results.nsmallest(5, 'nutriscore_score') if 'nutriscore_score' in results.columns else results.head(5)
            
            st.markdown("#### 🏆 Top Results (Best to Worst):")
            for idx, row in top_results.iterrows():
                grade = row.get('nutriscore_grade', 'unknown').upper()
                score = row.get('nutriscore_score', 'N/A')
                
                grade_colors = {'A': '🟢', 'B': '🟡', 'C': '🟠', 'D': '🔴', 'E': '⛔'}
                emoji = grade_colors.get(grade, '⚪')
                
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.markdown(f"**{row['product_name'][:60]}**")
                with col_b:
                    st.markdown(f"{emoji} Grade **{grade}**")
                with col_c:
                    st.markdown(f"Score: **{score}**")
        else:
            st.warning(f"No products found for '{search_query}'. Try a different search term!")

st.markdown("---")

# === SHOCKING STATS SECTION ===
st.markdown("## 🚨 Shocking Findings from Our Database")

# Calculate shocking stats
total_products = len(df)
if 'nutriscore_grade' in df.columns:
    grade_counts = df['nutriscore_grade'].value_counts()
    poor_grades = grade_counts.get('d', 0) + grade_counts.get('e', 0)
    poor_pct = (poor_grades / total_products * 100) if total_products > 0 else 0
    
    good_grades = grade_counts.get('a', 0) + grade_counts.get('b', 0)
    good_pct = (good_grades / total_products * 100) if total_products > 0 else 0
else:
    poor_pct = 0
    good_pct = 0

if 'nova_group' in df.columns:
    ultra_processed = len(df[df['nova_group'] == 4])
    ultra_pct = (ultra_processed / total_products * 100) if total_products > 0 else 0
else:
    ultra_pct = 0

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style='background-color: #ff4444; padding: 20px; border-radius: 10px; text-align: center;'>
        <h2 style='color: white; margin: 0;'>{poor_pct:.0f}%</h2>
        <p style='color: white; margin: 5px 0 0 0;'>of products have POOR nutrition (Grade D/E)</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background-color: #ff9800; padding: 20px; border-radius: 10px; text-align: center;'>
        <h2 style='color: white; margin: 0;'>{ultra_pct:.0f}%</h2>
        <p style='color: white; margin: 5px 0 0 0;'>are ultra-processed (NOVA 4)</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background-color: #4CAF50; padding: 20px; border-radius: 10px; text-align: center;'>
        <h2 style='color: white; margin: 0;'>{good_pct:.0f}%</h2>
        <p style='color: white; margin: 5px 0 0 0;'>are actually HEALTHY (Grade A/B)</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# === WHAT YOU CAN DO HERE ===
st.markdown("## 🎯 What You Can Do Here")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ✅ Available Features:
    
    🔍 **Healthy Food Finder**  
    Find the healthiest products in any category
    
    ⚔️ **Product Comparison**  
    Compare nutrition between products side-by-side
    
    🧮 **Nutrition Calculator**  
    Calculate health scores for any food
    
    🔄 **My Healthy Swap List**  
    Build your grocery list with healthier alternatives
    """)

with col2:
    st.markdown("""
    ### 💡 Questions We Answer:
    
    ❓ Which "healthy" brands are actually junk?
    
    ❓ What's the healthiest chocolate/cereal/yogurt?
    
    ❓ How does my favorite snack compare?
    
    ❓ What should I swap in my weekly groceries?
    """)

st.markdown("---")

# === PROJECT STATS ===
st.markdown("## 📊 Project Overview")

total_brands = df['brand_name'].nunique() if 'brand_name' in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Products Analyzed", f"{total_products:,}")
col2.metric("Unique Brands", f"{total_brands:,}")
col3.metric("Nutrition Grades", "A → E")
col4.metric("Data Freshness", "2024")

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Global Food & Nutrition Explorer</strong> | Built with Open Food Facts Data</p>
    <p>Making healthier food choices easier, one product at a time</p>
</div>
""", unsafe_allow_html=True)