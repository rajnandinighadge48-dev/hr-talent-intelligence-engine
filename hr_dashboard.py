
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# HR TALENT INTELLIGENCE ENGINE
# Premium Workforce Analytics Dashboard
# =========================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "Data" / "Raw" / "employees.csv"

st.set_page_config(
    page_title="HR Talent Intelligence Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- PREMIUM DESIGN --------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}
.stApp {
    background: #0B1120;
    color: #E8EEF8;
}
[data-testid="stSidebar"] {
    background: #111C30;
    border-right: 1px solid #263650;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}
h1, h2, h3 {
    color: #F4F7FC !important;
    letter-spacing: -0.5px;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #17263E, #111B2D);
    border: 1px solid #2A3C58;
    border-radius: 15px;
    padding: 18px 20px;
}
[data-testid="stMetricLabel"] {
    color: #AAB9D0;
    font-size: 0.88rem;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF;
    font-weight: 800;
}
div[data-testid="stPlotlyChart"] {
    background: #111C30;
    border: 1px solid #263650;
    border-radius: 15px;
    padding: 10px 8px 0 8px;
}
[data-testid="stDataFrame"] {
    border: 1px solid #263650;
    border-radius: 12px;
}
hr {
    border-color: #263650;
}
.small-muted {
    color: #AAB9D0;
    font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------- DATA LOADING --------------------

@st.cache_data(show_spinner="Loading employee dataset...")
def load_data(path, modified_time):
    data = pd.read_csv(path, low_memory=False)
    data.columns = data.columns.astype(str).str.strip()

    required = [
        "Employee_ID",
        "Department",
        "Annual_Salary_INR",
        "Tenure_Years",
        "Engagement_Score",
        "Performance_Rating",
        "Attrition",
    ]

    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(
            f"Required columns missing: {missing}. "
            f"Available columns: {data.columns.tolist()}"
        )

    # Convert numeric fields safely
    for col in [
        "Annual_Salary_INR",
        "Tenure_Years",
        "Engagement_Score",
        "Performance_Rating",
    ]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # Normalize department labels
    data["Department"] = (
        data["Department"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
        .fillna("Unknown")
    )

    # Normalize attrition without guessing unknown labels
    raw_attrition = (
        data["Attrition"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    yes_values = {"yes", "y", "true", "1"}
    no_values = {"no", "n", "false", "0"}

    data["Employee_Left"] = raw_attrition.isin(yes_values).astype(int)

    # Keep only recognized Yes/No records for attrition calculations
    data["Attrition_Known"] = raw_attrition.isin(
        yes_values | no_values
    )

    return data


st.sidebar.title("📊 Talent Intelligence")
st.sidebar.caption("WORKFORCE ANALYTICS")

if not DATA_FILE.exists():
    st.error("The employee CSV file could not be found.")
    st.code(str(DATA_FILE))
    st.info(
        "Check that employees.csv exists in "
        "Data/Raw inside your project folder."
    )
    st.stop()

try:
    df = load_data(str(DATA_FILE), DATA_FILE.stat().st_mtime)
except Exception as error:
    st.error(f"Could not load employee data: {error}")
    st.stop()

if df.empty:
    st.error("The employee dataset is empty.")
    st.stop()

# -------------------- HEADER --------------------

st.markdown("# HR Talent Intelligence Engine")
st.markdown(
    '<div class="small-muted">'
    'Workforce intelligence  /  Attrition analytics  /  '
    'Compensation insights'
    '</div>',
    unsafe_allow_html=True,
)
st.write("")

header_a, header_b = st.columns([3, 1])
with header_a:
    st.caption("EXECUTIVE WORKFORCE OVERVIEW")
with header_b:
    st.caption(f"Source records: {len(df):,}")

st.divider()

# -------------------- SIDEBAR FILTERS --------------------

st.sidebar.subheader("Dashboard Filters")

department_options = sorted(df["Department"].unique().tolist())

selected_departments = st.sidebar.multiselect(
    "Department",
    options=department_options,
    default=department_options,
)

filtered = df[
    df["Department"].isin(selected_departments)
].copy()

if filtered.empty:
    st.warning("Select at least one department to view analytics.")
    st.stop()

st.sidebar.caption(f"Filtered records: {len(filtered):,}")
# -------------------- EXPORT FILTERED DATA --------------------

st.sidebar.divider()
st.sidebar.subheader("Export Report")

@st.cache_data
def convert_to_csv(data):
    return data.to_csv(index=False).encode("utf-8-sig")

csv_data = convert_to_csv(filtered)

st.sidebar.download_button(
    label="⬇️ Download Filtered CSV",
    data=csv_data,
    file_name="HR_Talent_Intelligence_Report.csv",
    mime="text/csv",
    key="download_filtered_csv",
    use_container_width=True,
)

# -------------------- KPI METRICS --------------------

st.subheader("Workforce Overview")

known_attrition = filtered[filtered["Attrition_Known"]].copy()

total_records = len(filtered)
employees_left = int(known_attrition["Employee_Left"].sum())
active_employees = len(known_attrition) - employees_left

attrition_rate = (
    employees_left / len(known_attrition) * 100
    if len(known_attrition) else None
)

# Count unique IDs for the employee KPI
unique_employee_count = filtered["Employee_ID"].nunique()

salary_avg = filtered["Annual_Salary_INR"].mean()
experience_avg = filtered["Tenure_Years"].mean()

k1, k2, k3, k4 = st.columns(4)

k1.metric("Unique Employees", f"{unique_employee_count:,}")
k2.metric(
    "Attrition Rate",
    f"{attrition_rate:.2f}%" if attrition_rate is not None else "N/A",
)
k3.metric(
    "Average Annual Salary",
    f"₹{salary_avg:,.0f}" if pd.notna(salary_avg) else "N/A",
)
k4.metric(
    "Average Tenure",
    f"{experience_avg:.1f} years"
    if pd.notna(experience_avg) else "N/A",
)

st.caption(
    f"Records in selection: {total_records:,} · "
    f"Known attrition records: {len(known_attrition):,} · "
    f"Active/left counts exclude unrecognized attrition labels."
)

st.divider()

# -------------------- CHART HELPERS --------------------

COLORS = {
    "blue": "#60A5FA",
    "purple": "#A78BFA",
    "teal": "#2DD4BF",
    "orange": "#FBBF24",
    "red": "#FB7185",
}

def style_chart(fig, height=360):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color="#E8EEF8",
            size=12,
        ),
        margin=dict(l=20, r=20, t=65, b=35),
        title=dict(
            x=0.03,
            xanchor="left",
            font=dict(size=17, color="#F4F7FC"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#34445D",
        tickfont=dict(color="#B9C7DA"),
    )
    fig.update_yaxes(
        gridcolor="#263650",
        zerolinecolor="#34445D",
        tickfont=dict(color="#B9C7DA"),
    )
    return fig


def attrition_summary(data, group_col):
    valid = data[data["Attrition_Known"]].copy()

    if valid.empty:
        return pd.DataFrame(
            columns=[group_col, "Total_Employees",
                     "Employees_Left", "Attrition_Rate"]
        )

    result = (
        valid.groupby(group_col, dropna=False)
        .agg(
            Total_Employees=("Employee_Left", "size"),
            Employees_Left=("Employee_Left", "sum"),
        )
        .reset_index()
    )

    result["Attrition_Rate"] = (
        result["Employees_Left"]
        / result["Total_Employees"]
        * 100
    )

    return result


# -------------------- DEPARTMENT ATTRITION --------------------

st.subheader("Department-wise Attrition")

left, right = st.columns(2)

with left:
    dept = attrition_summary(filtered, "Department")
    dept = dept.sort_values("Attrition_Rate", ascending=False)

    if not dept.empty:
        fig = px.bar(
            dept,
            x="Department",
            y="Attrition_Rate",
            text="Attrition_Rate",
            color="Attrition_Rate",
            color_continuous_scale=["#2DD4BF", "#60A5FA", "#A78BFA"],
            labels={"Attrition_Rate": "Attrition Rate (%)"},
            title="Attrition Rate by Department",
        )
        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False,
        )
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis_title="Attrition Rate (%)",
            xaxis_title="Department",
        )
        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )
    else:
        st.info("No recognized attrition records for this selection.")

with right:
    if not dept.empty:
        fig = px.bar(
            dept.sort_values("Employees_Left", ascending=True),
            x="Employees_Left",
            y="Department",
            orientation="h",
            text="Employees_Left",
            color="Employees_Left",
            color_continuous_scale=["#60A5FA", "#A78BFA"],
            title="Employees Left by Department",
            labels={"Employees_Left": "Employees Left"},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Employees Left",
            yaxis_title="",
        )
        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )
    else:
        st.info("No department attrition data available.")

st.divider()

# -------------------- TENURE ATTRITION --------------------

st.subheader("Attrition by Tenure")

tenure_df = filtered.dropna(subset=["Tenure_Years"]).copy()
tenure_df = tenure_df[tenure_df["Attrition_Known"]].copy()

tenure_bins = [-0.001, 1, 3, 5, 10, float("inf")]
tenure_labels = [
    "0–1 years", "1–3 years", "3–5 years",
    "5–10 years", "10+ years"
]

tenure_df["Tenure_Group"] = pd.cut(
    tenure_df["Tenure_Years"],
    bins=tenure_bins,
    labels=tenure_labels,
    right=True,
    include_lowest=True,
)

tenure = attrition_summary(tenure_df, "Tenure_Group")

# Preserve the intended chronological order
if not tenure.empty:
    tenure["Tenure_Group"] = pd.Categorical(
        tenure["Tenure_Group"],
        categories=tenure_labels,
        ordered=True,
    )
    tenure = tenure.sort_values("Tenure_Group")

    fig = px.bar(
        tenure,
        x="Tenure_Group",
        y="Attrition_Rate",
        text="Attrition_Rate",
        color="Attrition_Rate",
        color_continuous_scale=["#2DD4BF", "#FBBF24", "#FB7185"],
        title="Attrition Rate Across Tenure Groups",
        labels={
            "Tenure_Group": "Tenure",
            "Attrition_Rate": "Attrition Rate (%)",
        },
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis_title="Attrition Rate (%)",
        xaxis_title="Tenure Group",
    )
    st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("Tenure attrition chart needs valid tenure and attrition data.")

st.divider()

# -------------------- SALARY COMPARISON --------------------

st.subheader("Compensation Intelligence")

left, right = st.columns(2)

with left:
    salary_df = filtered.dropna(
        subset=["Annual_Salary_INR"]
    ).copy()
    salary_df = salary_df[salary_df["Attrition_Known"]]

    if not salary_df.empty:
        salary_df["Employee_Status"] = salary_df[
            "Employee_Left"
        ].map({0: "Stayed", 1: "Left"})

        salary_summary = (
            salary_df.groupby("Employee_Status")["Annual_Salary_INR"]
            .agg(["mean", "count"])
            .reindex(["Stayed", "Left"])
            .dropna(subset=["mean"])
            .reset_index()
        )
        salary_summary.columns = [
            "Employee_Status", "Average_Salary_INR", "Employee_Count"
        ]

        fig = px.bar(
            salary_summary,
            x="Employee_Status",
            y="Average_Salary_INR",
            text="Average_Salary_INR",
            color="Employee_Status",
            color_discrete_map={
                "Stayed": COLORS["teal"],
                "Left": COLORS["red"],
            },
            title="Average Annual Salary: Stayed vs Left",
            labels={
                "Employee_Status": "Employee Status",
                "Average_Salary_INR": "Average Salary (INR)",
            },
        )
        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig.update_layout(
            showlegend=False,
            yaxis_title="Average Salary (₹)",
            xaxis_title="",
            yaxis_tickprefix="₹",
            yaxis_tickformat=",",
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No valid salary and attrition values available.")

with right:
    if not salary_df.empty:
        salary_dept = (
            salary_df.groupby("Department")["Annual_Salary_INR"]
            .mean()
            .sort_values()
            .reset_index()
        )

        fig = px.bar(
            salary_dept,
            x="Annual_Salary_INR",
            y="Department",
            orientation="h",
            color="Annual_Salary_INR",
            color_continuous_scale=["#60A5FA", "#A78BFA"],
            title="Average Salary by Department",
            labels={
                "Annual_Salary_INR": "Average Salary (INR)",
                "Department": "",
            },
        )
        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_tickprefix="₹",
            xaxis_tickformat=",",
            xaxis_title="Average Salary (₹)",
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No salary data available.")

st.divider()

# -------------------- ENGAGEMENT ATTRITION --------------------

st.subheader("Engagement Intelligence")

engagement_df = filtered.dropna(
    subset=["Engagement_Score"]
).copy()
engagement_df = engagement_df[engagement_df["Attrition_Known"]]

if not engagement_df.empty:
    # Round to one decimal to reduce noisy score variations
    engagement_df["Engagement_Group"] = (
        engagement_df["Engagement_Score"].round(1)
    )

    engagement = attrition_summary(
        engagement_df,
        "Engagement_Group",
    ).sort_values("Engagement_Group")

    fig = px.line(
        engagement,
        x="Engagement_Group",
        y="Attrition_Rate",
        markers=True,
        title="Attrition Rate by Engagement Score",
        labels={
            "Engagement_Group": "Engagement Score",
            "Attrition_Rate": "Attrition Rate (%)",
        },
        hover_data=["Total_Employees", "Employees_Left"],
    )
    fig.update_traces(
        line=dict(color=COLORS["purple"], width=3),
        marker=dict(size=8, color=COLORS["teal"]),
        hovertemplate=(
            "Engagement: %{x}<br>"
            "Attrition rate: %{y:.2f}%<extra></extra>"
        ),
    )
    st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No valid engagement and attrition values available.")

st.divider()

# -------------------- PERFORMANCE ATTRITION --------------------

st.subheader("Performance Intelligence")

performance_df = filtered.dropna(
    subset=["Performance_Rating"]
).copy()
performance_df = performance_df[performance_df["Attrition_Known"]]

if not performance_df.empty:
    performance = attrition_summary(
        performance_df,
        "Performance_Rating",
    ).sort_values("Performance_Rating")

    fig = px.bar(
        performance,
        x="Performance_Rating",
        y="Attrition_Rate",
        text="Attrition_Rate",
        color="Attrition_Rate",
        color_continuous_scale=["#2DD4BF", "#60A5FA", "#FB7185"],
        title="Attrition Rate by Performance Rating",
        labels={
            "Performance_Rating": "Performance Rating",
            "Attrition_Rate": "Attrition Rate (%)",
        },
        hover_data=["Total_Employees", "Employees_Left"],
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Performance Rating",
        yaxis_title="Attrition Rate (%)",
    )
    st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No valid performance and attrition values available.")

# -------------------- DEPARTMENT SUMMARY --------------------

st.divider()
st.subheader("Department Summary")

dept_summary = attrition_summary(filtered, "Department")

if not dept_summary.empty:
    dept_summary["Average_Salary_INR"] = (
        filtered.groupby("Department")["Annual_Salary_INR"]
        .mean()
        .reindex(dept_summary["Department"])
        .to_numpy()
    )

    dept_summary["Average_Tenure_Years"] = (
        filtered.groupby("Department")["Tenure_Years"]
        .mean()
        .reindex(dept_summary["Department"])
        .to_numpy()
    )

    dept_summary = dept_summary.rename(
        columns={
            "Total_Employees": "Employees",
            "Employees_Left": "Employees Left",
            "Attrition_Rate": "Attrition Rate (%)",
            "Average_Salary_INR": "Average Salary (INR)",
            "Average_Tenure_Years": "Average Tenure (Years)",
        }
    )

    dept_summary["Attrition Rate (%)"] = (
        dept_summary["Attrition Rate (%)"].round(2)
    )
    dept_summary["Average Salary (INR)"] = (
        dept_summary["Average Salary (INR)"].round(0)
    )
    dept_summary["Average Tenure (Years)"] = (
        dept_summary["Average Tenure (Years)"].round(2)
    )

    dept_summary = dept_summary.sort_values(
        "Attrition Rate (%)",
        ascending=False,
    )

    st.dataframe(
        dept_summary,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Department summary unavailable.")

# -------------------- DATA QUALITY --------------------

with st.expander("Data Quality & Dataset Preview"):
    unknown_attrition = int((~df["Attrition_Known"]).sum())
    missing_ids = int(df["Employee_ID"].isna().sum())
    duplicate_ids = int(
        df["Employee_ID"].duplicated().sum()
    )

    q1, q2, q3 = st.columns(3)
    q1.metric("Unrecognized Attrition Labels", f"{unknown_attrition:,}")
    q2.metric("Missing Employee IDs", f"{missing_ids:,}")
    q3.metric("Duplicate Employee IDs", f"{duplicate_ids:,}")

    st.caption("Detected source columns")
    st.write(df.columns.tolist())

    st.caption("First 100 source records")
    st.dataframe(df.head(100), use_container_width=True)

st.caption(
    "HR Talent Intelligence Engine | "
    "Observed associations do not establish causes of attrition."
)
