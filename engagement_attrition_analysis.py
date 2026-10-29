
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# HR Workforce Intelligence
# Engagement and Attrition Analysis

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "Data" / "Raw" / "employees.csv"
OUTPUT_DIR = PROJECT_DIR / "Data" / "Processed"
CHART_DIR = OUTPUT_DIR / "Charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, low_memory=False)

required = ["Engagement_Score", "Attrition"]
missing = [col for col in required if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["Engagement_Score"] = pd.to_numeric(
    df["Engagement_Score"], errors="coerce"
)

df["Attrition_Clean"] = (
    df["Attrition"].astype("string").str.strip().str.lower()
)

yes_values = {"yes", "y", "true", "1"}
no_values = {"no", "n", "false", "0"}

df = df[
    df["Attrition_Clean"].isin(yes_values | no_values)
    & df["Engagement_Score"].notna()
].copy()

df["Employee_Left"] = (
    df["Attrition_Clean"].isin(yes_values).astype(int)
)

# Summarize by engagement score
summary = (
    df.groupby("Engagement_Score")
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

print("\nENGAGEMENT & ATTRITION ANALYSIS")
print("=" * 55)
print(summary.to_string(index=False))

report_file = OUTPUT_DIR / "engagement_attrition_analysis.csv"
summary.to_csv(report_file, index=False)

# Plot attrition rate by engagement score
plt.figure(figsize=(9, 5))
bars = plt.bar(
    summary["Engagement_Score"].astype(str),
    summary["Attrition_Rate"]
)

plt.title("Employee Attrition Rate by Engagement Score")
plt.xlabel("Engagement Score")
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

chart_file = CHART_DIR / "engagement_attrition_analysis.png"
plt.savefig(chart_file, dpi=300, bbox_inches="tight")
plt.close()

print("\nAnalysis completed successfully.")
print("Report:", report_file)
print("Chart:", chart_file)
