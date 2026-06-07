import polars as pl
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-results')
args = parser.parse_args()
results_path = Path(args.results)
csv_files = list(results_path.glob("*.csv"))

# Subset of cols
numeric_cols = [
    "total_floor_area",
    "energy_consumption_current",
    "current_energy_efficiency",
    "heating_cost_current",
]
category_cols = [
    "current_energy_rating",
    "property_type",
    "construction_age_band",
    "main_fuel",
    "built_form",
    "tenure",
    "mains_gas_flag",
    "walls_energy_eff",
    "roof_energy_eff",
    "floor_energy_eff",
    "windows_energy_eff",
]
all_needed_cols = numeric_cols + category_cols

# Create output
output_dir = Path("plots_full")
output_dir.mkdir(parents=True, exist_ok=True)


lazy_df = pl.scan_csv(
    csv_files,
    schema_overrides={
        "energy_consumption_current": pl.Float64,
        "total_floor_area": pl.Float64,
        "heating_cost_current": pl.Float64,
        "current_energy_efficiency": pl.Float64
    }
).select(all_needed_cols) 


# Read the data once into memory
df = lazy_df.collect()

sampled_num_df = (
    df
    .select(numeric_cols)
    .drop_nulls()
)
if len(sampled_num_df) > 100000:
    sampled_num_df = sampled_num_df.sample(n=100000, seed=42)

desc_df = df.describe()
desc_df.write_csv(output_dir / "descriptive_stats.csv")

cat_uniques_data = []
category_cols1 = df.select(pl.selectors.by_dtype(pl.String)).columns

for col in category_cols1:
    # Get unique non-null values, sort them, and convert to a plain Python list
    uniques = df[col].drop_nulls().unique().sort().to_list()
    
    # Append a row for every unique item found
    for value in uniques:
        cat_uniques_data.append({
            "column_name": col,
            "unique_value": str(value)
        })

# 2. Build the dataframe and save to disk
cat_values_df = pl.DataFrame(cat_uniques_data)
cat_values_df.write_csv(output_dir / "categorical_unique_values.csv")

# --- Numeric Plots ---
for col in numeric_cols:
    plt.figure(figsize=(8, 4))
    plt.boxplot(sampled_num_df[col], vert=False, patch_artist=True, showfliers=False,
                boxprops=dict(facecolor="#0072B2", color="black"),
                medianprops=dict(color="black"))
    plt.title(f"Distribution of {col}")
    plt.xlabel(col)
    plt.yticks([])  
    plt.grid(axis='x', alpha=0.75)
    plt.tight_layout()
    plt.savefig(f"plots_full/boxplot_{col}.png")  
    plt.close()



# --- Categorical Plots ---
for col in category_cols:
    counts_df = (
        df
        .group_by(col)
        .len(name="count")
        .drop_nulls()
        .sort("count", descending=True)
        .limit(15) 
    )
    short_labels = [str(x)[:40] + '...' if len(str(x)) > 40 else str(x) for x in counts_df[col]]

    plt.figure(figsize=(10, 5))
    plt.bar(short_labels, counts_df["count"].to_list(), color="#CC79A7", edgecolor="black")
    plt.title(f"Property Count by {col}")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Number of Properties")
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    plt.savefig(f"plots_full/bar_{col}.png")
    plt.clf()
    plt.close()
