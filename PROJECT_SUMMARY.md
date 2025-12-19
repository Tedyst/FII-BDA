# Project Summary: Food Nutritional Analysis (USDA FDC)

## Overview

This project analyzes food composition and nutrients using the USDA FoodData Central (FDC) dataset. It converts the official CSVs to Parquet, optionally samples a manageable subset, and uses Apache Spark to aggregate and pivot nutrient values into comprehensive per-food profiles.

You need the full dataset from: https://fdc.nal.usda.gov/download-datasets

## Key Features

1. **CSV → Parquet conversion** for efficient IO (`pandas` + `pyarrow`)
2. **Sampling utility** to create smaller, consistent subsets
3. **Spark aggregation and pivot** to build per-food nutrient profiles
4. **Parquet export** of final nutritional profiles

## Technical Architecture

### Data Flow

1. **Extract**: Download FDC CSVs and place in [dataset/](dataset/)
2. **Transform**:

- Convert CSVs to Parquet in [converted-dataset/](converted-dataset/)
- (Optional) Sample related tables to [sampled_dataset/](sampled_dataset/)

3. **Load/Process (Spark)**:

- Read Parquet inputs
- Aggregate nutrient values per `fdc_id`
- Pivot nutrients into wide profiles

4. **Export**:

- Write final profiles to [output/nutritional_profiles_parquet/](output/nutritional_profiles_parquet/)

### Model Training

- **Algorithm**: ALS (Alternating Least Squares)
- **Hyperparameters**:
  - Rank: 5-20 (latent factors)
  - Regularization: 0.01-1.0
  - Max Iterations: 5-15
- **Optimization**: Grid search to achieve target RMSE
- **Evaluation**: RMSE and MAE metrics

### Nutritional Profile Generation

- Joins `food`, `food_nutrient`, `nutrient`, and related tables
- Aggregates and pivots nutrient amounts into a single wide table per `fdc_id`
- Outputs comprehensive Parquet dataset for downstream use

## File Structure

```
FII-BDA/
├── dataset/                       # Official FDC CSVs (downloaded)
├── converted-dataset/             # Parquet after conversion
├── sampled_dataset/               # Optional Parquet subset
├── output/                        # Results
│   └── nutritional_profiles_parquet/
├── convert_csvs_to_parquet.py     # CSV → Parquet converter
├── sample_datasets.py             # Sampling (Parquet only)
├── generate_nutritional_values.ipynb  # Spark processing
├── README.md
├── QUICKSTART.md
└── PROJECT_SUMMARY.md
```

## Performance Notes

- Performance depends on Parquet conversion, Spark memory, and partitioning.

## Usage

1. Download FDC CSVs to [dataset/](dataset/): https://fdc.nal.usda.gov/download-datasets
2. Convert to Parquet:

```bash
uv run python convert_csvs_to_parquet.py --input-dir dataset --output-dir converted-dataset
```

3. (Optional) Sample subset:

```bash
uv run python sample_datasets.py
```

4. Generate nutritional profiles:

- Run [generate_nutritional_values.ipynb](generate_nutritional_values.ipynb)

## Technologies Used

- **Apache Spark 3.5+**
- **PySpark**
- **Pandas + PyArrow** (Parquet conversion)
- **JupyterLab**
- **Python 3.10+**

## Data Sources

- **USDA FoodData Central (FDC)**: Food composition and nutrient information
  - Download: https://fdc.nal.usda.gov/download-datasets

## Future Enhancements

- Add delta updates when new FDC releases drop
- Validate units and conversions across tables
- Provide lightweight APIs for profile queries

### Planned Additions

- **Food statistics**: Compute top foods by metrics such as:
  - Calories per gram
  - Protein per calorie
  - Protein per gram
  - Fiber per calorie
  - Sugar per gram (lowest/highest)
  - Sodium per calorie (lowest/highest)
  - Nutrient density scores (composite)
- **Healthy recommendations from likes**: Given a list of liked foods, suggest alternatives that maximize healthfulness under constraints (e.g., higher protein density, lower sugar/sodium, adequate fiber), while keeping similar categories.
- **Dietary filters**: Support goals and constraints (e.g., high-protein, low-carb, low-sodium, vegetarian/vegan, allergen exclusions).
- **Targets-based ranking**: Rank foods against user macro/micro targets (e.g., 30g protein, <10g sugars per serving).
- **Visualization & dashboards**: Small notebook widgets/plots to explore distributions and top-k foods by metric.
- **Meal composition hints**: Suggest complement foods to reach target macros with minimal sugar/sodium.

## License

Educational project for Big Data Analytics course.
