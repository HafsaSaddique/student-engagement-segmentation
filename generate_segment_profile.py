
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Keep paths relative to this script's location.
PROJECT_DIR = Path(__file__).resolve().parent

DATA_PATH = PROJECT_DIR / "labeled_students.csv"
REPORT_PATH = PROJECT_DIR / "segment_profile_report.md"

GRADE_PLOT_PATH = PROJECT_DIR / "segment_grade.png"
ATTENDANCE_PLOT_PATH = PROJECT_DIR / "segment_attendance.png"

FEATURES = [
    "AttendanceRate",
    "AvgGrade",
    "Segment",
]


def main():
    # 1. Check that the input file exists.
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Labeled dataset not found: {DATA_PATH}"
        )

    # 2. Load the labeled student data.
    df = pd.read_csv(DATA_PATH)

    # Check required columns.
    missing_columns = [
        column for column in FEATURES
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("The labeled dataset is empty.")

    # Ensure the analysis columns are numeric.
    for column in FEATURES:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    if df[FEATURES].isnull().any().any():
        raise ValueError(
            "Missing or non-numeric values found "
            "in the required columns."
        )

    # 3. Calculate summary statistics for every segment.
    profile = (
        df.groupby("Segment")
        .agg(
            StudentCount=("Segment", "size"),
            MeanAttendanceRate=("AttendanceRate", "mean"),
            MeanAvgGrade=("AvgGrade", "mean"),
        )
        .reset_index()
        .sort_values("Segment")
    )

    # 4. Create a bar chart of average grade by segment.
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(8, 5))

    sns.barplot(
        data=df,
        x="Segment",
        y="AvgGrade",
        hue="Segment",
        estimator="mean",
        errorbar=None,
        legend=False,
    )

    plt.title("Average Grade by Student Segment")
    plt.xlabel("Student Segment")
    plt.ylabel("Mean Average Grade")
    plt.tight_layout()
    plt.savefig(GRADE_PLOT_PATH, dpi=300)
    plt.close()

    # 5. Create a box plot of attendance by segment.
    plt.figure(figsize=(8, 5))

    sns.boxplot(
        data=df,
        x="Segment",
        y="AttendanceRate",
        hue="Segment",
        legend=False,
    )

    plt.title("Attendance Rate Distribution by Segment")
    plt.xlabel("Student Segment")
    plt.ylabel("Attendance Rate")
    plt.tight_layout()
    plt.savefig(ATTENDANCE_PLOT_PATH, dpi=300)
    plt.close()

    # 6. Prepare a readable Markdown summary table.
    report_table = profile.copy()

    report_table["MeanAttendanceRate"] = (
        report_table["MeanAttendanceRate"].map(
            lambda value: f"{value:.3f}"
        )
    )

    report_table["MeanAvgGrade"] = (
        report_table["MeanAvgGrade"].map(
            lambda value: f"{value:.2f}"
        )
    )

    report_table = report_table.rename(
        columns={
            "Segment": "Segment",
            "StudentCount": "Student Count",
            "MeanAttendanceRate": "Mean Attendance Rate",
            "MeanAvgGrade": "Mean Average Grade",
        }
    )

    # Generate the Markdown table without tabulate.
    headers = list(report_table.columns)

    table_lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for _, row in report_table.iterrows():
        values = [str(value) for value in row]
        table_lines.append("| " + " | ".join(values) + " |")

    table_markdown = "\n".join(table_lines)

    # 7. Write the report and embed the saved PNG charts.
    report = f"""# Student Engagement Segment Profile Report

## 1. Introduction

This report summarizes the characteristics of student segments
created using K-Means clustering. The analysis uses attendance
rate, average grade, and the segment labels in the dataset.

The dataset contains **{len(df)} student records** across
**{df["Segment"].nunique()} segments**.

## 2. Segment Summary

The table below shows the number of students in each segment,
their mean attendance rate, and their mean average grade.

{table_markdown}

**Note:** The attendance rate is reported on the same scale as
the input dataset. If it is stored between 0 and 1, a value of
0.85 represents 85% attendance.

## 3. Average Grade by Segment

The bar chart compares the mean average grade across segments.

![Average grade by student segment](segment_grade.png)

## 4. Attendance Distribution by Segment

The box plot shows the distribution of attendance rates in each
segment. The median, spread, and potential outliers illustrate
how attendance varies within each group.

![Attendance rate distribution by segment](segment_attendance.png)

## 5. Interpretation

Use the table and charts together to compare the segments.
A higher mean grade or attendance rate describes the observed
dataset; it does not prove that a segment is inherently better
or that one factor caused another.

Segment numbers are identifiers, not performance rankings.

## 6. Limitations

The dataset may be synthetic, and the profiles have not been
validated against real student outcomes. These findings are
exploratory and should not be used to make decisions about real
students without further validation.

## 7. Generated Files

- `segment_grade.png` — average grade by segment.
- `segment_attendance.png` — attendance distribution by segment.
- `segment_profile_report.md` — this report.
"""

    # Save the Markdown report.
    REPORT_PATH.write_text(report, encoding="utf-8")

    # 8. Display the results.
    print("Segment profile report generated successfully!")
    print(f"Students analyzed: {len(df)}")
    print(f"Segments analyzed: {df['Segment'].nunique()}")

    print("\nSegment summary:")
    print(profile.to_string(index=False))

    print(f"\nGrade chart: {GRADE_PLOT_PATH}")
    print(f"Attendance chart: {ATTENDANCE_PLOT_PATH}")
    print(f"Markdown report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
