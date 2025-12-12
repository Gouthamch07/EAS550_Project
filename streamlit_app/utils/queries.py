import pandas as pd
from .database import execute_query

def get_nutrition_distribution_by_category():
    """Get nutritional content distribution across categories"""
    query = """
    SELECT 
        c.category_name,
        AVG(nf.energy_100g) as avg_energy,
        AVG(nf.fat_100g) as avg_fat,
        AVG(nf.carbohydrates_100g) as avg_carbs,
        AVG(nf.proteins_100g) as avg_protein,
        AVG(nf.sugars_100g) as avg_sugars,
        AVG(nf.salt_100g) as avg_salt,
        COUNT(p.product_id) as product_count
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    LEFT JOIN nutrition_facts nf ON p.product_id = nf.product_id
    WHERE nf.energy_100g IS NOT NULL
    GROUP BY c.category_name
    HAVING COUNT(p.product_id) >= 10
    ORDER BY product_count DESC
    LIMIT 20;
    """
    return execute_query(query)

def get_nutrition_by_grade():
    """Get nutrition statistics by grade"""
    query = """
    SELECT 
        p.nutrition_grade,
        COUNT(*) as product_count,
        AVG(nf.energy_100g) as avg_energy,
        AVG(nf.fat_100g) as avg_fat,
        AVG(nf.sugars_100g) as avg_sugars,
        AVG(nf.proteins_100g) as avg_protein
    FROM products p
    JOIN nutrition_facts nf ON p.product_id = nf.product_id
    WHERE p.nutrition_grade IS NOT NULL
        AND nf.energy_100g IS NOT NULL
    GROUP BY p.nutrition_grade
    ORDER BY p.nutrition_grade;
    """
    return execute_query(query)

def get_energy_vs_nutrients_scatter():
    """Get data for energy vs nutrients scatter plot"""
    query = """
    SELECT 
        p.product_name,
        c.category_name,
        nf.energy_100g,
        nf.fat_100g,
        nf.sugars_100g,
        nf.proteins_100g,
        p.nutrition_grade
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    JOIN nutrition_facts nf ON p.product_id = nf.product_id
    WHERE nf.energy_100g IS NOT NULL
        AND nf.fat_100g IS NOT NULL
        AND nf.energy_100g < 3000  -- Remove outliers
        AND nf.fat_100g < 100
    LIMIT 5000;
    """
    return execute_query(query)

def get_categories_list():
    """Get list of categories for filtering"""
    query = """
    SELECT DISTINCT category_name 
    FROM categories 
    ORDER BY category_name;
    """
    return execute_query(query)

def get_high_sugar_products(threshold: float = 15.0):
    """Get products with high sugar content"""
    query = """
    SELECT 
        p.product_name,
        b.brand_name,
        c.category_name,
        nf.sugars_100g,
        nf.energy_100g,
        p.nutrition_grade
    FROM products p
    JOIN brands b ON p.brand_id = b.brand_id
    JOIN categories c ON p.category_id = c.category_id
    JOIN nutrition_facts nf ON p.product_id = nf.product_id
    WHERE nf.sugars_100g > :threshold
        AND nf.sugars_100g IS NOT NULL
    ORDER BY nf.sugars_100g DESC
    LIMIT 100;
    """
    return execute_query(query, params={'threshold': threshold})

def get_nutrition_by_filtered_category(category: str = None):
    """Get nutrition facts filtered by category"""
    if category and category != "All Categories":
        query = """
        SELECT 
            p.product_name,
            nf.energy_100g,
            nf.fat_100g,
            nf.carbohydrates_100g,
            nf.proteins_100g,
            nf.sugars_100g,
            nf.salt_100g,
            p.nutrition_grade
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN nutrition_facts nf ON p.product_id = nf.product_id
        WHERE c.category_name = :category
            AND nf.energy_100g IS NOT NULL
        LIMIT 1000;
        """
        return execute_query(query, params={'category': category})
    else:
        query = """
        SELECT 
            p.product_name,
            nf.energy_100g,
            nf.fat_100g,
            nf.carbohydrates_100g,
            nf.proteins_100g,
            nf.sugars_100g,
            nf.salt_100g,
            p.nutrition_grade
        FROM products p
        JOIN nutrition_facts nf ON p.product_id = nf.product_id
        WHERE nf.energy_100g IS NOT NULL
        LIMIT 1000;
        """
        return execute_query(query)