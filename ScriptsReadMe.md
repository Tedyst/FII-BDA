# Detailed Notebook Overview

This document explains, one by one, what each notebook does, the exact steps implemented inside, and the formulas used locally in that notebook. No prerequisites are included here. All formulas are written in plain text (no LaTeX) to avoid rendering issues on GitHub.

## Top 10 Protein per Kcal — [generate_top10_prot_per_kcal.ipynb](generate_top10_prot_per_kcal.ipynb)

- What it does: finds the 10 foods with the highest protein density (grams of protein per kcal).
- Steps (in order):
  - Initialize Spark and read Parquet from [output/nutritional_profiles](output/nutritional_profiles). If the folder is missing, fall back to a specific part file in the same area.
  - Detect required columns via exact and then contains matching (case‑insensitive):
    - ID: `fdc_id`, `id`.
    - Name: `description`, `food_name`, `name`, `brand_name`.
    - Calories (kcal): `energy_kcal`, `energy`, `kcal`, `calories`, or nutrient code `1008`.
    - Protein (g): `protein_g`, `protein`, or nutrient code `1003`.
  - Filter rows with `kcal > 0`.
  - Compute density: `protein_per_kcal = protein_g / kcal`.
  - Sort descending by `protein_per_kcal` and take Top 10.
  - Write results as CSV and Parquet to [output/Top10_bestfoods_prots_per_kcal](output/Top10_bestfoods_prots_per_kcal).
- Saved fields: ID, Name, `kcal`, `protein_g`, `protein_per_kcal`.
- Notes: when scores tie, ordering is determined by the DataFrame’s implicit secondary sort (ID/Name).

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

- What it does: explores Top‑K nutrient densities both per kcal and per 100g for selected nutrients (protein, fiber, sugar, fat, sodium), with optional WWEIA category filters. Displays styled tables and a bar chart; writes CSV and Parquet outputs per metric.
- Steps (in order):
  - Initialize Spark; read Parquet from [output/nutritional_profiles](output/nutritional_profiles).
  - Detect columns: ID (`fdc_id`/`id`), Name (`description`/`food_name`/`name`/`brand_name`), Calories (`energy_kcal`/`kcal`/`1008`), nutrients (`protein_g`, `fiber_g`/`1079`, `carb_g`/`1005`, `sugar_g`/`2000`, `fat_g`/`1004`, `sodium_mg`/`1093`), optional weight in grams (`serving_size_g`/`gram_weight`), and optional category (`wweia_*`/`food_category`).
  - Filter rows with positive calories.
  - Compute densities:
    - Per kcal: `nutrient_per_kcal = nutrient_g / kcal` (for sodium: `sodium_mg_per_kcal = sodium_mg / kcal`).
    - Per 100g: if a weight column exists, `nutrient_per_100g = nutrient_g / weight_g * 100`; otherwise, treat nutrient values as already per 100g.
  - Optional category filtering: include or exclude WWEIA categories if the category column exists; otherwise, filters are ignored with a message.
  - Top‑K selection: order ascending/descending and limit to `top_k`, separately for per‑kcal and per‑100g.
  - Display: styled Pandas table highlighting the selected metric plus a Top 10 bar chart.
  - Outputs: per metric, write Top‑K to [output/NutrientDensityExplorer](output/NutrientDensityExplorer) under `<metric>/per_kcal_csv`, `<metric>/per_kcal_parquet`, `<metric>/per_100g_csv`, `<metric>/per_100g_parquet`. Batch cell can save all metrics at once.

- Example output (table) — `protein` per kcal:

| id    | name                                 | kcal | category                  | protein_per_kcal |
|-------|--------------------------------------|------|---------------------------|------------------|
| 214123| Chicken breast (roasted, skinless)   | 165  | Poultry                   | 0.188            |
| 735221| Tuna (canned in water, drained)      | 116  | Fish and Shellfish        | 0.224            |
Values are illustrative; exact categories depend on your dataset.

- Example output (table) — `protein` per 100g:

| id    | name                                 | kcal | category                  | protein_per_100g |
|-------|--------------------------------------|------|---------------------------|------------------|
| 214123| Chicken breast (roasted, skinless)   | 165  | Poultry                   | 31.0             |
| 735221| Tuna (canned in water, drained)      | 116  | Fish and Shellfish        | 26.0             |
If weight is available, values are normalized to 100g; otherwise the dataset’s values are used as‑is.

- Example output (table) — `sodium` densities:

| id    | name                                 | kcal | category                  | sodium_mg_per_kcal | sodium_mg_per_100g |
|-------|--------------------------------------|------|---------------------------|-------------------|--------------------|
| 600111| Canned soup (tomato)                 | 90   | Mixed Dishes              | 4.8               | 430                |
| 600512| Cheese (cheddar)                     | 403  | Milk and Dairy Products   | 1.0               | 620                |
Units: sodium per kcal in mg/kcal; sodium per 100g in mg/100g.

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

## Why the plan stays balanced

- It simultaneously optimizes the macro mix and per‑meal calories. Very low‑calorie but unbalanced items (e.g., just an apple) score poorly on macro proportions and often on calorie fit—so they aren’t favored.
- Like/pantry bonuses personalize choices, and a repeat penalty pushes diversity across the week.


