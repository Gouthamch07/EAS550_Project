import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Nutrition Calculator", page_icon="🧮", layout="wide")

from utils.connector import get_data

# Load fact_nutrition (has all the nutrition columns)
df = get_data("fact_nutrition", schema="analytics")

# --- PAGE CONTENT ---
st.title("🧮 Interactive Nutrition Score Calculator")
st.markdown("""
Calculate the Nutri-Score for any food and discover similar or healthier products from our database of 100,000+ items.
""")

# --- CALCULATION LOGIC (SIMPLIFIED NUTRI-SCORE) ---
def calculate_nutriscore(energy, sugars, sat_fat, sodium, protein, fiber):
    # Points for "Negative" Nutrients (more points = worse)
    energy_points = min(10, max(0, int(energy / 335)))
    sugar_points = min(10, max(0, int(sugars / 4.5)))
    sat_fat_points = min(10, max(0, int(sat_fat / 1)))
    sodium_points = min(10, max(0, int(sodium / 90)))
    
    negative_points = energy_points + sugar_points + sat_fat_points + sodium_points
    
    # Points for "Positive" Nutrients (more points = better)
    protein_points = min(5, max(0, int(protein / 1.6)))
    fiber_points = min(5, max(0, int(fiber / 0.9)))
    
    # Final Score Calculation
    final_score = negative_points - (protein_points + fiber_points)
    
    # Map score to grade
    if final_score <= -1:
        grade = 'A'
        color = 'green'
    elif final_score <= 2:
        grade = 'B'
        color = 'lightgreen'
    elif final_score <= 10:
        grade = 'C'
        color = 'yellow'
    elif final_score <= 18:
        grade = 'D'
        color = 'orange'
    else:
        grade = 'E'
        color = 'red'
    
    return final_score, grade, color

# --- USER INPUT INTERFACE ---
st.markdown("---")
st.markdown("## ⚙️ Input Nutritional Values (per 100g)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⚠️ Negative Nutrients")
    energy_input = st.slider("⚡ Energy (kcal)", 0, 900, 250, help="Calories per 100g")
    sugars_input = st.slider("🍬 Sugars (g)", 0.0, 100.0, 10.0, 0.1, help="Sugar content per 100g")
    sat_fat_input = st.slider("🧈 Saturated Fat (g)", 0.0, 50.0, 5.0, 0.1, help="Saturated fat per 100g")
    sodium_input = st.slider("🧂 Sodium (mg)", 0, 2000, 500, help="Sodium content per 100g")

with col2:
    st.markdown("### ✅ Positive Nutrients")
    protein_input = st.slider("💪 Protein (g)", 0.0, 100.0, 8.0, 0.1, help="Protein content per 100g")
    fiber_input = st.slider("🌾 Fiber (g)", 0.0, 50.0, 3.0, 0.1, help="Fiber content per 100g")

st.markdown("---")

if st.button("🔍 Calculate Score & Find Products", use_container_width=True, type="primary"):
    score, grade, color = calculate_nutriscore(
        energy_input * 4.184,  # Convert to kJ
        sugars_input,
        sat_fat_input,
        sodium_input,
        protein_input,
        fiber_input
    )
    
    # === RESULTS SECTION ===
    st.markdown("---")
    st.markdown("## 📊 Your Results")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        # Grade display
        st.markdown(f"""
        <div style='background-color: {color}; padding: 30px; border-radius: 15px; text-align: center;'>
            <h1 style='color: white; font-size: 4em; margin: 0;'>{grade}</h1>
            <p style='color: white; font-size: 1.2em; margin: 10px 0 0 0;'>Nutrition Grade</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.metric("Calculated Score", f"{score}", help="Lower is better")
    
    with col3:
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Nutriscore", 'font': {'size': 20}},
            delta={'reference': 0, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge={
                'axis': {'range': [-10, 40], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-10, -1], 'color': '#4CAF50'},
                    {'range': [-1, 2], 'color': '#8BC34A'},
                    {'range': [2, 10], 'color': '#FFC107'},
                    {'range': [10, 18], 'color': '#FF9800'},
                    {'range': [18, 40], 'color': '#F44336'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    # === INTERPRETATION ===
    st.markdown("---")
    st.markdown("### 💡 What This Means")
    
    interpretations = {
        'A': "🟢 **Excellent!** This product has outstanding nutritional quality. It's low in sugar, fat, and sodium while being high in beneficial nutrients.",
        'B': "🟡 **Good!** This product has good nutritional quality. It's a solid choice for regular consumption.",
        'C': "🟠 **Fair.** This product has average nutritional quality. Consume in moderation as part of a balanced diet.",
        'D': "🔴 **Poor.** This product has low nutritional quality. High in sugar, fat, or sodium. Consume occasionally.",
        'E': "⛔ **Very Poor.** This product has very low nutritional quality. Reserve for rare treats only."
    }
    
    st.info(interpretations[grade])
    
    # === NUTRITION PROFILE ===
    st.markdown("---")
    st.markdown("### 📋 Your Nutrition Profile")
    
    profile_data = {
        'Nutrient': ['Energy', 'Sugar', 'Sat Fat', 'Sodium', 'Protein', 'Fiber'],
        'Value': [
            f"{energy_input} kcal",
            f"{sugars_input}g",
            f"{sat_fat_input}g",
            f"{sodium_input}mg",
            f"{protein_input}g",
            f"{fiber_input}g"
        ],
        'Category': ['Negative', 'Negative', 'Negative', 'Negative', 'Positive', 'Positive']
    }
    
    st.dataframe(pd.DataFrame(profile_data), use_container_width=True, hide_index=True)
    
    # === PRODUCT RECOMMENDATIONS ===
    st.markdown("---")
    st.markdown("## 🎯 Find Similar Products")
    
    tolerance = 0.25
    
    similar_df = df[
        (df['energy_kcal_100g'].between(energy_input * (1-tolerance), energy_input * (1+tolerance))) &
        (df['sugars_100g'].between(sugars_input * (1-tolerance), sugars_input * (1+tolerance))) &
        (df['proteins_100g'].between(protein_input * (1-tolerance), protein_input * (1+tolerance)))
    ].copy()
    
    if len(similar_df) > 0:
        st.success(f"Found **{len(similar_df)}** products with similar nutrition profile")
        
        # Show top 10
        display_cols = ['product_name', 'brand_name', 'energy_kcal_100g', 'sugars_100g', 'proteins_100g']
        available_cols = [c for c in display_cols if c in similar_df.columns]
        
        st.dataframe(
            similar_df[available_cols].head(10),
            use_container_width=True,
            hide_index=True,
            column_config={
                'product_name': 'Product Name',
                'brand_name': 'Brand',
                'energy_kcal_100g': 'Energy (kcal)',
                'sugars_100g': 'Sugar (g)',
                'proteins_100g': 'Protein (g)'
            }
        )
    else:
        st.warning("No products found with similar nutrition profile.")
    
    # === HEALTHIER ALTERNATIVES ===
    st.markdown("---")
    st.markdown("## 💚 Healthier Alternatives")
    
    healthier_df = df[
        (df['sugars_100g'] < sugars_input) &
        (df['proteins_100g'] > protein_input) &
        (df['energy_kcal_100g'].between(energy_input * 0.7, energy_input * 1.3))
    ].copy()
    
    if len(healthier_df) > 0:
        st.success(f"Found **{len(healthier_df)}** healthier alternatives")
        
        healthier_df = healthier_df.sort_values('proteins_100g', ascending=False)
        
        display_cols = ['product_name', 'brand_name', 'energy_kcal_100g', 'sugars_100g', 'proteins_100g']
        available_cols = [c for c in display_cols if c in healthier_df.columns]
        
        st.dataframe(
            healthier_df[available_cols].head(10),
            use_container_width=True,
            hide_index=True,
            column_config={
                'product_name': 'Product Name',
                'brand_name': 'Brand',
                'energy_kcal_100g': 'Energy (kcal)',
                'sugars_100g': 'Sugar (g)',
                'proteins_100g': 'Protein (g)'
            }
        )
        
        # Download option
        csv = healthier_df[available_cols].head(50).to_csv(index=False)
        st.download_button(
            label="📥 Download Top 50 Healthier Alternatives",
            data=csv,
            file_name="healthier_alternatives.csv",
            mime="text/csv"
        )
    else:
        st.info("No healthier alternatives found. Your nutrition profile might already be optimal!")

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Nutrition Score Calculator</strong> | Powered by Analytics Schema</p>
    <p>Simplified Nutri-Score algorithm for educational purposes</p>
</div>
""", unsafe_allow_html=True)