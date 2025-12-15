import streamlit as st
import pandas as pd
from utils.queries import search_products, get_product_details, find_healthier_alternatives

st.set_page_config(page_title="My Healthy Swap List", page_icon="🔄", layout="wide")
st.title("🔄 My Healthy Swap List")
st.markdown("### Build your grocery list and discover healthier alternatives")

# Initialize Session State
if 'grocery_list' not in st.session_state:
    st.session_state.grocery_list = []

# ==============================================================================
# 1. BUILD YOUR LIST
# ==============================================================================
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    search_term = st.text_input("Search product to add:", placeholder="e.g. Nutella, Coca Cola, Doritos")

with col2:
    st.write("") # Spacer
    st.write("") # Spacer
    # We don't strictly need a button here as text_input triggers on enter, 
    # but it helps UI alignment

if search_term:
    # Efficient SQL Search
    results = search_products(search_term, limit=10)
    
    if not results.empty:
        selected = st.selectbox("Select exact product:", results['product_name'].tolist())
        
        if st.button("➕ Add to List"):
            if selected not in st.session_state.grocery_list:
                st.session_state.grocery_list.append(selected)
                st.success(f"Added **{selected}** to your list!")
                st.rerun()
            else:
                st.warning("Item already in list.")
    else:
        st.warning("No products found.")

# ==============================================================================
# 2. CURRENT LIST DISPLAY
# ==============================================================================
if st.session_state.grocery_list:
    st.markdown("---")
    st.header("📋 Your Grocery List")
    
    # Display list items with remove buttons
    for item in st.session_state.grocery_list:
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**• {item}**")
        if c2.button("🗑️ Remove", key=f"del_{item}"):
            st.session_state.grocery_list.remove(item)
            st.rerun()

    # ==========================================================================
    # 3. FIND SWAPS & CALCULATE IMPACT
    # ==========================================================================
    st.markdown("---")
    if st.button("🔍 Find Healthier Alternatives", type="primary", use_container_width=True):
        
        st.header("🎯 Recommended Swaps")
        
        # Initialize counters for Total Impact
        total_sugar_saved = 0.0
        total_protein_gained = 0.0
        total_calories_saved = 0.0
        swap_count = 0
        
        # Iterate through list
        for item in st.session_state.grocery_list:
            # Get details from DB
            details = get_product_details(item)
            
            if not details.empty:
                prod = details.iloc[0]
                
                # Extract current values (handle None/NaN safely)
                p_sugar = float(prod.get('sugars_100g') or 0)
                p_protein = float(prod.get('proteins_100g') or 0)
                p_energy = float(prod.get('energy_kcal_100g') or 0)
                
                # Find swaps using SQL
                swaps = find_healthier_alternatives(item, p_sugar, p_protein, p_energy)
                
                if not swaps.empty:
                    best = swaps.iloc[0]
                    
                    # Extract new values
                    b_sugar = float(best.get('sugars_100g') or 0)
                    b_protein = float(best.get('proteins_100g') or 0)
                    b_energy = float(best.get('energy_kcal_100g') or 0)
                    
                    # Calculate savings
                    s_saved = p_sugar - b_sugar
                    p_gained = b_protein - p_protein
                    e_saved = p_energy - b_energy
                    
                    # Add to totals (only if positive improvement)
                    total_sugar_saved += max(0, s_saved)
                    total_protein_gained += max(0, p_gained)
                    total_calories_saved += max(0, e_saved)
                    swap_count += 1
                    
                    # Display Swap Card
                    with st.expander(f"🔄 Swap found for: {item}", expanded=True):
                        c1, c2, c3 = st.columns([2, 1, 2])
                        
                        with c1:
                            st.markdown("🔴 **Current Choice**")
                            st.write(f"{item}")
                            st.caption(f"Sugar: {p_sugar:.1f}g | Protein: {p_protein:.1f}g")
                        
                        with c2:
                            st.markdown("## ➡️")
                        
                        with c3:
                            st.markdown("🟢 **Better Alternative**")
                            st.write(f"**{best['product_name']}**")
                            st.caption(f"Sugar: {b_sugar:.1f}g | Protein: {b_protein:.1f}g")
                        
                        # Individual Impact
                        st.success(f"✅ Save **{s_saved:.1f}g** Sugar & Gain **{p_gained:.1f}g** Protein per 100g!")
                else:
                    st.info(f"👍 **{item}** is already a solid choice! (No significantly better swaps found)")
            else:
                st.warning(f"Could not retrieve details for {item}")

        # ======================================================================
        # 4. TOTAL HEALTH IMPROVEMENT SECTION
        # ======================================================================
        if swap_count > 0:
            st.markdown("---")
            st.markdown("## 🏆 Total Health Improvement")
            st.markdown("If you make these swaps every week, here is your impact:")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Sugar Reduced", f"{total_sugar_saved:.1f} g", help="Total sugar saved per 100g serving of each item")
            m2.metric("Protein Gained", f"{total_protein_gained:.1f} g", help="Total protein gained")
            m3.metric("Calories Cut", f"{total_calories_saved:.0f} kcal", help="Total calories reduced")
            
            # Motivational Notes
            st.success(f"""
            ### 🎉 Amazing Progress!
            By making these **{swap_count} simple swaps**, you are significantly improving your nutritional intake.
            - **{total_sugar_saved:.1f}g less sugar** is roughly **{int(total_sugar_saved/4)} sugar cubes**! 🧊
            - Small changes add up to big results over time.
            """)
            
            st.balloons()

    # ==========================================================================
    # 5. CLEAR LIST BUTTON
    # ==========================================================================
    st.markdown("---")
    if st.button("🗑️ Clear Entire List", type="secondary"):
        st.session_state.grocery_list = []
        st.rerun()

else:
    # Empty State
    st.info("👆 Add products to your grocery list to get started!")
    
    st.markdown("---")
    st.markdown("### 💡 Example Lists")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🥤 Beverages**\n- Coca-Cola\n- Orange Juice")
    with c2:
        st.markdown("**🍪 Snacks**\n- Nutella\n- Doritos")