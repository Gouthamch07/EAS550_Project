import os
from openfoodfacts import ProductDataset, DatasetType
import pandas as pd
import numpy as np # Import numpy to handle NaN values

# --- Download Configuration ---
slice_size = 200000  # Target number of US products to find
products = []

# --- Recommended Columns ---
# This is the subset of columns we will keep for the project
selected_columns = [
    # Core Identification
    'code', 'product_name', 'quantity', 'image_url',
    # Categorization & Relationships
    'brands', 'categories_en', 'countries_en', 'ingredients_text',
    'allergens_en', 'labels_en',
    # Health & Nutrition Scores
    'nutriscore_score', 'nutriscore_grade', 'nova_group', 'pnns_groups_2',
    # Key Nutritional Values
    'energy-kcal_100g', 'fat_100g', 'saturated-fat_100g', 'carbohydrates_100g',
    'sugars_100g', 'fiber_100g', 'proteins_100g', 'salt_100g', 'sodium_100g',
]

# --- Data Fetching Loop ---
print(f"Starting download... looking for {slice_size} products sold in the US.")
dataset = ProductDataset(dataset_type=DatasetType.csv)

for product in dataset:
    # Check if the product dictionary has the 'countries_tags' key and it's not empty
    if (
        "countries_tags" in product and product["countries_tags"]
        and isinstance(product["countries_tags"], str) # Ensure it's a string to avoid errors
        and "en:united-states" in product["countries_tags"]
    ):
        products.append(product)
    
    # Stop when the desired number of products is reached
    if len(products) >= slice_size:
        break

print(f"\nFound and downloaded {len(products)} initial products.")

# --- Data Processing and Filtering ---

# 1. Convert the list of dictionaries to a Pandas DataFrame
df_raw = pd.DataFrame(products)

# 2. Select only the desired columns
# We check if each column exists in the DataFrame before trying to select it
existing_columns = [col for col in selected_columns if col in df_raw.columns]
df_subset = df_raw[existing_columns].copy()
print(f"Filtered down to {len(df_subset.columns)} relevant columns.")

# 3. Filter rows to keep only those where 'nutriscore_score' is populated
# First, ensure the column exists
if 'nutriscore_score' in df_subset.columns:
    # Replace empty strings with NaN to ensure dropna() works correctly
    df_subset['nutriscore_score'].replace('', np.nan, inplace=True)
    
    # Get the count before dropping
    rows_before_drop = len(df_subset)
    
    # Drop rows where 'nutriscore_score' is NaN
    df_final = df_subset.dropna(subset=['nutriscore_score']).copy()
    
    rows_after_drop = len(df_final)
    print(f"Filtered rows based on 'nutriscore_score': Kept {rows_after_drop} out of {rows_before_drop} rows.")
else:
    print("Warning: 'nutriscore_score' column not found. Skipping row filtering.")
    df_final = df_subset

# --- Save the Final DataFrame ---
output_filename = "./data/openfoodfacts_data.csv"
output_dir = os.path.dirname(output_filename)
os.makedirs(output_dir, exist_ok=True)  # Make data directory if it doesn't exist

# --- Final Output ---
print(f"\nProcessing complete!")
print(f"Final DataFrame shape: {df_final.shape}")
print(f"Clean data saved to '{output_filename}'")
print("\nFirst 5 rows of the final dataset:")
print(df_final.head())