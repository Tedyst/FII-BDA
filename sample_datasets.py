import os

import pandas as pd


dataset_dir = "/home/tedy/Git/FII-BDA/converted-dataset"
output_dir = "/home/tedy/Git/FII-BDA/sampled_dataset"

os.makedirs(output_dir, exist_ok=True)

print("Starting dataset sampling...")
print("Note: Sampling is SLOW due to large file sizes. Please be patient...")
print("This may take 5-10 minutes...")

print("\n1. Selecting random foods and filtering nutrients...")
food_df_full = pd.read_parquet(f"{dataset_dir}/food.parquet")
print(f"   food.parquet rows: {len(food_df_full)}")

fn_df = pd.read_parquet(f"{dataset_dir}/food_nutrient.parquet")
print(f"   food_nutrient.parquet rows: {len(fn_df)}")

eligible_foods_df = food_df_full.copy()
print(f"   eligible foods (all food.csv rows): {len(eligible_foods_df)}")

target_food_count = 5000
if len(eligible_foods_df) < target_food_count:
    target_food_count = len(eligible_foods_df)

sampled_foods_df = eligible_foods_df.sample(n=target_food_count, random_state=42)
unique_fdc_ids = set(sampled_foods_df["fdc_id"].unique())
print(f"   sampled foods: {len(unique_fdc_ids)}")

sampled_fn_df = fn_df[fn_df["fdc_id"].isin(unique_fdc_ids)].copy()
print(f"   food-nutrient rows for sampled foods: {len(sampled_fn_df)}")

sampled_fn_df.to_parquet(
    f"{output_dir}/food_nutrient.parquet", engine="pyarrow", index=False
)
print(f"   Saved to {output_dir}/food_nutrient.parquet")

unique_nutrient_ids = set(sampled_fn_df["nutrient_id"].unique())
print(f"   Unique nutrient_ids: {len(unique_nutrient_ids)}")

# 2. Filter food.csv by fdc_id
print("\n2. Filtering food.parquet...")
food_df = food_df_full
print(f"   Original: {len(food_df)} rows")

filtered_food_df = food_df[food_df["fdc_id"].isin(unique_fdc_ids)]
print(f"   Filtered: {len(filtered_food_df)} rows")
filtered_food_df.to_parquet(f"{output_dir}/food.parquet", engine="pyarrow", index=False)
print(f"   Saved to {output_dir}/food.parquet")

# 3. Copy all nutrient.csv
print("\n3. Copying nutrient.parquet...")
nutrient_df = pd.read_parquet(f"{dataset_dir}/nutrient.parquet")
print(f"   Total: {len(nutrient_df)} rows")
nutrient_df.to_parquet(f"{output_dir}/nutrient.parquet", engine="pyarrow", index=False)

# 4. Filter food_portion.csv by fdc_id
print("\n4. Filtering food_portion.parquet...")
if os.path.exists(f"{dataset_dir}/food_portion.parquet"):
    fp_df = pd.read_parquet(f"{dataset_dir}/food_portion.parquet")
    print(f"   Original: {len(fp_df)} rows")
    filtered_fp_df = fp_df[fp_df["fdc_id"].isin(unique_fdc_ids)]
    print(f"   Filtered: {len(filtered_fp_df)} rows")
    filtered_fp_df.to_parquet(
        f"{output_dir}/food_portion.parquet", engine="pyarrow", index=False
    )
    print(f"   Saved to {output_dir}/food_portion.parquet")

    # 5. Filter measure_unit.csv
    print("\n5. Filtering measure_unit.parquet...")
    if (
        os.path.exists(f"{dataset_dir}/measure_unit.parquet")
        and "measure_unit_id" in filtered_fp_df.columns
    ):
        mu_df = pd.read_parquet(f"{dataset_dir}/measure_unit.parquet")
        print(f"   Original: {len(mu_df)} rows")
        unique_mu_ids = set(filtered_fp_df["measure_unit_id"].dropna().unique())
        filtered_mu_df = mu_df[mu_df["id"].isin(unique_mu_ids)]
        print(f"   Filtered: {len(filtered_mu_df)} rows")
        filtered_mu_df.to_parquet(
            f"{output_dir}/measure_unit.parquet", engine="pyarrow", index=False
        )

# 6. Copy food_category.csv (all records)
print("\n6. Copying food_category.parquet...")
if os.path.exists(f"{dataset_dir}/food_category.parquet"):
    fc_df = pd.read_parquet(f"{dataset_dir}/food_category.parquet")
    print(f"   Total: {len(fc_df)} rows")
    fc_df.to_parquet(
        f"{output_dir}/food_category.parquet", engine="pyarrow", index=False
    )

# 7. Filter wweia_food_category.csv
print("\n7. Filtering wweia_food_category.parquet...")
if os.path.exists(f"{dataset_dir}/wweia_food_category.parquet"):
    wfc_df = pd.read_parquet(f"{dataset_dir}/wweia_food_category.parquet")
    print(f"   Original: {len(wfc_df)} rows")
    if "fdc_id" in wfc_df.columns:
        filtered_wfc_df = wfc_df[wfc_df["fdc_id"].isin(unique_fdc_ids)]
        print(f"   Filtered: {len(filtered_wfc_df)} rows")
        filtered_wfc_df.to_parquet(
            f"{output_dir}/wweia_food_category.parquet", engine="pyarrow", index=False
        )

# 8. Copy/filter reference and conversion tables
print("\n8. Copying reference and conversion tables...")
reference_tables = [
    "food_nutrient_derivation.parquet",
    "lab_method.parquet",
    "lab_method_code.parquet",
    "lab_method_nutrient.parquet",
]

for table in reference_tables:
    table_path = f"{dataset_dir}/{table}"
    if os.path.exists(table_path):
        ref_df = pd.read_parquet(table_path)
        print(f"   {table}: {len(ref_df)} rows")
        ref_df.to_parquet(f"{output_dir}/{table}", engine="pyarrow", index=False)

# 9. Copy calorie and nutrient conversion factors (all - they're small)
print("\n9. Copying calorie and nutrient conversion factors...")
conversion_tables = [
    "food_calorie_conversion_factor.parquet",
    "food_nutrient_conversion_factor.parquet",
    "food_protein_conversion_factor.parquet",
]

for table in conversion_tables:
    table_path = f"{dataset_dir}/{table}"
    if os.path.exists(table_path):
        conv_df = pd.read_parquet(table_path)
        print(f"   {table}: {len(conv_df)} rows")
        conv_df.to_parquet(f"{output_dir}/{table}", engine="pyarrow", index=False)

# 10. Copy food type tables (all - reference data)
print("\n10. Copying food type reference tables...")
food_type_tables = [
    "foundation_food.parquet",
    "sr_legacy_food.parquet",
    "survey_fndds_food.parquet",
]

for table in food_type_tables:
    table_path = f"{dataset_dir}/{table}"
    if os.path.exists(table_path):
        type_df = pd.read_parquet(table_path)
        print(f"   {table}: {len(type_df)} rows")
        type_df.to_parquet(f"{output_dir}/{table}", engine="pyarrow", index=False)

# 11. Copy food attribute tables (all - reference data)
print("\n11. Copying food attribute tables...")
attribute_tables = [
    "food_attribute_type.parquet",
    "food_attribute.parquet",
]

for table in attribute_tables:
    table_path = f"{dataset_dir}/{table}"
    if os.path.exists(table_path):
        attr_df = pd.read_parquet(table_path)
        print(f"   {table}: {len(attr_df)} rows")
        attr_df.to_parquet(f"{output_dir}/{table}", engine="pyarrow", index=False)

# 12. Filter food source and metadata tables by fdc_id
print("\n12. Filtering food source and metadata tables...")
source_tables = [
    "food_nutrient_source.parquet",
    "food_update_log_entry.parquet",
]

for table in source_tables:
    table_path = f"{dataset_dir}/{table}"
    if os.path.exists(table_path):
        source_df = pd.read_parquet(table_path)
        print(f"   {table} (original): {len(source_df)} rows")
        if "fdc_id" in source_df.columns:
            filtered_source_df = source_df[source_df["fdc_id"].isin(unique_fdc_ids)]
            print(f"   {table} (filtered): {len(filtered_source_df)} rows")
            filtered_source_df.to_parquet(
                f"{output_dir}/{table}", engine="pyarrow", index=False
            )
        else:
            print(f"   {table}: {len(source_df)} rows (copied all)")
            source_df.to_parquet(f"{output_dir}/{table}", engine="pyarrow", index=False)

# 13. Copy food component table (all records)
print("\n13. Copying food_component.parquet...")
if os.path.exists(f"{dataset_dir}/food_component.parquet"):
    fc_df = pd.read_parquet(f"{dataset_dir}/food_component.parquet")
    print(f"   Total: {len(fc_df)} rows")
    fc_df.to_parquet(
        f"{output_dir}/food_component.parquet", engine="pyarrow", index=False
    )

# 14. Filter branded_food.csv by fdc_id
print("\n14. Filtering branded_food.parquet...")
if os.path.exists(f"{dataset_dir}/branded_food.parquet"):
    bf_df = pd.read_parquet(f"{dataset_dir}/branded_food.parquet")
    print(f"   Original: {len(bf_df)} rows")
    if "fdc_id" in bf_df.columns:
        filtered_bf_df = bf_df[bf_df["fdc_id"].isin(unique_fdc_ids)]
        print(f"   Filtered: {len(filtered_bf_df)} rows")
        filtered_bf_df.to_parquet(
            f"{output_dir}/branded_food.parquet", engine="pyarrow", index=False
        )

# 15. Filter input_food.csv by fdc_id
print("\n15. Filtering input_food.parquet...")
if os.path.exists(f"{dataset_dir}/input_food.parquet"):
    if_df = pd.read_parquet(f"{dataset_dir}/input_food.parquet")
    print(f"   Original: {len(if_df)} rows")
    if "fdc_id" in if_df.columns:
        filtered_if_df = if_df[if_df["fdc_id"].isin(unique_fdc_ids)]
        print(f"   Filtered: {len(filtered_if_df)} rows")
        filtered_if_df.to_parquet(
            f"{output_dir}/input_food.parquet", engine="pyarrow", index=False
        )

# 16. Filter sample_food.csv by fdc_id
print("\n16. Filtering sample_food.parquet...")
if os.path.exists(f"{dataset_dir}/sample_food.parquet"):
    sf_df = pd.read_parquet(f"{dataset_dir}/sample_food.parquet")
    print(f"   Original: {len(sf_df)} rows")
    if "fdc_id" in sf_df.columns:
        filtered_sf_df = sf_df[sf_df["fdc_id"].isin(unique_fdc_ids)]
        print(f"   Filtered: {len(filtered_sf_df)} rows")
        filtered_sf_df.to_parquet(
            f"{output_dir}/sample_food.parquet", engine="pyarrow", index=False
        )

# 17. Copy specialized analysis tables (all records)
print("\n17. Copying specialized analysis tables...")
specialized_tables = [
    "retention_factor.parquet",
    "microbe.parquet",
    "market_acquisition.parquet",
]

for table in specialized_tables:
    table_path = f"{dataset_dir}/{table}"
    if os.path.exists(table_path):
        spec_df = pd.read_parquet(table_path)
        print(f"   {table}: {len(spec_df)} rows")
        spec_df.to_parquet(f"{output_dir}/{table}", engine="pyarrow", index=False)

# 18. Copy FNDDS-specific tables (all records)
print("\n18. Copying FNDDS-specific tables...")
fndds_tables = [
    "fndds_derivation.parquet",
    "fndds_ingredient_nutrient_value.parquet",
]

for table in fndds_tables:
    table_path = f"{dataset_dir}/{table}"
    if os.path.exists(table_path):
        fndds_df = pd.read_parquet(table_path)
        print(f"   {table}: {len(fndds_df)} rows")
        fndds_df.to_parquet(f"{output_dir}/{table}", engine="pyarrow", index=False)

# 19. Copy sampling and acquisition tables (all records)
print("\n19. Copying sampling and acquisition tables...")
sampling_tables = [
    "acquisition_samples.parquet",
    "agricultural_samples.parquet",
    "sub_sample_food.parquet",
    "sub_sample_result.parquet",
]

for table in sampling_tables:
    table_path = f"{dataset_dir}/{table}"
    if os.path.exists(table_path):
        samp_df = pd.read_parquet(table_path)
        print(f"   {table}: {len(samp_df)} rows")
        samp_df.to_parquet(f"{output_dir}/{table}", engine="pyarrow", index=False)

print("\n" + "=" * 60)
print("Dataset sampling complete!")
print(f"Output directory: {output_dir}")
print("=" * 60)

print("\nSampled dataset summary:")
for f in sorted(os.listdir(output_dir)):
    if not f.endswith(".parquet"):
        continue
    df = pd.read_parquet(f"{output_dir}/{f}")
    print(f"  {f}: {len(df)} rows")
