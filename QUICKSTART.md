# Quick Start Guide (Food Nutritional Analysis)

## Prerequisites

1. **Java 8 or 11** (required for Spark)

   ```bash
   java -version
   ```

2. **Python 3.10+**

   ```bash
   python --version
   ```

3. **Apache Spark 3.5+**
   - Download from: https://spark.apache.org/downloads.html
   - Set environment variables:
     ```bash
     export SPARK_HOME=/path/to/spark
     export PATH=$SPARK_HOME/bin:$PATH
     ```

## Installation

1. **Clone/Download the project**

2. **Install Python dependencies** (uv recommended):

   ```bash
   uv sync
   ```

3. **Verify Spark installation**:
   ```bash
   pyspark --version
   ```

## Data Download (Required)

Download the full USDA FoodData Central (FDC) dataset (CSV) and extract into [dataset/](dataset/):

- https://fdc.nal.usda.gov/download-datasets
- Ensure files like `food.csv`, `nutrient.csv`, `food_nutrient.csv`, `food_portion.csv`, `measure_unit.csv` exist.

## Convert CSV to Parquet

Use the provided converter to speed up processing:

```bash
uv run python convert_csvs_to_parquet.py --input-dir dataset --output-dir converted-dataset
```

## (Optional) Sample a Subset

Create a smaller, related subset in Parquet:

```bash
uv run python sample_datasets.py
```

## Run Spark Notebook

Generate comprehensive nutritional profiles:

```bash
jupyter lab
```

Open and run [generate_nutritional_values.ipynb](generate_nutritional_values.ipynb).

## Expected Output

- Parquet files under [output/nutritional_profiles_parquet/](output/nutritional_profiles_parquet/)
- Console counts for loaded datasets and aggregated results

## Troubleshooting

- Parquet operations require `pyarrow`.
- Verify Parquet inputs exist in [converted-dataset/](converted-dataset/) if Spark reads fail.
- Increase Spark memory via `spark.driver.memory` and `spark.executor.memory` in the notebook.

## Outputs

- Final profiles: [output/nutritional_profiles_parquet/](output/nutritional_profiles_parquet/)
