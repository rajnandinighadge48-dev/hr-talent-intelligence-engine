
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# HR Workforce Intelligence
# Salary and Attrition Analysis

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "Data" / "Raw" / "employees.csv"
OUTPUT_DIR = PROJECT_DIR / "Data" / "Processed"
CHART_DIR = OUTPUT_DIR / "Charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, low_memory=False)

required = ["Annual_Salary_INR", "Attrition"]
missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["Annual_Salary_INR"] = pd.to_numeric(
    df["Annual_Salary_INR"], errors="coerce"
)

df["Attrition_Clean"] = (
    df["Attrition"].astype("string").str.strip().str.lower()
)

yes_values = {"yes", "y", "true", "1"}
no_values = {"no", "n", "false", "0"}

df = df[
    df["Attrition_Clean"].isin(yes_values | no_values)
].copy()

df["Employee_Left"] = (
    df["Attrition_Clean"].isin(yes_values).astype(int)
)

# Compare salary for employees who stayed vs left
summary = (
    df.groupby("Employee_Left")["Annual_Salary_INR"]
    .agg(["count", "mean", "median"])
    .rename(index={0: "Stayed", 1: "Left"})
    .round(2)
)

print("\nSALARY & ATTRITION ANALYSIS")
print("=" * 45)
print(summary)

summary.to_csv(OUTPUT_DIR / "salary_attrition_summary.csv")

# Visualize average salary
plot_data = (
    df.groupby("Employee_Left")["Annual_Salary_INR"]
    .mean()
    .rename(index={0: "Stayed", 1: "Left"})
    .dropna()
)

plt.figure(figsize=(8, 5))
bars = plt.bar(plot_data.index, plot_data.values)

plt.title("Average Annual Salary: Stayed vs Left")
plt.xlabel("Employee Status")
plt.ylabel("Average Annual Salary (INR)")

for bar, value in zip(bars, plot_data.values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"₹{value:,.0f}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()
plt.savefig(
    CHART_DIR / "salary_attrition_comparison.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("\nAnalysis completed successfully.")
print("Report saved: salary_attrition_summary.csv")
print("Chart saved: salary_attrition_comparison.png")
