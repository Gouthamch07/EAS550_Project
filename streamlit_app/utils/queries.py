import pandas as pd
from .database import execute_query

def get_nutrition_distribution_by_category():
    """Get nutriscore distribution across pnns_groups_2"""
    query = """
    SELECT 
        COALESCE(pnns_groups_2, 'Unknown') as category_name,
        AVG(nutriscore_score) as avg_score,
        COUNT(*) as product_count
    FROM products
    WHERE pnns_groups_2 IS NOT NULL
        AND nutriscore_score IS NOT NULL
    GROUP BY pnns_groups_2
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC
    LIMIT 20;
    """
    return execute_query(query)

def get_nutrition_by_grade():
    """Get product counts by nutriscore grade"""
    query = """
    SELECT 
        nutriscore_grade as nutrition_grade,
        COUNT(*) as product_count,
        AVG(nutriscore_score) as avg_score
    FROM products
    WHERE nutriscore_grade IS NOT NULL
    GROUP BY nutriscore_grade
    ORDER BY nutriscore_grade;
    """
    return execute_query(query)

def get_energy_vs_nutrients_scatter():
    """Get nutriscore vs nova group scatter"""
    query = """
    SELECT 
        product_name,
        COALESCE(pnns_groups_2, 'Unknown') as category_name,
        nutriscore_score,
        nova_group,
        nutriscore_grade as nutrition_grade
    FROM products
    WHERE nutriscore_score IS NOT NULL
        AND nutriscore_grade IS NOT NULL
        AND nova_group IS NOT NULL
        AND product_name IS NOT NULL
        AND product_name != ''
    ORDER BY RANDOM()
    LIMIT 5000;
    """
    return execute_query(query)

def get_categories_list():
    """Get list of food categories"""
    query = """
    SELECT DISTINCT pnns_groups_2 as category_name
    FROM products 
    WHERE pnns_groups_2 IS NOT NULL
    ORDER BY pnns_groups_2;
    """
    return execute_query(query)

def get_high_sugar_products(threshold: float = 5.0):
    """Get products with poor nutriscore (> threshold)"""
    query = """
    SELECT 
        p.product_name,
        'Unknown' as brand_name,
        COALESCE(p.pnns_groups_2, 'Unknown') as category_name,
        p.nutriscore_score,
        p.nutriscore_grade as nutrition_grade
    FROM products p
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
        FROM products
        WHERE pnns_groups_2 = :category
            AND nutriscore_score IS NOT NULL
        LIMIT 1000;
        """
        return execute_query(query, params={'category': category})
    else:
        query = """
        SELECT 
            product_name,
            nutriscore_score,
            nutriscore_grade as nutrition_grade,
            nova_group
        FROM products
        WHERE nutriscore_score IS NOT NULL
        LIMIT 1000;
        """
        return execute_query(query)