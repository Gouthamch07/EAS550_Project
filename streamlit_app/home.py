import streamlit as st
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
sys.path.insert(0, current_dir)

from utils.database import test_connection
from utils.queries import get_dashboard_stats, search_products
from config import APP_TITLE, APP_ICON, LAYOUT

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout=LAYOUT)

# === HERO SECTION ===
st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown("### Discover the truth about what you eat")

# === SEARCH BAR ===
st.markdown("---")
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("## 🔍 What food are you curious about?")
    search_query = st.text_input("", placeholder="Try: chocolate, yogurt, cereal...", label_visibility="collapsed")
    
    if search_query:
        # Use SQL Search
        results = search_products(search_query)
        
        if not results.empty:
            st.success(f"Found {len(results)} matching products")
            st.markdown("#### 🏆 Top Results:")
            for idx, row in results.iterrows():
                grade = str(row['nutriscore_grade']).upper()
                score = row['nutriscore_score']
                grade_colors = {'A': '🟢', 'B': '🟡', 'C': '🟠', 'D': '🔴', 'E': '⛔'}
                emoji = grade_colors.get(grade, '⚪')
                
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**{row['product_name']}**")
                c2.markdown(f"{emoji} Grade **{grade}**")
                c3.markdown(f"Score: **{score}**")
        else:
            st.warning(f"No products found for '{search_query}'.")

st.markdown("---")

# === SHOCKING STATS (From DB) ===
st.markdown("## 🚨 Database Insights")

# Get stats from DB
stats = get_dashboard_stats()
if not stats.empty:
    row = stats.iloc[0]
    total = row['total']
    poor_pct = (row['poor_count'] / total * 100)
    ultra_pct = (row['ultra_processed_count'] / total * 100)
    good_pct = (row['healthy_count'] / total * 100)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div style='background-color:#ff4444;padding:20px;border-radius:10px;text-align:center;'><h2 style='color:white;margin:0;'>{poor_pct:.0f}%</h2><p style='color:white;margin:0;'>POOR Nutrition (D/E)</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='background-color:#ff9800;padding:20px;border-radius:10px;text-align:center;'><h2 style='color:white;margin:0;'>{ultra_pct:.0f}%</h2><p style='color:white;margin:0;'>Ultra-Processed (NOVA 4)</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div style='background-color:#4CAF50;padding:20px;border-radius:10px;text-align:center;'><h2 style='color:white;margin:0;'>{good_pct:.0f}%</h2><p style='color:white;margin:0;'>Healthy (A/B)</p></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🎯 Explore the Sidebar for Deep Dives, Comparisons, and Swaps!")