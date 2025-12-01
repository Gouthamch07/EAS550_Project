-- ============================================================================
-- PHASE 2.1: ADVANCED ANALYTICAL QUERIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: The "Healthy Brand" Leaderboard
-- Goal: Rank brands with >50 products by their average Nutri-Score.
-- Complexity: Aggregation, HAVING, Multi-table JOINs
-- ----------------------------------------------------------------------------
SELECT 
    b.brand_name,
    COUNT(p.code) as product_count,
    ROUND(AVG(p.nutriscore_score), 2) as avg_nutriscore,
    ROUND(
        100.0 * SUM(CASE WHEN p.nutriscore_grade = 'a' THEN 1 ELSE 0 END) / COUNT(p.code), 
        1
    ) as pct_grade_a
FROM brands b
JOIN product_brands pb ON b.brand_id = pb.brand_id
JOIN products p ON pb.product_code = p.code
WHERE p.nutriscore_score IS NOT NULL
GROUP BY b.brand_name
HAVING COUNT(p.code) > 50
ORDER BY avg_nutriscore ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 2: Category Protein Champions
-- Goal: Find the top 3 highest protein products within each major category.
-- Complexity: Window Function (DENSE_RANK), CTE, Filtering
-- ----------------------------------------------------------------------------
WITH RankedProtein AS (
    SELECT 
        c.category_name,
        p.product_name,
        b.brand_name,
        nf.proteins_100g,
        DENSE_RANK() OVER (
            PARTITION BY c.category_name 
            ORDER BY nf.proteins_100g DESC
        ) as rank_in_category
    FROM categories c
    JOIN product_categories pc ON c.category_id = pc.category_id
    JOIN products p ON pc.product_code = p.code
    JOIN product_brands pb ON p.code = pb.product_code
    JOIN brands b ON pb.brand_id = b.brand_id
    JOIN nutrition_facts nf ON p.code = nf.product_code
    WHERE c.category_name IN ('Plant-based foods', 'Snacks', 'Beverages', 'Dairies')
      AND nf.proteins_100g IS NOT NULL
)
SELECT * 
FROM RankedProtein 
WHERE rank_in_category <= 3
ORDER BY category_name, rank_in_category;

-- ----------------------------------------------------------------------------
-- QUERY 3: The "Hidden Sugar" Detector
-- Goal: Find "Organic" products that have higher sugar than the global average.
-- Complexity: Subquery, Text Pattern Matching (ILIKE), Multi-table JOINs
-- ----------------------------------------------------------------------------
SELECT 
    p.product_name,
    b.brand_name,
    nf.sugars_100g,
    l.label_name
FROM products p
JOIN product_labels pl ON p.code = pl.product_code
JOIN labels l ON pl.label_id = l.label_id
JOIN nutrition_facts nf ON p.code = nf.product_code
JOIN product_brands pb ON p.code = pb.product_code
JOIN brands b ON pb.brand_id = b.brand_id
WHERE l.label_name ILIKE '%organic%'
  AND nf.sugars_100g > (SELECT AVG(sugars_100g) FROM nutrition_facts)
ORDER BY nf.sugars_100g DESC
LIMIT 20;