
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ============================================
# HR TALENT INTELLIGENCE ENGINE
# Department-wise Attrition Analysis
# ============================================

PYTHON_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PYTHON_DIR.parent

DATA_FILE = PROJECT_DIR / "Data" / "Raw" / "employees.csv"
OUTPUT_DIR = PROJECT_DIR / "Data" / "Processed"
CHART_DIR = OUTPUT_DIR / "Charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 55)
print("       DEPARTMENT-WISE ATTRITION ANALYSIS")
print("=" * 55)

# 1. Load employee data
df = pd.read_csv(DATA_FILE, low_memory=False)

# 2. Check required columns
required_columns = ["Department", "Attrition"]
missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required columns not found: {missing_columns}"
    )

# 3. Standardize Attrition labels
df["Attrition_Clean"] = (
    df["Attrition"].astype("string").str.strip().str.lower()
)

yes_values = {"yes", "y", "true", "1"}
no_values = {"no", "n", "false", "0"}

valid = df["Attrition_Clean"].isin(yes_values | no_values)
analysis_df = df.loc[valid].copy()

if analysis_df.empty:
    raise ValueError("No valid Yes/No attrition records found.")

analysis_df["Employee_Left"] = (
    analysis_df["Attrition_Clean"].isin(yes_values).astype(int)
)

# 4. Overall attrition results
total_employees = len(analysis_df)
employees_left = int(analysis_df["Employee_Left"].sum())
overall_rate = employees_left / total_employees * 100

print(f"\nEmployees analyzed: {total_employees:,}")
print(f"Employees who left: {employees_left:,}")
print(f"Overall attrition rate: {overall_rate:.2f}%")

# 5. Department-wise analysis
department_summary = (
    analysis_df.groupby("Department", dropna=False)
    .agg(
        Total_Employees=("Employee_Left", "size"),
        Employees_Left=("Employee_Left", "sum"),
        Attrition_Rate=("Employee_Left", "mean")
    )
    .reset_index()
)

department_summary["Attrition_Rate"] *= 100
department_summary["Attrition_Rate"] = (
    department_summary["Attrition_Rate"].round(2)
)

department_summary = department_summary.sort_values(
    "Attrition_Rate", ascending=False
)

print("\nDEPARTMENT-WISE RESULTS")
print("-" * 55)
print(department_summary.to_string(index=False))

# 6. Save results
report_file = OUTPUT_DIR / "department_attrition_analysis.csv"
department_summary.to_csv(report_file, index=False)

# 7. Create professional chart
chart_data = department_summary.sort_values("Attrition_Rate")

plt.figure(figsize=(10, 6))
bars = plt.barh(
    chart_data["Department"].astype(str),
    chart_data["Attrition_Rate"]
)

plt.title(
    "Department-wise Employee Attrition Rate",
    fontsize=15,
    fontweight="bold"
)
plt.xlabel("Attrition Rate (%)")
plt.ylabel("Department")

for bar, value in zip(bars, chart_data["Attrition_Rate"]):
    plt.text(
        bar.get_width() + 0.2,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}%",
        va="center",
        fontsize=9
    )

plt.tight_layout()

chart_file = CHART_DIR / "department_attrition_rate.png"
plt.savefig(chart_file, dpi=300, bbox_inches="tight")
plt.close()

print("\n" + "=" * 55)
print("ATTRITION ANALYSIS COMPLETED!")
print("Report:", report_file)
print("Chart:", chart_file)
print("=" * 55)
