-- ============================================================================
-- PHASE 2 (BONUS): DATA WAREHOUSE ANALYTICS
-- Queries targeting the Star Schema (analytics.fact_nutrition & analytics.dim_products)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Nutri-Score vs. Macronutrients
-- Goal: Analyze how average calories and sugar correlate with Nutri-Score grades.
-- Demonstrates: Joining Fact and Dimension tables to slice metrics by attributes.
-- ----------------------------------------------------------------------------
SELECT 
    dp.nutriscore_grade,
    COUNT(*) as total_products,
    ROUND(AVG(fn.energy_kcal_100g), 2) as avg_calories,
    ROUND(AVG(fn.sugars_100g), 2) as avg_sugar_g,
    ROUND(AVG(fn.fat_100g), 2) as avg_fat_g
FROM analytics.fact_nutrition fn
JOIN analytics.dim_products dp ON fn.product_id = dp.product_id
WHERE dp.nutriscore_grade IS NOT NULL
GROUP BY dp.nutriscore_grade
ORDER BY dp.nutriscore_grade;

-- ----------------------------------------------------------------------------
-- QUERY 2: Brand Sugar Analysis (Top 10 Sweetest Brands)
-- Goal: Identify brands with the highest average sugar content (min 10 products).
-- Demonstrates: Querying the Fact table directly (since we denormalized brand_name).
-- ----------------------------------------------------------------------------
SELECT 
    fn.brand_name,
    COUNT(*) as product_count,
    ROUND(AVG(fn.sugars_100g), 2) as avg_sugar_per_100g
FROM analytics.fact_nutrition fn
WHERE fn.brand_name IS NOT NULL
GROUP BY fn.brand_name
HAVING COUNT(*) >= 10
ORDER BY avg_sugar_per_100g DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 3: Ultra-Processed High-Protein Foods
-- Goal: Find high-protein products that are classified as Ultra-Processed (NOVA 4).
-- Demonstrates: Filtering by Dimension attributes (NOVA) to find specific Facts.
-- ----------------------------------------------------------------------------
SELECT 
    dp.product_name,
    fn.brand_name,
    fn.proteins_100g,
    fn.energy_kcal_100g,
    dp.nova_group
FROM analytics.fact_nutrition fn
JOIN analytics.dim_products dp ON fn.product_id = dp.product_id
WHERE dp.nova_group = 4  -- Ultra-processed food products
  AND fn.proteins_100g > 20 -- High protein
ORDER BY fn.proteins_100g DESC
LIMIT 15;