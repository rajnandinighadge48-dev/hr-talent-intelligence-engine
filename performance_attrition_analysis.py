
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "Data" / "Raw" / "employees.csv"
OUTPUT_DIR = PROJECT_DIR / "Data" / "Processed"
CHART_DIR = OUTPUT_DIR / "Charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, low_memory=False)

required = ["Performance_Rating", "Attrition"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")

df["Performance_Rating"] = pd.to_numeric(
    df["Performance_Rating"], errors="coerce"
)
df["Attrition_Clean"] = (
    df["Attrition"].astype("string").str.strip().str.lower()
)

yes_values = {"yes", "y", "true", "1"}
no_values = {"no", "n", "false", "0"}

df = df[
    df["Attrition_Clean"].isin(yes_values | no_values)
    & df["Performance_Rating"].notna()
].copy()

df["Employee_Left"] = (
    df["Attrition_Clean"].isin(yes_values).astype(int)
)

summary = (
    df.groupby("Performance_Rating")
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

print("\nPERFORMANCE & ATTRITION ANALYSIS")
print("=" * 50)
print(summary.to_string(index=False))

summary.to_csv(
    OUTPUT_DIR / "performance_attrition_analysis.csv",
    index=False
)

plt.figure(figsize=(9, 5))
bars = plt.bar(
    summary["Performance_Rating"].astype(str),
    summary["Attrition_Rate"]
)
plt.title("Attrition Rate by Performance Rating")
plt.xlabel("Performance Rating")
plt.ylabel("Attrition Rate (%)")

for bar, value in zip(bars, summary["Attrition_Rate"]):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.1f}%",
        ha="center",
        va="bottom"
    )

plt.tight_layout()
plt.savefig(
    CHART_DIR / "performance_attrition_analysis.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("\nAnalysis completed successfully.")
print("Report saved in Data/Processed")
print("Chart saved in Data/Processed/Charts")
