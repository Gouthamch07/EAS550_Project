import pandas as pd
from typing import Optional
from .database import execute_query

# ==============================================================================
# 1. GENERAL SEARCH & LOOKUP
# ==============================================================================

def search_products(search_term, limit=20):
    """Search for products by name (fuzzy match)."""
    query = """
    SELECT 
        dp.product_name,
        fn.brand_name,
        dp.nutriscore_grade,
        dp.nutriscore_score,
        fn.energy_kcal_100g,
        fn.sugars_100g,
        fn.fat_100g,
        fn.proteins_100g,
        dp.nova_group
    FROM analytics.dim_products dp
    JOIN analytics.fact_nutrition fn ON dp.product_id = fn.product_id
    WHERE dp.product_name ILIKE :search
    ORDER BY dp.nutriscore_score ASC
    LIMIT :limit;
    """
    return execute_query(query, params={'search': f"%{search_term}%", 'limit': limit})

def get_product_details(product_name):
    """Get full details for a specific product name"""
    query = """
    SELECT 
        dp.product_name,
        fn.brand_name,
        dp.nutriscore_grade,
        dp.nutriscore_score,
        fn.energy_kcal_100g,
        fn.sugars_100g,
        fn.fat_100g,
        fn.proteins_100g,
        dp.nova_group
    FROM analytics.dim_products dp
    JOIN analytics.fact_nutrition fn ON dp.product_id = fn.product_id
    WHERE dp.product_name = :name
    LIMIT 1;
    """
    return execute_query(query, params={'name': product_name})

# ==============================================================================
# 2. DASHBOARD STATS
# ==============================================================================

def get_dashboard_stats():
    query = """
    SELECT
        COUNT(*) as total,
        COUNT(DISTINCT brand_name) as brands,
        SUM(CASE WHEN nutriscore_grade IN ('a', 'b') THEN 1 ELSE 0 END) as healthy_count,
        SUM(CASE WHEN nutriscore_grade IN ('d', 'e') THEN 1 ELSE 0 END) as poor_count,
        SUM(CASE WHEN nova_group = 4 THEN 1 ELSE 0 END) as ultra_processed_count
    FROM analytics.dim_products dp
    JOIN analytics.fact_nutrition fn ON dp.product_id = fn.product_id;
    """
    return execute_query(query)

# ==============================================================================
# 3. HEALTHY FOOD FINDER
# ==============================================================================

def find_products_by_category_keyword(keyword, sort_order='ASC', limit=50):
    order_clause = "dp.nutriscore_score ASC"
    if sort_order == 'DESC':
        order_clause = "dp.nutriscore_score DESC"
    elif sort_order == 'ALPHA':
        order_clause = "dp.product_name ASC"

    query = f"""
    SELECT 
        dp.product_name,
        fn.brand_name,
        dp.nutriscore_grade,
        dp.nutriscore_score,
        fn.sugars_100g,
        fn.proteins_100g
    FROM analytics.dim_products dp
    JOIN analytics.fact_nutrition fn ON dp.product_id = fn.product_id
    WHERE dp.product_name ILIKE :keyword
    ORDER BY {order_clause}
    LIMIT :limit;
    """
    return execute_query(query, params={'keyword': f"%{keyword}%", 'limit': limit})

# ==============================================================================
# 4. SWAPS & TWINS (COMPLEX LOGIC)
# ==============================================================================

def find_healthier_alternatives(product_name, current_sugar, current_protein, current_energy):
    """Find healthier alternatives using native Python types to avoid numpy errors"""
    first_word = product_name.split(' ')[0]
    
    # FIX: Explicitly cast numpy floats to python floats
    c_sugar = float(current_sugar)
    c_protein = float(current_protein)
    c_energy = float(current_energy)
    
    query = """
    SELECT 
        dp.product_name,
        fn.brand_name,
        fn.energy_kcal_100g,
        fn.sugars_100g,
        fn.proteins_100g,
        dp.nutriscore_grade
    FROM analytics.dim_products dp
    JOIN analytics.fact_nutrition fn ON dp.product_id = fn.product_id
    WHERE dp.product_name ILIKE :cat_search
      AND dp.product_name != :current_name
      AND fn.sugars_100g < :sugar
      AND fn.proteins_100g >= (:protein * 0.8)
      AND fn.energy_kcal_100g BETWEEN (:energy * 0.7) AND (:energy * 1.3)
    ORDER BY fn.sugars_100g ASC
    LIMIT 10;
    """
    return execute_query(query, params={
        'cat_search': f"%{first_word}%",
        'current_name': product_name,
        'sugar': c_sugar,
        'protein': c_protein,
        'energy': c_energy
    })

def find_similar_products_by_macros(energy, sugar, protein, tolerance=0.2):
    """Find products with similar nutritional profile"""
    # FIX: Explicitly cast to python floats
    val_e = float(energy)
    val_s = float(sugar)
    val_p = float(protein)
    
    query = """
    SELECT 
        dp.product_name,
        fn.brand_name,
        fn.energy_kcal_100g,
        fn.sugars_100g,
        fn.proteins_100g
    FROM analytics.fact_nutrition fn
    JOIN analytics.dim_products dp ON fn.product_id = dp.product_id
    WHERE fn.energy_kcal_100g BETWEEN :min_e AND :max_e
      AND fn.sugars_100g BETWEEN :min_s AND :max_s
      AND fn.proteins_100g BETWEEN :min_p AND :max_p
    LIMIT 10;
    """
    return execute_query(query, params={
        'min_e': val_e * (1 - tolerance), 'max_e': val_e * (1 + tolerance),
        'min_s': val_s * (1 - tolerance), 'max_s': val_s * (1 + tolerance),
        'min_p': val_p * (1 - tolerance), 'max_p': val_p * (1 + tolerance)
    })

# ==============================================================================
# 5. EXISTING ANALYTICS
# ==============================================================================

def get_nutrition_distribution_by_category(grade=None):
    query = """
    SELECT 
        COALESCE(pnns_groups_2, 'Unknown') as category_name,
        AVG(nutriscore_score) as avg_score,
        COUNT(*) as product_count
    FROM public.products
    WHERE pnns_groups_2 IS NOT NULL AND nutriscore_score IS NOT NULL
    """
    params = {}
    if grade and grade != "All Grades":
        query += " AND nutriscore_grade = :grade"
        params['grade'] = grade.lower()
    query += " GROUP BY pnns_groups_2 HAVING COUNT(*) >= 10 ORDER BY product_count DESC LIMIT 20;"
    return execute_query(query, params)

def get_nutrition_by_grade():
    return execute_query("SELECT nutriscore_grade as nutrition_grade, COUNT(*) as product_count FROM analytics.dim_products WHERE nutriscore_grade IS NOT NULL GROUP BY nutriscore_grade ORDER BY nutriscore_grade;")

def get_energy_vs_nutrients_scatter():
    return execute_query("SELECT product_name, COALESCE(pnns_groups_2, 'Unknown') as category_name, nutriscore_score, nova_group, nutriscore_grade as nutrition_grade FROM public.products WHERE nutriscore_score IS NOT NULL AND nutriscore_grade IS NOT NULL AND nova_group IS NOT NULL ORDER BY RANDOM() LIMIT 2000;")

def get_categories_list():
    return execute_query("SELECT DISTINCT pnns_groups_2 as category_name FROM public.products WHERE pnns_groups_2 IS NOT NULL ORDER BY pnns_groups_2;")

def get_high_sugar_products(threshold: float = 5.0):
    query = """
    SELECT p.product_name, 'Unknown' as brand_name, COALESCE(p.pnns_groups_2, 'Unknown') as category_name, p.nutriscore_score, p.nutriscore_grade as nutrition_grade, nf.sugars_100g 
    FROM public.products p JOIN public.nutrition_facts nf ON p.code = nf.product_code 
    WHERE p.nutriscore_score > :threshold AND p.nutriscore_score IS NOT NULL ORDER BY p.nutriscore_score DESC LIMIT 100;
    """
    return execute_query(query, params={'threshold': float(threshold)})

def get_nutrition_by_filtered_category(category: Optional[str] = None):
    if category and category != "All Categories":
        return execute_query("SELECT product_name, nutriscore_score, nutriscore_grade as nutrition_grade, nova_group FROM public.products WHERE pnns_groups_2 = :category AND nutriscore_score IS NOT NULL LIMIT 1000;", params={'category': category})
    return execute_query("SELECT product_name, nutriscore_score, nutriscore_grade as nutrition_grade, nova_group FROM analytics.dim_products WHERE nutriscore_score IS NOT NULL LIMIT 1000;")