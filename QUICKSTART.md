# Quick Start Guide

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

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using uv:
   ```bash
   uv sync
   ```

3. **Verify Spark installation**:
   ```bash
   pyspark --version
   ```

## Running Stage 1 (Local)

### Option 1: Jupyter Notebook (Recommended)

1. Start JupyterLab:
   ```bash
   jupyter lab
   ```

2. Open `notebooks/restaurant_recommendation_system.ipynb`

3. Run all cells (Cell → Run All)

### Option 2: Python Script

```bash
python scripts/stage1_local.py
```

## Expected Output

After running the notebook, you should see:

1. **Data Loading**: Counts of users, restaurants, recipes
2. **Model Training**: Progress of ALS training
3. **Hyperparameter Optimization**: Testing different parameter combinations
4. **Final Metrics**:
   - RMSE: Should be between 0.88 - 0.92
   - MAE: Mean Absolute Error
   - Best parameters used
5. **Recommendations**: Top 5 restaurants for sample users

## Troubleshooting

### Issue: "Java not found"
**Solution**: Install Java 8 or 11 and set JAVA_HOME:
```bash
export JAVA_HOME=/path/to/java
```

### Issue: "Spark not found"
**Solution**: Install Spark and set SPARK_HOME:
```bash
export SPARK_HOME=/path/to/spark
export PATH=$SPARK_HOME/bin:$PATH
```

### Issue: Memory errors
**Solution**: Reduce data size in notebook or increase Spark memory:
- Edit notebook cell with Spark session configuration
- Increase `spark.executor.memory` and `spark.driver.memory`

### Issue: Slow execution
**Solution**: 
- Reduce data samples (limit recipes/users)
- Increase Spark partitions
- Use smaller hyperparameter grid

## Next Steps

- **Stage 2**: Configure SSH access and run `scripts/stage2_private_cloud.py`
- **Stage 3**: Set up GCP credentials and run `scripts/stage3_gcp_dataproc.sh`

## Data Files

Ensure all CSV files are in the `data/` directory:
- `10_002_users-food_allergy.csv`
- `9558_restaurants.csv`
- `2_231_151_recipes_data.csv`
- `food.csv`
- `nutrient.csv`
- `food_nutrient.csv`
- And other required files

## Model Output

Trained models are saved to:
- `models/als_restaurant_recommendation_model/`

Recommendations are saved to:
- `output/recommendations/`

