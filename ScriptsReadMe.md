# Detailed Notebook Overview

This document explains, one by one, what each notebook does, the exact steps implemented inside, and the formulas used locally in that notebook. No prerequisites are included here.

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
  - Compute density: $$\text{protein\_per\_kcal} = \frac{\text{protein\_g}}{\text{kcal}}.$$
  - Sort descending by `protein_per_kcal` and take Top 10.
  - Write results as CSV and Parquet to [output/Top10_bestfoods_prots_per_kcal](output/Top10_bestfoods_prots_per_kcal).
- Saved fields: ID, Name, `kcal`, `protein_g`, `protein_per_kcal`.
- Notes: when scores tie, ordering is determined by the DataFrame’s implicit secondary sort (ID/Name).

- Example output (CSV):

```csv
fdc_id,name,kcal,protein_g,protein_per_kcal
214123,Chicken breast (roasted, skinless),165,31.0,0.188
735221,Tuna (canned in water, drained),116,26.0,0.224
```
Values are illustrative; the full list contains 10 lines.

## Configurable Recommendations — [generate_recommendations.ipynb](generate_recommendations.ipynb)

- What it does: produces a Top‑K based on filters (allergens/keywords, calorie range) and either a single sort field or a composite score.
- Steps (in order):
  - Read Parquet and detect columns for ID, Name, `kcal`, `protein_g`, optional `fiber_g` (code `1079`), `carb_g` (`1005`), `sugar_g` (`2000`), `fat_g` (`1004`), and a text column (usually `ingredients` or `description`).
  - Filtering:
    - Exclusions (allergens/words): drop rows where the text contains any excluded term.
    - Inclusions: flag rows where the text contains preferred terms; if `must_include=True`, keep only those.
    - Calorie range: keep `kcal` in `[calorie_min, calorie_max]`.
  - Per‑kcal densities for each available nutrient: $$\text{density} = \frac{\text{nutrient\_g}}{\text{kcal}}.$$
  - Ranking (two paths):
    - Single‑field sort: set `sort_by` (e.g., `protein_per_kcal`, `fiber_per_kcal`, `sugar_per_kcal`, `fat_per_kcal`) and direction (desc/asc).
    - Composite score (when `sort_by` is empty):
      $$\text{Score}=\sum_i w_i\cdot \text{density}_i + w_{\text{include}}\cdot \mathbf{1}_{\text{has\_included}}.$$
      Here $w_i$ are your weights for protein/fiber/carb/sugar/fat, and $\mathbf{1}_{\text{has\_included}}$ is 1 if the row has included terms, else 0.
      Example: if `protein_per_kcal=0.12`, `fiber_per_kcal=0.03`, `fat_per_kcal=0.01`, weights $(w_p,w_f,w_fat)=(1.0,0.5,0.2)$ and bonus `w_include=0.1` (with included terms), then $$\text{Score}=1.0\cdot0.12+0.5\cdot0.03+0.2\cdot0.01+0.1\cdot1=0.237.$$
  - Notebook output: a styled Pandas table that colors the chosen metric (`sort_by`, or `Score` when using composite scoring) and a chart based on the same metric. The index is hidden with a compatibility‑safe approach across Pandas versions.
  - Write results: CSV + Parquet to [output/Recommendations](output/Recommendations), including base fields + densities and `Score` (if applicable).

- Example output (CSV) — with `sort_by="protein_per_kcal"`:

```csv
id,name,kcal,protein_g,protein_per_kcal,fiber_per_kcal,carb_per_kcal,sugar_per_kcal,fat_per_kcal
214123,Chicken breast (roasted, skinless),165,31.0,0.188,0.000,0.000,0.000,0.024
735221,Tuna (canned in water, drained),116,26.0,0.224,0.000,0.000,0.000,0.009
```

- Example output (CSV) — with composite `Score`:

```csv
id,name,kcal,protein_g,protein_per_kcal,fiber_per_kcal,carb_per_kcal,sugar_per_kcal,fat_per_kcal,Score
498311,Greek yogurt (plain, nonfat),59,10.3,0.175,0.000,0.081,0.032,0.000,0.231
214123,Chicken breast (roasted, skinless),165,31.0,0.188,0.000,0.000,0.000,0.024,0.227
```
Values are examples; exact columns depend on which densities exist in your dataset.

## Weekly Meal Plan (7 days, 3 meals/day) — [generate_meal_plan.ipynb](generate_meal_plan.ipynb)

- What it does: builds a balanced 7‑day plan with 3 meals/day based on profile (gender, age, weight, height), activity, goal (loss/maintenance/gain), allergens/preferences, and pantry flags.
- Steps (in order):
  - Read Parquet; detect columns for ID, Name, `kcal`, `protein_g`, `carb_g`, `fat_g`, and a text column.
  - Filtering & flags: exclude allergens/dislikes; set `has_like` and `has_pantry` flags via keyword detection.
  - Targets & formulas (local to this notebook):
    - BMR (Mifflin–St Jeor): $$\text{BMR}=10\,w+6.25\,h-5\,a+s,$$ where $s=5$ (male) or $s=-161$ (female).
    - TDEE: $$\text{TDEE}=\text{BMR}\cdot m,$$ with $m\in\{1.2,1.375,1.55,1.725\}$ (sedentary/light/moderate/intense).
    - Daily kcal by goal: $$\text{daily\_kcal}=\text{TDEE}\cdot \alpha,$$ with $\alpha=0.85$ (loss), $1.0$ (maintenance), $1.10$ (gain).
    - Macro grams: $$\text{protein\_g}=\frac{\text{daily\_kcal}\cdot p_{\%}}{4},\quad \text{carb\_g}=\frac{\text{daily\_kcal}\cdot c_{\%}}{4},\quad \text{fat\_g}=\frac{\text{daily\_kcal}\cdot f_{\%}}{9}.$$
    - Meal kcal targets: $$\text{meal\_kcal}[m]=\text{daily\_kcal}\cdot \text{meal\_splits}[m],$$ e.g., `Breakfast=0.25, Lunch=0.4, Dinner=0.35` summing to 1.0.
    - Per‑kcal macro densities in the dataset: $$p_{\text{kcal}}=\frac{p_g}{\text{kcal}},\quad c_{\text{kcal}}=\frac{c_g}{\text{kcal}},\quad f_{\text{kcal}}=\frac{f_g}{\text{kcal}}.$$
  - Numerical example (illustrative): male, 80 kg, 180 cm, 30 y/o, moderate activity ($m=1.55$), maintenance ($\alpha=1.0$).
    - $$\text{BMR}=10\cdot80+6.25\cdot180-5\cdot30+5=1780.$$
    - $$\text{TDEE}=1780\cdot1.55\approx2759\ \text{kcal/day}.$$
    - If macro targets are 30% protein, 40% carbs, 30% fat: $$\text{protein\_g}=\frac{2759\cdot0.30}{4}\approx207\ g;\ \text{carb\_g}=\frac{2759\cdot0.40}{4}\approx276\ g;\ \text{fat\_g}=\frac{2759\cdot0.30}{9}\approx92\ g.$$
  - Scoring (per meal):
    - Macro proportion fit: normalize $(p,c,f)$ to proportions $pp,cp,fp$ and $$\text{macro\_fit}=1-(|pp-tp|+|cp-tc|+|fp-tf|).$$
    - Calorie fit: $$\text{calorie\_fit}=\max\!\left(0,1-\frac{|\text{kcal}-\text{meal\_kcal\_target}|}{\text{meal\_kcal\_target}}\right).$$
    - Total: $$\text{Score}=w_m\cdot\text{macro\_fit}+w_c\cdot\text{calorie\_fit}+\text{bonuses}-\text{repeat\_penalty},$$ with configurable weights $w_m,w_c$ (e.g., $0.6/0.4$) and bonuses for `has_like`/`has_pantry`.
  - Plan assembly: convert candidates to Pandas, score against the current meal target, and select the highest‑scoring item for each meal on each day (7×3). Apply a small repeat penalty to encourage variety.
  - Display & results: styled weekly table (Day, Meal, Name, `kcal`, `protein_g`, `carb_g`, `fat_g`, densities, score) and a stacked macro chart by day. Optionally write CSV/JSON to [output/MealPlan](output/MealPlan).

- Example output (CSV) — first 3 meals of Day 1:

```csv
Day,Meal,name,kcal,protein_g,carb_g,fat_g,protein_per_kcal,carb_per_kcal,fat_per_kcal,score
Day 1,Breakfast,Greek yogurt + berries,450,28.0,55.0,12.0,0.062,0.122,0.027,0.81
Day 1,Lunch,Grilled chicken salad,700,42.0,60.0,24.0,0.060,0.086,0.034,0.88
Day 1,Dinner,Salmon + quinoa + veggies,610,38.0,48.0,22.0,0.062,0.079,0.036,0.85
```

- Example output (JSON) — day‑structured:

```json
{
  "Day": "Day 1",
  "Meals": [
    {"meal": "Breakfast", "name": "Greek yogurt + berries", "kcal": 450, "protein_g": 28.0, "carb_g": 55.0, "fat_g": 12.0, "score": 0.81},
    {"meal": "Lunch", "name": "Grilled chicken salad", "kcal": 700, "protein_g": 42.0, "carb_g": 60.0, "fat_g": 24.0, "score": 0.88},
    {"meal": "Dinner", "name": "Salmon + quinoa + veggies", "kcal": 610, "protein_g": 38.0, "carb_g": 48.0, "fat_g": 22.0, "score": 0.85}
  ]
}
```
Values are illustrative; scores depend on your settings (macro targets, `meal_splits`, bonuses).

## Why the plan stays balanced

- It simultaneously optimizes the macro mix and per‑meal calories. Very low‑calorie but unbalanced items (e.g., just an apple) score poorly on macro proportions and often on calorie fit—so they aren’t favored.
- Like/pantry bonuses personalize choices, and a repeat penalty pushes diversity across the week.


