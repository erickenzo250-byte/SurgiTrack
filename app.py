# ---------------------------
# app.py - Ortho Tracker Pro
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
st.set_page_config(page_title="🦴 Ortho Tracker Pro", page_icon="🩺", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4B0082;'>🦴 Ortho Tracker Pro Dashboard</h1>", unsafe_allow_html=True)

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
# Animated Metric
# ---------------------------
def animated_metric(label, value, change=None):
    placeholder = st.empty()
    for i in range(value + 1):
        if change:
            placeholder.metric(label, i, delta=f"{change:+}")
        else:
            placeholder.metric(label, i)
        time.sleep(0.01)

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
    
    # Auto-remove
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
        # Total cases
        last_30_days = datetime.today() - timedelta(days=30)
        prev_df = df_all[df_all['Date'] < last_30_days]
        prev_count = len(prev_df)
        change_cases = len(df_filtered) - prev_count
        animated_metric("🟢 Total Cases (last 90 days)", len(df_filtered), change=change_cases)

        # Surgeons
        total_surgeons = df_filtered["Surgeon"].nunique()
        animated_metric("🔵 Active Surgeons", total_surgeons)

        # Staff coverage
        staff_count = df_filtered["Staff"].str.split(",").explode().str.strip().nunique()
        animated_metric("🟡 Staff Coverage", staff_count)

        # Top hospitals & procedures
        top_hospitals = df_filtered['Hospital'].value_counts().head(3)
        st.bar_chart(top_hospitals)
        st.info(f"🏥 Top Hospitals: {', '.join(top_hospitals.index.tolist())}")
        top_procs = df_filtered['Procedure'].value_counts().head(3)
        st.bar_chart(top_procs)
        st.info(f"⚕️ Top Procedures: {', '.join(top_procs.index.tolist())}")

        # Smart Recommendations
        st.markdown("<h3 style='color: #8B0000;'>💡 Recommendations</h3>", unsafe_allow_html=True)
        staff_series = df_filtered['Staff'].str.split(",").explode().str.strip().value_counts()
        overloaded_staff = staff_series[staff_series > 5]
        if not overloaded_staff.empty:
            toast_alert(f"⚠️ Staff Overload Alert: {', '.join(overloaded_staff.index.tolist())} handling many procedures!", "warning", 7)

        hosp_counts = df_filtered['Hospital'].value_counts()
        high_load_hosp = hosp_counts[hosp_counts > hosp_counts.mean() + hosp_counts.std()]
        if not high_load_hosp.empty:
            toast_alert(f"🏥 High Procedure Load: {', '.join(high_load_hosp.index.tolist())}. Allocate resources.", "warning", 7)

# ---------------------------
# Trends Tab
# ---------------------------
with tab_trends:
    st.markdown("<h2 style='text-align: center; color: #1E90FF;'>📈 Procedure Trends</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        # Weekly trend
        df_trend = df_filtered.groupby([pd.Grouper(key="Date", freq="W"), "Procedure"]).size().reset_index(name="Count")
        fig_line = px.line(df_trend, x="Date", y="Count", color="Procedure",
                           markers=True, color_discrete_sequence=px.colors.qualitative.Bold)
        fig_line.update_traces(hovertemplate="<b>%{y} procedures</b> in %{x} for %{color}")
        st.plotly_chart(fig_line, use_container_width=True)

        # Cumulative trend
        df_cum = df_filtered.groupby("Date").size().cumsum().reset_index(name="Cumulative")
        fig_cum = px.line(df_cum, x="Date", y="Cumulative", title="Cumulative Procedures")
        st.plotly_chart(fig_cum, use_container_width=True)

# ---------------------------
# Leaderboard Tab
# ---------------------------
with tab_leaderboard:
    st.markdown("<h2 style='text-align: center; color: #FF8C00;'>🏆 Leaderboard</h2>", unsafe_allow_html=True)
    if role == "Admin":
        if df_all.empty:
            st.info("No procedures recorded yet.")
        else:
            lb_surgeons = df_all['Surgeon'].value_counts().reset_index()
            lb_surgeons.columns = ['Surgeon', 'Procedures Done']
            lb_surgeons['Efficiency'] = lb_surgeons['Procedures Done'] / lb_surgeons['Procedures Done'].sum() * 100
            fig_surgeon = px.bar(lb_surgeons, x='Surgeon', y='Procedures Done', text='Procedures Done',
                                 color='Efficiency', color_continuous_scale=px.colors.sequential.Viridis)
            st.plotly_chart(fig_surgeon, use_container_width=True)
            st.success(f"🏅 Top Surgeon: {lb_surgeons.iloc[0]['Surgeon']}")

            staff_series = df_all['Staff'].str.split(",").explode().str.strip().dropna()
            lb_staff = staff_series.value_counts().reset_index()
            lb_staff.columns = ["Staff", "Appearances"]
            fig_staff = px.bar(lb_staff, x="Staff", y="Appearances", text="Appearances",
                               color="Appearances", color_continuous_scale=px.colors.sequential.Plasma)
            st.plotly_chart(fig_staff, use_container_width=True)
            st.success(f"🏅 Top Staff: {lb_staff.iloc[0]['Staff']}")

# ---------------------------
# Reports Tab
# ---------------------------
with tab_reports:
    st.markdown("<h2 style='text-align: center; color: #4B0082;'>🗂 Reports</h2>", unsafe_allow_html=True)
    st.write("Download filtered procedures:")
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
            st.success("✅ Procedure added successfully!")
