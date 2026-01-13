
## scripts/nutritional_correlation_analysis.ipynb

This notebook analyzes correlations between nutrients using PySpark and pandas, with a strict column mapping. Each cell has the following role:

### Cell 1: Introduction
- Explains the notebook's purpose: to compute and visualize correlations between nutrients using PySpark, with a strict schema.

### Cell 2: Imports and Spark Initialization
- Imports required libraries: PySpark, pandas, seaborn, matplotlib.
- Creates the Spark session and prints the Spark version.

### Cell 3: Configuration and Schema Mapping
- Defines the input and fallback data paths.
- Sets up a strict mapping from source columns to standardized names (e.g., 'protein' <- 'protein').
- Lists the nutrient columns to be analyzed.

### Cell 4: Data Loading and Schema Application
- The `read_profiles` function loads data from the Parquet folder or fallback file.
- The `apply_strict_schema` function selects and renames columns according to the mapping.
- Data is loaded, mapped, and the first 5 rows are displayed. The total row count is printed.

### Cell 5: Optional Filtering
- Allows filtering by food category or text (commented out, example: only 'branded_food').

### Cell 6: Preparation for Correlation
- Selects only the nutrient columns.
- Drops rows with too many missing values (requires at least 3 valid nutrients).
- Converts the result to a pandas DataFrame for Pearson correlation matrix calculation.
- Computes and displays the correlation matrix between nutrients.

### Cell 7: Heatmap Visualization
- Uses seaborn to visualize the correlation matrix as a colored heatmap.
- Allows quick identification of strong relationships between nutrients.

### Cell 8: Extract Strong Correlations
- Iterates through the matrix and extracts nutrient pairs with absolute correlation > 0.5 (positive or negative).
- Sorts and displays these pairs with their correlation coefficient values.

### Cell 9: Interpretation
- Explains how to interpret strong correlations: nutrients that appear together, inverse effects, usefulness for research or product development.

**Notes:**
- The "score" here is the Pearson correlation coefficient between each pair of nutrients, not a health or preference score.
- The Pearson correlation coefficient (r) measures the linear relationship between two variables, ranging from -1 (perfect negative correlation) to +1 (perfect positive correlation). A value close to 0 means no linear correlation. In this context, it shows how strongly two nutrients tend to increase or decrease together across foods.
- The notebook can be extended with additional filters or other correlation/statistical methods.

## scripts/nutritional_outlier_analysis.ipynb

This notebook detects foods with extreme (outlier) values for key nutrients using PySpark, and provides recommendations for special dietary needs. Each cell has the following role:

### Cell 1: Introduction
- Describes the notebook's purpose: to detect foods with extreme nutrient values and generate dietary recommendations.

### Cell 2: Imports and Spark Initialization
- Imports required libraries: PySpark, pandas, seaborn, matplotlib, os.
- Creates the Spark session and prints the Spark version.

### Cell 3: Configuration and Schema Mapping
- Sets up input/output paths and output directory.
- Defines a strict mapping from source columns to standardized names (e.g., 'protein' <- 'protein').
- Lists the nutrient columns to be analyzed.

### Cell 4: Data Loading and Schema Application
- Loads the data from Parquet, applies the strict schema, selects relevant columns, and ensures all nutrients are cast to numeric type.
- Displays the first 5 rows of the processed data.

### Cell 5: Outlier Detection (IQR Method)
- For each nutrient, calculates the first (Q1) and third (Q3) quartiles using approxQuantile.
- Computes the interquartile range (IQR = Q3 - Q1).
- Defines outlier thresholds:
    - Lower bound: Q1 - 1.5 × IQR (values below are considered 'low' outliers)
    - Upper bound: Q3 + 1.5 × IQR (values above are considered 'high' outliers)
- Identifies and stores foods that are high or low outliers for each nutrient.
- Prints the bounds and the number of high/low outliers for each nutrient.

### Cell 6: Outlier Visualization
- Defines a function to plot bar charts for the top high or low outliers for a selected nutrient.
- Example plots are generated for several nutrients.

### Cell 7: Dietary Recommendations
- Defines functions to recommend foods for nutrient deficiency (using high outliers) or for restriction (using low outliers).
- Displays the top foods for each case.

### Cell 8: Save Outlier and Recommendation Results
- Saves all detected high and low outliers for each nutrient as CSV files in the output directory.
- Also saves specific recommendations for iron deficiency and sodium restriction as CSV files.
- Prints confirmation for each file saved.

**Formulas and Methods Used:**
- **Quartiles (Q1, Q3):** Computed using Spark's approxQuantile function for each nutrient column.
- **Interquartile Range (IQR):**
  $$ IQR = Q3 - Q1 $$
- **Outlier Thresholds:**
  - Lower bound: $$ Q1 - 1.5 \times IQR $$
  - Upper bound: $$ Q3 + 1.5 \times IQR $$
- **Outlier Detection:**
  - Foods with values below the lower bound are 'low' outliers.
  - Foods with values above the upper bound are 'high' outliers.
- **Visualization:**
  - Bar charts for top high/low outliers using matplotlib.
- **Recommendation Logic:**
  - For deficiency: recommend foods from high outliers.
  - For restriction: recommend foods from low outliers.

This approach allows for robust detection of foods with extreme nutrient values and supports targeted dietary recommendations.

## scripts/nutrient_similarity_search.ipynb

This notebook finds foods with similar nutritional profiles using PySpark and pandas. Each cell has the following role:

### Cell 1: Imports and Spark Session
- Imports required libraries: PySpark, pandas, numpy, etc.
- Creates the Spark session and prints the Spark version.

### Cell 2: Configuration
- Sets input/output paths and fallback file.
- Allows you to select the reference product by name or ID.
- Configures the number of results (top_k), category restriction, normalization (per kcal), scaling (zscore), and chart display.
- Allows text-based filters (exclude allergens, dislikes).
- Defines a strict schema for column mapping.
- **feature_config**: lets you choose which nutrients to use, their weights, and constraints (see below for details).

### Cell 3: Data Loading
- Loads the dataset from Parquet and prints the schema.

### Cell 4: Column Detection
- Detects and maps the relevant columns for each nutrient and metadata (id, name, category, etc.), using the strict schema or auto-detection.
- Updates feature_config with the actual column names found in the dataset.

### Cell 5: Feature Engineering
- Computes per-kcal (or per-100g) values for all selected nutrients.
- Builds a feature matrix (numpy array) for all foods, with missing values filled as 0.
- Applies z-score scaling if selected.
- Applies the weights from feature_config to each nutrient.

### Cell 6: Reference Item Selection
- Selects the reference product (by name substring or ID) and extracts its feature vector.


### Cell 7: Similarity Calculation
- Calculates cosine similarity between the nutrient vector of the reference product and all other products:
  $$ similarity(A, B) = \frac{A \cdot B}{\|A\| \cdot \|B\|} $$
- Excludes the reference product from the results.

### Cell 8: Filtering and Constraints
- Applies additional filters:
  - **same_category_only**: keeps only products in the same category as the reference.
  - **exclude_allergens/dislikes**: removes products containing certain allergens or unwanted ingredients.
  - **feature_config constraints**: for each nutrient you can set:
    - **'none'**: no restriction.
    - **'less'**: keeps only products with value less than or equal to the reference.
    - **'more'**: keeps only products with value greater than or equal to the reference.

### Cell 9: Result Formatting
- Sorts results by similarity and keeps the top_k most similar products.
- Calculates and displays percent differences from the reference for each nutrient used.

### Cell 10: Visualization
- Displays results in a styled table and, optionally, as a chart.

**How Similarity is Calculated:**
- Each food is represented as a vector of nutrients (with weights and optional z-score normalization).
- Similarity is the cosine of the angle between the reference vector and the others.
- The weights in feature_config control how much each nutrient influences the similarity (higher weight = more influence).

**Constraints in feature_config:**
- **'none'**: no restriction for that nutrient.
- **'less'**: keeps only products with value <= reference (e.g., less sodium).
- **'more'**: keeps only products with value >= reference (e.g., more protein).

**Summary:**
- The script allows advanced configuration of nutritional similarity criteria, weights, restrictions, and filters, so you can quickly find products with a nutritional profile close to any reference food, according to your rules.

## scripts/nutrient_density_explorer.ipynb

This notebook ranks foods by nutrient density (e.g., protein, fiber, vitamins per kcal or per 100 kcal) using PySpark and pandas, with flexible configuration and strict schema mapping. It supports advanced metric selection and outputs top foods for any nutrient, with optional charting and batch export.

### Cell 1: Imports and Spark Initialization
- Imports required libraries: PySpark, pandas, matplotlib.
- Creates the Spark session and prints the Spark version.

### Cell 2: Configuration and Schema Mapping
- Sets input/output paths and fallback file (for legacy compatibility).
- Configures output directory, top_k, sorting order, unit (per_kcal or per_100kcal), and output/chart options.
- Defines a strict mapping from source columns to standardized names (e.g., 'protein' <- 'protein').
- Lists all available metrics (nutrients) and sets which are enabled by default.

### Cell 3: Column Detection and Data Loading
- Defines helper functions to detect and map columns from the dataset, using strict schema or fuzzy matching.
- Loads the dataset from Parquet (using input_path or fallback_file).
- Identifies all relevant columns for id, name, category, kcal, and each nutrient.
- Builds a dictionary mapping each metric to its column name.
- Filters metrics to only those present in the data.
- Selects the default metric for display.

### Cell 4: Density Calculation
- Filters out foods with kcal <= 0.
- For each metric, computes three columns:
    - Per kcal (e.g., protein_per_kcal = protein / kcal)
    - Per 100 kcal (for readability)
    - Per 100g/raw (original value)
- Appends all computed density columns to the DataFrame.

### Cell 5: Filtering (No Filters Applied)
- No category, allergen, or dislike filters are applied (all foods are included).
- The DataFrame is ready for ranking.

### Cell 6: Helpers for Top-K and Display
- Defines helper functions to select columns, compute top-K foods for a metric, and display results as styled tables and bar charts.
- Uses pandas for table formatting and matplotlib for visualization.

### Cell 7: Compute and Display for Selected Metric
- For the selected metric and unit (per_kcal or per_100kcal), computes the top-K foods.
- Displays results as a table and bar chart.
- Optionally saves outputs as CSV/Parquet if enabled.

### Cell 8: Batch Save for All Enabled Metrics
- If batch export is enabled, computes and saves top-K tables for all enabled metrics in the output directory.

**How It Works:**
- The notebook loads a precomputed nutritional profile dataset (Parquet format).
- It maps all relevant columns using a strict schema, with fallback to fuzzy matching if needed.
- For each nutrient, it computes density per kcal and per 100 kcal, enabling fair comparison across foods.
- You can select any metric (nutrient) to rank foods by, and see the top-K results, with optional visualization.
- No foods are excluded by category, allergen, or dislike (all are included in the analysis).
- Batch export allows saving results for all metrics at once.

**Formulas Used:**
- Per-kcal density:  
  $\text{density}_{\text{per kcal}} = \frac{\text{nutrient}}{\text{kcal}}$
- Per-100kcal:  
  $\text{density}_{\text{per 100 kcal}} = \text{density}_{\text{per kcal}} \times 100$

**Summary:**
- This script provides a flexible, schema-driven way to rank foods by any nutrient density, with full control over metrics, units, and outputs. It is suitable for nutritional research, product development, or dietary planning.

## scripts/ingredient_frequency_analysis.ipynb

This notebook analyzes the frequency of ingredients across all foods in the dataset using PySpark and pandas, with strict schema enforcement and advanced normalization.

**Main features:**
- Loads data with a strict schema (fdc_id, description, all_ingredients).
- Normalizes ingredient names: lowercase, removes spaces, special characters, and '&'.
- Counts each ingredient only once per food (no duplicates).
- Calculates the frequency of each ingredient and collects example foods where it appears.
- Visualizes the top 10 most common and top 10 rarest ingredients, with examples.
- Saves the complete ingredient frequency list to `output/ingredient_frequency/ingredient_frequency.csv`.

**How to use:**
1. Run the notebook to generate statistics and visualizations.
2. Check the tables in the notebook for top ingredients and examples.
3. Find the CSV file with all ingredients and their frequency in the output folder for further analysis.

**Summary:**
This script provides a robust method for analyzing ingredient frequency, identifying the most and least common ingredients, and exporting results for research or reporting.

## Healthiness Scoring Script

The healthiness scoring script calculates a score for each food item by combining ingredient and nutrient information to assess how healthy a product is.

### How the Score is Calculated
- **Initial Filtering:** Only foods with non-null and non-zero values for the main nutrients (energy, protein, fiber, sugars, fat) are kept.
- **Ingredient Score:** Each ingredient receives +1 if considered healthy (e.g., vegetables, nuts, whole grains) and -1 if considered unhealthy (e.g., sugar, hydrogenated oils, artificial additives).
- **Nutrient Score:** Points are awarded for beneficial nutrients (protein, fiber, vitamins, minerals) and penalties are applied for less healthy nutrients (sugars, saturated fat, sodium, cholesterol).
- **Nutri-Score Integration:** An external Nutri-Score is included, which considers both positive and negative nutrients according to European standards.
- **Final Score:** The total score is the sum of the ingredient score, nutrient score, and the Nutri-Score adjustment.

### Score Interpretation
- A high score indicates a healthy food, rich in beneficial nutrients and natural ingredients.
- A negative score indicates an unhealthy food, high in sugar, unhealthy fats, or artificial additives.

### Export and Visualization
- The script exports scores to a CSV file in the `output/HealthinessScores` folder.
- It displays the top 10 healthiest and least healthy foods, with details about their score and composition.

### Customization
- Weights and ingredient lists can be adjusted in the script to reflect your preferences or desired standards.
- Graphical visualizations of score distributions can be added for deeper analysis.

For more details, see the notebook `scripts/healthiness_scoring.ipynb`.

## Recipe Ideas Script

This script suggests recipe ideas based on the ingredients you have, your dislikes, calorie preferences, and nutrition profile. It is robust, flexible, and uses both ingredient and nutrient data for ranking.

### How it works
- Loads food and ingredient data, normalizes ingredient names, and builds a set for each food.
- You provide:
  - `ingredients`: List of ingredients you have at home.
  - `dislikes`: List of ingredients to exclude.
  - `kcal_min`/`kcal_max`: Minimum/maximum allowed calories per food.
  - `profile`: Nutrition profile to use for scoring. Only one can be active at a time: 'none', 'healthy', 'high_protein', 'high_fiber'.
- The script filters foods to only those that use at least 3 of your ingredients (or all, if you provide fewer than 3).
- Foods containing any disliked ingredient are excluded.
- Foods are further filtered by calorie range if specified.

### Scoring and Profiles
- Each food is scored based on:
  - Number of matching ingredients (higher is better)
  - Nutrient values, weighted according to the selected profile:
    - **none**: No nutrient weights, only ingredient match matters.
    - **healthy**: Favors high fiber/protein, penalizes sugars, fat, and calories.
    - **high_protein**: Strongly favors protein content.
    - **high_fiber**: Strongly favors fiber content.
- Only one profile can be active at a time. The weights for each profile are defined in the script and can be customized.

### Output
- The script displays the top N recipe ideas (foods) that best match your configuration, showing their ingredients, energy, fiber, protein, sugars, fat, and score.

### Customization
- You can adjust the ingredient list, dislikes, calorie limits, and profile at the top of the notebook.
- You can also modify the scoring weights in the `PROFILE_WEIGHTS` dictionary to better fit your needs.

For more details, see the notebook `scripts/recipe_ideas.ipynb`.

## Model-based Scripts

This section contains scripts that use machine learning or NLP models for advanced recommendations or similarity search.

### scripts/semantic_similarity_nlp.ipynb

This notebook recommends foods/products that are semantically similar to a given query (e.g., a product name and its ingredients), using a modern NLP model.

**Model Used:**
- [Sentence Transformers](https://www.sbert.net/) – specifically, the `all-MiniLM-L6-v2` model, a fast and efficient transformer-based model for generating dense semantic embeddings of text.

**How the Model Works:**
- The model converts each product's name and ingredient list into a single text string (e.g., "Product Name. Ingredients: ...").
- It generates a vector embedding for each product using the transformer model.
- For a user query (e.g., a product description and ingredients), the model generates an embedding and computes cosine similarity with all product embeddings.
- The top-N most similar products are recommended, based on semantic meaning, not just keyword overlap.

**Cell-by-cell breakdown:**

1. **Imports**
  - Loads pandas, numpy, and Sentence Transformers libraries.

2. **Load Data**
  - Loads the ingredients dataset (Parquet format) using pandas.
  - Keeps only the product ID, description, and ingredient list.

3. **Create Text for Embedding**
  - Defines a function to join the ingredient list into a string.
  - Creates a new column combining the product description and ingredients into a single text string for each product.

4. **Load Embedding Model**
  - Loads the `all-MiniLM-L6-v2` Sentence Transformer model.

5. **Compute Embeddings**
  - Computes the embedding vector for each product's combined text.

6. **Recommendation Function**
  - Defines a function that takes a query (product description + ingredients), encodes it, computes cosine similarity to all products, and returns the top-N most similar products.

7. **Usage Example**
  - Shows how to use the function to recommend products similar to a given query.
  - Displays the results with similarity scores.

**Summary:**
- This script enables semantic product recommendations using state-of-the-art NLP embeddings, making it possible to find similar foods even if they don't share exact keywords or ingredient names.