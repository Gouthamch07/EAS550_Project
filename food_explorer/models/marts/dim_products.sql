-- Dimension Table: Products
SELECT
    code as product_id,
    product_name,
    quantity_numeric,
    quantity_unit,
    nutriscore_grade,
    nutriscore_score,
    nova_group
FROM {{ source('public', 'products') }}