# ---------------------------
# app.py - OrthoPulse (Sophisticated Ortho Tracker)
# ---------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta
import threading
import time

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="OrthoPulse 🦴", page_icon="🩺", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4B0082;'>OrthoPulse 🦴 Dashboard</h1>", unsafe_allow_html=True)

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
        date = datetime.today() - timedelta(days=random.randint(0, 90))
        hospital = random.choice(hospitals)
        region = hospital_region_map[hospital]
        procedure = random.choice(procedures)
        surgeon = random.choice(surgeons)
        staff_count = random.randint(1, 3)
        staff = ", ".join(random.sample(staff_members, k=staff_count))
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
# Data filtering
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
min_date = df['Date'].min()
max_date = df['Date'].max()
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
]

# ---------------------------
# Toast-style Notification
# ---------------------------
def toast_alert(message, alert_type="info", duration=5):
    placeholder = st.empty()
    if alert_type == "warning":
        placeholder.warning(message)
    elif alert_type == "success":
        placeholder.success(message)
    else:
        placeholder.info(message)
    
    def remove_after_delay(ph, dur):
        time.sleep(dur)
        ph.empty()
    
    threading.Thread(target=remove_after_delay, args=(placeholder, duration), daemon=True).start()

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
    st.markdown("<h2 style='text-align: center; color: #228B22;'>📊 Key Insights</h2>", unsafe_allow_html=True)
    if df_filtered.empty:
        st.info("No data available.")
    else:
        # KPIs
        total_cases = len(df_filtered)
        total_surgeons = df_filtered["Surgeon"].nunique()
        staff_count = df_filtered["Staff"].str.split(",").explode().str.strip().nunique()
        top_hospitals = df_filtered['Hospital'].value_counts().head(3)
        top_procs = df_filtered['Procedure'].value_counts().head(3)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🟢 Total Cases", total_cases)
        col2.metric("🔵 Active Surgeons", total_surgeons)
        col3.metric("🟡 Staff Coverage", staff_count)
        col4.metric("🏥 Top Hospitals", ", ".join(top_hospitals.index.tolist()))
        col5.metric("⚕️ Top Procedures", ", ".join(top_procs.index.tolist()))

        # Smart Recommendations (Admin)
        if role == "Admin":
            staff_series = df_filtered['Staff'].str.split(",").explode().str.strip().value_counts()
            overloaded_staff = staff_series[staff_series > 5]
            if not overloaded_staff.empty:
                toast_alert(f"⚠️ Staff Overload: {', '.join(overloaded_staff.index.tolist())}!", "warning", 7)

            hosp_counts = df_filtered['Hospital'].value_counts()
            high_load_hosp = hosp_counts[hosp_counts > hosp_counts.mean() + hosp_counts.std()]
            if not high_load_hosp.empty:
                toast_alert(f"🏥 High Procedure Load: {', '.join(high_load_hosp.index.tolist())}", "warning", 7)

# ---------------------------
# Trends Tab
# ---------------------------
with tab_trends:
    st.markdown("<h2 style='text-align: center; color: #1E90FF;'>📈 Procedure Trends</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        df_trend = df_filtered.groupby([pd.Grouper(key="Date", freq="W"), "Procedure"]).size().reset_index(name="Count")
        fig_line = px.line(df_trend, x="Date", y="Count", color="Procedure", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------
# Leaderboard Tab
# ---------------------------
with tab_leaderboard:
    st.markdown("<h2 style='text-align: center; color: #FF8C00;'>🏆 Leaderboard</h2>", unsafe_allow_html=True)
    if role == "Admin" and not df_all.empty:
        lb_surgeons = df_all['Surgeon'].value_counts().reset_index()
        lb_surgeons.columns = ['Surgeon', 'Procedures Done']
        fig_surgeon = px.bar(lb_surgeons, x='Surgeon', y='Procedures Done', text='Procedures Done')
        st.plotly_chart(fig_surgeon, use_container_width=True)

        staff_series = df_all['Staff'].str.split(",").explode().str.strip().dropna()
        lb_staff = staff_series.value_counts().reset_index()
        lb_staff.columns = ["Staff", "Appearances"]
        fig_staff = px.bar(lb_staff, x="Staff", y="Appearances", text="Appearances")
        st.plotly_chart(fig_staff, use_container_width=True)

# ---------------------------
# Reports Tab
# ---------------------------
with tab_reports:
    st.markdown("<h2 style='text-align: center; color: #4B0082;'>🗂 Reports</h2>", unsafe_allow_html=True)
    st.download_button("📥 Download CSV", df_filtered.to_csv(index=False), "ortho_procedures.csv", "text/csv")

# ---------------------------
# Add Procedure Tab
# ---------------------------
with tab_add:
    st.markdown("<h2 style='text-align: center; color: #006400;'>➕ Add Procedure</h2>", unsafe_allow_html=True)
    with st.form("add_proc"):
        date = st.date_input("Date", datetime.today())
        hospital = st.selectbox("Hospital", list(hospital_region_map.keys()))
        procedure = st.selectbox("Procedure", ["THA", "TKA", "Hip Revision", "Knee Revision", "Trauma Fixation"])
        surgeon = st.text_input("Surgeon")
        staff = st.text_input("Staff (comma separated)")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Procedure")
        if submitted:
            new_row = pd.DataFrame([[date, hospital_region_map[hospital], hospital, procedure, surgeon, staff, notes]],
                                   columns=df_all.columns)
            st.session_state["procedures"] = pd.concat([st.session_state["procedures"], new_row], ignore_index=True)
            toast_alert("✅ Procedure added successfully!", "success", 5)
