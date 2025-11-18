import os
from openfoodfacts import ProductDataset, DatasetType
import pandas as pd
import numpy as np

df=pd.read_csv("./data/openfoodfacts_data.csv")
print("\n--- Starting Data Cleaning Process ---")


# ---Step 1: standardization of missing values & column removal---

# Replace all known text placeholders with a standard null value (np.nan)
placeholders = ['unknown', 'Undefined']
df.replace(placeholders, np.nan, inplace=True)
print("Step 1a: Standardized placeholder text ('unknown', 'Undefined') to null.")

# Remove the 'allergens_en' column as it's not needed
if 'allergens_en' in df.columns:
    df.drop(columns=['allergens_en'], inplace=True)
    print("Step 1b: Removed the 'allergens_en' column.")


# ---Step 2: Cleaning columns---

# --- Text and Identifier Columns ---
df['product_name'] = df['product_name'].str.strip()
df['image_url'] = df['image_url'].str.strip()
df['pnns_groups_2'] = df['pnns_groups_2'].str.strip()
df['nutriscore_grade'] = df['nutriscore_grade'].str.strip().str.lower()
df['ingredients_text'] = df['ingredients_text'].str.strip()
print("Step 2a: Cleaned and trimmed whitespace from single-value text columns.")

# --- Deconstruct the 'quantity' Column ---
if 'quantity' in df.columns:
    # Extract numeric and unit parts using regex
    extracted_qty = df['quantity'].str.extract(r'(\d+\.?\d*)\s*([a-zA-Z]+)', expand=True)
    
    # Create new columns and convert the numeric part
    df['quantity_numeric'] = pd.to_numeric(extracted_qty[0], errors='coerce')
    df['quantity_unit'] = extracted_qty[1].str.strip()
    
    # Drop the original column
    df.drop(columns=['quantity'], inplace=True)
    print("Step 2b: Deconstructed 'quantity' into 'quantity_numeric' and 'quantity_unit'.")

# --- Handle Multi-Valued Text Columns ---
multi_value_cols = ['brands', 'categories_en', 'countries_en', 'labels_en']
for col in multi_value_cols:
    if col in df.columns:
        # Fill nulls with an empty string temporarily to allow .str accessor
        # Then split, creating lists. Nulls will result in an empty list.
        df[col] = df[col].fillna('').apply(
            lambda x: [item.strip() for item in x.split(',') if item.strip()]
        )
print("Step 2c: Cleaned and split multi-valued columns into lists.")

# --- Clean and Convert All Numeric Columns ---
numeric_cols = [
    'nutriscore_score', 'nova_group', 'energy-kcal_100g', 'fat_100g',
    'saturated-fat_100g', 'carbohydrates_100g', 'sugars_100g', 'fiber_100g',
    'proteins_100g', 'salt_100g', 'sodium_100g'
]
for col in numeric_cols:
    if col in df.columns:
        # 'coerce' will turn any non-numeric values (including existing NaNs) into NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Round to 3 decimal places for consistency
        df[col] = df[col].round(3)
print("Step 2d: Converted all nutrition and score columns to numeric and rounded them.")

# --- FINAL OUTPUT ---

print("\n\n--- CLEANING PROCESS COMPLETE ---")
print("The DataFrame 'df' is now fully cleaned in memory and ready for database ingestion.")
print(f"Final DataFrame shape: {df.shape}")

print("\nData types and non-null counts of the final DataFrame:")
df.info()

print("\nFirst 5 rows of the final, cleaned dataset to demonstrate the changes:")
# Displaying a subset of columns to clearly show the transformations
display_cols = [
    'product_name', 'brands', 'categories_en', 'nutriscore_grade',
    'pnns_groups_2', 'saturated-fat_100g', 'quantity_numeric', 'quantity_unit'
]
# Ensure display_cols exist before trying to print them
existing_display_cols = [col for col in display_cols if col in df.columns]
print(df[existing_display_cols].head())

output_filename = "./data/openfoodfacts_data.csv"
df.to_csv(output_filename, index=False)