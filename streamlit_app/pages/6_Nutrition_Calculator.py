import streamlit as st
import plotly.graph_objects as go
from utils.queries import find_similar_products_by_macros

st.set_page_config(page_title="Nutrition Calculator", page_icon="🧮", layout="wide")
st.title("🧮 Nutrition Calculator")
st.markdown("Estimate a Nutri-Score grade and find real products matching your macros.")

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⚠️ Negative Nutrients")
    energy = st.slider("Energy (kcal)", 0, 800, 250)
    sugar = st.slider("Sugar (g)", 0.0, 50.0, 10.0)
    sat_fat = st.slider("Saturated Fat (g)", 0.0, 20.0, 2.0) # Restored
    sodium = st.slider("Sodium (mg)", 0, 1000, 200)          # Restored

with col2:
    st.markdown("### ✅ Positive Nutrients")
    protein = st.slider("Protein (g)", 0.0, 50.0, 5.0)
    fiber = st.slider("Fiber (g)", 0.0, 20.0, 2.0)           # Added Fiber for completeness if you want

if st.button("Calculate & Find Matches", type="primary"):
    # === CALCULATION LOGIC (Simplified Nutri-Score) ===
    # Points for negatives (higher is worse)
    p_energy = min(10, int(energy / 80))
    p_sugar = min(10, int(sugar / 4.5))
    p_sat_fat = min(10, int(sat_fat / 1))
    p_sodium = min(10, int(sodium / 90))
    
    # Points for positives (higher is better)
    p_protein = min(5, int(protein / 1.6))
    p_fiber = min(5, int(fiber / 0.9))
    
    final_score = (p_energy + p_sugar + p_sat_fat + p_sodium) - (p_protein + p_fiber)
    
    # Map to Grade
    if final_score <= -1: grade, color = "A", "green"
    elif final_score <= 2: grade, color = "B", "lightgreen"
    elif final_score <= 10: grade, color = "C", "orange"
    elif final_score <= 18: grade, color = "D", "red"
    else: grade, color = "E", "darkred"
    
    # === RESULT ===
    st.markdown("---")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
        <div style='background-color:{color};padding:20px;border-radius:10px;text-align:center;color:white'>
            <h1>{grade}</h1>
            <p>Estimated Grade</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.info(f"Calculated Score: **{final_score}** (Lower is better)")
        st.write("This calculation is an approximation based on the official Nutri-Score algorithm.")

    # === REAL PRODUCT MATCHES ===
    st.markdown("---")
    st.subheader("🔍 Real Products with Similar Macros")
    st.caption("Matching based on Energy, Sugar, and Protein")
    
    # We use the 3 main macros for search because they are most common
    matches = find_similar_products_by_macros(energy, sugar, protein)
    
    if not matches.empty:
        st.dataframe(
            matches[['product_name', 'brand_name', 'energy_kcal_100g', 'sugars_100g', 'proteins_100g']], 
            use_container_width=True
        )
    else:
        st.warning("No exact matches found in database for this specific profile.")