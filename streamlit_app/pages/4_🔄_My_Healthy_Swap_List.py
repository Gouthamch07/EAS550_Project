import streamlit as st
import pandas as pd
from utils.connector import get_data

st.set_page_config(page_title="My Healthy Swap List", page_icon="🔄", layout="wide")

# Load data
df_fact = get_data("fact_nutrition", schema="analytics")

st.title("🔄 My Healthy Swap List")
st.markdown("### Build your grocery list and discover healthier alternatives")

# === SESSION STATE FOR GROCERY LIST ===
if 'grocery_list' not in st.session_state:
    st.session_state.grocery_list = []

# === ADD TO GROCERY LIST ===
st.markdown("---")
st.markdown("## 🛒 Step 1: Build Your Current Grocery List")

col1, col2 = st.columns([3, 1])

with col1:
    search_product = st.text_input(
        "Search for a product you regularly buy:",
        placeholder="e.g., Coca Cola, Nutella, Doritos",
        key="product_search"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    add_button = st.button("➕ Add to List", use_container_width=True)

if search_product:
    results = df_fact[df_fact['product_name'].str.contains(search_product, case=False, na=False)]
    
    if len(results) > 0:
        selected_product = st.selectbox(
            "Select the exact product:",
            results['product_name'].tolist(),
            key="product_select"
        )
        
        if add_button and selected_product:
            if selected_product not in st.session_state.grocery_list:
                st.session_state.grocery_list.append(selected_product)
                st.success(f"✅ Added '{selected_product}' to your list!")
                st.rerun()
            else:
                st.warning("This product is already in your list!")

# === DISPLAY CURRENT LIST ===
if len(st.session_state.grocery_list) > 0:
    st.markdown("---")
    st.markdown("## 📋 Your Current Grocery List")
    
    for idx, item in enumerate(st.session_state.grocery_list):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{idx + 1}.** {item}")
        with col2:
            if st.button("🗑️ Remove", key=f"remove_{idx}"):
                st.session_state.grocery_list.pop(idx)
                st.rerun()
    
    # === FIND HEALTHIER SWAPS ===
    st.markdown("---")
    st.markdown("## 💡 Step 2: Discover Healthier Swaps")
    
    if st.button("🔍 Find Healthier Alternatives", use_container_width=True, type="primary"):
        st.markdown("---")
        st.markdown("## 🎯 Recommended Swaps")
        
        total_sugar_saved = 0
        total_protein_gained = 0
        total_calories_saved = 0
        
        swap_recommendations = []
        
        for product in st.session_state.grocery_list:
            # Get current product data
            current_data = df_fact[df_fact['product_name'] == product]
            
            if len(current_data) == 0:
                continue
            
            current_data = current_data.iloc[0]
            current_sugar = current_data.get('sugars_100g', 0)
            current_protein = current_data.get('proteins_100g', 0)
            current_energy = current_data.get('energy_kcal_100g', 0)
            
            # Find category (simplified: use first word of product name)
            category_keyword = product.split()[0].lower()
            
            # Find similar products (same category keyword)
            similar_products = df_fact[
                df_fact['product_name'].str.contains(category_keyword, case=False, na=False) &
                (df_fact['product_name'] != product)
            ].copy()
            
            if len(similar_products) == 0:
                continue
            
            # Find healthier alternatives (lower sugar, higher protein)
            healthier = similar_products[
                (similar_products['sugars_100g'] < current_sugar) &
                (similar_products['proteins_100g'] >= current_protein * 0.8)  # Allow 20% less protein
            ]
            
            if len(healthier) > 0:
                # Get best alternative (lowest sugar)
                best_alternative = healthier.nsmallest(1, 'sugars_100g').iloc[0]
                
                alt_name = best_alternative['product_name']
                alt_sugar = best_alternative.get('sugars_100g', 0)
                alt_protein = best_alternative.get('proteins_100g', 0)
                alt_energy = best_alternative.get('energy_kcal_100g', 0)
                
                # Calculate improvements
                sugar_diff = current_sugar - alt_sugar
                protein_diff = alt_protein - current_protein
                energy_diff = current_energy - alt_energy
                
                total_sugar_saved += sugar_diff
                total_protein_gained += protein_diff
                total_calories_saved += energy_diff
                
                # Display swap recommendation
                st.markdown(f"### 🔄 Swap Recommendation #{len(swap_recommendations) + 1}")
                
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    st.markdown("**Current:**")
                    st.markdown(f"🔴 {product[:40]}")
                    st.caption(f"🍬 Sugar: {current_sugar:.1f}g | 💪 Protein: {current_protein:.1f}g | ⚡ {current_energy:.0f} kcal")
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### ➡️")
                
                with col3:
                    st.markdown("**Healthier Alternative:**")
                    st.markdown(f"🟢 {alt_name[:40]}")
                    st.caption(f"🍬 Sugar: {alt_sugar:.1f}g | 💪 Protein: {alt_protein:.1f}g | ⚡ {alt_energy:.0f} kcal")
                
                # Show improvements
                improvements = []
                if sugar_diff > 0:
                    improvements.append(f"💚 **{sugar_diff:.1f}g less sugar**")
                if protein_diff > 0:
                    improvements.append(f"💪 **{protein_diff:.1f}g more protein**")
                if energy_diff > 0:
                    improvements.append(f"⚡ **{energy_diff:.0f} fewer calories**")
                
                if improvements:
                    st.success(" | ".join(improvements))
                
                swap_recommendations.append({
                    'current': product,
                    'alternative': alt_name,
                    'sugar_saved': sugar_diff,
                    'protein_gained': protein_diff,
                    'calories_saved': energy_diff
                })
                
                st.markdown("---")
            else:
                st.info(f"ℹ️ No healthier alternatives found for **{product}** (it might already be one of the best choices!)")
                st.markdown("---")
        
        # === TOTAL IMPACT ===
        if len(swap_recommendations) > 0:
            st.markdown("## 🏆 Total Health Improvement")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style='background-color: #4CAF50; padding: 20px; border-radius: 10px; text-align: center;'>
                    <h2 style='color: white; margin: 0;'>{total_sugar_saved:.1f}g</h2>
                    <p style='color: white; margin: 5px 0 0 0;'>Less Sugar per Week</p>
                </div>
                """, unsafe_allow_html=True)
                st.caption("≈ " + str(int(total_sugar_saved / 4)) + " sugar cubes! 🧊")
            
            with col2:
                st.markdown(f"""
                <div style='background-color: #2196F3; padding: 20px; border-radius: 10px; text-align: center;'>
                    <h2 style='color: white; margin: 0;'>{total_protein_gained:.1f}g</h2>
                    <p style='color: white; margin: 5px 0 0 0;'>More Protein per Week</p>
                </div>
                """, unsafe_allow_html=True)
                st.caption("💪 Build muscle, stay full longer")
            
            with col3:
                st.markdown(f"""
                <div style='background-color: #FF9800; padding: 20px; border-radius: 10px; text-align: center;'>
                    <h2 style='color: white; margin: 0;'>{total_calories_saved:.0f}</h2>
                    <p style='color: white; margin: 5px 0 0 0;'>Fewer Calories per Week</p>
                </div>
                """, unsafe_allow_html=True)
                st.caption("⚖️ Better weight management")
            
            # === DOWNLOAD SWAP LIST ===
            st.markdown("---")
            swap_df = pd.DataFrame(swap_recommendations)
            csv = swap_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download My Swap List",
                data=csv,
                file_name="my_healthy_swaps.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # === MOTIVATIONAL MESSAGE ===
            st.markdown("---")
            st.success(f"""
            ### 🎉 Amazing Progress!
            
            By making these **{len(swap_recommendations)} simple swaps**, you're:
            - Reducing sugar intake by **{total_sugar_saved:.0f}g per week** (that's **{total_sugar_saved * 52:.0f}g per year**!)
            - Adding **{total_protein_gained:.0f}g** more protein weekly
            - Cutting **{total_calories_saved:.0f}** calories without feeling deprived
            
            💡 **Small changes, BIG impact!** Keep it up!
            """)
        else:
            st.info("No swap recommendations available. Your current list might already be pretty healthy! 🎉")
    
    # Clear list button
    st.markdown("---")
    if st.button("🗑️ Clear Entire List", type="secondary"):
        st.session_state.grocery_list = []
        st.rerun()

else:
    st.info("👆 Add products to your grocery list to get started!")
    
    # === EXAMPLE GROCERIES ===
    st.markdown("---")
    st.markdown("## 💡 Example Grocery Lists")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🥤 Typical Beverages:
        - Coca-Cola
        - Orange Juice
        - Energy Drink
        - Sweetened Coffee
        """)
    
    with col2:
        st.markdown("""
        ### 🍪 Common Snacks:
        - Doritos
        - Nutella
        - Oreos
        - Chips Ahoy
        """)

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>My Healthy Swap List | Building healthier habits, one swap at a time</p>
</div>
""", unsafe_allow_html=True)