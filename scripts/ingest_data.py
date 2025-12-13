"""
Phase 1: Complete Database Foundation Pipeline
EAS 550 - Global Food & Nutrition Explorer

This script handles:
1. Data Download from Open Food Facts
2. Data Cleaning & Standardization
3. Data Normalization (3NF)
4. PostgreSQL Schema Creation
5. Data Ingestion via SQLAlchemy

Team: Akash Ankush Kamble, Nidhi Rajani, Goutham Chengalvala
"""

import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from openfoodfacts import ProductDataset, DatasetType
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

SLICE_SIZE = 200000  # Target number of US products
# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# Define the data directory relative to the project root
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

RAW_DATA_FILE = os.path.join(DATA_DIR, "openfoodfacts_raw.csv")
CLEANED_DATA_FILE = os.path.join(DATA_DIR, "openfoodfacts_cleaned.csv")

# Database connection string (update with your credentials)
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "food_nutrition_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Selected columns for the project
SELECTED_COLUMNS = [
    'code', 'product_name', 'quantity', 'image_url',
    'brands', 'categories_en', 'countries_en', 'ingredients_text',
    'allergens_en', 'labels_en',
    'nutriscore_score', 'nutriscore_grade', 'nova_group', 'pnns_groups_2',
    'energy-kcal_100g', 'fat_100g', 'saturated-fat_100g', 'carbohydrates_100g',
    'sugars_100g', 'fiber_100g', 'proteins_100g', 'salt_100g', 'sodium_100g',
]

# ============================================================================
# STEP 1: DATA DOWNLOAD
# ============================================================================

def download_openfoodfacts_data():
    """
    Download food products data from Open Food Facts API
    Filter for US products with nutriscore
    """
    print("=" * 80)
    print("STEP 1: DOWNLOADING DATA FROM OPEN FOOD FACTS")
    print("=" * 80)
    
    # Skip if file already exists
    if os.path.exists(RAW_DATA_FILE):
        print(f"✓ Raw data file already exists: {RAW_DATA_FILE}")
        print("  Skipping download. Delete file to re-download.\n")
        return pd.read_csv(RAW_DATA_FILE)
    
    products = []
    print(f"Looking for {SLICE_SIZE} US products with nutriscore...")
    
    dataset = ProductDataset(dataset_type=DatasetType.csv)
    
    for product in dataset:
        # Filter: US products only
        if (
            "countries_tags" in product 
            and product["countries_tags"]
            and isinstance(product["countries_tags"], str)
            and "en:united-states" in product["countries_tags"]
        ):
            products.append(product)
        
        # Progress indicator
        if len(products) % 10000 == 0 and len(products) > 0:
            print(f"  Progress: {len(products)} products collected...")
        
        if len(products) >= SLICE_SIZE:
            break
    
    print(f"\n✓ Downloaded {len(products)} products")
    
    # Convert to DataFrame and save
    df_raw = pd.DataFrame(products)
    
    # Select relevant columns
    existing_columns = [col for col in SELECTED_COLUMNS if col in df_raw.columns]
    df_subset = df_raw[existing_columns].copy()
    
    # Filter: Keep only products with nutriscore
    if 'nutriscore_score' in df_subset.columns:
        df_subset['nutriscore_score'].replace('', np.nan, inplace=True)
        rows_before = len(df_subset)
        df_subset = df_subset.dropna(subset=['nutriscore_score']).copy()
        rows_after = len(df_subset)
        print(f"✓ Filtered by nutriscore: {rows_after}/{rows_before} rows kept")
    
    # Save raw data
    os.makedirs(DATA_DIR, exist_ok=True)
    df_subset.to_csv(RAW_DATA_FILE, index=False)
    print(f"✓ Raw data saved to: {RAW_DATA_FILE}\n")
    
    return df_subset


# ============================================================================
# STEP 2: DATA CLEANING
# ============================================================================

def clean_data(df):
    """
    Clean and standardize the raw data
    - Handle missing values
    - Normalize text fields
    - Parse quantity into numeric and unit
    - Convert multi-valued columns to lists
    """
    print("=" * 80)
    print("STEP 2: DATA CLEANING & STANDARDIZATION")
    print("=" * 80)
    
    df = df.copy()
    
    # 2a: Standardize missing values
    placeholders = ['unknown', 'Undefined', '']
    df.replace(placeholders, np.nan, inplace=True)
    print("✓ Standardized missing value placeholders")
    
    # 2b: Remove allergens column (not needed)
    if 'allergens_en' in df.columns:
        df.drop(columns=['allergens_en'], inplace=True)
        print("✓ Removed 'allergens_en' column")
    
    # 2c: Clean single-value text columns
    text_cols = ['product_name', 'image_url', 'pnns_groups_2', 'nutriscore_grade', 'ingredients_text']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', np.nan)
    
    # Lowercase nutriscore grade
    if 'nutriscore_grade' in df.columns:
        df['nutriscore_grade'] = df['nutriscore_grade'].str.lower()
    
    print("✓ Cleaned and trimmed text columns")
    
    # 2d: Parse quantity into numeric and unit
    if 'quantity' in df.columns:
        extracted_qty = df['quantity'].astype(str).str.extract(r'(\d+\.?\d*)\s*([a-zA-Z]+)', expand=True)
        df['quantity_numeric'] = pd.to_numeric(extracted_qty[0], errors='coerce')
        df['quantity_unit'] = extracted_qty[1].str.strip()
        df.drop(columns=['quantity'], inplace=True)
        print("✓ Parsed 'quantity' into numeric and unit")
    
    # 2e: Handle multi-valued columns (convert to lists)
    multi_value_cols = ['brands', 'categories_en', 'countries_en', 'labels_en']
    for col in multi_value_cols:
        if col in df.columns:
            df[col] = df[col].fillna('').apply(
                lambda x: [item.strip() for item in str(x).split(',') if item.strip() and item.strip() != 'nan']
            )
    print("✓ Converted multi-valued columns to lists")
    
    # 2f: Convert numeric columns
    numeric_cols = [
        'nutriscore_score', 'nova_group', 'energy-kcal_100g', 'fat_100g',
        'saturated-fat_100g', 'carbohydrates_100g', 'sugars_100g', 'fiber_100g',
        'proteins_100g', 'salt_100g', 'sodium_100g'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].round(3)
    print("✓ Converted and rounded numeric columns")
    
    # 2g: Enforce non-negative constraints for nutritional values
    negative_values_count = 0
    for col in numeric_cols:
        if col in df.columns:
            # Count how many values are negative before changing them
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                negative_values_count += negative_count
                # Replace negative values with NaN (which becomes NULL in SQL)
                df.loc[df[col] < 0, col] = np.nan
    
    if negative_values_count > 0:
        print(f"✓ Enforced non-negative constraint. Replaced {negative_values_count} negative values with NaN.")
    else:
        print("✓ No negative nutritional values found. No changes needed.")
    
    # Save cleaned data
    df.to_csv(CLEANED_DATA_FILE, index=False)
    print(f"✓ Cleaned data saved to: {CLEANED_DATA_FILE}")
    print(f"  Final shape: {df.shape}\n")
    
    return df


# ============================================================================
# STEP 3: DATA NORMALIZATION (3NF)
# ============================================================================

def normalize_data(df):
    """
    Normalize data into 3NF relational schema:
    
    1. products (main entity)
    2. brands (many-to-many with products)
    3. categories (many-to-many with products)
    4. countries (many-to-many with products)
    5. labels (many-to-many with products)
    6. nutrition_facts (one-to-one with products)
    
    Returns: Dictionary of normalized DataFrames
    """
    print("=" * 80)
    print("STEP 3: DATA NORMALIZATION (3NF)")
    print("=" * 80)
    
    # Ensure 'code' is string type for consistency
    df['code'] = df['code'].astype(str)
    
    # -------------------------------------------------------------------------
    # Table 1: products (core product information)
    # -------------------------------------------------------------------------
    products_df = df[[
        'code', 'product_name', 'quantity_numeric', 'quantity_unit',
        'image_url', 'ingredients_text', 'nutriscore_score', 
        'nutriscore_grade', 'nova_group', 'pnns_groups_2'
    ]].copy()
    
    # Remove products without a valid code
    products_df = products_df[products_df['code'].notna() & (products_df['code'] != 'nan')]
    
    print(f"✓ Created 'products' table: {len(products_df)} rows")
    
    # -------------------------------------------------------------------------
    # Table 2: brands (normalized brand names)
    # -------------------------------------------------------------------------
    brands_list = []
    for brands in df['brands']:
        if isinstance(brands, list):
            brands_list.extend(brands)
    
    brands_df = pd.DataFrame({
        'brand_name': list(set(brands_list))
    })
    brands_df = brands_df[brands_df['brand_name'] != '']
    brands_df['brand_id'] = range(1, len(brands_df) + 1)
    brands_df = brands_df[['brand_id', 'brand_name']]
    
    print(f"✓ Created 'brands' table: {len(brands_df)} unique brands")
    
    # -------------------------------------------------------------------------
    # Table 3: product_brands (many-to-many relationship)
    # -------------------------------------------------------------------------
    product_brands_list = []
    for idx, row in df.iterrows():
        product_code = str(row['code'])
        if pd.notna(product_code) and product_code != 'nan':
            brands = row['brands']
            if isinstance(brands, list):
                for brand in set(brands):
                    if brand:
                        product_brands_list.append({
                            'product_code': product_code,
                            'brand_name': brand
                        })
    
    product_brands_df = pd.DataFrame(product_brands_list)
    
    # Map brand names to IDs
    if len(product_brands_df) > 0:
        brand_name_to_id = brands_df.set_index('brand_name')['brand_id'].to_dict()
        product_brands_df['brand_id'] = product_brands_df['brand_name'].map(brand_name_to_id)
        product_brands_df = product_brands_df[['product_code', 'brand_id']].dropna()
    
    print(f"✓ Created 'product_brands' junction table: {len(product_brands_df)} relationships")
    
    # -------------------------------------------------------------------------
    # Table 4: categories (normalized categories)
    # -------------------------------------------------------------------------
    categories_list = []
    for categories in df['categories_en']:
        if isinstance(categories, list):
            categories_list.extend(categories)
    
    categories_df = pd.DataFrame({
        'category_name': list(set(categories_list))
    })
    categories_df = categories_df[categories_df['category_name'] != '']
    categories_df['category_id'] = range(1, len(categories_df) + 1)
    categories_df = categories_df[['category_id', 'category_name']]
    
    print(f"✓ Created 'categories' table: {len(categories_df)} unique categories")
    
    # -------------------------------------------------------------------------
    # Table 5: product_categories (many-to-many relationship)
    # -------------------------------------------------------------------------
    product_categories_list = []
    for idx, row in df.iterrows():
        product_code = str(row['code'])
        if pd.notna(product_code) and product_code != 'nan':
            categories = row['categories_en']
            if isinstance(categories, list):
                for category in set(categories):
                    if category:
                        product_categories_list.append({
                            'product_code': product_code,
                            'category_name': category
                        })
    
    product_categories_df = pd.DataFrame(product_categories_list)
    
    if len(product_categories_df) > 0:
        category_name_to_id = categories_df.set_index('category_name')['category_id'].to_dict()
        product_categories_df['category_id'] = product_categories_df['category_name'].map(category_name_to_id)
        product_categories_df = product_categories_df[['product_code', 'category_id']].dropna()
    
    print(f"✓ Created 'product_categories' junction table: {len(product_categories_df)} relationships")
    
    # -------------------------------------------------------------------------
    # Table 6: countries (normalized countries)
    # -------------------------------------------------------------------------
    countries_list = []
    for countries in df['countries_en']:
        if isinstance(countries, list):
            countries_list.extend(countries)
    
    countries_df = pd.DataFrame({
        'country_name': list(set(countries_list))
    })
    countries_df = countries_df[countries_df['country_name'] != '']
    countries_df['country_id'] = range(1, len(countries_df) + 1)
    countries_df = countries_df[['country_id', 'country_name']]
    
    print(f"✓ Created 'countries' table: {len(countries_df)} unique countries")
    
    # -------------------------------------------------------------------------
    # Table 7: product_countries (many-to-many relationship)
    # -------------------------------------------------------------------------
    product_countries_list = []
    for idx, row in df.iterrows():
        product_code = str(row['code'])
        if pd.notna(product_code) and product_code != 'nan':
            countries = row['countries_en']
            if isinstance(countries, list):
                for country in set(countries):
                    if country:
                        product_countries_list.append({
                            'product_code': product_code,
                            'country_name': country
                        })
    
    product_countries_df = pd.DataFrame(product_countries_list)
    
    if len(product_countries_df) > 0:
        country_name_to_id = countries_df.set_index('country_name')['country_id'].to_dict()
        product_countries_df['country_id'] = product_countries_df['country_name'].map(country_name_to_id)
        product_countries_df = product_countries_df[['product_code', 'country_id']].dropna()
    
    print(f"✓ Created 'product_countries' junction table: {len(product_countries_df)} relationships")
    
    # -------------------------------------------------------------------------
    # Table 8: labels (normalized labels)
    # -------------------------------------------------------------------------
    labels_list = []
    for labels in df['labels_en']:
        if isinstance(labels, list):
            labels_list.extend(labels)
    
    labels_df = pd.DataFrame({
        'label_name': list(set(labels_list))
    })
    labels_df = labels_df[labels_df['label_name'] != '']
    labels_df['label_id'] = range(1, len(labels_df) + 1)
    labels_df = labels_df[['label_id', 'label_name']]
    
    print(f"✓ Created 'labels' table: {len(labels_df)} unique labels")
    
    # -------------------------------------------------------------------------
    # Table 9: product_labels (many-to-many relationship)
    # -------------------------------------------------------------------------
    product_labels_list = []
    for idx, row in df.iterrows():
        product_code = str(row['code'])
        if pd.notna(product_code) and product_code != 'nan':
            labels = row['labels_en']
            if isinstance(labels, list):
                for label in set(labels):
                    if label:
                        product_labels_list.append({
                            'product_code': product_code,
                            'label_name': label
                        })
    
    product_labels_df = pd.DataFrame(product_labels_list)
    
    if len(product_labels_df) > 0:
        label_name_to_id = labels_df.set_index('label_name')['label_id'].to_dict()
        product_labels_df['label_id'] = product_labels_df['label_name'].map(label_name_to_id)
        product_labels_df = product_labels_df[['product_code', 'label_id']].dropna()
    
    print(f"✓ Created 'product_labels' junction table: {len(product_labels_df)} relationships")
    
    # -------------------------------------------------------------------------
    # Table 10: nutrition_facts (one-to-one with products)
    # -------------------------------------------------------------------------
    nutrition_facts_df = df[[
        'code', 'energy-kcal_100g', 'fat_100g', 'saturated-fat_100g',
        'carbohydrates_100g', 'sugars_100g', 'fiber_100g', 'proteins_100g',
        'salt_100g', 'sodium_100g'
    ]].copy()
    
    nutrition_facts_df.rename(columns={'code': 'product_code'}, inplace=True)
    nutrition_facts_df = nutrition_facts_df[
        nutrition_facts_df['product_code'].notna() & 
        (nutrition_facts_df['product_code'] != 'nan')
    ]
    
    print(f"✓ Created 'nutrition_facts' table: {len(nutrition_facts_df)} rows")
    
    print("\n3NF Normalization Complete!\n")
    
    return {
        'products': products_df,
        'brands': brands_df,
        'product_brands': product_brands_df,
        'categories': categories_df,
        'product_categories': product_categories_df,
        'countries': countries_df,
        'product_countries': product_countries_df,
        'labels': labels_df,
        'product_labels': product_labels_df,
        'nutrition_facts': nutrition_facts_df
    }


# ============================================================================
# STEP 4: CREATE DATABASE SCHEMA
# ============================================================================

# The database schema creation is handled via docker-compose and SQL scripts.
# Therefore, this step is omitted in the script.

# ============================================================================
# STEP 5: DATA INGESTION
# ============================================================================

def ingest_data_to_database(normalized_data, engine):
    """
    Load normalized data into PostgreSQL database
    """
    print("=" * 80)
    print("STEP 5: DATA INGESTION TO POSTGRESQL")
    print("=" * 80)
    
    # Define ingestion order (respecting foreign key dependencies)
    ingestion_order = [
        'products',
        'brands',
        'categories',
        'countries',
        'labels',
        'nutrition_facts',
        'product_brands',
        'product_categories',
        'product_countries',
        'product_labels'
    ]
    
    for table_name in ingestion_order:
        df = normalized_data[table_name]
        
        # Handle column name mapping for nutrition_facts
        if table_name == 'nutrition_facts':
            df = df.rename(columns={
                'energy-kcal_100g': 'energy_kcal_100g',
                'saturated-fat_100g': 'saturated_fat_100g'
            })
        
        # Convert product_code to string to match schema
        if 'product_code' in df.columns:
            df['product_code'] = df['product_code'].astype(str)
        if 'code' in df.columns:
            df['code'] = df['code'].astype(str)
        
        # Ingest data
        try:
            df.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
            print(f"✓ Ingested {len(df):,} rows into '{table_name}'")
        except Exception as e:
            print(f"✗ Error ingesting '{table_name}': {str(e)}")
            raise
    
    print("\n✓ Data ingestion complete!\n")


# ============================================================================
# STEP 6: VERIFICATION QUERIES
# ============================================================================

def verify_database(engine):
    """
    Run verification queries to ensure data integrity
    """
    print("=" * 80)
    print("STEP 6: DATABASE VERIFICATION")
    print("=" * 80)
    
    queries = {
        "Total products": "SELECT COUNT(*) FROM products",
        "Products with nutrition data": "SELECT COUNT(*) FROM nutrition_facts",
        "Unique brands": "SELECT COUNT(*) FROM brands",
        "Unique categories": "SELECT COUNT(*) FROM categories",
        "Unique countries": "SELECT COUNT(*) FROM countries",
        "Unique labels": "SELECT COUNT(*) FROM labels",
        "Average nutriscore": "SELECT AVG(nutriscore_score) FROM products WHERE nutriscore_score IS NOT NULL",
        "Products by grade": """
            SELECT nutriscore_grade, COUNT(*) as count 
            FROM products 
            WHERE nutriscore_grade IS NOT NULL 
            GROUP BY nutriscore_grade 
            ORDER BY nutriscore_grade
        """
    }
    
    with engine.connect() as conn:
        for query_name, query in queries.items():
            result = conn.execute(text(query))
            
            if "by grade" in query_name.lower():
                print(f"\n{query_name}:")
                for row in result:
                    print(f"  Grade {row[0].upper()}: {row[1]:,} products")
            else:
                value = result.scalar()
                if isinstance(value, float):
                    print(f"✓ {query_name}: {value:.2f}")
                else:
                    print(f"✓ {query_name}: {value:,}")
    
    print("\n" + "=" * 80)
    print("DATABASE VERIFICATION COMPLETE!")
    print("=" * 80 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function - runs all pipeline steps
    """
    print("\n")
    print("=" * 80)
    print("PHASE 1: DATABASE FOUNDATION PIPELINE")
    print("Global Food & Nutrition Explorer")
    print("=" * 80)
    print("\n")
    
    # Step 1: Download data
    df_raw = download_openfoodfacts_data()
    
    # Step 2: Clean data
    df_cleaned = clean_data(df_raw)
    
    # Step 3: Normalize data
    normalized_data = normalize_data(df_cleaned)
    
    # Step 4: Create database connection
    print("=" * 80)
    print("CONNECTING TO DATABASE")
    print("=" * 80)
    try:
        engine = create_engine(DATABASE_URL)
        print(f"✓ Connected to database: {DATABASE_URL.split('@')[1]}\n")
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'food_nutrition_db' exists")
        print("  3. Credentials in DATABASE_URL are correct")
        return
    
    # Step 5: Create schema
    # create_database_schema(engine)
    # docker-compose will handle schema creation
    
    # Step 6: Ingest data
    ingest_data_to_database(normalized_data, engine)
    
    # Step 7: Verify
    verify_database(engine)
    
    print("=" * 80)
    print("✓✓✓ PHASE 1 PIPELINE COMPLETED SUCCESSFULLY ✓✓✓")
    print("=" * 80)
    print("\nNext Steps:")
    print("  1. Review the ERD diagram (create using dbdiagram.io or similar)")
    print("  2. Write 3NF justification report")
    print("  3. Create demo video showing:")
    print("     - Your data model")
    print("     - This script running")
    print("     - Sample queries on the populated database")
    print("  4. Set up docker-compose.yml for easy deployment")
    print("\n")


if __name__ == "__main__":
    main()