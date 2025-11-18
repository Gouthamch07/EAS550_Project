-- ============================================================================
-- PHASE 1: DATABASE SCHEMA (3NF)
-- Global Food & Nutrition Explorer
-- Team: Akash Ankush Kamble, Nidhi Rajani, Goutham Chengalvala
-- ============================================================================

-- Drop existing tables (CASCADE to handle dependencies)
DROP TABLE IF EXISTS nutrition_facts CASCADE;
DROP TABLE IF EXISTS product_labels CASCADE;
DROP TABLE IF EXISTS product_countries CASCADE;
DROP TABLE IF EXISTS product_categories CASCADE;
DROP TABLE IF EXISTS product_brands CASCADE;
DROP TABLE IF EXISTS labels CASCADE;
DROP TABLE IF EXISTS countries CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS brands CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- ============================================================================
-- CORE ENTITY: products
-- ============================================================================
-- Stores main product information
-- PK: code (product identifier from Open Food Facts)
CREATE TABLE products (
    code VARCHAR(50) PRIMARY KEY,
    product_name TEXT,
    quantity_numeric NUMERIC(10, 2),
    quantity_unit VARCHAR(20),
    image_url TEXT,
    ingredients_text TEXT,
    nutriscore_score NUMERIC(5, 2),
    nutriscore_grade VARCHAR(1) CHECK (nutriscore_grade IN ('a', 'b', 'c', 'd', 'e')),
    nova_group INTEGER CHECK (nova_group BETWEEN 1 AND 4),
    pnns_groups_2 VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE products IS 'Core product information from Open Food Facts';
COMMENT ON COLUMN products.code IS 'Unique product identifier (barcode)';
COMMENT ON COLUMN products.nutriscore_grade IS 'Nutritional quality score: a (best) to e (worst)';
COMMENT ON COLUMN products.nova_group IS 'Food processing level: 1 (unprocessed) to 4 (ultra-processed)';

-- ============================================================================
-- DIMENSION: brands
-- ============================================================================
-- Normalized brand names (eliminates redundancy)
CREATE TABLE brands (
    brand_id SERIAL PRIMARY KEY,
    brand_name VARCHAR(200) UNIQUE NOT NULL
);

COMMENT ON TABLE brands IS 'Normalized brand names';

-- ============================================================================
-- JUNCTION: product_brands (Many-to-Many)
-- ============================================================================
-- Associates products with brands (a product can have multiple brands)
CREATE TABLE product_brands (
    product_code VARCHAR(50) REFERENCES products(code) ON DELETE CASCADE,
    brand_id INTEGER REFERENCES brands(brand_id) ON DELETE CASCADE,
    PRIMARY KEY (product_code, brand_id)
);

COMMENT ON TABLE product_brands IS 'Many-to-many relationship between products and brands';

-- ============================================================================
-- DIMENSION: categories
-- ============================================================================
-- Normalized category names
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(200) UNIQUE NOT NULL
);

COMMENT ON TABLE categories IS 'Normalized product categories';

-- ============================================================================
-- JUNCTION: product_categories (Many-to-Many)
-- ============================================================================
CREATE TABLE product_categories (
    product_code VARCHAR(50) REFERENCES products(code) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(category_id) ON DELETE CASCADE,
    PRIMARY KEY (product_code, category_id)
);

-- ============================================================================
-- DIMENSION: countries
-- ============================================================================
-- Normalized country names
CREATE TABLE countries (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) UNIQUE NOT NULL
);

COMMENT ON TABLE countries IS 'Countries where products are sold';

-- ============================================================================
-- JUNCTION: product_countries (Many-to-Many)
-- ============================================================================
CREATE TABLE product_countries (
    product_code VARCHAR(50) REFERENCES products(code) ON DELETE CASCADE,
    country_id INTEGER REFERENCES countries(country_id) ON DELETE CASCADE,
    PRIMARY KEY (product_code, country_id)
);

-- ============================================================================
-- DIMENSION: labels
-- ============================================================================
-- Normalized label names (e.g., "Organic", "Gluten-Free")
CREATE TABLE labels (
    label_id SERIAL PRIMARY KEY,
    label_name VARCHAR(200) UNIQUE NOT NULL
);

COMMENT ON TABLE labels IS 'Product labels and certifications';

-- ============================================================================
-- JUNCTION: product_labels (Many-to-Many)
-- ============================================================================
CREATE TABLE product_labels (
    product_code VARCHAR(50) REFERENCES products(code) ON DELETE CASCADE,
    label_id INTEGER REFERENCES labels(label_id) ON DELETE CASCADE,
    PRIMARY KEY (product_code, label_id)
);

-- ============================================================================
-- DEPENDENT ENTITY: nutrition_facts (One-to-One with products)
-- ============================================================================
-- Nutritional information per 100g
CREATE TABLE nutrition_facts (
    product_code VARCHAR(50) PRIMARY KEY REFERENCES products(code) ON DELETE CASCADE,
    energy_kcal_100g NUMERIC(8, 3),
    fat_100g NUMERIC(8, 3),
    saturated_fat_100g NUMERIC(8, 3),
    carbohydrates_100g NUMERIC(8, 3),
    sugars_100g NUMERIC(8, 3),
    fiber_100g NUMERIC(8, 3),
    proteins_100g NUMERIC(8, 3),
    salt_100g NUMERIC(8, 3),
    sodium_100g NUMERIC(8, 3),
    -- Ensure nutritional values are non-negative
    CHECK (energy_kcal_100g >= 0),
    CHECK (fat_100g >= 0),
    CHECK (carbohydrates_100g >= 0),
    CHECK (proteins_100g >= 0)
);

COMMENT ON TABLE nutrition_facts IS 'Nutritional information per 100g of product';

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================
CREATE INDEX idx_products_nutriscore ON products(nutriscore_grade);
CREATE INDEX idx_products_nova ON products(nova_group);
CREATE INDEX idx_products_pnns ON products(pnns_groups_2);
CREATE INDEX idx_brands_name ON brands(brand_name);
CREATE INDEX idx_categories_name ON categories(category_name);
CREATE INDEX idx_countries_name ON countries(country_name);
CREATE INDEX idx_labels_name ON labels(label_name);
CREATE INDEX idx_nutrition_energy ON nutrition_facts(energy_kcal_100g);
CREATE INDEX idx_nutrition_fat ON nutrition_facts(fat_100g);
CREATE INDEX idx_nutrition_sugars ON nutrition_facts(sugars_100g);

-- ============================================================================
-- SAMPLE QUERIES FOR VERIFICATION
-- ============================================================================

-- Query 1: Get all products with their brands
-- SELECT p.product_name, b.brand_name
-- FROM products p
-- JOIN product_brands pb ON p.code = pb.product_code
-- JOIN brands b ON pb.brand_id = b.brand_id;

-- Query 2: Find high-nutrition products (A-grade nutriscore)
-- SELECT p.product_name, p.nutriscore_grade, nf.energy_kcal_100g
-- FROM products p
-- JOIN nutrition_facts nf ON p.code = nf.product_code
-- WHERE p.nutriscore_grade = 'a'
-- ORDER BY nf.energy_kcal_100g;

-- Query 3: Count products by category
-- SELECT c.category_name, COUNT(*) as product_count
-- FROM categories c
-- JOIN product_categories pc ON c.category_id = pc.category_id
-- GROUP BY c.category_name
-- ORDER BY product_count DESC;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================