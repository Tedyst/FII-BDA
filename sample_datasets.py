import pandas as pd
import os

dataset_dir = "/home/tedy/Git/FII-BDA/dataset"
output_dir = "/home/tedy/Git/FII-BDA/sampled_dataset"

os.makedirs(output_dir, exist_ok=True)

print("Starting dataset sampling...")

# 1. Sample food_nutrient.csv (~100k lines)
print("\n1. Sampling food_nutrient.csv...")
fn_df = pd.read_csv(f"{dataset_dir}/food_nutrient.csv", low_memory=False)
print(f"   Original: {len(fn_df)} rows")

sampled_fn_df = fn_df.sample(n=100000, random_state=42)
print(f"   Sampled: {len(sampled_fn_df)} rows")

sampled_fn_df.to_csv(f"{output_dir}/food_nutrient.csv", index=False)
print(f"   Saved to {output_dir}/food_nutrient.csv")

unique_fdc_ids = set(sampled_fn_df['fdc_id'].unique())
unique_nutrient_ids = set(sampled_fn_df['nutrient_id'].unique())
print(f"   Unique fdc_ids: {len(unique_fdc_ids)}")
print(f"   Unique nutrient_ids: {len(unique_nutrient_ids)}")

# 2. Filter food.csv by fdc_id
print("\n2. Filtering food.csv...")
food_df = pd.read_csv(f"{dataset_dir}/food.csv", low_memory=False)
print(f"   Original: {len(food_df)} rows")

filtered_food_df = food_df[food_df['fdc_id'].isin(unique_fdc_ids)]
print(f"   Filtered: {len(filtered_food_df)} rows")
filtered_food_df.to_csv(f"{output_dir}/food.csv", index=False)
print(f"   Saved to {output_dir}/food.csv")

# 3. Copy all nutrient.csv
print("\n3. Copying nutrient.csv...")
nutrient_df = pd.read_csv(f"{dataset_dir}/nutrient.csv", low_memory=False)
print(f"   Total: {len(nutrient_df)} rows")
nutrient_df.to_csv(f"{output_dir}/nutrient.csv", index=False)

# 4. Filter food_portion.csv by fdc_id
print("\n4. Filtering food_portion.csv...")
if os.path.exists(f"{dataset_dir}/food_portion.csv"):
    fp_df = pd.read_csv(f"{dataset_dir}/food_portion.csv", low_memory=False)
    print(f"   Original: {len(fp_df)} rows")
    filtered_fp_df = fp_df[fp_df['fdc_id'].isin(unique_fdc_ids)]
    print(f"   Filtered: {len(filtered_fp_df)} rows")
    filtered_fp_df.to_csv(f"{output_dir}/food_portion.csv", index=False)
    print(f"   Saved to {output_dir}/food_portion.csv")
    
    # 5. Filter measure_unit.csv
    print("\n5. Filtering measure_unit.csv...")
    if os.path.exists(f"{dataset_dir}/measure_unit.csv") and 'measure_unit_id' in filtered_fp_df.columns:
        mu_df = pd.read_csv(f"{dataset_dir}/measure_unit.csv", low_memory=False)
        print(f"   Original: {len(mu_df)} rows")
        unique_mu_ids = set(filtered_fp_df['measure_unit_id'].dropna().unique())
        filtered_mu_df = mu_df[mu_df['id'].isin(unique_mu_ids)]
        print(f"   Filtered: {len(filtered_mu_df)} rows")
        filtered_mu_df.to_csv(f"{output_dir}/measure_unit.csv", index=False)

# 6. Copy food_category.csv (all records)
print("\n6. Copying food_category.csv...")
if os.path.exists(f"{dataset_dir}/food_category.csv"):
    fc_df = pd.read_csv(f"{dataset_dir}/food_category.csv", low_memory=False)
    print(f"   Total: {len(fc_df)} rows")
    fc_df.to_csv(f"{output_dir}/food_category.csv", index=False)

# 7. Filter wweia_food_category.csv
print("\n7. Filtering wweia_food_category.csv...")
if os.path.exists(f"{dataset_dir}/wweia_food_category.csv"):
    wfc_df = pd.read_csv(f"{dataset_dir}/wweia_food_category.csv", low_memory=False)
    print(f"   Original: {len(wfc_df)} rows")
    if 'fdc_id' in wfc_df.columns:
        filtered_wfc_df = wfc_df[wfc_df['fdc_id'].isin(unique_fdc_ids)]
        print(f"   Filtered: {len(filtered_wfc_df)} rows")
        filtered_wfc_df.to_csv(f"{output_dir}/wweia_food_category.csv", index=False)

# 8. Copy reference tables
print("\n8. Copying reference tables...")
reference_tables = [
    'food_nutrient_derivation.csv',
    'lab_method.csv',
    'lab_method_code.csv',
    'lab_method_nutrient.csv'
]

for table in reference_tables:
    table_path = f"{dataset_dir}/{table}"
    if os.path.exists(table_path):
        ref_df = pd.read_csv(table_path, low_memory=False)
        print(f"   {table}: {len(ref_df)} rows")
        ref_df.to_csv(f"{output_dir}/{table}", index=False)

print("\n" + "="*60)
print("Dataset sampling complete!")
print(f"Output directory: {output_dir}")
print("="*60)

print("\nSampled dataset summary:")
for f in sorted(os.listdir(output_dir)):
    df = pd.read_csv(f"{output_dir}/{f}", low_memory=False)
    print(f"  {f}: {len(df)} rows")
