import streamlit as st
import pandas as pd
import plotly.express as px
from utils.queries import search_products, get_product_details, find_similar_products_by_macros

st.set_page_config(page_title="Find Your Health Twin", page_icon="🎯", layout="wide")

st.title("🎯 Find Your Health Twin")
st.markdown("### Discover products similar to your favorites, ranked by healthiness")

# === PRODUCT SELECTION ===
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    search_fav = st.text_input("What's your favorite product?", placeholder="e.g., Nutella")

if search_fav:
    results = search_products(search_fav)
    if not results.empty:
        favorite_product = st.selectbox("Select your favorite:", results['product_name'].tolist())
        
        if favorite_product:
            # Get details
            details = get_product_details(favorite_product).iloc[0]
            fav_energy = float(details.get('energy_kcal_100g') or 0)
            fav_sugar = float(details.get('sugars_100g') or 0)
            fav_protein = float(details.get('proteins_100g') or 0)
            
            st.markdown(f"### 📌 Your Choice: {favorite_product}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Energy", f"{fav_energy:.0f} kcal")
            c2.metric("Sugar", f"{fav_sugar:.1f}g")
            c3.metric("Protein", f"{fav_protein:.1f}g")
            
            st.markdown("---")
            
            # Dynamic Tolerance Loop
            similar_products = pd.DataFrame()
            current_tolerance = 0.2
            found_match = False
            
            with st.spinner("Hunting for twins..."):
                while not found_match and current_tolerance <= 0.6:
                    similar_products = find_similar_products_by_macros(
                        fav_energy, fav_sugar, fav_protein, tolerance=current_tolerance
                    )
                    if not similar_products.empty:
                        similar_products = similar_products[similar_products['product_name'] != favorite_product]
                    
                    if len(similar_products) > 0:
                        found_match = True
                    else:
                        current_tolerance += 0.1
            
            if len(similar_products) > 0:
                if current_tolerance > 0.21: 
                    st.info(f"⚠️ Widened search tolerance to +/- {current_tolerance*100:.0f}% to find matches.")

                # === RECOMMENDED SWAP ===
                # Find the one with lowest sugar
                best_twin = similar_products.sort_values('sugars_100g', ascending=True).iloc[0]
                best_sugar = float(best_twin.get('sugars_100g') or 0)
                
                if best_sugar < fav_sugar:
                    st.success(f"""
                    ### 🎯 Recommended Swap: **{best_twin['product_name']}**
                    It has **{fav_sugar - best_sugar:.1f}g less sugar** than your favorite!
                    """)
                else:
                    st.info("Your favorite is already quite healthy compared to its twins!")

                # === SCATTER PLOT VISUALIZATION ===
                st.markdown("### 📊 Nutrition Profile Comparison")
                
                # Prepare data for plot
                plot_data = similar_products.copy()
                plot_data['Type'] = 'Twin'
                
                # Add favorite
                fav_df = pd.DataFrame([{
                    'product_name': favorite_product,
                    'sugars_100g': fav_sugar,
                    'proteins_100g': fav_protein,
                    'energy_kcal_100g': fav_energy,
                    'Type': 'Your Favorite'
                }])
                plot_data = pd.concat([plot_data, fav_df], ignore_index=True)
                
                fig = px.scatter(
                    plot_data,
                    x='sugars_100g',
                    y='proteins_100g',
                    size='energy_kcal_100g',
                    color='Type',
                    hover_name='product_name',
                    title='Sugar vs Protein (Size = Calories)',
                    color_discrete_map={'Your Favorite': 'red', 'Twin': 'blue'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Table
                st.markdown("### 📋 Detailed List")
                st.dataframe(similar_products[['product_name', 'brand_name', 'sugars_100g', 'proteins_100g']], use_container_width=True)
                
            else:
                st.warning("No similar products found.")
    else:
        st.warning("No products found.")