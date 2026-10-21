
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------- PAGE SETTINGS ----------------
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "labeled_students.csv"
GRADE_IMAGE = BASE_DIR / "segment_grade.png"
ATTENDANCE_IMAGE = BASE_DIR / "segment_attendance.png"

st.set_page_config(
    page_title="Student Engagement Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- DESIGN / STYLING ----------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }

    [data-testid="stSidebar"] {
        background-color: #101d36;
    }

    [data-testid="stSidebar"] * {
        color: #f4f7ff;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #17233b;
    }

    .hero {
        background: linear-gradient(115deg, #14213d, #284b82);
        padding: 27px 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: white;
        font-size: 30px;
        margin: 0 0 8px 0;
    }

    .hero p {
        color: #e0eaff;
        font-size: 15px;
        margin: 0;
    }

    .section-title {
        color: #172b4d;
        font-size: 21px;
        font-weight: 700;
        margin: 12px 0 4px 0;
    }

    .section-help {
        color: #68758a;
        font-size: 14px;
        margin-bottom: 14px;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e3e9f2;
        border-radius: 15px;
        padding: 19px 20px;
        min-height: 120px;
        box-shadow: 0 3px 12px rgba(31, 50, 81, 0.045);
    }

    .metric-label {
        color: #65738a;
        font-size: 14px;
        margin-bottom: 9px;
    }

    .metric-value {
        color: #172b4d;
        font-size: 29px;
        font-weight: 750;
    }

    .metric-note {
        color: #7d899b;
        font-size: 12px;
        margin-top: 5px;
    }

    .info-card {
        background: #ffffff;
        border: 1px solid #e3e9f2;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 12px;
    }

    div[data-testid="stPlotlyChart"] {
        background: #ffffff;
        border: 1px solid #e3e9f2;
        border-radius: 14px;
        padding: 8px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #e3e9f2;
        border-radius: 12px;
        overflow: hidden;
    }

    .footer {
        text-align: center;
        color: #8490a3;
        font-size: 12px;
        padding-top: 24px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    required_columns = [
        "Segment",
        "AttendanceRate",
        "AvgGrade",
        "ExtracurricularCount",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    for column in required_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=required_columns)

    if data.empty:
        raise ValueError("The dataset has no usable student records.")

    return data


if not DATA_FILE.exists():
    st.error(
        "Could not find labeled_students.csv. "
        "Please keep it in the same folder as this Python file."
    )
    st.stop()

try:
    df = load_data(DATA_FILE)
except Exception as error:
    st.error(f"Could not load the student dataset: {error}")
    st.stop()


# ---------------- HELPER FUNCTIONS ----------------
def format_attendance(value, series):
    """Show attendance as a percentage when stored as a 0–1 fraction."""
    if series.dropna().empty:
        return f"{value:.1f}"

    if series.max() <= 1.0:
        return f"{value * 100:.1f}%"

    return f"{value:.1f}%"


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height=350):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial, sans-serif",
            color="#34445e",
            size=12,
        ),
        margin=dict(l=18, r=18, t=55, b=25),
        title_font=dict(size=17, color="#172b4d"),
        legend_title_text="",
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#e3e9f2",
    )
    fig.update_yaxes(
        gridcolor="#edf1f7",
        zerolinecolor="#edf1f7",
    )
    return fig


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("# 🎓 Student Insights")
    st.caption("Student Engagement Segmentation")
    st.divider()

    st.markdown("### Navigation")
    page = st.radio(
        "Choose a page",
        ["Overview", "Segment Details", "Student Records"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### Segment Filter")

    segments = sorted(df["Segment"].unique().tolist())

    selected_segment = st.selectbox(
        "Select a student segment",
        options=segments,
        format_func=lambda value: (
            f"Segment {int(value)}"
            if float(value).is_integer()
            else f"Segment {value}"
        ),
        help="Choose a segment to view its summary and student records.",
    )

    st.caption(f"Available segments: {len(segments)}")
    st.caption(f"Records loaded: {len(df):,}")

    st.divider()
    st.caption("Student analytics • Local dashboard")


# ---------------- COMMON METRICS ----------------
total_students = len(df)
overall_grade = df["AvgGrade"].mean()
overall_attendance = df["AttendanceRate"].mean()

segment_df = df[df["Segment"] == selected_segment].copy()
segment_count = len(segment_df)

segment_grade = segment_df["AvgGrade"].mean()
segment_attendance = segment_df["AttendanceRate"].mean()
segment_extracurricular = segment_df["ExtracurricularCount"].mean()

segment_label = (
    str(int(selected_segment))
    if float(selected_segment).is_integer()
    else str(selected_segment)
)

attendance_display = format_attendance(
    overall_attendance, df["AttendanceRate"]
)
segment_attendance_display = format_attendance(
    segment_attendance, df["AttendanceRate"]
)


# ---------------- HEADER ----------------
st.markdown(
    """
    <div class="hero">
        <h1>Student Engagement Dashboard</h1>
        <p>
            Explore student attendance, academic performance, and engagement
            patterns through interactive analytics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ======================== OVERVIEW PAGE ========================
if page == "Overview":
    st.markdown('<div class="section-title">At a glance</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-help">'
        'A quick summary of all students in the dataset.'
        '</div>',
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        metric_card("Total Students", f"{total_students:,}",
                    "Records in the dataset")

    with k2:
        metric_card("Overall Average Grade", f"{overall_grade:.1f}",
                    "Average across all students")

    with k3:
        metric_card("Average Attendance", attendance_display,
                    "Across all students")

    with k4:
        metric_card("Student Segments", str(len(segments)),
                    "Groups identified by clustering")

    st.markdown("")
    st.markdown('<div class="section-title">Segment comparison</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-help">'
        'Compare average grades and attendance across student segments.'
        '</div>',
        unsafe_allow_html=True,
    )

    profile = (
        df.groupby("Segment")
        .agg(
            Students=("Segment", "size"),
            AverageGrade=("AvgGrade", "mean"),
            AverageAttendance=("AttendanceRate", "mean"),
        )
        .reset_index()
    )

    profile["SegmentLabel"] = profile["Segment"].apply(
        lambda value: f"Segment {int(value)}"
        if float(value).is_integer()
        else f"Segment {value}"
    )

    left, right = st.columns(2)

    with left:
        grade_fig = px.bar(
            profile,
            x="SegmentLabel",
            y="AverageGrade",
            color="SegmentLabel",
            title="Average Grade by Segment",
            labels={
                "SegmentLabel": "Student segment",
                "AverageGrade": "Average grade",
            },
            text_auto=".1f",
        )
        grade_fig.update_layout(showlegend=False)
        st.plotly_chart(
            style_chart(grade_fig),
            use_container_width=True,
        )

    with right:
        attendance_fig = px.bar(
            profile,
            x="SegmentLabel",
            y="AverageAttendance",
            color="SegmentLabel",
            title="Average Attendance by Segment",
            labels={
                "SegmentLabel": "Student segment",
                "AverageAttendance": "Average attendance",
            },
            text_auto=".1f",
        )
        attendance_fig.update_layout(showlegend=False)
        if df["AttendanceRate"].max() <= 1.0:
            attendance_fig.update_yaxes(tickformat=".0%")
        else:
            attendance_fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(
            style_chart(attendance_fig),
            use_container_width=True,
        )

    st.markdown('<div class="section-title">Report charts</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-help">'
        'Original charts generated for the segment profile report.'
        '</div>',
        unsafe_allow_html=True,
    )

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("**Average grade by segment**")
        if GRADE_IMAGE.exists():
            st.image(str(GRADE_IMAGE), use_container_width=True)
        else:
            st.info("segment_grade.png was not found.")

    with chart_right:
        st.markdown("**Attendance distribution by segment**")
        if ATTENDANCE_IMAGE.exists():
            st.image(str(ATTENDANCE_IMAGE), use_container_width=True)
        else:
            st.info("segment_attendance.png was not found.")


# ======================== SEGMENT DETAILS PAGE ========================
elif page == "Segment Details":
    st.markdown(
        f'<div class="section-title">Segment {segment_label} details</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-help">'
        'Use the sidebar selector to switch between segments.'
        '</div>',
        unsafe_allow_html=True,
    )

    if segment_df.empty:
        st.warning("There are no records for this segment.")
        st.stop()

    a, b, c, d = st.columns(4)

    with a:
        metric_card("Students", f"{segment_count:,}",
                    "Students in this segment")

    with b:
        metric_card("Average Grade", f"{segment_grade:.1f}",
                    "Academic performance")

    with c:
        metric_card("Average Attendance", segment_attendance_display,
                    "Attendance for this segment")

    with d:
        metric_card("Avg. Activities", f"{segment_extracurricular:.1f}",
                    "Extracurricular count")

    st.markdown("")
    st.markdown('<div class="section-title">Explore this segment</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-help">'
        'Charts below update according to your selected segment.'
        '</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        grade_hist = px.histogram(
            segment_df,
            x="AvgGrade",
            nbins=15,
            title="Grade Distribution",
            labels={"AvgGrade": "Average grade"},
            color_discrete_sequence=["#4776c5"],
        )
        grade_hist.update_traces(
            marker_line_color="white",
            marker_line_width=1,
        )
        st.plotly_chart(
            style_chart(grade_hist),
            use_container_width=True,
        )

    with right:
        attendance_box = px.box(
            segment_df,
            y="AttendanceRate",
            points="all",
            title="Attendance Distribution",
            labels={"AttendanceRate": "Attendance rate"},
            color_discrete_sequence=["#23a69a"],
        )
        if df["AttendanceRate"].max() <= 1.0:
            attendance_box.update_yaxes(tickformat=".0%")
        else:
            attendance_box.update_yaxes(ticksuffix="%")
        st.plotly_chart(
            style_chart(attendance_box),
            use_container_width=True,
        )

    st.markdown('<div class="section-title">Segment summary</div>',
                unsafe_allow_html=True)

    summary = pd.DataFrame(
        {
            "Metric": [
                "Number of students",
                "Average grade",
                "Average attendance",
                "Average extracurricular count",
            ],
            "Value": [
                segment_count,
                round(segment_grade, 2),
                segment_attendance_display,
                round(segment_extracurricular, 2),
            ],
        }
    )
    st.dataframe(summary, hide_index=True, use_container_width=True)


# ======================== STUDENT RECORDS PAGE ========================
else:
    st.markdown('<div class="section-title">Student records</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-help">'
        'View and download records for the selected segment.'
        '</div>',
        unsafe_allow_html=True,
    )

    show_all = st.checkbox(
        "Show all segments",
        value=False,
        help="When unchecked, only the selected segment is displayed.",
    )

    if show_all:
        records = df.copy()
    else:
        records = segment_df.copy()

    st.markdown(f"**Records displayed:** {len(records):,}")

    st.dataframe(
        records,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = records.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download displayed records (CSV)",
        data=csv_data,
        file_name=(
            "all_student_records.csv"
            if show_all
            else f"segment_{segment_label}_students.csv"
        ),
        mime="text/csv",
        use_container_width=False,
    )


# ---------------- FOOTER ----------------
st.markdown(
    """
    <div class="footer">
        Student Engagement Segmentation Project
        • Interactive analytics dashboard
    </div>
    """,
    unsafe_allow_html=True,
)
