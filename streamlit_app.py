import streamlit as st
import pandas as pd

# Constants
GRADE_POINTS = {
    "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "F": 0.0,
    "IP (In Progress)": None,
    "Not Taken": None
}

DEFAULT_CREDITS = 4

def apply_custom_styles():
    st.markdown(
        """
        <style>
        :root {
            --primary-color: #FFD700;
        }
        .main {
            color: #FFD700;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #FFD700 !important;
        }
        .stMetric label {
            color: #FFD700 !important;
        }
        .stMetric [data-testid="stMetricValue"] {
            color: #FFD700 !important;
        }
        div[data-baseweb="select"] > div {
            border-color: #FFD700 !important;
        }
        .stButton>button {
            background-color: #FFD700 !important;
            color: black !important;
        }
        .stProgress > div > div > div > div {
            background-color: #FFD700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def init_session_state():
    if 'catalog' not in st.session_state:
        csv_path = "course_catalog.csv"
        try:
            df = pd.read_csv(csv_path)
            df = df.fillna("")
            if 'offering_year' not in df.columns:
                df['offering_year'] = ""
            if 'offering_semester' not in df.columns:
                df['offering_semester'] = ""
            if 'category' not in df.columns:
                df['category'] = "Uncategorized"
            if 'major_restriction' not in df.columns:
                df['major_restriction'] = ""
                
            st.session_state['catalog'] = df.to_dict('records')
        except FileNotFoundError:
            st.session_state['catalog'] = [
                {"code": "SOC 410", "name": "Identity: Gender, Race", "credits": 4},
                {"code": "ECON 251", "name": "Principles of Economics", "credits": 4},
                {"code": "SECP 498", "name": "Senior Capstone", "credits": 4},
                {"code": "POL 100", "name": "Intro to Politics", "credits": 4},
                {"code": "FYS 101", "name": "First Year Seminar I", "credits": 4},
                {"code": "FYS 102", "name": "First Year Seminar II", "credits": 4},
                {"code": "ENG 101", "name": "College Writing", "credits": 4},
            ]
            pd.DataFrame(st.session_state['catalog']).to_csv(csv_path, index=False)
    
    if 'plan' not in st.session_state:
        st.session_state['plan'] = {
            f"Year {y}": {s: {} for s in ["Fall", "Spring", "Summer"]}
            for y in range(1, 5)
        }

def calculate_gpa(course_grades, catalog=None):
    if catalog is None:
        catalog = st.session_state.get('catalog', [])
        
    total_points = 0
    total_credits = 0
    
    catalog_dict = {c['code']: c['credits'] for c in catalog}
    
    for code, grade in course_grades.items():
        if grade in GRADE_POINTS and GRADE_POINTS[grade] is not None:
            credits = catalog_dict.get(code, DEFAULT_CREDITS)
            points = GRADE_POINTS[grade]
            total_points += points * credits
            total_credits += credits
            
    gpa = total_points / total_credits if total_credits > 0 else 0.0
    return gpa, total_credits

def sidebar_section():
    st.sidebar.header("Settings")
    
    st.sidebar.subheader("1. Course Catalog")
    uploaded_file = st.sidebar.file_uploader("Upload CSV Catalog", type="csv")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df = df.fillna("")
            for col in ['offering_year', 'offering_semester', 'major_restriction']:
                if col not in df.columns:
                    df[col] = ""
            if 'category' not in df.columns:
                df['category'] = "Uncategorized"
                
            st.session_state['catalog'] = df.to_dict('records')
            st.sidebar.success("Catalog Loaded!")
        except Exception as e:
            st.sidebar.error(f"Error loading CSV: {e}")
            
    st.sidebar.divider()
    st.sidebar.subheader("2. Student Profile")
    
    if 'profile' not in st.session_state:
        st.session_state['profile'] = {'start_year': 2022, 'major': 'Undeclared'}
        
    start_year = st.sidebar.number_input(
        "Start Year (Year 1)", 
        min_value=2020, 
        max_value=2030, 
        value=st.session_state['profile']['start_year'],
        key="start_year_input"
    )
    
    majors = ["Undeclared", "Statistic and Data Science (SDS)", "Politics Philosophy and Economics (PPE)", "Environmental and Sustainability Studies (ESS)"]
    current_major_idx = 0
    if st.session_state['profile']['major'] in majors:
        current_major_idx = majors.index(st.session_state['profile']['major'])
        
    major = st.sidebar.selectbox(
        "Select Major", 
        majors, 
        index=current_major_idx,
        key="major_input"
    )
    
    st.session_state['profile']['start_year'] = start_year
    st.session_state['profile']['major'] = major

    st.sidebar.divider()
    
    with st.sidebar.expander("Admin Tools (Add Course)"):
        admin_form()

def admin_form():
    with st.form("add_course_form"):
        new_code = st.text_input("Course Code", placeholder="e.g. CS 101")
        new_name = st.text_input("Course Name", placeholder="e.g. Intro to CS")
        new_credits = st.number_input("Credits", min_value=1, max_value=10, value=4)
        
        st.write("Offering Availability (Leave empty for 'Always Available')")
        col_avail1, col_avail2 = st.columns(2)
        with col_avail1:
            new_year = st.number_input("Year (Optional)", min_value=2020, max_value=2030, value=None, placeholder="e.g. 2023")
        with col_avail2:
            new_semester = st.selectbox("Semester (Optional)", ["", "Fall", "Spring", "Summer"])
            
        st.write("Course Details")
        col_det1, col_det2 = st.columns(2)
        with col_det1:
            new_category = st.selectbox("Category", ["Uncategorized", "Arts", "Interdisciplinary", "Mathematics and Science", "Humanities and Social Sciences", "Pillar"])
        with col_det2:
            new_restriction = st.selectbox("Major Restriction (Optional)", ["", "SDS", "PPE", "ESS"])
            
        submitted = st.form_submit_button("Add Course")
        
        if submitted:
            if new_code and new_name:
                if any(c['code'] == new_code for c in st.session_state['catalog']):
                    st.sidebar.error(f"Course {new_code} already exists!")
                else:
                    st.session_state['catalog'].append({
                        "code": new_code,
                        "name": new_name,
                        "credits": new_credits,
                        "offering_year": int(new_year) if new_year else "",
                        "offering_semester": new_semester,
                        "category": new_category,
                        "major_restriction": new_restriction
                    })
                    pd.DataFrame(st.session_state['catalog']).to_csv("course_catalog.csv", index=False)
                    st.sidebar.success(f"Added {new_code}")
            else:
                st.sidebar.warning("Please fill in both Code and Name.")
    
    st.sidebar.divider()
    st.sidebar.subheader("Current Catalog")
    df_catalog = pd.DataFrame(st.session_state['catalog'])
    if not df_catalog.empty:
        df_catalog = df_catalog.fillna("")
        st.sidebar.dataframe(df_catalog, hide_index=True, use_container_width=True)

def student_view():
    st.title("Academic Degree Planner")
    
    if 'profile' not in st.session_state:
        st.session_state['profile'] = {'start_year': 2022, 'major': 'Undeclared'}
    
    start_year = st.session_state['profile']['start_year']
    student_major = st.session_state['profile']['major']
    
    all_course_grades = {}
    for year in st.session_state['plan']:
        for sem in st.session_state['plan'][year]:
            all_course_grades.update(st.session_state['plan'][year][sem])
            
    cum_gpa, cum_credits = calculate_gpa(all_course_grades)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cumulative GPA", f"{cum_gpa:.2f}")
    col2.metric("Total Credits", f"{cum_credits}")
    col3.metric("Courses Taken", f"{len(all_course_grades)}")
    col4.metric("Major", student_major)
    
    progress_val = min(cum_credits / 120, 1.0)
    st.progress(progress_val, text=f"Degree Progress: {cum_credits} / 120 Credits")

    with st.expander("Performance Insights", expanded=False):
        viz_col1, viz_col2 = st.columns([2, 1])
        
        with viz_col1:
            st.caption("GPA Trend over Semesters")
            trend_data = []
            for y_key in st.session_state['plan']:
                for s_key in st.session_state['plan'][y_key]:
                    sem_data = st.session_state['plan'][y_key][s_key]
                    if sem_data:
                        gpa, _ = calculate_gpa(sem_data)
                        trend_data.append({"Term": f"{y_key[5:]} {s_key}", "GPA": gpa})
            
            if trend_data:
                df_trend = pd.DataFrame(trend_data)
                st.line_chart(df_trend.set_index("Term"), height=250)
            else:
                st.info("Plan your course schedule to see GPA trends.")
                
        with viz_col2:
            st.caption("Grade Distribution")
            grades_list = [g for g in all_course_grades.values() if g in GRADE_POINTS and GRADE_POINTS[g] is not None]
            if grades_list:
                grade_counts = pd.Series(grades_list).value_counts()
                sort_order = [k for k in GRADE_POINTS.keys() if k in grade_counts.index]
                grade_counts = grade_counts.reindex(sort_order)
                st.bar_chart(grade_counts, height=250)
            else:
                st.info("Add grades to see distribution.")

    st.divider()
    
    tabs = st.tabs(["Year 1", "Year 2", "Year 3", "Year 4"])
    
    catalog_map = {c['code']: c for c in st.session_state['catalog']}
    
    PILLARS = {
        "FYS 101": ("Year 1", "Fall"),
        "ENG 101": ("Year 1", "Fall"),
        "FYS 102": ("Year 2", "Fall")
    }
    
    for code, (pyear, psem) in PILLARS.items():
        if code in catalog_map:
             if code not in st.session_state['plan'][pyear][psem]:
                 st.session_state['plan'][pyear][psem][code] = "IP (In Progress)"

    for year_idx, tab in enumerate(tabs):
        year_key = f"Year {year_idx + 1}"
        current_academic_year = start_year + year_idx
        
        with tab:
            st.caption(f"Academic Year: {current_academic_year} - {current_academic_year + 1}")
            cols = st.columns(3)
            semesters = ["Fall", "Spring", "Summer"]
            
            for i, semester in enumerate(semesters):
                if semester == "Fall":
                    term_year = current_academic_year
                else:
                    term_year = current_academic_year + 1
                    
                with cols[i]:
                    st.subheader(f"{semester} {term_year}")
                    
                    filter_col1, = st.columns(1)
                    with filter_col1:
                        cat_filter = st.multiselect(
                            "Filter Category", 
                            ["Arts", "Interdisciplinary", "Mathematics and Science", "Humanities and Social Sciences", "Pillar"],
                            key=f"cat_{year_key}_{semester}",
                            label_visibility="collapsed",
                            placeholder="Filter by Category..."
                        )

                    available_courses = []
                    for c in st.session_state['catalog']:
                        c_year = c.get('offering_year')
                        c_sem = c.get('offering_semester')
                        
                        if pd.isna(c_year) or c_year == "": c_year = None
                        else: c_year = int(c_year)
                        
                        if pd.isna(c_sem) or c_sem == "": c_sem = None
                        
                        match_term = True
                        if c_year and c_year != term_year: match_term = False
                        if c_sem and c_sem != semester: match_term = False
                        
                        course_restriction = c.get('major_restriction', "")
                        if pd.isna(course_restriction): course_restriction = ""
                        
                        match_major = False
                        if course_restriction == "":
                            match_major = True
                        elif course_restriction in student_major:
                            match_major = True
                            
                        match_cat = True
                        if cat_filter:
                            c_cat = c.get('category', "Uncategorized")
                            if c_cat not in cat_filter:
                                match_cat = False

                        if match_term and match_major and match_cat:
                            available_courses.append(c)
                            
                    available_courses.sort(key=lambda x: x['code'])
                    
                    catalog_options = [f"{c['code']}: {c['name']}" for c in available_courses]
                    local_catalog_map = {f"{c['code']}: {c['name']}": c['code'] for c in available_courses}
                    local_reverse_map = {c['code']: f"{c['code']}: {c['name']}" for c in available_courses}

                    current_sem_data = st.session_state['plan'][year_key][semester]
                    
                    current_selected_formatted = [
                        local_reverse_map.get(code, f"{code} (Unavailable)") 
                        for code in current_sem_data.keys()
                    ]
                     
                    selected_formatted = st.multiselect(
                        "Select Courses",
                        options=catalog_options,
                        default=[c for c in current_selected_formatted if "(Unavailable)" not in c], 
                        key=f"{year_key}_{semester}_select",
                        label_visibility="collapsed"
                    )
                    
                    selected_codes = [local_catalog_map[f] for f in selected_formatted]
                    
                    for code in list(current_sem_data.keys()):
                        if code not in selected_codes:
                            if code in local_reverse_map:
                                del st.session_state['plan'][year_key][semester][code]
                            
                    for code in selected_codes:
                        if code not in current_sem_data:
                            st.session_state['plan'][year_key][semester][code] = "IP (In Progress)"
                    
                    if current_sem_data:
                        st.caption("Grades")
                        for code in list(current_sem_data.keys()):
                            grade_key = f"{year_key}_{semester}_{code}_grade"
                            
                            def update_grade(c=code, k=grade_key, y=year_key, s=semester):
                                st.session_state['plan'][y][s][c] = st.session_state[k]

                            current_grade = st.session_state['plan'][year_key][semester].get(code, "IP (In Progress)")
                            
                            st.selectbox(
                                f"{code}",
                                options=list(GRADE_POINTS.keys()),
                                index=list(GRADE_POINTS.keys()).index(current_grade) if current_grade in GRADE_POINTS else 0,
                                key=grade_key,
                                on_change=update_grade,
                                label_visibility="visible" 
                            )

                    sem_gpa, sem_credits = calculate_gpa(current_sem_data, st.session_state['catalog']) 
                    st.info(f"GPA: {sem_gpa:.2f} | Credits: {sem_credits}")

if __name__ == "__main__":
    st.set_page_config(page_title="Academic Planner", layout="wide")
    apply_custom_styles() # Apply styles after config
    init_session_state()
    sidebar_section()
    student_view()
