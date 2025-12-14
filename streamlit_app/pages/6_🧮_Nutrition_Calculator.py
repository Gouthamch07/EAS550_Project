import streamlit as st
import plotly.graph_objects as go
from utils.queries import find_similar_products_by_macros

st.set_page_config(page_title="Nutrition Calculator", page_icon="🧮", layout="wide")
st.title("🧮 Nutrition Calculator")

col1, col2 = st.columns(2)
with col1:
    energy = st.slider("Energy (kcal)", 0, 800, 250)
    sugar = st.slider("Sugar (g)", 0.0, 50.0, 10.0)
with col2:
    fat = st.slider("Fat (g)", 0.0, 50.0, 5.0)
    protein = st.slider("Protein (g)", 0.0, 50.0, 5.0)

if st.button("Calculate & Find Matches", type="primary"):
    # Simple Score Logic
    score = 0
    if sugar > 20: score += 5
    if fat > 10: score += 5
    if protein > 10: score -= 5
    
    grade = "A" if score < 0 else ("C" if score < 5 else "E")
    color = "green" if grade == "A" else ("orange" if grade == "C" else "red")
    
    st.markdown(f"<h1 style='color:{color};text-align:center'>Estimated Grade: {grade}</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🔍 Real Products with this Profile")
    
    # Use SQL to find matches
    matches = find_similar_products_by_macros(energy, sugar, protein)
    
    if not matches.empty:
        st.dataframe(matches, use_container_width=True)
    else:
        st.info("No exact matches found in database.")