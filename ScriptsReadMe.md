# Nutritional Correlation Analysis — [nutritional_correlation_analysis.ipynb](nutritional_correlation_analysis.ipynb)

- **What it does:** Computes and visualizes correlations between nutrients in foods using PySpark, with strict schema mapping. Useful for research, product development, or exploring hidden associations in food composition data.

- **Steps (in order):**
  - **Imports and Spark session:** Uses PySpark for data processing, pandas for correlation, seaborn/matplotlib for visualization.
  - **Configuration:** 
    - Input/output paths for Parquet data.
    - `schema_columns`: strict mapping for all relevant columns (ID, name, category, energy, macros, lipids, minerals, vitamins).
    - `nutrient_cols`: list of nutrients to include in the correlation matrix.
  - **Data loading and schema mapping:** Reads Parquet, applies strict schema mapping (missing columns are filled with nulls).
  - **Filtering:** Optionally restricts to a food category or applies text filters (template code provided).
  - **Preparation:** Selects only nutrient columns, drops rows with too many missing values (requires at least 3 non-null nutrients).
  - **Correlation computation:** Collects data to pandas and computes the Pearson correlation matrix for the selected nutrients.
  - **Visualization:** Plots the correlation matrix as a heatmap using seaborn.
  - **Strong correlation extraction:** Extracts and displays all nutrient pairs with strong correlations (|r| > 0.5, off-diagonal).
  - **Interpretation:** Provides guidance on interpreting positive/negative correlations and their practical implications.

- **Key configuration:**
  - `schema_columns`: strict mapping for all relevant columns.
  - `nutrient_cols`: list of nutrients to include in the analysis.
  - `min_valid`: minimum number of non-null nutrients required per row (default: 3).

- **Outputs:**
  - Printed correlation matrix.
  - Heatmap visualization.
  - List of nutrient pairs with strong correlations (|r| > 0.5).

- **Example output (strong correlations):**

```
Nutrient pairs with strong correlations (|r| > 0.5):
protein - sodium: r = 0.68
carb - sugar: r = 0.82
fat - saturated_fat: r = 0.77
fiber - carb: r = 0.54
calcium - vitamin_b12: r = 0.51
```
Values are illustrative; actual results depend on your dataset.

- **Notes:**
  - The notebook is modular and can be extended with additional filters or nutrients.
  - All logic is performed in PySpark except for the final correlation and plotting (done in pandas/seaborn).
  - Structure and approach are similar to the nutrient similarity search notebook for consistency.
# Detailed Notebook Overview

This document explains, one by one, what each notebook does, the exact steps implemented inside, and the formulas used locally in that notebook. No prerequisites are included here. All formulas are written in plain text (no LaTeX) to avoid rendering issues on GitHub.


## Top 10 Protein per Kcal — [generate_top10_prot_per_kcal.ipynb](generate_top10_prot_per_kcal.ipynb)

- What it does: Finds the 10 foods with the highest protein density (grams of protein per kcal).
- Steps (in order):
  - Initialize Spark and read Parquet from [output/nutritional_profiles](output/nutritional_profiles). If the folder is missing, fall back to a specific part file in the same area.
  - Detect required columns via exact and then contains matching (case-insensitive):
    - ID: `fdc_id`, `id`.
    - Name: `description`, `food_name`, `name`.
    - Calories (kcal): `energy_kcal`, `energy`, `kcal`, `calories`, or nutrient code `1008`.
    - Protein (g): `protein_g`, `protein`, or nutrient code `1003`.
  - Filter rows with `kcal > 0`.
  - Compute density: `protein_per_kcal = protein_g / kcal`.
  - Sort descending by `protein_per_kcal` and take Top 10.
  - Write results as CSV and Parquet to [output/Top10_bestfoods_prots_per_kcal](output/Top10_bestfoods_prots_per_kcal).
- Saved fields: ID, Name, `kcal`, `protein_g`, `protein_per_kcal`.
- Notes: If scores tie, ordering is determined by the DataFrame’s implicit secondary sort (ID/Name).

- Example output (table):

| fdc_id | name                                   | kcal | protein_g | protein_per_kcal |
|--------|----------------------------------------|------|-----------|------------------|
| 214123 | Chicken breast (roasted, skinless)     | 165  | 31.0      | 0.188            |
| 735221 | Tuna (canned in water, drained)        | 116  | 26.0      | 0.224            |
Values are illustrative; the full list contains 10 rows.

## Configurable Recommendations — [generate_recommendations.ipynb](generate_recommendations.ipynb)

- What it does: produces a Top‑K based on filters (allergens/keywords, calorie range) and either a single sort field or a composite score.
- Steps (in order):
  - Read Parquet and detect columns for ID, Name, `kcal`, `protein_g`, optional `fiber_g` (code `1079`), `carb_g` (`1005`), `sugar_g` (`2000`), `fat_g` (`1004`), and a text column (usually `ingredients` or `description`).
  - Filtering:
    - Exclusions (allergens/words): drop rows where the text contains any excluded term.
    - Inclusions: flag rows where the text contains preferred terms; if `must_include=True`, keep only those.
    - Calorie range: keep `kcal` in `[calorie_min, calorie_max]`.
  - Per‑kcal densities for each available nutrient: `density = nutrient_g / kcal`.
  - Ranking (two paths):
    - Single‑field sort: set `sort_by` (e.g., `protein_per_kcal`, `fiber_per_kcal`, `sugar_per_kcal`, `fat_per_kcal`) and direction (desc/asc).
    - Composite score (when `sort_by` is empty):
      `Score = sum(w_i * density_i) + w_include * has_included`.
      Here `w_i` are your weights for protein/fiber/carb/sugar/fat, and `has_included` is `1` if the row has included terms, else `0`.
      Example: if `protein_per_kcal=0.12`, `fiber_per_kcal=0.03`, `fat_per_kcal=0.01`, weights `(w_p,w_f,w_fat)=(1.0, 0.5, 0.2)` and bonus `w_include=0.1` (with included terms), then `Score = 1.0*0.12 + 0.5*0.03 + 0.2*0.01 + 0.1*1 = 0.237`.
  - Notebook output: a styled Pandas table that colors the chosen metric (`sort_by`, or `Score` when using composite scoring) and a chart based on the same metric. The index is hidden with a compatibility‑safe approach across Pandas versions.
  - Write results: CSV + Parquet to [output/Recommendations](output/Recommendations), including base fields + densities and `Score` (if applicable).

- Example output (table) — with `sort_by="protein_per_kcal"`:

| id    | name                                 | kcal | protein_g | protein_per_kcal | fiber_per_kcal | carb_per_kcal | sugar_per_kcal | fat_per_kcal |
|-------|--------------------------------------|------|-----------|------------------|----------------|---------------|----------------|--------------|
| 214123| Chicken breast (roasted, skinless)   | 165  | 31.0      | 0.188            | 0.000          | 0.000         | 0.000          | 0.024        |
| 735221| Tuna (canned in water, drained)      | 116  | 26.0      | 0.224            | 0.000          | 0.000         | 0.000          | 0.009        |

- Example output (table) — with composite `Score`:

| id    | name                          | kcal | protein_g | protein_per_kcal | fiber_per_kcal | carb_per_kcal | sugar_per_kcal | fat_per_kcal | Score |
|-------|--------------------------------|------|-----------|------------------|----------------|---------------|----------------|--------------|-------|
| 498311| Greek yogurt (plain, nonfat)   | 59   | 10.3      | 0.175            | 0.000          | 0.081         | 0.032          | 0.000        | 0.231 |
| 214123| Chicken breast (roasted, skinless) | 165 | 31.0      | 0.188            | 0.000          | 0.000         | 0.000          | 0.024        | 0.227 |
Values are examples; exact columns depend on which densities exist in your dataset.

## Nutrient Density Explorer — [nutrient_density_explorer.ipynb](nutrient_density_explorer.ipynb)

- What it does: ranks foods by nutrient density with a selectable unit (per kcal or per 100 kcal) and a broad set of nutrients. It uses strict, dataset‑specific schema mapping, optional category and text filters (allergens/dislikes), shows a styled table + horizontal bar chart, and can save Top‑K results per metric.

- Key configuration
  - `unit_choice`: `'per_kcal'` or `'per_100kcal'` (default: `'per_100kcal'`).
  - `selected_metric`: the nutrient shown on screen. `metrics_available` lists all candidates; `metric_use` toggles which ones are included in batch saves.
  - `top_k`, `order_desc`: how many rows to show/save and sort direction.
  - `save_outputs`, `show_chart`: write CSV/Parquet and render the chart.
  - `category_filter`, `exclude_allergens`, `dislikes`: equality filter on category and substring exclusion in a text column.
  - `strict_schema` + `schema_columns`: exact mappings for this dataset.

- Columns and strict schema
  - Base: ID → `fdc_id`; Name → `food_description`; Category → `food_type`; Energy → `energy`.
  - Nutrients mapped (when present):
    - Macros: `protein`, `carbs`, `total_fat`, `fiber`, `sugars`.
    - Lipids detail: `saturated_fat`, `monounsaturated_fat`, `polyunsaturated_fat`, `trans_fat`.
    - Sugars detail: `glucose`, `fructose`, `sucrose`, `lactose`.
    - Other: `cholesterol`, `water`, `ash`, `alcohol`, `caffeine`.
    - Minerals: `calcium`, `iron`, `magnesium`, `phosphorus`, `potassium`, `zinc`, `copper`, `manganese`, `selenium`.
    - Vitamins: `vitamin_a`, `vitamin_c`, `vitamin_d`, `vitamin_e`, `vitamin_k`, `thiamin_b1`, `riboflavin_b2`, `niacin_b3`, `vitamin_b6`, `folate`, `vitamin_b12`, `choline`.
    - Pigments: `beta_carotene`, `lycopene`, `lutein_zeaxanthin`.
  - Text column for filters: prefer `ingredients`/`ingredients_text`, otherwise fall back to `food_description`.
  - Detection does schema‑exact match first, then a small synonym fallback if missing.

- Densities and formulas
  - Filter out rows with `energy > 0`.
  - Per‑kcal for any nutrient `x`: `x_per_kcal = x / energy` (units follow `x`, e.g., mg/kcal for sodium).
  - Per‑100kcal for readability: `x_per_100kcal = x_per_kcal * 100`.
  - These columns are built for all available metrics so switching metrics/units is instant.

- Ranking, display, and UX
  - Choose the nutrient and unit via small UI widgets (dropdown + toggle) or by setting variables in the config cell.
  - Apply optional filters: `category_filter` equality, and substring exclusion via `exclude_allergens`/`dislikes` against the text column.
  - Sort by the chosen metric column and take `top_k`.
  - Display a styled Pandas table (index hidden) and a horizontal Top‑10 bar chart with wrapped labels and value annotations.

- Saving outputs
  - Path: [output/NutrientDensityExplorer](output/NutrientDensityExplorer)/`<metric>`/`<unit>_{csv|parquet}` where `<unit>` is `per_kcal` or `per_100kcal`.
  - Batch save uses the same unit and includes the metrics enabled in `metric_use`.

- Notes
  - Per‑100g rankings are intentionally not displayed/exported to avoid unit inconsistencies in branded entries. Use kcal‑based units for consistent comparisons.
  - If a nutrient column is truly missing, that metric is skipped (not added to `metrics_available`).

- Example formulas
  - `protein_per_kcal = protein / energy`
  - `protein_per_100kcal = protein_per_kcal * 100`
  - For sodium in mg: `sodium_per_kcal = sodium / energy` and `sodium_per_100kcal = sodium_per_kcal * 100`

## Weekly Meal Plan (7 days, 3 meals/day) — [generate_meal_plan.ipynb](generate_meal_plan.ipynb)

- What it does: builds a balanced 7‑day plan (3 meals/day) from your profile (gender, age, weight, height), activity, goal (loss/maintenance/gain), allergens/preferences, and pantry availability. Also produces a weekly Shopping List with items missing from your pantry.
- Steps (in order):
  - Read Parquet; detect columns for ID, Name, `kcal`, `protein_g`, `carb_g`, `fat_g`, and a text column (ingredients/description).
  - Filtering & flags: exclude allergens and dislikes; set `has_like` and `has_pantry` flags via case‑insensitive keyword detection against `likes` and `pantry_items`.
  - Targets & formulas (local to this notebook):
    - BMR (Mifflin–St Jeor): `BMR = 10*w + 6.25*h - 5*a + s`, with `s=5` (male) or `s=-161` (female).
    - TDEE: `TDEE = BMR * m`, with `m ∈ {1.2, 1.375, 1.55, 1.725}` (sedentary/light/moderate/heavy).
    - Daily kcal by goal: `daily_kcal = TDEE * α`, with `α = 0.85` (loss), `1.0` (maintenance), `1.10` (gain).
    - Macro grams: `protein_g = (daily_kcal * p_pct) / 4`, `carb_g = (daily_kcal * c_pct) / 4`, `fat_g = (daily_kcal * f_pct) / 9`.
    - Meal kcal targets: `meal_kcal[m] = daily_kcal * meal_splits[m]` (splits must sum to `1.0`).
    - Per‑kcal macro densities used for matching: `protein_per_kcal = protein_g / kcal`, `carb_per_kcal = carb_g / kcal`, `fat_per_kcal = fat_g / kcal`.
  - Scoring (per meal):
    - Macro proportion fit: normalize `(p, c, f)` per kcal to `(pp, cp, fp)` and compute `macro_fit = 1 - (|pp - tp| + |cp - tc| + |fp - tf|)`.
    - Calorie fit: `calorie_fit = max(0, 1 - |kcal - meal_kcal_target| / meal_kcal_target)`.
    - Total: `Score = w_m*macro_fit + w_c*calorie_fit + like_bonus + pantry_bonus - repeat_penalty` (small penalty if the same food was already used that week).
  - Plan assembly: convert candidates to Pandas, score against the current meal target, and pick the top‑scoring item for each meal on each day (7×3). Variety is encouraged via the repeat penalty.
  - Display & results: styled weekly table (Day, Meal, Food, `Calories (kcal)`, macro densities, flags, score) and a stacked macro chart by day. When `write_outputs=True`, saves CSV and JSON to [output/MealPlan](output/MealPlan).

- New: Weekly Shopping List
  - Ingredients column: the notebook keeps both `Food` and `Ingredients` (if a dedicated ingredients text exists; otherwise falls back to description) to build the list.
  - Extraction: parses the `Ingredients` text into items (comma‑separated, with simple cleanup), then removes any item that matches `pantry_items` (substring, case‑insensitive).
  - Aggregation: counts remaining items across all selected meals for the week and shows a table `Ingredient, Count`.
  - Saving: writes the table to [output/MealPlan/shopping_list.csv](output/MealPlan/shopping_list.csv) alongside the plan exports.
  - Fallback: if no ingredients are available, the list contains unique foods from the plan that don’t match your pantry keywords.

- Numerical example (illustrative): male, 80 kg, 180 cm, 30 y/o, moderate activity ($m=1.55$), maintenance ($\alpha=1.0$).
  - `BMR = 10*80 + 6.25*180 - 5*30 + 5 = 1780`.
  - `TDEE = 1780 * 1.55 ≈ 2759 kcal/day`.
  - If macro targets are `30% protein`, `40% carbs`, `30% fat`:
    `protein_g = (2759*0.30)/4 ≈ 207 g`; `carb_g = (2759*0.40)/4 ≈ 276 g`; `fat_g = (2759*0.30)/9 ≈ 92 g`.

- Example output (table) — first 3 meals of Day 1:

| Day   | Meal      | Food                          | Calories (kcal) | Protein/kcal | Carb/kcal | Fat/kcal | Score |
|-------|-----------|-------------------------------|-----------------|--------------|-----------|----------|-------|
| Day 1 | Breakfast | Greek yogurt + berries        | 450             | 0.062        | 0.122     | 0.027    | 0.81  |
| Day 1 | Lunch     | Grilled chicken salad         | 700             | 0.060        | 0.086     | 0.034    | 0.88  |
| Day 1 | Dinner    | Salmon + quinoa + veggies     | 610             | 0.062        | 0.079     | 0.036    | 0.85  |
Values are illustrative; scores depend on your settings (macro targets, `meal_splits`, bonuses).

### Why the plan stays balanced

- It simultaneously optimizes the macro mix and per‑meal calories. Very low‑calorie but unbalanced items (e.g., just an apple) score poorly on macro proportions and often on calorie fit—so they aren’t favored.
- Like/pantry bonuses personalize choices, and a repeat penalty pushes diversity across the week.



## Nutrient Similarity Search — [nutrient_similarity_search.ipynb](nutrient_similarity_search.ipynb)

What it does: finds foods similar to a chosen reference item using a nutrient vector (macros + optional micronutrients), with configurable feature toggles, weights, and constraints (e.g., “less sodium”, “more protein”). It renders a styled table and a Top‑N chart, then saves results (CSV/JSON) plus a `meta.json` containing the active configuration.

### Configuration (key variables)
- `input_path`, `fallback_file`, `output_dir`: I/O paths.
- `query_by_name` or `query_by_id`: how the reference item is selected (name substring, or exact ID).
- `top_k`: number of candidates to keep after sorting.
- `same_category_only`: restrict results to the reference item’s category (when present).
- `use_per_kcal`: normalize features per kcal; otherwise use raw values (effectively per 100g as provided).
- `scaling`: `zscore` or `none` (see scaling formula below).
- `exclude_allergens`, `dislikes`: keyword lists used for negative text filtering (ingredients/description).
- `feature_config`: per‑nutrient dictionary with `use` (include in vector), `weight` (feature weight), and `constraint` (`None` | `less` | `more`). The detected column is attached at runtime as `column`.

### Dataset‑Specific Schema (this repository)
- `strict_schema`: defaults to `True`. When enabled, the notebook uses exact column names from this dataset via `schema_columns` and only falls back to fuzzy detection if a column is missing.
- Core mappings used:
  - ID → `fdc_id`; Name → `food_description`; Category → `food_type`.
  - Energy → `energy`; Macros → `protein`, `carbs`, `total_fat`; Carbs detail → `sugars` (plus optional `glucose`, `fructose`, `sucrose`, `lactose`).
  - Lipids detail → `saturated_fat`, `trans_fat`, `monounsaturated_fat`, `polyunsaturated_fat`; Cholesterol → `cholesterol`.
  - Sodium → `sodium`; Selected minerals/vitamins (if present) → `potassium`, `calcium`, `iron`, `magnesium`, `phosphorus`, `zinc`, `copper`, `manganese`, `selenium`, and common vitamins (`vitamin_a`, `vitamin_c`, `vitamin_d`, `vitamin_e`, `vitamin_k`, `thiamin_b1`, `riboflavin_b2`, `niacin_b3`, `vitamin_b6`, `folate`, `vitamin_b12`).
- Auto‑detect of extra nutrients: disabled when `strict_schema=True` to keep behavior deterministic. Set `strict_schema=False` to re‑enable scanning for additional vitamin/mineral columns.
- Energy as a feature: usually keep disabled when `use_per_kcal=True` because energy/kcal equals 1 by construction.

### Column detection
Algorithm: first exact (lowercased) match, then “contains” (lowercased) against common synonyms/codes:
- ID: `fdc_id`, `id`
- Name: `description`, `food_name`, `name`, `brand_name`
- Energy (kcal): `energy_kcal`, `energy`, `kcal`, `calories`, or nutrient code `1008`
- Macros: `protein_g`/`1003`, `carbohydrate_g`/`1005`, `fat_g`/`1004`
- Carb details: `fiber_g`/`dietary_fiber`/`1079`, `sugar_g`/`2000`
- Sodium: `sodium_mg`/`1093`
- Category (optional): `food_category`, `wweia_food_category`, `category`
- Free‑text (ingredients/description): `ingredients`, `ingredients_text`, `description`, `food_name`, `name`, `brand_name`
- Micronutrients (if present): `calcium_mg`, `iron_mg`, `potassium_mg`, `magnesium_mg`, `zinc_mg`

Auto‑detect: when `auto_detect_extra_nutrients=True`, scan all columns for nutrient‑like keywords (`vitamin`, `vit_`, `phosphorus`, `cholesterol`, etc.) and add new entries in `feature_config` with `use=False` and `weight=0.3`.

### Densities (per kcal / per 100g)
- Filter rows with `kcal > 0`.
- Per‑kcal density for nutrient `x` (g or mg): `x_per_kcal = x / kcal`.
- Per 100g mode: if `use_per_kcal=False`, keep the dataset’s raw values (typically per 100g) without dividing by kcal.
- Missing nutrient columns (`use=True` but column absent): insert a literal `0.0` to keep the feature vector shape consistent.

### Feature matrix, scaling, and weighting
- Collect the selected feature columns (those with `use=True`) into matrix `X` (N×D).
- Scaling `zscore` (per column): `z = (x - mean) / std`. When `std <= 1e-12`, set `std = 1.0` for stability. If `scaling="none"`, then `mean=0` and `std=1` (no change).
- Weighting: multiply each column by its `weight` from `feature_config`.
- Row norms: `row_norm = ||X_i|| = sqrt(sum_j X_ij^2) + 1e-12` (the small term avoids division by zero).

### Selecting the reference item
- By ID: compare `ID` (as string) against `query_by_id` (exact equality).
- By name: look for `query_by_name` as a substring in the `Food` column (lowercased `contains`); take the first match. If `Food` is duplicated (from renaming), use the first sub‑column.
- Save `q_idx` (row index in `pdf`), `q_vec` (1×D vector), `q_norm` (its norm), `q_name`, and `q_cat`.

### Similarity (cosine)
- Formula: `sim(i) = (X_i · X_q) / (||X_i|| * ||X_q||)`.
- Set `sim(q_idx) = -1.0` to exclude the reference item from results.
- Sort descending and take `top_k` candidates.

### Constraints and filters
- Per‑nutrient constraints: for each used nutrient `k`, if `constraint='less'`, require `cand[k] <= q[k]`; if `constraint='more'`, require `cand[k] >= q[k]`. The reference value `q[k]` comes from the selected density column (per kcal or per 100g).
- Same category only: if `same_category_only=True` and `Category` exists, keep only `Category == q_cat`.
- Text filters: in `Text` (ingredients/description), drop any row containing any term from `exclude_allergens` or `dislikes` (lowercased `contains`).
- Percent deltas (transparency): for each used nutrient `k`, `Delta k (%) = ((cand[k] - q[k]) / (q[k] + 1e-12)) * 100`.

### Result columns
- `ID`, `Food`, optional `Category`.
- `Similarity` (cosine).
- Actual nutrient values used (e.g., `protein_per_kcal`, `sodium_mg_per_kcal`, etc.).
- `Delta k (%)` for each active nutrient.

### Visualization and saving
- Pandas `Styler` table: hidden index, formatting for `Similarity` and selected `Delta` columns (e.g., Protein, Sodium), and a green gradient over `Similarity`.
- “Top‑N Similarity” chart: horizontal bar chart for the first `top_n_chart` items with title “Top similar (to <q_name>)”.
- Saving: under [output/SimilaritySearch/<slug>](output/SimilaritySearch) write `similar_results.csv`, `similar_results.json`, and `meta.json` (containing `query`, `config`, `features_used`, and the `feature_config` with attached detected columns).

### Practical notes
- If many rows have near‑identical values (after `zscore` and weighting), cosine scores can approach 1. Adjust `feature_config` (select relevant nutrients, tune `weight`) and/or enable `same_category_only` and text filters to narrow the search.
- Ensure the reference item is excluded (explicitly set with `sims[q_idx] = -1`).
- When a nutrient is missing, it enters the vector as zero—shape stays consistent, but that nutrient won’t influence similarity unless given a non‑zero weight (in which case zero can lower similarity versus rows with high values for that nutrient).


