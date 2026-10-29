
from pathlib import Path
import pandas as pd

# ====================================================
# HR TALENT INTELLIGENCE ENGINE
# Consolidated Workforce Business Insights
# ====================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "Data" / "Raw" / "employees.csv"
OUTPUT_DIR = PROJECT_DIR / "Data" / "Processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, low_memory=False)

required = [
    "Employee_ID", "Department", "Annual_Salary_INR",
    "Tenure_Years", "Engagement_Score",
    "Performance_Rating", "Attrition"
]

missing = [col for col in required if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Clean fields
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

for col in [
    "Annual_Salary_INR", "Tenure_Years",
    "Engagement_Score", "Performance_Rating"
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Overall workforce KPIs
total = len(df)
left = int(df["Employee_Left"].sum())
active = total - left
attrition_rate = left / total * 100 if total else 0

kpis = pd.DataFrame({
    "Metric": [
        "Total Employees",
        "Active Employees",
        "Employees Left",
        "Overall Attrition Rate (%)",
        "Average Annual Salary (INR)",
        "Average Tenure (Years)",
        "Average Engagement Score",
        "Average Performance Rating"
    ],
    "Value": [
        total,
        active,
        left,
        round(attrition_rate, 2),
        round(df["Annual_Salary_INR"].mean(), 2),
        round(df["Tenure_Years"].mean(), 2),
        round(df["Engagement_Score"].mean(), 2),
        round(df["Performance_Rating"].mean(), 2)
    ]
})

# Department insights
department = (
    df.groupby("Department", dropna=False)
    .agg(
        Total_Employees=("Employee_ID", "size"),
        Employees_Left=("Employee_Left", "sum"),
        Average_Salary_INR=("Annual_Salary_INR", "mean"),
        Average_Tenure=("Tenure_Years", "mean"),
        Average_Engagement=("Engagement_Score", "mean"),
        Average_Performance=("Performance_Rating", "mean")
    )
    .reset_index()
)

department["Attrition_Rate_Pct"] = (
    department["Employees_Left"]
    / department["Total_Employees"] * 100
).round(2)

department = department.round(2).sort_values(
    "Attrition_Rate_Pct", ascending=False
)

# Tenure-group insights
df["Tenure_Group"] = pd.cut(
    df["Tenure_Years"],
    bins=[-0.001, 1, 3, 5, 10, float("inf")],
    labels=["0-1 years", "1-3 years", "3-5 years",
            "5-10 years", "10+ years"]
)

tenure = (
    df.groupby("Tenure_Group", observed=False)
    .agg(
        Total_Employees=("Employee_ID", "size"),
        Employees_Left=("Employee_Left", "sum")
    )
    .reset_index()
)

tenure["Attrition_Rate_Pct"] = (
    tenure["Employees_Left"] / tenure["Total_Employees"] * 100
).round(2)

# Engagement-group insights
df["Engagement_Group"] = pd.cut(
    df["Engagement_Score"],
    bins=[-float("inf"), 2, 3, 4, float("inf")],
    labels=["Low (<=2)", "Moderate (>2-3)",
            "High (>3-4)", "Very High (>4)"],
    include_lowest=True
)

engagement = (
    df.groupby("Engagement_Group", observed=False)
    .agg(
        Total_Employees=("Employee_ID", "size"),
        Employees_Left=("Employee_Left", "sum")
    )
    .reset_index()
)

engagement["Attrition_Rate_Pct"] = (
    engagement["Employees_Left"] / engagement["Total_Employees"] * 100
).round(2)

# Performance-group insights
performance = (
    df.groupby("Performance_Rating", dropna=False)
    .agg(
        Total_Employees=("Employee_ID", "size"),
        Employees_Left=("Employee_Left", "sum")
    )
    .reset_index()
)

performance["Attrition_Rate_Pct"] = (
    performance["Employees_Left"] / performance["Total_Employees"] * 100
).round(2)

# Save separate reports
kpis.to_csv(OUTPUT_DIR / "hr_overall_kpis.csv", index=False)
department.to_csv(OUTPUT_DIR / "hr_department_insights.csv", index=False)
tenure.to_csv(OUTPUT_DIR / "hr_tenure_insights.csv", index=False)
engagement.to_csv(OUTPUT_DIR / "hr_engagement_insights.csv", index=False)
performance.to_csv(OUTPUT_DIR / "hr_performance_insights.csv", index=False)

# Create readable business findings
highest_dept = department.iloc[0]
highest_tenure = tenure.loc[tenure["Attrition_Rate_Pct"].idxmax()]
highest_performance = performance.loc[
    performance["Attrition_Rate_Pct"].idxmax()
]

findings = pd.DataFrame([
    {
        "Business_Area": "Overall Workforce",
        "Finding": f"Overall attrition rate is {attrition_rate:.2f}%.",
        "Recommendation": "Monitor attrition trends and review retention initiatives."
    },
    {
        "Business_Area": "Department",
        "Finding": (
            f"{highest_dept['Department']} has the highest department "
            f"attrition rate at {highest_dept['Attrition_Rate_Pct']:.2f}%."
        ),
        "Recommendation": "Investigate department-level exit reasons and employee feedback."
    },
    {
        "Business_Area": "Tenure",
        "Finding": (
            f"{highest_tenure['Tenure_Group']} has the highest tenure-group "
            f"attrition rate at {highest_tenure['Attrition_Rate_Pct']:.2f}%."
        ),
        "Recommendation": "Review onboarding and retention support for this tenure group."
    },
    {
        "Business_Area": "Performance",
        "Finding": (
            f"Performance rating {highest_performance['Performance_Rating']} "
            f"has the highest observed attrition rate."
        ),
        "Recommendation": "Review exit feedback and other factors before drawing conclusions."
    }
])

findings.to_csv(OUTPUT_DIR / "hr_business_findings.csv", index=False)

print("\n" + "=" * 55)
print("HR WORKFORCE BUSINESS INSIGHTS")
print("=" * 55)

print("\nOVERALL KPIs")
print(kpis.to_string(index=False))

print("\nDEPARTMENT INSIGHTS")
print(department.to_string(index=False))

print("\nTENURE INSIGHTS")
print(tenure.to_string(index=False))

print("\nENGAGEMENT INSIGHTS")
print(engagement.to_string(index=False))

print("\nPERFORMANCE INSIGHTS")
print(performance.to_string(index=False))

print("\nBUSINESS FINDINGS")
print(findings.to_string(index=False))

print("\nReports saved in:", OUTPUT_DIR)
print("BUSINESS INSIGHTS ANALYSIS COMPLETED SUCCESSFULLY!")
