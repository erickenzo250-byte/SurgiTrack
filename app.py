# ---------------------------
# OrthoPulse Pro 🦴 - High-End Version
# ---------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import time

# Optional forecasting
try:
    from sklearn.linear_model import LinearRegression
    has_sklearn = True
except ImportError:
    has_sklearn = False
    st.warning("scikit-learn not installed. Forecast feature disabled.")

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="OrthoPulse Pro 🦴", page_icon="🩺", layout="wide")
st.markdown(
    "<h1 style='text-align: center; color: #4B0082;'>OrthoPulse Pro 🦴 Dashboard</h1>",
    unsafe_allow_html=True
)

# ---------------------------
# Hospital -> Region mapping
# ---------------------------
hospital_region_map = {
    "Nairobi General": "Nairobi",
    "Kijabe Hospital": "Western",
    "Meru County": "Meru",
    "Mombasa Central": "Coast",
    "Kisii Teaching": "Kisii"
}

# ---------------------------
# Generate random procedures
# ---------------------------
def generate_random_procedures(num_records=150):
    hospitals = list(hospital_region_map.keys())
    procedures = ["THA", "TKA", "Hip Revision", "Knee Revision", "Trauma Fixation"]
    surgeons = ["Dr. Mwangi", "Dr. Kimani", "Dr. Ochieng", "Dr. Wanjiru", "Dr. Njoroge"]
    staff_members = ["Alice", "Bob", "Charles", "Diana", "Eunice", "Francis"]

    data = []
    for _ in range(num_records):
        date = datetime.today() - pd.to_timedelta(np.random.randint(0, 90), unit='d')
        hospital = np.random.choice(hospitals)
        region = hospital_region_map[hospital]
        procedure = np.random.choice(procedures)
        surgeon = np.random.choice(surgeons)
        staff_count = np.random.randint(1, 4)
        staff = ", ".join(np.random.choice(staff_members, size=staff_count, replace=False))
        notes = "Routine procedure"
        data.append([date, region, hospital, procedure, surgeon, staff, notes])
    
    df = pd.DataFrame(data, columns=["Date","Region","Hospital","Procedure","Surgeon","Staff","Notes"])
    df["Date"] = pd.to_datetime(df["Date"])
    df["Staff"] = df["Staff"].fillna("")
    return df

# ---------------------------
# Preload procedures
# ---------------------------
if "procedures" not in st.session_state:
    st.session_state["procedures"] = generate_random_procedures(150)

# ---------------------------
# Role selection
# ---------------------------
role = st.selectbox("Select Role", ["Admin", "Staff"])
staff_name = ""
staff_region = ""
if role == "Staff":
    staff_name = st.text_input("Enter Your Name (as in Staff list)")
st.markdown("---")

# ---------------------------
# Filter Data
# ---------------------------
df_all = st.session_state["procedures"]
df = df_all.copy()

if role == "Staff" and staff_name:
    df = df[df['Staff'].str.contains(staff_name, case=False, na=False)]
    if not df.empty:
        staff_region = df['Region'].iloc[0]

if role == "Admin":
    regions = ["All"] + sorted(df_all["Region"].unique().tolist())
    selected_region = st.sidebar.selectbox("Filter by Region", regions)
    if selected_region != "All":
        df = df[df["Region"] == selected_region]
elif role == "Staff" and staff_region:
    df = df[df["Region"] == staff_region]

# ---------------------------
# Advanced Filters
# ---------------------------
st.sidebar.subheader("Filters")
min_date = df['Date'].min() if not df.empty else datetime.today()
max_date = df['Date'].max() if not df.empty else datetime.today()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])
proc_types = st.sidebar.multiselect("Procedure Types", df['Procedure'].unique(), default=df['Procedure'].unique())
hosp_filter = st.sidebar.multiselect("Hospitals", df['Hospital'].unique(), default=df['Hospital'].unique())
surgeon_filter = st.sidebar.multiselect("Surgeons", df['Surgeon'].unique(), default=df['Surgeon'].unique())
staff_filter = st.sidebar.multiselect("Staff", list(set(",".join(df['Staff']).split(", "))), default=list(set(",".join(df['Staff']).split(", "))))

df_filtered = df[
    (df['Date'] >= pd.to_datetime(date_range[0])) &
    (df['Date'] <= pd.to_datetime(date_range[1])) &
    (df['Procedure'].isin(proc_types)) &
    (df['Hospital'].isin(hosp_filter)) &
    (df['Surgeon'].isin(surgeon_filter)) &
    (df['Staff'].apply(lambda x: any(s in x for s in staff_filter)))
] if not df.empty else pd.DataFrame(columns=df.columns)

# ---------------------------
# Animated Metric Function
# ---------------------------
def animated_metric(label, value):
    placeholder = st.empty()
    for i in range(value+1):
        placeholder.metric(label, i)
        time.sleep(0.01)

# ---------------------------
# Tabs
# ---------------------------
tab_metrics, tab_trends, tab_leaderboard, tab_reports, tab_add = st.tabs(
    ["Metrics","Trends","Leaderboard","Reports","Add Procedure"]
)

# ---------------------------
# Metrics Tab
# ---------------------------
with tab_metrics:
    st.markdown("### 📊 Key Insights")
    if df_filtered.empty:
        st.info("No data available.")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        animated_metric("🟢 Total Cases", len(df_filtered))
        animated_metric("🔵 Active Surgeons", df_filtered["Surgeon"].nunique())
        animated_metric("🟡 Staff Coverage", df_filtered["Staff"].str.split(",").explode().str.strip().nunique())
        top_hospital = df_filtered['Hospital'].value_counts().idxmax()
        top_procedure = df_filtered['Procedure'].value_counts().idxmax()
        col4.metric("🏥 Top Hospital", top_hospital)
        col5.metric("⚕️ Top Procedure", top_procedure)
        st.info(f"💡 Recommendation: Monitor resources at {top_hospital}, highest number of procedures.")

# ---------------------------
# Trends Tab
# ---------------------------
with tab_trends:
    st.markdown("### 📈 Procedure Trends (Last 1 Month)")
    one_month_ago = datetime.today() - timedelta(days=30)
    df_last_month = df_filtered[df_filtered['Date'] >= one_month_ago] if not df_filtered.empty else pd.DataFrame(columns=df_filtered.columns)

    if not df_last_month.empty:
        df_trend = df_last_month.groupby(pd.Grouper(key="Date", freq="W")).size().reset_index(name="Total Procedures")
        fig_line = px.line(df_trend, x="Date", y="Total Procedures", markers=True, color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_line, use_container_width=True)

        # Forecast next week procedures
        if has_sklearn and len(df_trend) > 1:
            X = np.arange(len(df_trend)).reshape(-1, 1)
            y = df_trend['Total Procedures'].values
            model = LinearRegression().fit(X, y)
            pred = model.predict([[len(df_trend)]])[0]
            st.success(f"🔮 Forecasted procedures for next week: {int(pred)}")
    else:
        st.info("No procedures recorded in the last month.")

# ---------------------------
# Leaderboard Tab
# ---------------------------
with tab_leaderboard:
    st.markdown("### 🏆 Leaderboard")
    if df_filtered.empty:
        st.info("No procedures available.")
    else:
        lb_surgeons = df_filtered['Surgeon'].value_counts().reset_index()
        lb_surgeons.columns = ['Surgeon', 'Procedures Done']
        fig_surgeon = px.bar(lb_surgeons, x='Surgeon', y='Procedures Done', text='Procedures Done', color='Procedures Done', color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_surgeon, use_container_width=True)

        staff_series = df_filtered['Staff'].str.split(",").explode().str.strip().dropna()
        lb_staff = staff_series.value_counts().reset_index()
        lb_staff.columns = ["Staff", "Appearances"]
        fig_staff = px.pie(lb_staff, names='Staff', values='Appearances', title="Staff Workload Distribution")
        st.plotly_chart(fig_staff, use_container_width=True)

# ---------------------------
# Reports Tab
# ---------------------------
with tab_reports:
    st.markdown("### 📝 Generate Reports")
    if not df_filtered.empty:
        csv = df_filtered.to_csv(index=False)
        st.download_button("Download CSV Report", csv, "OrthoPulse_Report.csv", "text/csv")
        excel = df_filtered.to_excel(index=False, engine='openpyxl')
        st.download_button("Download Excel Report", excel, "OrthoPulse_Report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.dataframe(df_filtered)
    else:
        st.info("No data to generate report.")

# ---------------------------
# Add Procedure Tab
# ---------------------------
with tab_add:
    st.markdown("### ➕ Add Procedure")
    with st.form("add_proc_form"):
        date = st.date_input("Procedure Date", datetime.today())
        region = st.selectbox("Region", list(set(hospital_region_map.values())))
        hospital = st.selectbox("Hospital", list(hospital_region_map.keys()))
        procedure = st.selectbox("Procedure Type", ["THA", "TKA", "Hip Revision", "Knee Revision", "Trauma Fixation"])
        surgeon = st.text_input("Surgeon Name")
        staff = st.text_input("Staff involved (comma separated)")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Procedure")
        if submitted:
            new_row = pd.DataFrame([[date, region, hospital, procedure, surgeon, staff, notes]],
                                   columns=["Date","Region","Hospital","Procedure","Surgeon","Staff","Notes"])
            st.session_state["procedures"] = pd.concat([st.session_state["procedures"], new_row], ignore_index=True)
            st.success("✅ Procedure Added Successfully!")
