
from pathlib import Path
import pandas as pd

# ==========================================================
# HR TALENT INTELLIGENCE ENGINE
# Professional HR Workforce Intelligence Analysis
# ==========================================================

print("=" * 60)
print("          HR WORKFORCE INTELLIGENCE")
print("          PYTHON DATA ANALYSIS")
print("=" * 60)

# 1. Locate the project and employee dataset
PYTHON_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PYTHON_DIR.parent
DATA_FILE = PROJECT_DIR / "Data" / "Raw" / "employees.csv"

print("\n[1] CHECKING DATASET LOCATION")
print("-" * 45)
print("Dataset path:", DATA_FILE)
print("File exists:", DATA_FILE.exists())

if not DATA_FILE.exists():
    raise FileNotFoundError(
        "\nemployees.csv was not found at the expected location.\n"
        f"Expected path: {DATA_FILE}\n"
        "Check the Data/Raw folder and filename."
    )

# 2. Load data
print("\n[2] LOADING EMPLOYEE DATA")
print("-" * 45)

df = pd.read_csv(DATA_FILE, low_memory=False)

print("Dataset loaded successfully!")
print(f"Total employee records: {len(df):,}")
print(f"Total columns: {len(df.columns)}")

# 3. Show column names
print("\n[3] DATASET COLUMNS")
print("-" * 45)

for number, column in enumerate(df.columns, start=1):
    print(f"{number}. {column}")

# 4. Display sample records
print("\n[4] FIRST FIVE RECORDS")
print("-" * 45)
print(df.head().to_string(index=False))

# 5. Data quality checks
print("\n[5] DATA QUALITY ANALYSIS")
print("-" * 45)

missing_values = df.isnull().sum()
missing_total = int(missing_values.sum())
duplicate_rows = int(df.duplicated().sum())

print("Total missing cells:", f"{missing_total:,}")
print("Duplicate rows:", f"{duplicate_rows:,}")

if missing_values.any():
    print("\nMissing values by column:")
    print(missing_values[missing_values > 0].to_string())
else:
    print("No missing values found.")

# 6. Check employee ID duplicates
normalized_columns = {
    str(column).strip().lower().replace(" ", "_"): column
    for column in df.columns
}

id_column = next(
    (
        normalized_columns[name]
        for name in ["employee_id", "employeeid", "emp_id"]
        if name in normalized_columns
    ),
    None
)

if id_column:
    duplicate_ids = int(df[id_column].duplicated().sum())
    missing_ids = int(df[id_column].isna().sum())

    print("\nEmployee ID column:", id_column)
    print("Duplicate employee IDs:", f"{duplicate_ids:,}")
    print("Missing employee IDs:", f"{missing_ids:,}")
else:
    print("\nEmployee ID column not detected.")
    print("Review the column names printed above.")

# 7. Numerical summary
print("\n[6] NUMERICAL SUMMARY")
print("-" * 45)
print(df.describe().round(2).to_string())

# 8. Create output folder
OUTPUT_DIR = PROJECT_DIR / "Data" / "Processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 9. Save data quality report
quality_report = pd.DataFrame({
    "Column": df.columns,
    "Data_Type": [str(dtype) for dtype in df.dtypes],
    "Missing_Values": df.isnull().sum().values,
    "Unique_Values": df.nunique(dropna=True).values
})

report_path = OUTPUT_DIR / "python_data_quality_report.csv"
quality_report.to_csv(report_path, index=False)

# 10. Save a numerical summary
summary_path = OUTPUT_DIR / "python_numerical_summary.csv"
df.describe().round(2).to_csv(summary_path)

print("\n[7] OUTPUT FILES")
print("-" * 45)
print("Data quality report:", report_path)
print("Numerical summary:", summary_path)

print("\n" + "=" * 60)
print("       PYTHON ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 60)
