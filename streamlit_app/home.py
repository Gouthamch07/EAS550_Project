import streamlit as st
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(_file_)))

from utils.database import test_connection, get_database_stats
from config import APP_TITLE, APP_ICON, LAYOUT

# Page config
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Main page
st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown("### Explore Global Food & Nutrition Data")

# Connection status
with st.spinner("Testing database connection..."):
    if test_connection():
        st.success("✅ Database connection established")
        
        # Get and display statistics
        stats = get_database_stats()
        
        st.markdown("---")
        st.markdown("### 📊 Dataset Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Products", f"{stats['total_products']:,}")
        with col2:
            st.metric("Brands", f"{stats['total_brands']:,}")
        with col3:
            st.metric("Categories", f"{stats['total_categories']:,}")
        with col4:
            st.metric("Countries", f"{stats['total_countries']:,}")
    else:
        st.error("❌ Database connection failed. Please check your configuration.")
        st.info("Make sure your PostgreSQL database is running via Docker.")