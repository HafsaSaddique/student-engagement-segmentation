import random
import pandas as pd
import os

# Make the random data reproducible
random.seed(42)

# Create the output folder if it does not exist
os.makedirs("data/raw", exist_ok=True)

rows = []

# Generate data for 300 students
for i in range(1, 301):
    rows.append({
        "StudentID": f"S{i:03d}",
        "Grade": random.choice([6, 7, 8, 9, 10]),
        "DaysPresent": random.choice([None] + list(range(120, 181))),
        "DaysTotal": 180,
        "MathScore": random.choice([None] + list(range(35, 101))),
        "EnglishScore": random.randint(30, 100),
        "ScienceScore": random.randint(30, 100),
        "Clubs": random.choice([
            "",
            "Sports",
            "Debate",
            "Sports;Art",
            "Science;Debate",
            "Art"
        ]),
    })

# Convert the list into a DataFrame
df = pd.DataFrame(rows)

# Save the raw dataset
df.to_csv("data/raw/raw_student_data.csv", index=False)

print("raw_student_data.csv created successfully!")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")