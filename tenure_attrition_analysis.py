
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# HR Workforce Intelligence
# Tenure and Attrition Analysis

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "Data" / "Raw" / "employees.csv"
OUTPUT_DIR = PROJECT_DIR / "Data" / "Processed"
CHART_DIR = OUTPUT_DIR / "Charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, low_memory=False)

required = ["Tenure_Years", "Attrition"]
missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["Tenure_Years"] = pd.to_numeric(
    df["Tenure_Years"], errors="coerce"
)

df["Attrition_Clean"] = (
    df["Attrition"].astype("string").str.strip().str.lower()
)

yes_values = {"yes", "y", "true", "1"}
no_values = {"no", "n", "false", "0"}

df = df[
    df["Attrition_Clean"].isin(yes_values | no_values)
    & df["Tenure_Years"].notna()
].copy()

df["Employee_Left"] = (
    df["Attrition_Clean"].isin(yes_values).astype(int)
)

# Group employees by tenure
df["Tenure_Group"] = pd.cut(
    df["Tenure_Years"],
    bins=[-0.001, 1, 3, 5, 10, float("inf")],
    labels=[
        "0-1 years",
        "1-3 years",
        "3-5 years",
        "5-10 years",
        "10+ years"
    ],
    right=True
)

# Calculate attrition by tenure group
summary = (
    df.groupby("Tenure_Group", observed=False)
    .agg(
        Total_Employees=("Employee_Left", "size"),
        Employees_Left=("Employee_Left", "sum"),
        Attrition_Rate=("Employee_Left", "mean")
    )
    .reset_index()
)

summary["Attrition_Rate"] = (
    summary["Attrition_Rate"] * 100
).round(2)

print("\nTENURE & ATTRITION ANALYSIS")
print("=" * 55)
print(summary.to_string(index=False))

# Save report
report_file = OUTPUT_DIR / "tenure_attrition_analysis.csv"
summary.to_csv(report_file, index=False)

# Create chart
plot_data = summary.dropna(subset=["Attrition_Rate"])

plt.figure(figsize=(10, 6))
bars = plt.bar(
    plot_data["Tenure_Group"].astype(str),
    plot_data["Attrition_Rate"]
)

plt.title("Employee Attrition by Tenure Group")
plt.xlabel("Tenure Group")
plt.ylabel("Attrition Rate (%)")
plt.xticks(rotation=20)

for bar, value in zip(bars, plot_data["Attrition_Rate"]):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.1f}%",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

chart_file = CHART_DIR / "tenure_attrition_analysis.png"
plt.savefig(chart_file, dpi=300, bbox_inches="tight")
plt.close()

print("\nAnalysis completed successfully.")
print("Report:", report_file)
print("Chart:", chart_file)
