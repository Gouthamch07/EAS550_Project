import streamlit as st
import sys
import os

# Add current directory to path - Fixed version
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
sys.path.insert(0, current_dir)

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
    connection_status = test_connection()
    
    if connection_status:
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
        
        # Show connection details for debugging
        with st.expander("🔧 Connection Details"):
            st.code(f"""
Database Host: localhost
Database Port: 5432
Database Name: food_nutrition_db
Database User: analyst_user

Check if Docker is running:
  docker ps

If not running:
  cd docker
  docker-compose up -d
            """)

# Introduction
st.markdown("---")
st.markdown("""
Welcome to the **Global Food & Nutrition Explorer**! This application provides comprehensive 
insights into food products from around the world using the Open Food Facts dataset.

### 🎯 Features

Navigate through the sidebar to explore:

- **🔬 Nutritional Deep Dive**: Analyze nutritional content across categories and grades
- **🏢 Brand Intelligence**: Compare brands and their product portfolios  
- **🔍 Product Search**: Find specific products and their details

### 🚀 Getting Started

1. Ensure your database is running (`docker-compose up -d`)
2. Select a page from the sidebar
3. Use filters to customize your analysis
4. Hover over charts for detailed information

### 📖 About the Data

This project uses the **Open Food Facts** dataset - a free, open database of food products from around the world.
The data has been cleaned, normalized to 3NF, and optimized for analytical queries.
""")

st.markdown("---")
st.info("👈 **Select a page from the sidebar to begin exploring!**")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>EAS 550 Project | Global Food & Nutrition Explorer</p>
    <p>Akash Ankush Kamble, Nidhi Rajani, Goutham Chengalvala</p>
</div>
""", unsafe_allow_html=True)