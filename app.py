import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import time

# Optional forecasting
try:
    from sklearn.linear_model import LinearRegression
    has_sklearn = True
except ImportError:
    has_sklearn = False

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
    return df

# ---------------------------
# Session state init
# ---------------------------
if "procedures" not in st.session_state:
    st.session_state["procedures"] = generate_random_procedures()

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
# Sidebar functions
# ---------------------------
st.sidebar.header("Advanced Filters & Options")
if not df.empty:
    min_date = df['Date'].min()
    max_date = df['Date'].max()
else:
    min_date = max_date = datetime.today()

date_range = st.sidebar.date_input("Procedure Date Range", [min_date, max_date])
proc_types = st.sidebar.multiselect("Procedure Types", df['Procedure'].unique(), default=df['Procedure'].unique() if not df.empty else [])
hosp_filter = st.sidebar.multiselect("Hospitals", df['Hospital'].unique(), default=df['Hospital'].unique() if not df.empty else [])
surgeon_filter = st.sidebar.multiselect("Surgeons", df['Surgeon'].unique(), default=df['Surgeon'].unique() if not df.empty else [])
staff_filter = st.sidebar.multiselect("Staff", list(set(",".join(df['Staff']).split(", "))) if not df.empty else [], default=list(set(",".join(df['Staff']).split(", "))) if not df.empty else [])

show_weekly = st.sidebar.checkbox("Show Weekly Trends", value=True)
show_forecast = st.sidebar.checkbox("Enable Forecast (Next Week)", value=True if has_sklearn else False)
show_report = st.sidebar.checkbox("Show Full Report Table", value=True)
show_popups = st.sidebar.checkbox("Enable Tab Pop-ups", value=True)

if not df.empty:
    df_filtered = df[
        (df['Date'] >= pd.to_datetime(date_range[0])) &
        (df['Date'] <= pd.to_datetime(date_range[1])) &
        (df['Procedure'].isin(proc_types)) &
        (df['Hospital'].isin(hosp_filter)) &
        (df['Surgeon'].isin(surgeon_filter)) &
        (df['Staff'].apply(lambda x: any(s in x for s in staff_filter)))
    ]
else:
    df_filtered = pd.DataFrame(columns=df.columns)

# ---------------------------
# Tabs
# ---------------------------
tab_metrics, tab_trends, tab_leaderboard, tab_reports, tab_add = st.tabs(
    ["Metrics","Trends","Leaderboards","Reports","Add Procedure"]
)

# ---------------------------
# Metrics Tab
# ---------------------------
with tab_metrics:
    if show_popups:
        st.toast("Viewing Key Metrics", icon="📊")
    st.markdown("### 📊 Key Insights")
    if df_filtered.empty:
        st.info("No data available.")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🟢 Total Cases", len(df_filtered))
        col2.metric("🔵 Active Surgeons", df_filtered["Surgeon"].nunique())
        col3.metric("🟡 Staff Coverage", df_filtered["Staff"].str.split(",").explode().str.strip().nunique())
        top_hospital = df_filtered['Hospital'].value_counts().idxmax()
        top_procedure = df_filtered['Procedure'].value_counts().idxmax()
        col4.metric("🏥 Top Hospital", top_hospital)
        col5.metric("⚕️ Top Procedure", top_procedure)

# ---------------------------
# Trends Tab
# ---------------------------
with tab_trends:
    if show_popups:
        st.toast("Viewing Trends", icon="📈")
    st.markdown("### 📈 Procedure Trends (Last Month)")
    one_month_ago = datetime.today() - timedelta(days=30)
    df_last_month = df_filtered[df_filtered['Date'] >= one_month_ago] if not df_filtered.empty else pd.DataFrame(columns=df_filtered.columns)

    if not df_last_month.empty:
        if show_weekly:
            df_trend = df_last_month.groupby(pd.Grouper(key="Date", freq="W")).size().reset_index(name="Total Procedures")
            fig_line = px.line(df_trend, x="Date", y="Total Procedures", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
        if show_forecast and has_sklearn and len(df_trend) > 1:
            X = np.arange(len(df_trend)).reshape(-1, 1)
            y = df_trend['Total Procedures'].values
            model = LinearRegression().fit(X, y)
            pred = model.predict([[len(df_trend)]])[0]
            st.success(f"🔮 Forecasted procedures next week: {int(pred)}")
    else:
        st.info("No procedures in the last month.")

# ---------------------------
# Leaderboards Tab
# ---------------------------
with tab_leaderboard:
    if show_popups:
        st.toast("Viewing Leaderboards", icon="🏆")
    st.markdown("### 🏆 Leaderboards")
    if df_filtered.empty:
        st.info("No procedures available.")
    else:
        # Surgeons
        lb_surgeons = df_filtered['Surgeon'].value_counts().reset_index()
        lb_surgeons.columns = ['Surgeon', 'Procedures Done']
        st.markdown("#### 🥇 Surgeons")
        fig_surgeon = px.bar(lb_surgeons, x='Surgeon', y='Procedures Done', text='Procedures Done')
        st.plotly_chart(fig_surgeon, use_container_width=True)

        # Staff
        staff_series = df_filtered['Staff'].str.split(",").explode().str.strip().dropna()
        lb_staff = staff_series.value_counts().reset_index()
        lb_staff.columns = ["Staff", "Procedures Assisted"]
        st.markdown("#### 🥈 Staff")
        fig_staff = px.bar(lb_staff, x="Staff", y="Procedures Assisted", text="Procedures Assisted")
        st.plotly_chart(fig_staff, use_container_width=True)

        # Hospitals
        lb_hosp = df_filtered['Hospital'].value_counts().reset_index()
        lb_hosp.columns = ["Hospital", "Total Procedures"]
        st.markdown("#### 🏥 Hospitals")
        fig_hosp = px.bar(lb_hosp, x="Hospital", y="Total Procedures", text="Total Procedures")
        st.plotly_chart(fig_hosp, use_container_width=True)

# ---------------------------
# Reports Tab
# ---------------------------
with tab_reports:
    if show_popups:
        st.toast("Viewing Reports", icon="📝")
    st.markdown("### 📝 Full Report")
    if df_filtered.empty:
        st.info("No data available.")
    else:
        if show_report:
            st.dataframe(df_filtered.sort_values("Date", ascending=False))
        csv = df_filtered.to_csv(index=False)
        st.download_button("Download CSV", csv, "OrthoPulse_Report.csv", "text/csv")

# ---------------------------
# Add Procedure Tab
# ---------------------------
with tab_add:
    if show_popups:
        st.toast("Add New Procedure", icon="➕")
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
