# Food Nutritional Analysis (USDA FDC)

This project analyzes food composition and nutrients using the USDA FoodData Central (FDC) dataset. It converts the official CSVs to Parquet for faster processing, samples manageable subsets, and uses Apache Spark to build comprehensive nutritional profiles per food (`fdc_id`).

You need the full dataset from: https://fdc.nal.usda.gov/download-datasets

## Features

- **CSV → Parquet conversion**: Faster IO via `pandas` + `pyarrow`
- **Sampling utility**: Create a smaller Parquet subset preserving relationships
- **Spark processing**: Aggregate and pivot nutrient values into profiles
- **Export results**: Write final nutritional profiles to Parquet

## Project Structure

```
FII-BDA/
├── dataset/                       # Place official FDC CSVs here
├── converted-dataset/             # Generated Parquet files (CSV → Parquet)
├── sampled_dataset/               # Sampled Parquet subset (generated)
├── output/                        # Results (generated)
│   ├── nutritional_profiles_parquet/
├── convert_csvs_to_parquet.py     # CSV → Parquet converter (pandas)
├── sample_datasets.py             # Sampling script (reads/writes Parquet)
├── generate_nutritional_values.ipynb  # Spark processing to build profiles
├── main.py
├── pyproject.toml
├── README.md
├── QUICKSTART.md
└── PROJECT_SUMMARY.md
```

## Requirements

- Python 3.10+
- Apache Spark 3.5+
- Java 8 or 11 (for Spark)
- JupyterLab
- `pandas`, `pyarrow`, `pyspark` (managed via `pyproject.toml`)

## Install & Setup

1. Install Python deps (using uv recommended):

```bash
uv sync
```

2. Install Apache Spark:
   - Download: https://spark.apache.org/downloads.html
   - Set environment:

```bash
export SPARK_HOME=/path/to/spark
export PATH=$SPARK_HOME/bin:$PATH
```

3. Download the full FDC dataset (CSV) and extract into [dataset/](dataset/):

   - https://fdc.nal.usda.gov/download-datasets
   - Ensure files like `food.csv`, `nutrient.csv`, `food_nutrient.csv`, `food_portion.csv`, `measure_unit.csv` exist.

4. Convert CSVs to Parquet:

```bash
uv run python convert_csvs_to_parquet.py --input-dir dataset --output-dir converted-dataset
```

5. (Optional) Create a sampled Parquet subset:

```bash
uv run python sample_datasets.py
```

6. Generate nutritional profiles (Spark):
   - Open and run the notebook [generate_nutritional_values.ipynb](generate_nutritional_values.ipynb)
   - Outputs will be written to [output/nutritional_profiles_parquet/](output/nutritional_profiles_parquet/)

## Usage

Key flow:

- Place CSVs in [dataset/](dataset/)
- Convert to Parquet with [convert_csvs_to_parquet.py](convert_csvs_to_parquet.py)
- Optionally sample with [sample_datasets.py](sample_datasets.py)
- Run Spark notebook [generate_nutritional_values.ipynb](generate_nutritional_values.ipynb)

## Outputs

- Parquet: [output/nutritional_profiles_parquet/](output/nutritional_profiles_parquet/)

## Notes

- Ensure Parquet inputs exist in [converted-dataset/](converted-dataset/) before running the notebook.
- `pyarrow` is required for Parquet writes/reads in `pandas`.

## Roadmap

- **Food statistics**
  - Top foods by calories/gram, protein/calorie, protein/gram
  - Fiber/calorie, lowest/highest sugar/gram, sodium/calorie
  - Composite nutrient-density scoring
- **Healthy recommendations from likes**
  - Suggest similar-category foods optimizing health metrics (higher protein density, lower sugar/sodium, adequate fiber)
  - Respect dietary filters (vegetarian/vegan, allergen exclusions)
- **Goal-based ranking**
  - Rank foods against macro/micro targets (e.g., 30g protein, <10g sugars per serving)
- **Visual exploration**
  - Plots and small dashboards for distributions and top-k lists
- **Meal composition**
  - Complementary foods to meet targets with minimal sugar/sodium

## Datasets

USDA FoodData Central (FDC) — download from: https://fdc.nal.usda.gov/download-datasets
Place extracted CSVs under [dataset/](dataset/).

## Processing Overview

1. Convert CSVs to Parquet for efficient IO.
2. (Optional) Sample a subset of foods and related tables.
3. Use Spark to aggregate and pivot nutrient data to per-food profiles.
4. Export final profiles to Parquet.

## Output

- Final nutritional profiles in Parquet format under [output/nutritional_profiles_parquet/](output/nutritional_profiles_parquet/)

## Performance Notes

- Processing speed depends on Parquet conversion and Spark config (memory, partitions).

## Troubleshooting

- Ensure `pyarrow` is installed for Parquet operations.
- Verify Parquet files exist in [converted-dataset/](converted-dataset/) if Spark reads fail.
- Adjust Spark memory: `spark.driver.memory`, `spark.executor.memory`.

## License

Educational project for Big Data Analytics (FII).

## Authors

- Tedy Stoica, MISS2
- Dan Frunza, MISS2
- Iulian Gherghevici, MISS2
