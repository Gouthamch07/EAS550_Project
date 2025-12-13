import pandas as pd
from .database import execute_query

def get_nutrition_distribution_by_category(grade=None):
    """
    Get nutriscore distribution across categories.
    Uses public.products because category info is there.
    """
    query = """
    SELECT 
        COALESCE(pnns_groups_2, 'Unknown') as category_name,
        AVG(nutriscore_score) as avg_score,
        COUNT(*) as product_count
    FROM public.products
    WHERE pnns_groups_2 IS NOT NULL
        AND nutriscore_score IS NOT NULL
    """
    
    params = {}
    if grade and grade != "All Grades":
        query += " AND nutriscore_grade = :grade"
        params['grade'] = grade.lower()
        
    query += """
    GROUP BY pnns_groups_2
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC
    LIMIT 20;
    """
    return execute_query(query, params)

def get_nutrition_by_grade():
    """
    Get product counts by nutriscore grade.
    Uses analytics.dim_products (Fast Star Schema)
    """
    query = """
    SELECT 
        nutriscore_grade as nutrition_grade,
        COUNT(*) as product_count
    FROM analytics.dim_products
    WHERE nutriscore_grade IS NOT NULL
    GROUP BY nutriscore_grade
    ORDER BY nutriscore_grade;
    """
    return execute_query(query)

def get_energy_vs_nutrients_scatter():
    """
    Get nutriscore vs nova group scatter.
    Uses public.products to ensure category_name is available for hover data.
    """
    query = """
    SELECT 
        product_name,
        COALESCE(pnns_groups_2, 'Unknown') as category_name,
        nutriscore_score,
        nova_group,
        nutriscore_grade as nutrition_grade
    FROM public.products
    WHERE nutriscore_score IS NOT NULL
        AND nutriscore_grade IS NOT NULL
        AND nova_group IS NOT NULL
        AND product_name IS NOT NULL
        AND product_name != ''
    ORDER BY RANDOM()
    LIMIT 2000;
    """
    return execute_query(query)

def get_categories_list():
    """Get list of food categories"""
    query = """
    SELECT DISTINCT pnns_groups_2 as category_name
    FROM public.products 
    WHERE pnns_groups_2 IS NOT NULL
    ORDER BY pnns_groups_2;
    """
    return execute_query(query)

def get_high_sugar_products(threshold: float = 5.0):
    """
    Get products with poor nutriscore (> threshold).
    Uses public.products to ensure category_name is available.
    """
    query = """
    SELECT 
        p.product_name,
        'Unknown' as brand_name,
        COALESCE(p.pnns_groups_2, 'Unknown') as category_name,
        p.nutriscore_score,
        p.nutriscore_grade as nutrition_grade,
        nf.sugars_100g
    FROM public.products p
    JOIN public.nutrition_facts nf ON p.code = nf.product_code
    WHERE p.nutriscore_score > :threshold
        AND p.nutriscore_score IS NOT NULL
        AND p.product_name IS NOT NULL
        AND p.product_name != ''
    ORDER BY p.nutriscore_score DESC
    LIMIT 100;
    """
    return execute_query(query, params={'threshold': threshold})

def get_nutrition_by_filtered_category(category: str = None):
    """Get products filtered by category"""
    if category and category != "All Categories":
        query = """
        SELECT 
            product_name,
            nutriscore_score,
            nutriscore_grade as nutrition_grade,
            nova_group
        FROM public.products
        WHERE pnns_groups_2 = :category
            AND nutriscore_score IS NOT NULL
        LIMIT 1000;
        """
        return execute_query(query, params={'category': category})
    else:
        # Fallback to optimized table if no category selected
        query = """
        SELECT 
            product_name,
            nutriscore_score,
            nutriscore_grade as nutrition_grade,
            nova_group
        FROM analytics.dim_products
        WHERE nutriscore_score IS NOT NULL
        LIMIT 1000;
        """
        return execute_query(query)