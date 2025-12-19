# Restaurant Recommendation System

A comprehensive restaurant recommendation system using Apache Spark, PySpark, and SparkML with ALS (Alternating Least Squares) collaborative filtering algorithm. The system recommends restaurants based on user preferences, food allergies, dietary restrictions, and nutrient information.

## Features

- **Collaborative Filtering**: Uses ALS algorithm for personalized restaurant recommendations
- **Allergy & Dietary Restrictions**: Filters restaurants based on:
  - Food allergies
  - Diabetes
  - Celiac disease (gluten-free)
  - Lactose intolerance
  - Obesity considerations
- **Multi-Stage Deployment**: Supports three deployment scenarios:
  - **Stage 1**: Local execution with simulated cluster
  - **Stage 2**: Private cloud with SSH-based round-robin data loading
  - **Stage 3**: GCP Dataproc deployment
- **Model Optimization**: Hyperparameter tuning to achieve RMSE between 0.88-0.92
- **Cold Start Handling**: Uses "drop" strategy for new users/restaurants

## Project Structure

```
FII-BDA/
├── data/                          # CSV data files
│   ├── 10_002_users-food_allergy.csv
│   ├── 9558_restaurants.csv
│   ├── 2_231_151_recipes_data.csv
│   ├── food.csv
│   ├── nutrient.csv
│   ├── food_nutrient.csv
│   └── ...
├── src/                           # Source code modules
│   ├── __init__.py
│   ├── data_processor.py          # ETL operations
│   └── recommendation_engine.py   # ALS recommendation engine
├── notebooks/                     # Jupyter notebooks
│   └── restaurant_recommendation_system.ipynb
├── config/                        # Configuration files
│   ├── stage1_local.json
│   ├── stage2_private_cloud.json
│   └── stage3_gcp_dataproc.json
├── scripts/                       # Deployment scripts
│   ├── stage1_local.py
│   ├── stage2_private_cloud.py
│   ├── stage3_gcp_dataproc.sh
│   └── main_dataproc.py
├── models/                        # Saved models (generated)
├── output/                        # Output files (generated)
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.10+
- Apache Spark 3.5+
- Java 8 or 11 (required for Spark)
- JupyterLab (for notebook execution)

## Installation

1. **Install dependencies**:
```bash
pip install -e .
```

Or using uv:
```bash
uv sync
```

2. **Install Apache Spark**:
   - Download Spark from https://spark.apache.org/downloads.html
   - Extract and set `SPARK_HOME` environment variable
   - Add Spark binaries to PATH

3. **For JupyterLab**:
```bash
pip install jupyterlab
jupyter lab
```

## Usage

### Stage 1: Local Execution

Run the Jupyter notebook for interactive development:

```bash
jupyter lab notebooks/restaurant_recommendation_system.ipynb
```

Or run the Python script:

```bash
python scripts/stage1_local.py
```

The notebook includes:
- Data loading and ETL
- User preference and allergy processing
- Restaurant-recipe mapping
- Rating matrix generation
- Train/test split (80/20)
- ALS model training and optimization
- Hyperparameter tuning to achieve target RMSE
- Top 5 restaurant recommendations generation

### Stage 2: Private Cloud Deployment

For private cloud with limited resources and SSH-based data loading:

1. **Configure SSH access**:
   - Update `config/stage2_private_cloud.json` with your SSH credentials
   - Ensure SSH keys are set up for passwordless access

2. **Run the script**:
```bash
python scripts/stage2_private_cloud.py
```

The script uses round-robin method to load data from multiple remote hosts via SSH, distributing the load across available resources.

### Stage 3: GCP Dataproc Deployment

1. **Set up GCP credentials**:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. **Update configuration**:
   - Edit `config/stage3_gcp_dataproc.json` with your GCP project details
   - Set GCS bucket name

3. **Deploy**:
```bash
chmod +x scripts/stage3_gcp_dataproc.sh
./scripts/stage3_gcp_dataproc.sh
```

The script will:
- Upload data to Google Cloud Storage
- Create a Dataproc cluster
- Submit the Spark job
- Monitor job execution

## Model Configuration

The system uses ALS (Alternating Least Squares) with the following default parameters:

- **Rank**: 10 (latent factors)
- **Regularization Parameter**: 0.1
- **Max Iterations**: 10
- **Cold Start Strategy**: "drop"
- **Target RMSE**: 0.88 - 0.92

Hyperparameter optimization automatically searches for optimal parameters to achieve the target RMSE range.

## Data Processing

### User Data
- Processes user allergies from `10_002_users-food_allergy.csv`
- Extracts dietary restrictions (diabetes, celiac, lactose intolerance, obesity)
- Creates user profiles for filtering

### Restaurant Data
- Loads restaurant information from `9558_restaurants.csv`
- Includes ratings, cuisines, and location data

### Recipe Data
- Processes recipes from `2_231_151_recipes_data.csv`
- Extracts ingredients for allergy/dietary filtering
- Maps recipes to restaurants based on cuisine types

### Nutrient Data
- Loads food, nutrient, and food_nutrient data
- Used for advanced filtering (e.g., calorie content for obesity)

## Output

The system generates:
- **Trained Model**: Saved to `models/als_restaurant_recommendation_model/`
- **Recommendations**: Top 5 restaurants per user
- **Metrics**: RMSE, MAE, and other evaluation metrics

## Performance Targets

- **RMSE**: 0.88 - 0.92 (target achieved through hyperparameter optimization)
- **Training/Test Split**: 80/20
- **Recommendations**: Top 5 restaurants per user
- **Cold Start**: Handled via "drop" strategy

## Troubleshooting

### Common Issues

1. **Java not found**: Ensure Java 8 or 11 is installed and JAVA_HOME is set
2. **Memory errors**: Adjust Spark memory settings in configuration files
3. **SSH connection issues**: Verify SSH keys and host accessibility for Stage 2
4. **GCP authentication**: Ensure gcloud is authenticated and project is set

### Spark Configuration

Adjust memory and partition settings in configuration files:
- `spark.executor.memory`: Memory per executor
- `spark.driver.memory`: Driver memory
- `spark.sql.shuffle.partitions`: Number of partitions for shuffles

## License

This project is part of the Big Data Analytics course at FII.

## Authors

- Tedy Stoica, MISS2
- Dan Frunza, MISS2
- Iulian Gherghevici, MISS2


