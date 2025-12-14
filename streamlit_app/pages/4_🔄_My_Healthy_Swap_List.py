import streamlit as st
from utils.queries import search_products, get_product_details, find_healthier_alternatives

st.set_page_config(page_title="My Healthy Swap List", page_icon="🔄", layout="wide")
st.title("🔄 My Healthy Swap List")

if 'grocery_list' not in st.session_state:
    st.session_state.grocery_list = []

# 1. Build List
col1, col2 = st.columns([3, 1])
with col1:
    search_term = st.text_input("Search product to add:", placeholder="e.g. Nutella")
with col2:
    st.write("")
    add_btn = st.button("Search")

if search_term:
    results = search_products(search_term, limit=10)
    if not results.empty:
        selected = st.selectbox("Select product:", results['product_name'].tolist())
        if st.button("➕ Add to List"):
            if selected not in st.session_state.grocery_list:
                st.session_state.grocery_list.append(selected)
                st.success(f"Added {selected}")
                st.rerun()

# 2. Show List & Swaps
if st.session_state.grocery_list:
    st.markdown("---")
    st.header("Your List & Recommendations")
    
    for item in st.session_state.grocery_list:
        with st.expander(f"📦 {item}", expanded=True):
            # Get details from DB
            details = get_product_details(item)
            if not details.empty:
                prod = details.iloc[0]
                
                # Find swaps using SQL
                swaps = find_healthier_alternatives(
                    item, 
                    prod['sugars_100g'], 
                    prod['proteins_100g'], 
                    prod['energy_kcal_100g']
                )
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Current Choice**")
                    st.error(f"{item}")
                    st.caption(f"Sugar: {prod['sugars_100g']}g | Protein: {prod['proteins_100g']}g")
                
                with c2:
                    st.markdown("**Healthier Alternative**")
                    if not swaps.empty:
                        best = swaps.iloc[0]
                        st.success(f"{best['product_name']}")
                        st.caption(f"Sugar: {best['sugars_100g']}g | Protein: {best['proteins_100g']}g")
                        st.markdown(f"**Savings:** {prod['sugars_100g'] - best['sugars_100g']:.1f}g Sugar!")
                    else:
                        st.info("This is already a great choice!")
            
            if st.button("Remove", key=item):
                st.session_state.grocery_list.remove(item)
                st.rerun()