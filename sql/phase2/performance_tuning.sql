-- ============================================================================
-- PHASE 2.2: PERFORMANCE TUNING
-- ============================================================================
-- ============================================================================
-- OPTIMIZATION 1: Brand Leaderboard
-- ============================================================================
-- 1. Baseline
EXPLAIN ANALYZE
SELECT
    b.brand_name,
    COUNT(p.code)
FROM
    brands b
    JOIN product_brands pb ON b.brand_id = pb.brand_id
    JOIN products p ON pb.product_code = p.code
WHERE
    p.nutriscore_score IS NOT NULL
GROUP BY
    b.brand_name
HAVING
    COUNT(p.code) > 50;

-- 2. Create Indexes
-- Index the Foreign Key in the junction table
CREATE INDEX idx_pb_brand_id ON product_brands (brand_id);

CREATE INDEX idx_pb_product_code ON product_brands (product_code);

-- Index the filter column in products
CREATE INDEX idx_p_nutriscore ON products (nutriscore_score);

-- 3. Optimized
EXPLAIN ANALYZE
SELECT
    b.brand_name,
    COUNT(p.code)
FROM
    brands b
    JOIN product_brands pb ON b.brand_id = pb.brand_id
    JOIN products p ON pb.product_code = p.code
WHERE
    p.nutriscore_score IS NOT NULL
GROUP BY
    b.brand_name
HAVING
    COUNT(p.code) > 50;

-- ============================================================================
-- OPTIMIZATION 2: Category Protein Champions
-- ============================================================================
-- 1. Baseline
EXPLAIN ANALYZE
SELECT
    c.category_name,
    p.product_name,
    nf.proteins_100g
FROM
    categories c
    JOIN product_categories pc ON c.category_id = pc.category_id
    JOIN products p ON pc.product_code = p.code
    JOIN nutrition_facts nf ON p.code = nf.product_code
WHERE
    c.category_name = 'Snacks'
ORDER BY
    nf.proteins_100g DESC
LIMIT
    10;

-- 2. Create Indexes
-- Index the Foreign Keys
CREATE INDEX idx_pc_category_id ON product_categories (category_id);

CREATE INDEX idx_pc_product_code ON product_categories (product_code);

-- Index the sorting/filtering column in nutrition_facts
CREATE INDEX idx_nf_proteins ON nutrition_facts (proteins_100g);

-- 3. Optimized
EXPLAIN ANALYZE
SELECT
    c.category_name,
    p.product_name,
    nf.proteins_100g
FROM
    categories c
    JOIN product_categories pc ON c.category_id = pc.category_id
    JOIN products p ON pc.product_code = p.code
    JOIN nutrition_facts nf ON p.code = nf.product_code
WHERE
    c.category_name = 'Snacks'
ORDER BY
    nf.proteins_100g DESC
LIMIT
    10;

-- ============================================================================
-- OPTIMIZATION 3: Hidden Sugar Detector
-- ============================================================================
-- 1. Baseline
EXPLAIN ANALYZE
SELECT
    p.product_name,
    nf.sugars_100g
FROM
    products p
    JOIN product_labels pl ON p.code = pl.product_code
    JOIN labels l ON pl.label_id = l.label_id
    JOIN nutrition_facts nf ON p.code = nf.product_code
WHERE
    l.label_name ILIKE '%organic%'
    AND nf.sugars_100g > 50;

-- 2. Create Indexes
-- Index the Foreign Keys
CREATE INDEX idx_pl_label_id ON product_labels (label_id);

CREATE INDEX idx_pl_product_code ON product_labels (product_code);

-- Index the numeric filter
CREATE INDEX idx_nf_sugars ON nutrition_facts (sugars_100g);

-- Extension for text pattern matching (ILIKE) optimization
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_labels_name_trgm ON labels USING gin (label_name gin_trgm_ops);

-- 3. Optimized
EXPLAIN ANALYZE
SELECT
    p.product_name,
    nf.sugars_100g
FROM
    products p
    JOIN product_labels pl ON p.code = pl.product_code
    JOIN labels l ON pl.label_id = l.label_id
    JOIN nutrition_facts nf ON p.code = nf.product_code
WHERE
    l.label_name ILIKE '%organic%'
    AND nf.sugars_100g > 50;