import streamlit as st
import pandas as pd
import plotly.express as px
from utils.connector import get_data

st.set_page_config(page_title="Find Your Health Twin", page_icon="🎯", layout="wide")

# Load data
df_fact = get_data("fact_nutrition", schema="analytics")

st.title("🎯 Find Your Health Twin")
st.markdown("### Discover products similar to your favorites, ranked by healthiness")

# === PRODUCT SELECTION ===
st.markdown("---")
st.markdown("## Step 1: Pick Your Favorite Product")

col1, col2 = st.columns([3, 1])

with col1:
    search_fav = st.text_input(
        "What's your favorite product?",
        placeholder="e.g., Nutella, Coca Cola, Doritos, Ben & Jerry's",
        key="fav_search"
    )

if search_fav:
    results = df_fact[df_fact['product_name'].str.contains(search_fav, case=False, na=False)]
    
    if len(results) > 0:
        favorite_product = st.selectbox(
            "Select your favorite:",
            results['product_name'].tolist(),
            key="fav_select"
        )
        
        if favorite_product:
            st.markdown("---")
            st.markdown("## Step 2: Meet Your Health Twins")
            
            # Get favorite product data
            fav_data = df_fact[df_fact['product_name'] == favorite_product].iloc[0]
            fav_energy = fav_data.get('energy_kcal_100g', 0)
            fav_sugar = fav_data.get('sugars_100g', 0)
            fav_fat = fav_data.get('fat_100g', 0)
            fav_protein = fav_data.get('proteins_100g', 0)
            
            # Display favorite product stats
            st.markdown(f"### 📌 Your Current Choice: {favorite_product}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("⚡ Energy", f"{fav_energy:.0f} kcal")
            col2.metric("🍬 Sugar", f"{fav_sugar:.1f}g")
            col3.metric("🧈 Fat", f"{fav_fat:.1f}g")
            col4.metric("💪 Protein", f"{fav_protein:.1f}g")
            
            st.markdown("---")
            
            # Find category keyword
            category_keyword = favorite_product.split()[0].lower()
            
            # Find similar products
            tolerance = 0.3  # 30% tolerance
            
            similar_products = df_fact[
                (df_fact['product_name'] != favorite_product) &
                (df_fact['product_name'].str.contains(category_keyword, case=False, na=False)) &
                (df_fact['energy_kcal_100g'].between(fav_energy * (1-tolerance), fav_energy * (1+tolerance))) &
                (df_fact['fat_100g'].between(fav_fat * (1-tolerance), fav_fat * (1+tolerance)))
            ].copy()
            
            if len(similar_products) > 0:
                # Calculate similarity score (lower sugar + higher protein = better)
                similar_products['health_score'] = (
                    -similar_products['sugars_100g'] + 
                    similar_products['proteins_100g']
                )
                
                # Sort by health score
                similar_products = similar_products.sort_values('health_score', ascending=False)
                
                # Assign categories
                def categorize_product(row):
                    if row['sugars_100g'] < fav_sugar and row['proteins_100g'] >= fav_protein:
                        return "🟢 Healthier Alternative"
                    elif row['sugars_100g'] <= fav_sugar * 1.1 and row['proteins_100g'] >= fav_protein * 0.9:
                        return "🟡 Similar Health Profile"
                    else:
                        return "🔴 Less Healthy"
                
                similar_products['category'] = similar_products.apply(categorize_product, axis=1)
                
                # Display results
                st.markdown("### 🏆 Products Ranked by Healthiness")
                st.caption(f"Found {len(similar_products)} similar products with comparable taste/texture profile")
                
                # Show top 15
                top_products = similar_products.head(15)
                
                for idx, row in top_products.iterrows():
                    category = row['category']
                    
                    # Create expandable section
                    with st.expander(f"{category} - {row['product_name'][:60]}", expanded=(idx == top_products.index[0])):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Brand:** {row.get('brand_name', 'Unknown')}")
                            
                            # Nutrition comparison
                            energy_diff = row['energy_kcal_100g'] - fav_energy
                            sugar_diff = row['sugars_100g'] - fav_sugar
                            fat_diff = row['fat_100g'] - fav_fat
                            protein_diff = row['proteins_100g'] - fav_protein
                            
                            st.markdown("**Compared to your favorite:**")
                            
                            if abs(energy_diff) > 10:
                                emoji = "⬇️" if energy_diff < 0 else "⬆️"
                                st.markdown(f"{emoji} Energy: {abs(energy_diff):.0f} kcal {'less' if energy_diff < 0 else 'more'}")
                            
                            if abs(sugar_diff) > 0.5:
                                emoji = "💚" if sugar_diff < 0 else "⚠️"
                                st.markdown(f"{emoji} Sugar: {abs(sugar_diff):.1f}g {'less' if sugar_diff < 0 else 'more'}")
                            
                            if abs(fat_diff) > 0.5:
                                emoji = "⬇️" if fat_diff < 0 else "⬆️"
                                st.markdown(f"{emoji} Fat: {abs(fat_diff):.1f}g {'less' if fat_diff < 0 else 'more'}")
                            
                            if abs(protein_diff) > 0.5:
                                emoji = "💪" if protein_diff > 0 else "⬇️"
                                st.markdown(f"{emoji} Protein: {abs(protein_diff):.1f}g {'more' if protein_diff > 0 else 'less'}")
                        
                        with col2:
                            # Create simple bar chart with unique key
                            comparison_data = pd.DataFrame({
                                'Nutrient': ['Energy', 'Sugar', 'Fat', 'Protein'],
                                'Your Favorite': [fav_energy, fav_sugar, fav_fat, fav_protein],
                                'This Product': [
                                    row['energy_kcal_100g'],
                                    row['sugars_100g'],
                                    row['fat_100g'],
                                    row['proteins_100g']
                                ]
                            })
                            
                            fig = px.bar(
                                comparison_data,
                                x='Nutrient',
                                y=['Your Favorite', 'This Product'],
                                barmode='group',
                                height=200
                            )
                            fig.update_layout(
                                showlegend=True,
                                margin=dict(l=0, r=0, t=0, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )
                            # FIX: Added unique key using index
                            st.plotly_chart(fig, use_container_width=True, key=f"comparison_chart_{idx}")
                
                # === BEST SWAP RECOMMENDATION ===
                st.markdown("---")
                healthiest = similar_products.iloc[0]
                
                if healthiest['category'] == "🟢 Healthier Alternative":
                    sugar_saved = fav_sugar - healthiest['sugars_100g']
                    protein_gained = healthiest['proteins_100g'] - fav_protein
                    
                    st.success(f"""
                    ### 🎯 Recommended Swap:
                    
                    **{healthiest['product_name']}**
                    
                    This product offers similar taste/texture but with better nutrition:
                    - {abs(sugar_saved):.1f}g less sugar
                    - {abs(protein_gained):.1f}g more protein
                    
                    💡 **Impact:** Making this swap could save you **{sugar_saved * 52:.0f}g** of sugar per year (assuming weekly consumption)!
                    """)
                else:
                    st.info(f"""
                    ### ℹ️ Good News!
                    
                    **{favorite_product}** is already one of the better choices in its category!
                    
                    Most similar products have comparable or worse nutrition profiles.
                    """)
                
                # === VISUALIZATION ===
                st.markdown("---")
                st.markdown("### 📊 Nutrition Profile Comparison")
                
                # Create scatter plot
                plot_data = similar_products.head(20).copy()
                plot_data['is_favorite'] = False
                
                # Add favorite product
                fav_row = pd.DataFrame([{
                    'product_name': favorite_product,
                    'sugars_100g': fav_sugar,
                    'proteins_100g': fav_protein,
                    'energy_kcal_100g': fav_energy,
                    'category': "⭐ Your Favorite",
                    'is_favorite': True
                }])
                
                plot_data = pd.concat([plot_data, fav_row], ignore_index=True)
                
                fig_scatter = px.scatter(
                    plot_data,
                    x='sugars_100g',
                    y='proteins_100g',
                    size='energy_kcal_100g',
                    color='category',
                    hover_name='product_name',
                    title='Sugar vs Protein Content (size = energy)',
                    labels={
                        'sugars_100g': 'Sugar (g/100g)',
                        'proteins_100g': 'Protein (g/100g)'
                    },
                    color_discrete_map={
                        '🟢 Healthier Alternative': '#4CAF50',
                        '🟡 Similar Health Profile': '#FFC107',
                        '🔴 Less Healthy': '#F44336',
                        '⭐ Your Favorite': '#2196F3'
                    }
                )
                
                fig_scatter.update_layout(height=500)
                st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_plot_main")
                
            else:
                st.warning(f"No similar products found for '{favorite_product}'. Try a different product!")
    
    else:
        st.warning(f"No products found matching '{search_fav}'. Try a different search term!")

else:
    # === SHOW POPULAR EXAMPLES ===
    st.markdown("---")
    st.markdown("## 💡 Try These Popular Products")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🍫 Spreads
        - Nutella
        - Peanut Butter
        - Almond Butter
        - Cookie Butter
        """)
    
    with col2:
        st.markdown("""
        ### 🥤 Drinks
        - Coca-Cola
        - Red Bull
        - Orange Juice
        - Starbucks Frappuccino
        """)
    
    with col3:
        st.markdown("""
        ### 🍪 Snacks
        - Doritos
        - Oreos
        - Pringles
        - Cheetos
        """)

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Find Your Health Twin | Discover better alternatives without sacrificing taste</p>
</div>
""", unsafe_allow_html=True)