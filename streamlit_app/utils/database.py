import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import pandas as pd
from typing import Optional

# Import config - using try/except for robustness
try:
    import sys
    import os
    # Get the parent directory of utils (which is streamlit_app)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_file_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from config import DB_CONFIG
except:
    # Fallback config if import fails
    DB_CONFIG = {
        'host': 'localhost',
        'port': '5432',
        'database': 'food_nutrition_db',
        'user': 'analyst_user',
        'password': 'analyst_pass'
    }

@st.cache_resource
def get_engine():
    """Create and cache database engine"""
    connection_string = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(connection_string, poolclass=NullPool)

@st.cache_data(ttl=600)
def execute_query(query: str, params: Optional[dict] = None) -> pd.DataFrame:
    """Execute SQL query and return results as DataFrame"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            if params:
                result = pd.read_sql(text(query), conn, params=params)
            else:
                result = pd.read_sql(text(query), conn)
        return result
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()

def test_connection():
    """Test database connection"""
    try:
        df = execute_query("SELECT 1 as test")
        return len(df) > 0
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

@st.cache_data(ttl=3600)
def get_database_stats():
    """Get basic database statistics"""
    stats = {}
    
    try:
        # Total products
        df = execute_query("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = int(df['count'].iloc[0]) if not df.empty else 0
        
        # Total brands
        df = execute_query("SELECT COUNT(*) as count FROM brands")
        stats['total_brands'] = int(df['count'].iloc[0]) if not df.empty else 0
        
        # Total categories
        df = execute_query("SELECT COUNT(*) as count FROM categories")
        stats['total_categories'] = int(df['count'].iloc[0]) if not df.empty else 0
        
        # Total countries (if countries table exists)
        try:
            df = execute_query("SELECT COUNT(*) as count FROM countries")
            stats['total_countries'] = int(df['count'].iloc[0]) if not df.empty else 0
        except:
            # If countries table doesn't exist, try products table
            df = execute_query("SELECT COUNT(DISTINCT country_name) as count FROM products WHERE country_name IS NOT NULL")
            stats['total_countries'] = int(df['count'].iloc[0]) if not df.empty else 0
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        stats = {
            'total_products': 0,
            'total_brands': 0,
            'total_categories': 0,
            'total_countries': 0
        }
    
    return stats