"""
Attendify – Student Attendance Analysis
Analyze Attendance, Academic Performance and Student Trends
Built with Python, Streamlit, Pandas, NumPy, and Matplotlib.
"""

import os
import io
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from modules.data_processing import (
    REQUIRED_COLUMNS,
    load_dataset,
    save_dataset,
    add_student_record,
    clean_dataset,
    categorize_attendance,
    calculate_numpy_statistics,
    get_attendance_category_counts,
    get_below_threshold_students,
    get_excellent_students
)
from modules.regression import (
    perform_linear_regression,
    predict_final_marks
)
from modules.visualizations import (
    create_attendance_distribution_chart,
    create_regression_scatter_chart,
    create_study_hours_vs_marks_chart,
    create_avg_marks_by_category_chart,
    create_top_students_attendance_chart
)

# -----------------------------------------------------------------------------
# App Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Attendify – Student Attendance Analysis",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for academic, clean, professional styling
st.markdown("""
<style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 14px 18px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
    }
    /* Section callout cards */
    .info-card {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 16px;
        color: #1E40AF;
        font-size: 0.95rem;
    }
    .warning-card {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 16px;
        color: #991B1B;
        font-size: 0.95rem;
    }
    .equation-box {
        background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%);
        color: #FFFFFF !important;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-family: 'Courier New', monospace;
        font-size: 1.4rem;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(30, 58, 138, 0.2);
        margin: 15px 0;
    }
    .academic-header {
        margin-bottom: 4px;
        color: #0F172A;
    }
    .academic-subtitle {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

DEFAULT_CSV_PATH = os.path.join(os.path.dirname(__file__), 'attendance.csv')


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if 'current_df' not in st.session_state:
    if os.path.exists(DEFAULT_CSV_PATH):
        df_init, err = load_dataset(DEFAULT_CSV_PATH)
        if df_init is not None:
            st.session_state.current_df = df_init
        else:
            st.session_state.current_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    else:
        st.session_state.current_df = pd.DataFrame(columns=REQUIRED_COLUMNS)

if 'cleaning_report' not in st.session_state:
    st.session_state.cleaning_report = None


# -----------------------------------------------------------------------------
# Sidebar Navigation & Dataset Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    # Logo & Title
    logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
    if os.path.exists(logo_path):
        st.image(logo_path, width=72)
    st.title("Attendify")
    st.caption("Student Attendance Analysis")
    st.markdown("---")

    # Navigation menu
    menu_options = [
        "1. Dashboard",
        "2. Add Student",
        "3. Student Records",
        "4. Data Cleaning",
        "5. Attendance Analysis",
        "6. Regression Analysis",
        "7. Visualizations",
        "8. Findings & Summary"
    ]
    selected_page = st.radio("Navigation", menu_options, index=0)

    st.markdown("---")
    st.subheader("📁 Dataset Controls")

    # CSV Upload
    uploaded_file = st.file_uploader("Upload custom CSV", type=['csv'], help="Upload a student attendance CSV conforming to the required columns.")
    if uploaded_file is not None:
        try:
            uploaded_df, err_msg = load_dataset(uploaded_file)
            if err_msg:
                st.error(f"⚠ {err_msg}")
            else:
                st.session_state.current_df = uploaded_df
                st.success("Custom CSV loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load file: {e}")

    # Reset to default CSV
    if st.button("🔄 Reset to Default Dataset", use_container_width=True):
        if os.path.exists(DEFAULT_CSV_PATH):
            df_def, err = load_dataset(DEFAULT_CSV_PATH)
            if df_def is not None:
                st.session_state.current_df = df_def
                st.session_state.cleaning_report = None
                st.success("Reset to default attendance.csv")
                st.rerun()

    st.markdown("---")
    st.caption("Developed for Academic Data Analysis Coursework (2nd Year CSE).")


# -----------------------------------------------------------------------------
# Helper: Verify Active Data
# -----------------------------------------------------------------------------
df = st.session_state.current_df
has_data = df is not None and not df.empty


# =============================================================================
# 1. DASHBOARD PAGE
# =============================================================================
if selected_page == "1. Dashboard":
    st.markdown("<h1 class='academic-header'>Attendify – Student Attendance Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<div class='academic-subtitle'>Analyze Attendance, Academic Performance and Student Trends</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-card'>
        <strong>Purpose:</strong> Monitor student attendance and understand its relationship with academic performance.
        This academic dashboard provides instant KPI metrics, data audit indicators, and cohort breakdowns.
    </div>
    """, unsafe_allow_html=True)

    if not has_data:
        st.warning("⚠ No data available in the dataset. Please add records or upload a valid CSV file.")
    else:
        # Calculate dashboard metrics
        stats = calculate_numpy_statistics(df)
        total_students = len(df)
        avg_att = stats.get('mean_attendance', 0.0)
        avg_marks = stats.get('mean_final_marks', 0.0)
        below_75_df = get_below_threshold_students(df, 75.0)
        below_75_count = len(below_75_df)
        max_att = stats.get('max_attendance', 0.0)
        min_att = stats.get('min_attendance', 0.0)

        # KPI Cards (Row 1)
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Total Students", f"{total_students}")
        with kpi2:
            st.metric("Average Attendance", f"{avg_att:.1f}%")
        with kpi3:
            st.metric("Average Final Marks", f"{avg_marks:.1f}")

        # KPI Cards (Row 2)
        kpi4, kpi5, kpi6 = st.columns(3)
        with kpi4:
            st.metric(
                "Students Below 75%",
                f"{below_75_count}",
                delta=f"-{round((below_75_count / total_students) * 100, 1)}% of cohort" if total_students > 0 else "0%",
                delta_color="inverse"
            )
        with kpi5:
            st.metric("Highest Attendance", f"{max_att:.1f}%")
        with kpi6:
            st.metric("Lowest Attendance", f"{min_att:.1f}%")

        st.markdown("<br>", unsafe_allow_html=True)

        # Warning Alert if students below 75%
        if below_75_count > 0:
            st.markdown(f"""
            <div class='warning-card'>
                <strong>⚠ Attention:</strong> <strong>{below_75_count} student(s)</strong> have an attendance percentage 
                below the university mandatory threshold of <strong>75%</strong>. Review the Student Records or Attendance Analysis page for counseling.
            </div>
            """, unsafe_allow_html=True)

        # Overview Layout: Category Summary & Quick Chart
        c_left, c_right = st.columns([1, 1])

        with c_left:
            st.subheader("📊 Attendance Category Breakdown")
            cat_counts = get_attendance_category_counts(df)
            cat_summary_df = pd.DataFrame({
                "Category": ["Excellent (90-100%)", "Good (75-89%)", "Average (60-74%)", "Poor (<60%)"],
                "Student Count": [
                    cat_counts.get("Excellent", 0),
                    cat_counts.get("Good", 0),
                    cat_counts.get("Average", 0),
                    cat_counts.get("Poor", 0)
                ],
                "Percentage": [
                    f"{(cat_counts.get('Excellent', 0)/total_students*100):.1f}%",
                    f"{(cat_counts.get('Good', 0)/total_students*100):.1f}%",
                    f"{(cat_counts.get('Average', 0)/total_students*100):.1f}%",
                    f"{(cat_counts.get('Poor', 0)/total_students*100):.1f}%"
                ]
            })
            st.dataframe(cat_summary_df, use_container_width=True, hide_index=True)

        with c_right:
            st.subheader("📈 Quick Distribution Overview")
            fig = create_attendance_distribution_chart(df)
            st.pyplot(fig)
            plt.close(fig)

        # Recent Records Preview
        st.subheader("📋 Recent Student Records")
        display_cols = ['Student_ID', 'Student_Name', 'Department', 'Year', 'Classes_Attended', 'Total_Classes', 'Attendance', 'Final_Marks', 'Attendance_Category']
        st.dataframe(df[display_cols].tail(6), use_container_width=True, hide_index=True)


# =============================================================================
# 2. ADD STUDENT PAGE
# =============================================================================
elif selected_page == "2. Add Student":
    st.markdown("<h1 class='academic-header'>Add New Student Record</h1>", unsafe_allow_html=True)
    st.markdown("<div class='academic-subtitle'>Enroll a student and record attendance and academic marks</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='info-card'>
        <strong>Automatic Attendance Calculation:</strong> 
        Attendance is computed automatically as <code>(Classes Attended / Total Classes) × 100</code>.
        Manual entry of attendance percentage is disabled to guarantee mathematical integrity.
    </div>
    """, unsafe_allow_html=True)

    with st.form("add_student_form", clear_on_submit=False):
        f_col1, f_col2 = st.columns(2)

        with f_col1:
            student_id = st.text_input("Student ID *", placeholder="e.g. S021").strip().upper()
            student_name = st.text_input("Student Name *", placeholder="e.g. Ramesh Kumar").strip()
            department = st.selectbox("Department *", ["CSE", "ECE", "IT", "MECH", "CIVIL", "EEE", "AIDS"])
            year = st.selectbox("Academic Year *", [1, 2, 3, 4], index=1)
            study_hours = st.number_input("Weekly Independent Study Hours *", min_value=0.0, max_value=80.0, value=6.0, step=0.5)

        with f_col2:
            total_classes = st.number_input("Total Scheduled Classes *", min_value=1, max_value=200, value=50, step=1)
            classes_attended = st.number_input("Classes Attended *", min_value=0, max_value=200, value=40, step=1)
            
            # Live preview of calculated attendance
            calc_preview = round((classes_attended / total_classes * 100), 2) if total_classes > 0 else 0.0
            st.info(f"Calculated Attendance: **{calc_preview:.2f}%** ({categorize_attendance(calc_preview)})")

            internal_marks = st.number_input("Internal Marks (0 - 100) *", min_value=0.0, max_value=100.0, value=75.0, step=0.5)
            final_marks = st.number_input("Final Marks (0 - 100) *", min_value=0.0, max_value=100.0, value=78.0, step=0.5)

        submitted = st.form_submit_button("➕ Submit & Add Student", use_container_width=True)

        if submitted:
            # Prepare payload
            student_dict = {
                'Student_ID': student_id,
                'Student_Name': student_name,
                'Department': department,
                'Year': year,
                'Total_Classes': total_classes,
                'Classes_Attended': classes_attended,
                'Study_Hours': study_hours,
                'Internal_Marks': internal_marks,
                'Final_Marks': final_marks
            }

            updated_df, success, message = add_student_record(st.session_state.current_df, student_dict)

            if success:
                st.session_state.current_df = updated_df
                # Persist to default attendance.csv
                save_dataset(updated_df, DEFAULT_CSV_PATH)
                st.success("Student added successfully!")
                st.balloons()

                # Show preview card
                st.markdown("### Added Record Summary")
                new_entry = updated_df[updated_df['Student_ID'] == student_id]
                st.dataframe(new_entry, use_container_width=True, hide_index=True)
            else:
                st.error(f"⚠ {message}")


# =============================================================================
# 3. STUDENT RECORDS PAGE
# =============================================================================
elif selected_page == "3. Student Records":
    st.markdown("<h1 class='academic-header'>Student Records Directory</h1>", unsafe_allow_html=True)
    st.markdown("<div class='academic-subtitle'>Interactive dataset browser, filtering, search, and CSV export</div>", unsafe_allow_html=True)

    if not has_data:
        st.warning("⚠ No records available in dataset.")
    else:
        # Action Toolbar
        tb_col1, tb_col2, tb_col3 = st.columns([2, 1, 1])
        with tb_col1:
            search_query = st.text_input("🔍 Search by Student ID or Name", placeholder="Type ID or Name...")
        with tb_col2:
            st.write("")
            st.write("")
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        with tb_col3:
            st.write("")
            st.write("")
            csv_buffer = io.StringIO()
            cols_to_export = [c for c in REQUIRED_COLUMNS if c in df.columns]
            df[cols_to_export].to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_buffer.getvalue(),
                file_name="student_attendance_records.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Filters Row
        f1, f2, f3 = st.columns(3)
        with f1:
            all_depts = sorted(list(df['Department'].dropna().unique()))
            selected_depts = st.multiselect("Filter by Department", all_depts, default=all_depts)
        with f2:
            all_years = sorted(list(df['Year'].dropna().unique()))
            selected_years = st.multiselect("Filter by Year", all_years, default=all_years)
        with f3:
            att_range = st.slider("Attendance Percentage Range", 0.0, 100.0, (0.0, 100.0), step=1.0)

        # Apply Filters
        filtered_df = df.copy()
        if selected_depts:
            filtered_df = filtered_df[filtered_df['Department'].isin(selected_depts)]
        if selected_years:
            filtered_df = filtered_df[filtered_df['Year'].isin(selected_years)]
        filtered_df = filtered_df[
            (filtered_df['Attendance'] >= att_range[0]) & (filtered_df['Attendance'] <= att_range[1])
        ]
        if search_query.strip():
            query = search_query.strip().lower()
            filtered_df = filtered_df[
                filtered_df['Student_ID'].astype(str).str.lower().str.contains(query) |
                filtered_df['Student_Name'].astype(str).str.lower().str.contains(query)
            ]

        st.caption(f"Showing **{len(filtered_df)}** of **{len(df)}** student records.")

        # Highlighting function for Pandas Styler (< 75% attendance)
        def highlight_low_attendance(row):
            if row['Attendance'] < 75.0:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: bold;'] * len(row)
            return [''] * len(row)

        display_cols = [
            'Student_ID', 'Student_Name', 'Department', 'Year',
            'Total_Classes', 'Classes_Attended', 'Attendance',
            'Study_Hours', 'Internal_Marks', 'Final_Marks', 'Attendance_Category'
        ]
        valid_display_cols = [c for c in display_cols if c in filtered_df.columns]

        styled_df = filtered_df[valid_display_cols].style.apply(highlight_low_attendance, axis=1).format({
            'Attendance': '{:.2f}%',
            'Study_Hours': '{:.1f}',
            'Internal_Marks': '{:.1f}',
            'Final_Marks': '{:.1f}'
        })

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        st.caption("🔴 Red highlighted rows indicate students with attendance strictly below 75% threshold.")


# =============================================================================
# 4. DATA CLEANING PAGE
# =============================================================================
elif selected_page == "4. Data Cleaning":
    st.markdown("<h1 class='academic-header'>Data Cleaning & Preprocessing (Pandas)</h1>", unsafe_allow_html=True)
    st.markdown("<div class='academic-subtitle'>Demonstrating Pandas data auditing, missing value imputation, duplicate removal, and type casting</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='info-card'>
        <strong>Pandas Concept Showcase:</strong>
        This module verifies data integrity. It detects missing values using <code>df.isnull().sum()</code>, 
        imputes missing numeric values using column mean <code>df[col].fillna(df[col].mean())</code>,
        imputes categorical values using mode, removes duplicate records via <code>df.drop_duplicates()</code>,
        and enforces boundary constraints.
    </div>
    """, unsafe_allow_html=True)

    if not has_data:
        st.warning("⚠ No data to clean.")
    else:
        # Action controls for viva demonstration
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🧹 Clean Active Dataset Now", type="primary", use_container_width=True):
                cleaned_df, report = clean_dataset(df)
                st.session_state.current_df = cleaned_df
                st.session_state.cleaning_report = report
                save_dataset(cleaned_df, DEFAULT_CSV_PATH)
                st.success("Dataset successfully cleaned and persisted!")
                st.rerun()

        with btn_col2:
            if st.button("🧪 Simulate Dirty Data (for Viva Demo)", use_container_width=True):
                dirty_df = df.copy()
                if len(dirty_df) > 2:
                    dirty_df.loc[1, 'Study_Hours'] = np.nan
                    dirty_df.loc[2, 'Internal_Marks'] = np.nan
                    dup_row = dirty_df.iloc[[0]].copy()
                    dirty_df = pd.concat([dirty_df, dup_row], ignore_index=True)
                st.session_state.current_df = dirty_df
                st.session_state.cleaning_report = None
                st.warning("Introduced simulated missing values and duplicate rows. Click 'Clean Active Dataset Now' to observe cleaning.")
                st.rerun()

        # Audit Inspection
        st.subheader("1. Missing Values Audit (df.isnull().sum())")
        null_counts = df.isnull().sum()
        null_df = pd.DataFrame({
            "Column Name": null_counts.index,
            "Missing Count": null_counts.values,
            "Percentage Missing": [f"{(v / len(df) * 100):.1f}%" for v in null_counts.values],
            "Data Type": [str(df[c].dtype) for c in null_counts.index]
        })
        st.dataframe(null_df, use_container_width=True, hide_index=True)

        # Duplicates Audit
        st.subheader("2. Duplicate Records Audit")
        dup_count = int(df.duplicated(subset=['Student_ID']).sum()) if 'Student_ID' in df.columns else int(df.duplicated().sum())
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.metric("Detected Duplicate Records", f"{dup_count}")
        with d_col2:
            st.metric("Total Missing Cells", f"{int(df.isnull().sum().sum())}")

        # If a cleaning operation was performed, show before/after comparison
        if st.session_state.cleaning_report is not None:
            rep = st.session_state.cleaning_report
            st.markdown("---")
            st.subheader("3. Cleaning Operation Results")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Original Records", f"{rep['original_records']}")
            with m2:
                st.metric("Missing Values Cleaned", f"{rep['total_missing_before']}")
            with m3:
                st.metric("Duplicates Removed", f"{rep['duplicates_removed']}")
            with m4:
                st.metric("Cleaned Records", f"{rep['cleaned_records']}")

            st.success("All missing numerical values were imputed with the column mean. Categorical columns were filled with the mode. Constraints (0 <= marks <= 100, attended <= total) were audited.")


# =============================================================================
# 5. ATTENDANCE ANALYSIS PAGE
# =============================================================================
elif selected_page == "5. Attendance Analysis":
    st.markdown("<h1 class='academic-header'>Attendance Analysis (NumPy)</h1>", unsafe_allow_html=True)
    st.markdown("<div class='academic-subtitle'>Categorization, numerical distribution, and threshold monitoring</div>", unsafe_allow_html=True)

    if not has_data:
        st.warning("⚠ No data available for analysis.")
    else:
        st.markdown("""
        <div class='info-card'>
            <strong>Academic Policy Guidance:</strong>
            Students below the required attendance threshold (75%) may require additional academic monitoring and mentoring.
            High attendance provides continuous classroom interaction, though overall performance is also influenced by other factors.
        </div>
        """, unsafe_allow_html=True)

        # NumPy Statistical Summary
        st.subheader("1. NumPy Numerical Statistical Metrics")
        stats = calculate_numpy_statistics(df)

        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric("Mean Attendance (np.mean)", f"{stats.get('mean_attendance', 0.0):.2f}%")
            st.metric("Mean Final Marks (np.mean)", f"{stats.get('mean_final_marks', 0.0):.2f}")
        with stat_col2:
            st.metric("Median Attendance (np.median)", f"{stats.get('median_attendance', 0.0):.2f}%")
            st.metric("Median Final Marks (np.median)", f"{stats.get('median_final_marks', 0.0):.2f}")
        with stat_col3:
            st.metric("Standard Deviation (np.std)", f"{stats.get('std_attendance', 0.0):.2f}%")
            st.metric("Std Dev Final Marks (np.std)", f"{stats.get('std_final_marks', 0.0):.2f}")
        with stat_col4:
            st.metric("Range (Min / Max)", f"{stats.get('min_attendance', 0.0):.1f}% - {stats.get('max_attendance', 0.0):.1f}%")
            st.metric("Correlation (np.corrcoef)", f"{stats.get('correlation', 0.0):.4f}")

        st.markdown("---")

        # Attendance Tier Breakdown
        st.subheader("2. Academic Attendance Tiers")
        cat_counts = get_attendance_category_counts(df)
        t1, t2, t3, t4 = st.columns(4)
        with t1:
            st.metric("🌟 Excellent (90-100%)", f"{cat_counts.get('Excellent', 0)}")
        with t2:
            st.metric("👍 Good (75-89%)", f"{cat_counts.get('Good', 0)}")
        with t3:
            st.metric("⚠️ Average (60-74%)", f"{cat_counts.get('Average', 0)}")
        with t4:
            st.metric("🚨 Poor (< 60%)", f"{cat_counts.get('Poor', 0)}")

        # Cohort Tables
        st.markdown("---")
        c_left, c_right = st.columns(2)

        with c_left:
            st.subheader("🚨 Students Requiring Monitoring (< 75%)")
            below_75 = get_below_threshold_students(df, 75.0)
            if below_75.empty:
                st.success("🎉 Excellent news! All students have attendance at or above 75%.")
            else:
                st.dataframe(
                    below_75[['Student_ID', 'Student_Name', 'Department', 'Attendance', 'Final_Marks']],
                    use_container_width=True,
                    hide_index=True
                )

        with c_right:
            st.subheader("🌟 Students with Excellent Attendance (>= 90%)")
            excellent_df = get_excellent_students(df, 90.0)
            if excellent_df.empty:
                st.info("No students currently in the >= 90% bracket.")
            else:
                st.dataframe(
                    excellent_df[['Student_ID', 'Student_Name', 'Department', 'Attendance', 'Final_Marks']],
                    use_container_width=True,
                    hide_index=True
                )


# =============================================================================
# 6. REGRESSION ANALYSIS PAGE
# =============================================================================
elif selected_page == "6. Regression Analysis":
    st.markdown("<h1 class='academic-header'>Simple Linear Regression Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<div class='academic-subtitle'>Mathematical modeling of Attendance (X) vs Final Marks (Y) using NumPy Polyfit</div>", unsafe_allow_html=True)

    if not has_data:
        st.warning("⚠ Dataset is empty. Cannot compute regression.")
    else:
        reg_result, reg_err = perform_linear_regression(df, x_col='Attendance', y_col='Final_Marks')

        if reg_err:
            st.error(f"⚠ {reg_err}")
        else:
            slope = reg_result['slope']
            intercept = reg_result['intercept']
            r2 = reg_result['r2_score']
            corr = reg_result['correlation']
            eq = reg_result['equation']
            interp = reg_result['interpretation']

            # Mathematical Formula Callout
            st.markdown(f"""
            <div class='equation-box'>
                {eq}
            </div>
            """, unsafe_allow_html=True)

            # Regression Metrics Cards
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Slope (m)", f"{slope:.4f}")
            with m2:
                st.metric("Intercept (c)", f"{intercept:.2f}")
            with m3:
                st.metric("Correlation (r)", f"{corr:.4f}")
            with m4:
                st.metric("R² Score (Goodness of Fit)", f"{r2:.4f}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Two columns: Visualization & Prediction Tool
            col_chart, col_pred = st.columns([1.2, 0.8])

            with col_chart:
                st.subheader("📈 Matplotlib Regression Scatter Plot")
                fig = create_regression_scatter_chart(df, reg_result)
                st.pyplot(fig)
                plt.close(fig)

            with col_pred:
                st.subheader("🎯 Interactive Marks Predictor")
                st.markdown("Input an attendance percentage to predict estimated final marks:")
                
                input_att = st.slider("Select Attendance %", min_value=0.0, max_value=100.0, value=85.0, step=0.5)
                predicted_score = predict_final_marks(slope, intercept, input_att)

                st.markdown(f"""
                <div style='background-color:#F0FDF4; border:2px solid #86EFAC; padding:18px; border-radius:10px; margin-top:15px; text-align:center;'>
                    <span style='color:#166534; font-size:1rem; font-weight:600;'>Estimated Final Marks:</span><br>
                    <span style='color:#15803D; font-size:2.4rem; font-weight:800;'>{predicted_score:.1f} / 100</span><br>
                    <small style='color:#374151;'>Based on equation: {slope:.2f} × {input_att} + ({intercept:.2f})</small>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.info(f"Student attendance of {input_att}% maps to the **{categorize_attendance(input_att)}** category.")

            # Scientific Interpretation
            st.markdown("---")
            st.subheader("📚 Academic Interpretation & Findings")
            
            st.markdown(f"""
            * **Association Summary:** {interp['summary']}
            * **Slope Interpretation:** {interp['slope_explanation']}
            * **Coefficient of Determination ($R^2$):** {interp['r2_explanation']}
            """)

            st.markdown(f"""
            <div class='info-card'>
                <strong>Distinguishing Correlation vs Causation:</strong><br>
                {interp['causality_note']}
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# 7. VISUALIZATIONS PAGE
# =============================================================================
elif selected_page == "7. Visualizations":
    st.markdown("<h1 class='academic-header'>Matplotlib Visualizations Gallery</h1>", unsafe_allow_html=True)
    st.markdown("<div class='academic-subtitle'>Five comprehensive academic charts created strictly using Matplotlib</div>", unsafe_allow_html=True)

    if not has_data:
        st.warning("⚠ No data available to generate visualizations.")
    else:
        reg_info, _ = perform_linear_regression(df)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Chart 1: Distribution",
            "Chart 2: Attendance vs Marks",
            "Chart 3: Study Hours vs Marks",
            "Chart 4: Marks by Category",
            "Chart 5: Top 10 Students"
        ])

        with tab1:
            st.subheader("Chart 1 — Attendance Distribution by Tier")
            fig1 = create_attendance_distribution_chart(df)
            st.pyplot(fig1)
            plt.close(fig1)
            st.caption("Visualizes student population across Excellent (>=90%), Good (75-89%), Average (60-74%), and Poor (<60%) tiers.")

        with tab2:
            st.subheader("Chart 2 — Attendance vs Final Marks with Regression Line")
            fig2 = create_regression_scatter_chart(df, reg_info)
            st.pyplot(fig2)
            plt.close(fig2)
            st.caption("Scatter observations paired with linear best-fit regression line and 75% attendance threshold benchmark.")

        with tab3:
            st.subheader("Chart 3 — Study Hours vs Final Marks")
            fig3 = create_study_hours_vs_marks_chart(df)
            st.pyplot(fig3)
            plt.close(fig3)
            st.caption("Examines how self-study hours outside the classroom correlate with exam performance, color-coded by attendance.")

        with tab4:
            st.subheader("Chart 4 — Average Marks by Attendance Category")
            fig4 = create_avg_marks_by_category_chart(df)
            st.pyplot(fig4)
            plt.close(fig4)
            st.caption("Bar chart showing mean examination marks achieved by students within each attendance tier.")

        with tab5:
            st.subheader("Chart 5 — Top 10 Students by Attendance")
            fig5 = create_top_students_attendance_chart(df, top_n=10)
            st.pyplot(fig5)
            plt.close(fig5)
            st.caption("Rank-ordered horizontal bar chart highlighting students with the highest attendance records.")


# =============================================================================
# 8. FINDINGS & SUMMARY PAGE
# =============================================================================
elif selected_page == "8. Findings & Summary":
    st.markdown("<h1 class='academic-header'>Dynamically Generated Findings & Summary</h1>", unsafe_allow_html=True)
    st.markdown("<div class='academic-subtitle'>Synthesized takeaways computed directly from the active dataset</div>", unsafe_allow_html=True)

    if not has_data:
        st.warning("⚠ No data available to generate findings.")
    else:
        stats = calculate_numpy_statistics(df)
        reg_info, _ = perform_linear_regression(df)
        below_75_df = get_below_threshold_students(df, 75.0)
        total_students = len(df)
        below_count = len(below_75_df)

        avg_att = stats.get('mean_attendance', 0.0)
        max_att = stats.get('max_attendance', 0.0)
        min_att = stats.get('min_attendance', 0.0)
        corr = stats.get('correlation', 0.0)
        slope = reg_info['slope'] if reg_info else 0.0
        intercept = reg_info['intercept'] if reg_info else 0.0
        r2 = reg_info['r2_score'] if reg_info else 0.0

        max_student = df.loc[df['Attendance'] == max_att, ['Student_Name', 'Student_ID']].iloc[0].to_dict() if not df.empty else {'Student_Name': 'N/A', 'Student_ID': 'N/A'}
        min_student = df.loc[df['Attendance'] == min_att, ['Student_Name', 'Student_ID']].iloc[0].to_dict() if not df.empty else {'Student_Name': 'N/A', 'Student_ID': 'N/A'}

        st.subheader("📌 Key Empirical Findings")

        findings_markdown = f"""
        * **Average Attendance:** The cohort average attendance is **{avg_att:.1f}%**.
        * **Highest Attendance:** **{max_att:.1f}%** achieved by student **{max_student['Student_Name']} ({max_student['Student_ID']})**.
        * **Lowest Attendance:** **{min_att:.1f}%** recorded by student **{min_student['Student_Name']} ({min_student['Student_ID']})**.
        * **Attendance Defaulters:** **{below_count} student(s)** ({round(below_count/total_students*100, 1)}% of cohort) have attendance strictly below the university standard of 75%.
        * **Correlation Coefficient (r):** **{corr:.4f}**, demonstrating a **{'positive' if corr > 0 else 'negative'}** statistical association between attendance and final marks.
        * **Regression Model Equation:** <code>Final Marks = {slope:.2f} × Attendance {'+' if intercept >= 0 else '-'} {abs(intercept):.2f}</code>.
        * **Predictive Impact:** For every 10% increase in attendance, final marks are projected to change by **{slope * 10:+.1f} marks**.
        * **Variance Explained (R²):** **{r2:.4f}** ({r2 * 100:.1f}%), indicating that approximately **{r2 * 100:.1f}%** of score variation aligns linearly with attendance.
        """
        st.markdown(findings_markdown)

        st.markdown("---")
        st.subheader("💡 Actionable Academic Recommendations")

        st.markdown(f"""
        1. **Early Attendance Intervention:** Schedule proactive mentoring for the **{below_count} students** below 75% attendance before university semester examinations.
        2. **Holistic Support:** While higher attendance is strongly associated with higher scores ($r = {corr:.2f}$), the unexplained variance ({100 - (r2 * 100):.1f}%) highlights the importance of tutorial sessions, laboratory assignments, and independent study hours.
        3. **Continuous Monitoring:** Regularly upload weekly attendance sheets to Attendify to monitor positive or negative shifts in student attendance trajectories.
        """)

        st.markdown("""
        <div class='info-card'>
            <strong>Viva / Presentation Note:</strong>
            All statistics, equation coefficients, and findings listed on this page are computed dynamically in real-time from the dataset.
            If new students are added or another CSV file is uploaded, this summary automatically updates.
        </div>
        """, unsafe_allow_html=True)
