-- Fact Table: Nutrition
SELECT
    nf.product_code as product_id,
    p.product_name,
    -- We can denormalize brand here for easier analytics
    b.brand_name, 
    nf.energy_kcal_100g,
    nf.fat_100g,
    nf.sugars_100g,
    nf.proteins_100g
FROM {{ source('public', 'nutrition_facts') }} nf
JOIN {{ source('public', 'products') }} p ON nf.product_code = p.code
-- Join brands to get the name into the fact table (common in Star Schemas)
LEFT JOIN {{ source('public', 'product_brands') }} pb ON p.code = pb.product_code
LEFT JOIN {{ source('public', 'brands') }} b ON pb.brand_id = b.brand_id