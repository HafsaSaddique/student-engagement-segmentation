import os
import pandas as pd

# File paths
INPUT_FILE = "data/raw/raw_student_data.csv"
OUTPUT_FILE = "data/cleaned/cleaned_student_data.csv"


def prepare_student_data():
    # Load raw data
    df = pd.read_csv(INPUT_FILE)

    # Handle missing attendance values
    df["DaysPresent"] = df["DaysPresent"].fillna(
        df["DaysPresent"].median()
    )

    # Calculate attendance rate
    df["AttendanceRate"] = (
        df["DaysPresent"] / df["DaysTotal"]
    )

    # Handle missing Math scores
    df["MathScore"] = df["MathScore"].fillna(
        df["MathScore"].median()
    )

    # Calculate average grade
    df["AvgGrade"] = df[
        ["MathScore", "EnglishScore", "ScienceScore"]
    ].mean(axis=1)

    # Handle missing/empty clubs
    df["Clubs"] = df["Clubs"].fillna("")

    # Count extracurricular activities
    df["ExtracurricularCount"] = df["Clubs"].apply(
        lambda x: 0 if x == "" else len(x.split(";"))
    )

    # Select required columns
    cleaned_df = df[
        [
            "StudentID",
            "AttendanceRate",
            "AvgGrade",
            "ExtracurricularCount",
        ]
    ].copy()

    # Create output directory if needed
    os.makedirs("data/cleaned", exist_ok=True)

    # Save cleaned dataset
    cleaned_df.to_csv(OUTPUT_FILE, index=False)

    # Verify missing values
    missing_values = cleaned_df.isnull().sum().sum()

    if missing_values != 0:
        raise ValueError(
            "Cleaned dataset still contains missing values."
        )

    print("Student data preparation completed successfully!")
    print(f"Rows: {len(cleaned_df)}")
    print(f"Columns: {len(cleaned_df.columns)}")
    print(f"Output: {OUTPUT_FILE}")
    print("Missing values in cleaned data: 0")


if __name__ == "__main__":
    prepare_student_data()