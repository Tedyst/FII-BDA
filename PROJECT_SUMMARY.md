# Project Summary: Restaurant Recommendation System

## Overview

This project implements a comprehensive restaurant recommendation system using Apache Spark, PySpark, and SparkML with ALS (Alternating Least Squares) collaborative filtering. The system provides personalized restaurant recommendations based on user preferences, food allergies, dietary restrictions, and nutrient information.

## Key Features

### 1. Collaborative Filtering with ALS
- Implements Alternating Least Squares algorithm for matrix factorization
- Optimizes hyperparameters to achieve RMSE between 0.88-0.92
- Handles cold start problem with "drop" strategy
- Generates top 5 restaurant recommendations per user

### 2. User Profile Processing
- Processes user allergies from anonymized data
- Extracts dietary restrictions:
  - Diabetes
  - Celiac disease (gluten-free)
  - Lactose intolerance
  - Obesity considerations
- Creates compatibility scores based on user profiles

### 3. Data Integration
- **Users**: 10,002 users with allergy and medical condition data
- **Restaurants**: 9,558 restaurants with ratings and cuisine information
- **Recipes**: 2.2M+ recipes with ingredient lists
- **Nutrients**: Food composition and nutrient data
- **Mappings**: Restaurant-recipe relationships based on cuisines

### 4. Multi-Stage Deployment

#### Stage 1: Local Execution
- Simulates cluster with master + 2 workers
- Uses local data files
- Ideal for development and testing

#### Stage 2: Private Cloud
- SSH-based round-robin data loading
- Handles limited resources by distributing data across workers
- Loads data from remote hosts via SSH

#### Stage 3: GCP Dataproc
- Cloud-based execution on Google Cloud Platform
- Uses Google Cloud Storage for data
- Scalable cluster deployment

## Technical Architecture

### Data Flow
1. **Extract**: Load CSV files (users, restaurants, recipes, nutrients)
2. **Transform**: 
   - Process user allergies and dietary restrictions
   - Map recipes to restaurants
   - Filter restaurants based on user compatibility
   - Generate user-restaurant rating matrix
3. **Load**: 
   - Split into training (80%) and test (20%) sets
   - Train ALS model
   - Generate recommendations

### Model Training
- **Algorithm**: ALS (Alternating Least Squares)
- **Hyperparameters**:
  - Rank: 5-20 (latent factors)
  - Regularization: 0.01-1.0
  - Max Iterations: 5-15
- **Optimization**: Grid search to achieve target RMSE
- **Evaluation**: RMSE and MAE metrics

### Recommendation Generation
- Filters restaurants based on:
  - User allergies
  - Dietary restrictions
  - Ingredient compatibility
- Generates predicted ratings using trained model
- Returns top 5 restaurants per user

## File Structure

```
FII-BDA/
├── data/                          # CSV data files
├── src/                           # Source code
│   ├── data_processor.py          # ETL operations
│   └── recommendation_engine.py   # ALS engine
├── notebooks/                     # Jupyter notebook
│   └── restaurant_recommendation_system.ipynb
├── config/                        # Configuration files
│   ├── stage1_local.json
│   ├── stage2_private_cloud.json
│   └── stage3_gcp_dataproc.json
├── scripts/                       # Deployment scripts
│   ├── stage1_local.py
│   ├── stage2_private_cloud.py
│   ├── stage3_gcp_dataproc.sh
│   ├── main_dataproc.py
│   ├── verify_setup.py
│   └── run_notebook.py
└── docs/                          # Documentation
    ├── README.md
    ├── QUICKSTART.md
    └── PROJECT_SUMMARY.md
```

## Performance Targets

- **RMSE**: 0.88 - 0.92 (achieved through hyperparameter optimization)
- **Training/Test Split**: 80/20
- **Recommendations**: Top 5 restaurants per user
- **Cold Start**: Handled via "drop" strategy

## Usage

### Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Verify setup: `python scripts/verify_setup.py`
3. Run notebook: `jupyter lab notebooks/restaurant_recommendation_system.ipynb`

### Stage 1 (Local)
```bash
python scripts/stage1_local.py
```

### Stage 2 (Private Cloud)
```bash
# Configure SSH in config/stage2_private_cloud.json
python scripts/stage2_private_cloud.py
```

### Stage 3 (GCP Dataproc)
```bash
# Configure GCP in config/stage3_gcp_dataproc.json
./scripts/stage3_gcp_dataproc.sh
```

## Technologies Used

- **Apache Spark 3.5+**: Distributed computing framework
- **PySpark**: Python API for Spark
- **SparkML**: Machine learning library
- **ALS**: Alternating Least Squares algorithm
- **JupyterLab**: Interactive development environment
- **Python 3.10+**: Programming language

## Data Sources

1. **User Data**: Anonymized user profiles with allergies and medical conditions
2. **Restaurant Data**: Global restaurant database with ratings and cuisines
3. **Recipe Data**: Large-scale recipe database with ingredients
4. **Nutrient Data**: Food composition and nutrient information

## Future Enhancements

- Real-time recommendation API
- User feedback integration
- Advanced filtering using nutrient data
- A/B testing framework
- Model versioning and monitoring
- Integration with restaurant menu APIs

## License

Educational project for Big Data Analytics course.

