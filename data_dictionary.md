\# Student Engagement Data Dictionary



\## Overview



This document describes the columns in the cleaned student engagement dataset.



The dataset contains synthetic student records generated for the Bright Future School project.



\## Columns



| Column | Data Type | Description | Calculation / Notes |

|---|---|---|---|

| StudentID | String | Unique identifier for each student | Generated as S001, S002, etc. |

| AttendanceRate | Float | Proportion of school days attended by the student | DaysPresent / DaysTotal |

| AvgGrade | Float | Average academic score across Math, English, and Science | Mean of MathScore, EnglishScore, and ScienceScore |

| ExtracurricularCount | Integer | Number of extracurricular activities/clubs | Number of activities separated by semicolon |



\## Missing Value Handling



Missing `DaysPresent` values were replaced using the median of the available `DaysPresent` values.



Missing `MathScore` values were replaced using the median of the available `MathScore` values.



Empty club values were treated as zero extracurricular activities.



After cleaning, the three engagement feature columns contain no missing values.



\## Dataset Size



The synthetic raw dataset contains 300 students.



The cleaned dataset contains 300 rows and 4 required columns.

