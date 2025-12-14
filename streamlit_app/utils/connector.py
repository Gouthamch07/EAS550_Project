# streamlit_app/utils/connector.py
import streamlit as st
import pandas as pd
import psycopg2

@st.cache_data
def get_data(table_name, schema="analytics"):
    """
    Get data from PostgreSQL database
    
    Args:
        table_name: Name of the table (without schema prefix)
        schema: Schema name (default: analytics)
    """
    conn = psycopg2.connect(
        dbname="food_nutrition_db",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    
    # Add schema prefix
    query = f"SELECT * FROM {schema}.{table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df