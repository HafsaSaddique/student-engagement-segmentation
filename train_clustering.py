
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Keep all paths relative to this script's location.
PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "data" / "cleaned" / "cleaned_student_data.csv"

PLOT_PATH = PROJECT_DIR / "elbow_plot.png"
LABELED_DATA_PATH = PROJECT_DIR / "labeled_students.csv"
MODEL_PATH = PROJECT_DIR / "kmeans_model.pkl"

# The three engagement features used for clustering.
FEATURES = [
    "AttendanceRate",
    "AvgGrade",
    "ExtracurricularCount",
]


def main():
    # 1. Load the cleaned student dataset.
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    missing_columns = [col for col in FEATURES if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if df.empty:
        raise ValueError("The cleaned dataset is empty.")

    # Ensure all clustering features are numeric.
    df[FEATURES] = df[FEATURES].apply(
        pd.to_numeric, errors="coerce"
    )

    if df[FEATURES].isnull().any().any():
        raise ValueError(
            "Missing or non-numeric values found in clustering features."
        )

    if len(df) < 8:
        raise ValueError("At least 8 student records are needed.")

    X = df[FEATURES]

    # 2. Standardize the features so different scales
    # do not unfairly influence the clustering.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. Run elbow analysis for k values from 2 through 8.
    k_values = list(range(2, 9))
    inertias = []

    for k in k_values:
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )
        model.fit(X_scaled)
        inertias.append(model.inertia_)

    # Use the maximum distance from the straight line
    # between the first and last elbow-plot points
    # as a reproducible estimate of the elbow.
    points = np.column_stack((k_values, inertias)).astype(float)

    # Normalize both axes before calculating distances.
    points[:, 0] = (
        (points[:, 0] - points[:, 0].min())
        / (points[:, 0].max() - points[:, 0].min())
    )
    points[:, 1] = (
        (points[:, 1] - points[:, 1].min())
        / (points[:, 1].max() - points[:, 1].min())
    )

    start = points[0]
    end = points[-1]
    line = end - start

    distances = np.abs(
        line[0] * (start[1] - points[:, 1])
        - line[1] * (start[0] - points[:, 0])
    ) / np.linalg.norm(line)

    chosen_k = k_values[int(np.argmax(distances))]

    # Save the elbow plot.
    plt.figure(figsize=(8, 5))
    plt.plot(k_values, inertias, marker="o")
    plt.axvline(
        chosen_k,
        linestyle="--",
        label=f"Selected k = {chosen_k}"
    )
    plt.title("Elbow Method for Student Engagement Clustering")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia (Within-Cluster Sum of Squares)")
    plt.xticks(k_values)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=300)
    plt.close()

    # 4. Train the final K-Means model using the selected k.
    kmeans = KMeans(
        n_clusters=chosen_k,
        random_state=42,
        n_init=10
    )
    segments = kmeans.fit_predict(X_scaled)

    # Add the segment identifier to each student's record.
    labeled_df = df.copy()
    labeled_df["Segment"] = segments
    labeled_df.to_csv(LABELED_DATA_PATH, index=False)

    # 5. Save both the scaler and trained model together.
    # The scaler is needed to transform future data consistently.
    joblib.dump(
        {
            "scaler": scaler,
            "kmeans": kmeans,
            "feature_columns": FEATURES,
            "chosen_k": chosen_k,
        },
        MODEL_PATH
    )

    print("Student clustering completed successfully!")
    print(f"Students processed: {len(labeled_df)}")
    print(f"Selected number of clusters (k): {chosen_k}")
    print(f"Segment counts:\n{labeled_df['Segment'].value_counts().sort_index()}")
    print(f"Elbow plot: {PLOT_PATH}")
    print(f"Labeled dataset: {LABELED_DATA_PATH}")
    print(f"Saved model and scaler: {MODEL_PATH}")


if __name__ == "__main__":
    main()
