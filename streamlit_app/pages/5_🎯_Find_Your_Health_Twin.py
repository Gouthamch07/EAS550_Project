import streamlit as st
from utils.queries import search_products, get_product_details, find_similar_products_by_macros

st.set_page_config(page_title="Find Your Health Twin", page_icon="🎯", layout="wide")
st.title("🎯 Find Your Health Twin")

search_term = st.text_input("Enter your favorite product:", placeholder="e.g. Nutella")

if search_term:
    results = search_products(search_term)
    if not results.empty:
        selected = st.selectbox("Select exact product:", results['product_name'].tolist())
        
        if selected:
            # Get details
            details = get_product_details(selected).iloc[0]
            
            st.markdown("### 📌 Your Product Stats")
            c1, c2, c3 = st.columns(3)
            c1.metric("Energy", f"{details['energy_kcal_100g']} kcal")
            c2.metric("Sugar", f"{details['sugars_100g']} g")
            c3.metric("Protein", f"{details['proteins_100g']} g")
            
            st.markdown("---")
            st.subheader("👯 Health Twins (Similar Nutrition)")
            
            # Find twins using SQL
            twins = find_similar_products_by_macros(
                details['energy_kcal_100g'] or 0,
                details['sugars_100g'] or 0,
                details['proteins_100g'] or 0
            )
            
            if not twins.empty:
                # Filter out the product itself
                twins = twins[twins['product_name'] != selected]
                st.dataframe(twins[['product_name', 'brand_name', 'energy_kcal_100g', 'sugars_100g', 'proteins_100g']], use_container_width=True)
            else:
                st.info("No exact twins found.")
    else:
        st.warning("No products found.")