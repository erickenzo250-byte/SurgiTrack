# ---------------------------
# app.py - OrthoPulse Pro
# ---------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta
import threading, time
import numpy as np
from sklearn.linear_model import LinearRegression

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="OrthoPulse Pro 🦴", page_icon="🩺", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4B0082;'>OrthoPulse Pro 🦴 Dashboard</h1>", unsafe_allow_html=True)

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
    colors = {"info": "#17a2b8", "success": "#28a745", "warning": "#ffc107", "error": "#dc3545"}
    placeholder.markdown(
        f"<div style='padding:10px; border-radius:8px; background-color:{colors.get(alert_type,'#17a2b8')}; color:white;'>"
        f"{message}</div>", unsafe_allow_html=True
    )
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

        # Weekly Summary
        last_week = datetime.today() - timedelta(days=7)
        df_week = df_filtered[df_filtered['Date'] >= last_week]
        total_week = len(df_week)
        top_hosp_week = df_week['Hospital'].value_counts().idxmax() if not df_week.empty else "N/A"
        top_surgeon_week = df_week['Surgeon'].value_counts().idxmax() if not df_week.empty else "N/A"

        col6, col7, col8 = st.columns(3)
        col6.metric("🗓 Total Procedures (Last Week)", total_week)
        col7.metric("🏥 Top Hospital (Last Week)", top_hosp_week)
        col8.metric("⚕️ Top Surgeon (Last Week)", top_surgeon_week)

        # Smart Alerts
        if role == "Admin":
            staff_counts = df_filtered['Staff'].str.split(",").explode().value_counts()
            overworked = staff_counts[staff_counts > staff_counts.mean() + staff_counts.std()]
            if not overworked.empty:
                toast_alert(f"⚠️ Overworked Staff: {', '.join(overworked.index.tolist())}", "warning", 7)

            hosp_counts = df_filtered['Hospital'].value_counts()
            high_load_hosp = hosp_counts[hosp_counts > hosp_counts.mean() + hosp_counts.std()]
            if not high_load_hosp.empty:
                toast_alert(f"🏥 High Procedure Load: {', '.join(high_load_hosp.index.tolist())}", "warning", 7)

# ---------------------------
# Trends Tab (Last 1 Month, Total Procedures)
# ---------------------------
with tab_trends:
    st.markdown("<h2 style='text-align: center; color: #1E90FF;'>📈 Procedure Trends (Last 1 Month)</h2>", unsafe_allow_html=True)
    one_month_ago = datetime.today() - timedelta(days=30)
    df_last_month = df_filtered[df_filtered['Date'] >= one_month_ago]

    if not df_last_month.empty:
        # Total procedures per week
        df_trend = df_last_month.groupby(pd.Grouper(key="Date", freq="W")).size().reset_index(name="Total Procedures")
        df_trend = df_trend.sort_values("Date")

        fig_line = px.line(df_trend, x="Date", y="Total Procedures", markers=True,
                           title="Total Procedures per Week (Last 1 Month)", color_discrete_sequence=["#1f77b4"])
        st.plotly_chart(fig_line, use_container_width=True)

        # Most Active Staff
        staff_counts = df_last_month['Staff'].str.split(",").explode().str.strip().value_counts().head(5)
        st.subheader("🧑‍⚕️ Most Active Staff (Last Month)")
        st.bar_chart(staff_counts)

        # Procedure Type Distribution
        proc_counts = df_last_month['Procedure'].value_counts()
        st.subheader("📊 Procedure Distribution (Last Month)")
        st.pie_chart(proc_counts)

        # Surgeon Performance Over Time
        surgeon_weekly = df_last_month.groupby([pd.Grouper(key="Date", freq="W"), "Surgeon"]).size().reset_index(name="Count")
        fig_surgeon = px.line(surgeon_weekly, x="Date", y="Count", color="Surgeon", markers=True, title="Surgeon Weekly Activity")
        st.plotly_chart(fig_surgeon, use_container_width=True)

        # Hospital Share Donut
        hosp_counts = df_last_month['Hospital'].value_counts()
        fig_hosp = px.pie(values=hosp_counts.values, names=hosp_counts.index, hole=0.5, title="Hospital Procedure Share (Last Month)")
        st.plotly_chart(fig_hosp, use_container_width=True)

        # Procedure Forecast (Next Week)
        weekly_total = df_last_month.groupby(pd.Grouper(key="Date", freq="W")).size().reset_index(name="Total")
        weekly_total['Week_Number'] = np.arange(len(weekly_total))
        if len(weekly_total) >= 2:
            model = LinearRegression()
            model.fit(weekly_total[['Week_Number']], weekly_total['Total'])
            next_week = model.predict([[weekly_total['Week_Number'].max() + 1]])[0]
            st.info(f"📈 Predicted total procedures for next week: {int(next_week)}")

        # Trend Comparison
        compare_hospitals = st.multiselect("Compare Hospitals", df_last_month['Hospital'].unique())
        if compare_hospitals:
            compare_df = df_last_month[df_last_month['Hospital'].isin(compare_hospitals)]
            compare_trend = compare_df.groupby([pd.Grouper(key="Date", freq="W"), "Hospital"]).size().reset_index(name="Total")
            fig_compare = px.line(compare_trend, x="Date", y="Total", color="Hospital", markers=True, title="Hospital Comparison Trend")
            st.plotly_chart(fig_compare, use_container_width=True)
    else:
        st.info("No procedures recorded in the last month.")

# ---------------------------
# Leaderboard Tab
# ---------------------------
with tab_leaderboard:
    st.markdown("<h2 style='text-align: center; color: #FF8C00;'>🏆 Leaderboard</h2>", unsafe_allow_html=True)
    if df_all.empty:
        st.info("No procedures recorded yet.")
    else:
        lb_surgeons = df_all['Surgeon'].value_counts().reset_index()
        lb_surgeons.columns = ['Surgeon', 'Procedures Done']
        fig_surgeon = px.bar(lb_surgeons, x='Surgeon', y='Procedures Done', text='Procedures Done',
                             color='Procedures Done', color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_surgeon, use_container_width=True)
        top_surgeon = lb_surgeons.iloc[0]['Surgeon']
        st.success(f"🏅 Top Surgeon: {top_surgeon}")

        staff_series = df_all['Staff'].str.split(",").explode().str.strip().dropna()
        lb_staff = staff_series.value_counts().reset_index()
        lb_staff.columns = ["Staff", "Appearances"]
        fig_staff = px.bar(lb_staff, x="Staff", y="Appearances", text="Appearances",
                           color="Appearances", color_continuous_scale=px.colors.sequential.Plasma)
        st.plotly_chart(fig_staff, use_container_width=True)
        top_staff = lb_staff.iloc[0]["Staff"]
        st.success(f"🏅 Top Staff: {top_staff}")

# ---------------------------
# Reports Tab
# ---------------------------
with tab_reports:
    st.markdown("<h2 style='text-align: center; color: #8A2BE2;'>📝 Generate Reports</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        csv = df_filtered.to_csv(index=False)
        st.download_button("📥 Download CSV Report", csv, "OrthoPulse_Report.csv", "text/csv")
        st.dataframe(df_filtered)

# ---------------------------
# Add Procedure Tab
# ---------------------------
with tab_add:
    st.markdown("<h2 style='text-align: center; color: #FF1493;'>➕ Add Procedure</h2>", unsafe_allow_html=True)
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
            toast_alert(f"New procedure added at {hospital} by {surgeon}", "success", 5)
