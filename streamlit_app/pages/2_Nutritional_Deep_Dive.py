import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.queries import (
    get_nutrition_distribution_by_category,
    get_nutrition_by_grade,
    get_energy_vs_nutrients_scatter,
    get_categories_list,
    get_high_sugar_products,
    get_nutrition_by_filtered_category
)
from config import COLORS, GRADE_COLORS

# Page configuration
st.set_page_config(
    page_title="Nutritional Deep Dive",
    page_icon="🔬",
    layout="wide"
)

# Title and description
st.title("🔬 Nutritional Deep Dive")
st.markdown("""
Explore detailed nutritional analysis across products, categories, and nutrition grades.
Use the filters below to customize your analysis.
""")

# Sidebar filters
st.sidebar.header("🎛️ Filters")

# Category filter
with st.spinner("Loading categories..."):
    try:
        categories_df = get_categories_list()
        if not categories_df.empty:
            category_options = ["All Categories"] + categories_df['category_name'].tolist()
        else:
            category_options = ["All Categories"]
    except Exception as e:
        st.sidebar.error(f"Error loading categories: {str(e)}")
        category_options = ["All Categories"]

selected_category = st.sidebar.selectbox(
    "Select Category",
    options=category_options,
    index=0
)

# Nutrition grade filter
grade_options = ["All Grades", "a", "b", "c", "d", "e"]
selected_grade = st.sidebar.selectbox(
    "Nutrition Grade",
    options=grade_options,
    index=0
)

# Nutriscore threshold slider
sugar_threshold = st.sidebar.slider(
    "Poor Nutrition Threshold",
    min_value=0.0,
    max_value=20.0,
    value=5.0,
    step=0.5,
    help="Products above this nutriscore are considered poor nutrition"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Hover over charts for detailed information")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Distribution Analysis",
    "⚡ Nutriscore vs NOVA",
    "📦 Box Plot Analysis",
    "🔴 Poor Nutrition Detector"
])

# TAB 1: Distribution Analysis
with tab1:
    st.header("Nutriscore Distribution by Category")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.spinner("Loading distribution data..."):
            try:
                dist_df = get_nutrition_distribution_by_category()
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                dist_df = pd.DataFrame()
        
        if not dist_df.empty:
            # Create bar chart for nutriscore
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Average Nutriscore',
                x=dist_df['category_name'],
                y=dist_df['avg_score'],
                marker_color=COLORS['primary'],
                text=dist_df['avg_score'].round(2),
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Average Nutriscore by Category (lower is better)",
                xaxis_title="Category",
                yaxis_title="Average Nutriscore",
                height=500,
                hovermode='x unified'
            )
            
            fig.update_xaxes(tickangle=-45)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No data available. Please check your database connection.")
    
    with col2:
        st.subheader("📈 Category Statistics")
        
        if not dist_df.empty:
            # Display top categories (best scores)
            top_5 = dist_df.nsmallest(5, 'avg_score')[['category_name', 'avg_score', 'product_count']]
            
            st.markdown("**🥗 Best Scoring Categories:**")
            for idx, row in top_5.iterrows():
                st.metric(
                    label=row['category_name'][:30],
                    value=f"{row['avg_score']:.1f}",
                    delta=f"{row['product_count']} products"
                )
            
            st.markdown("---")
            
            # Nutrition grade distribution pie chart
            try:
                grade_df = get_nutrition_by_grade()
                if not grade_df.empty:
                    fig_pie = px.pie(
                        grade_df,
                        values='product_count',
                        names='nutrition_grade',
                        title='Products by Nutriscore Grade',
                        color='nutrition_grade',
                        color_discrete_map=GRADE_COLORS
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading grade data: {str(e)}")

# TAB 2: Nutriscore vs NOVA Group Scatter
with tab2:
    st.header("Nutriscore vs NOVA Group Analysis")
    
    with st.spinner("Loading scatter data..."):
        try:
            scatter_df = get_energy_vs_nutrients_scatter()
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            scatter_df = pd.DataFrame()
    
    if not scatter_df.empty:
        st.markdown("""
        **NOVA Classification:**
        - **Group 1**: Unprocessed or minimally processed
        - **Group 2**: Processed culinary ingredients
        - **Group 3**: Processed foods
        - **Group 4**: Ultra-processed foods
        """)
        
        # Create scatter plot
        fig = px.scatter(
            scatter_df,
            x='nova_group',
            y='nutriscore_score',
            color='nutrition_grade',
            hover_data=['product_name', 'category_name'],
            title='Nutriscore vs NOVA Processing Group',
            labels={
                'nova_group': 'NOVA Group (Processing Level)',
                'nutriscore_score': 'Nutriscore (lower is better)',
                'nutrition_grade': 'Grade'
            },
            color_discrete_map=GRADE_COLORS,
            opacity=0.6
        )
        
        fig.update_traces(marker=dict(size=8, line=dict(width=0.5, color='white')))
        fig.update_layout(height=600, hovermode='closest')
        fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_score = scatter_df['nutriscore_score'].mean()
            st.metric("Average Nutriscore", f"{avg_score:.2f}")
        with col2:
            st.metric("Total Products Analyzed", f"{len(scatter_df):,}")
        with col3:
            ultra_processed = len(scatter_df[scatter_df['nova_group'] == 4])
            pct = (ultra_processed / len(scatter_df) * 100)
            st.metric("Ultra-Processed (NOVA 4)", f"{ultra_processed:,} ({pct:.1f}%)")
    else:
        st.warning("⚠️ No data available. Please check your database connection.")

# TAB 3: Box Plot Analysis
with tab3:
    st.header("Nutriscore Distribution Analysis")
    
    with st.spinner("Loading box plot data..."):
        try:
            box_df = get_nutrition_by_filtered_category(selected_category)
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            box_df = pd.DataFrame()
    
    if not box_df.empty:
        # Create box plot by nutrition grade
        fig = px.box(
            box_df,
            x='nutrition_grade',
            y='nutriscore_score',
            color='nutrition_grade',
            title=f'Nutriscore Distribution by Grade',
            labels={
                'nutrition_grade': 'Nutriscore Grade',
                'nutriscore_score': 'Nutriscore'
            },
            color_discrete_map=GRADE_COLORS
        )
        
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_title="Nutriscore Grade",
            yaxis_title="Nutriscore (lower is better)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistical summary
        st.subheader("📊 Statistical Summary")
        
        summary_stats = box_df.groupby('nutrition_grade')['nutriscore_score'].describe()
        st.dataframe(summary_stats.round(2), use_container_width=True)
        
        # Additional insights
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Products Analyzed", f"{len(box_df):,}")
        with col2:
            grade_counts = box_df['nutrition_grade'].value_counts()
            best_grade = grade_counts.idxmax()
            st.metric("Most Common Grade", best_grade.upper())
    else:
        st.warning("⚠️ No data available for the selected category.")

# TAB 4: Poor Nutrition Score Detector
with tab4:
    st.header("🔴 Poor Nutrition Score Detector")
    
    st.markdown(f"""
    Products with nutriscore **above {sugar_threshold}** are considered to have poor nutritional quality.
    
    **Remember:** Lower nutriscore is better (Grade A = best, Grade E = worst)
    """)
    
    with st.spinner("Detecting poor nutrition products..."):
        try:
            high_sugar_df = get_high_sugar_products(sugar_threshold)
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            high_sugar_df = pd.DataFrame()
    
    if not high_sugar_df.empty:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Summary metrics
            st.metric("Products Found", len(high_sugar_df))
            st.metric("Avg Nutriscore", f"{high_sugar_df['nutriscore_score'].mean():.1f}")
            st.metric("Max Nutriscore", f"{high_sugar_df['nutriscore_score'].max():.1f}")
            
            st.markdown("---")
            
            # Top categories
            st.markdown("**Top Categories:**")
            top_categories = high_sugar_df['category_name'].value_counts().head(5)
            for cat, count in top_categories.items():
                st.write(f"• {cat}: {count} products")
            
            # Grade distribution
            st.markdown("---")
            st.markdown("**Grade Distribution:**")
            grade_counts = high_sugar_df['nutrition_grade'].value_counts().sort_index()
            for grade, count in grade_counts.items():
                st.write(f"• Grade {grade.upper()}: {count} products")
        
        with col2:
            # Horizontal bar chart
            top_20 = high_sugar_df.head(20)
            
            fig = go.Figure(go.Bar(
                x=top_20['nutriscore_score'],
                y=top_20['product_name'],
                orientation='h',
                marker=dict(
                    color=top_20['nutriscore_score'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Nutriscore")
                ),
                text=top_20['nutriscore_score'].round(1),
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Top 20 Products by Poor Nutrition Score",
                xaxis_title="Nutriscore (higher = worse)",
                yaxis_title="Product",
                height=600,
                yaxis=dict(autorange="reversed")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.subheader("📋 Detailed Product List")
        
        display_df = high_sugar_df[['product_name', 'brand_name', 'category_name', 
                                     'nutriscore_score', 'nutrition_grade']].copy()
        display_df.columns = ['Product', 'Brand', 'Category', 'Nutriscore', 'Grade']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Poor Nutrition Products CSV",
            data=csv,
            file_name=f"poor_nutrition_products_{sugar_threshold}.csv",
            mime="text/csv"
        )
    else:
        st.info(f"ℹ️ No products found with nutriscore above {sugar_threshold}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Global Food & Nutrition Explorer | Data from Open Food Facts</p>
    <p>Nutriscore Analysis: Lower scores indicate better nutritional quality</p>
</div>
""", unsafe_allow_html=True)