import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from io import BytesIO
from reportlab.pdfgen import canvas
import random

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="OrthoPulse Pro 🦴",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Tab Hover Pop-up Effect
# ---------------------------
st.markdown("""
<style>
.css-1aumxhk {
    transition: all 0.3s ease;
}
.css-1aumxhk:hover {
    transform: scale(1.05);
    background-color: #f0f8ff !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#4B0082'>OrthoPulse Pro 🦴 Dashboard</h1>", unsafe_allow_html=True)

# ---------------------------
# Database Setup
# ---------------------------
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS procedures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                region TEXT,
                hospital TEXT,
                procedure TEXT,
                surgeon TEXT,
                staff TEXT,
                notes TEXT
            )''')
conn.commit()

# ---------------------------
# Random Test Data Generator
# ---------------------------
def generate_random_procedures(num_records=200):
    hospitals = ["Nairobi General", "Kijabe Hospital", "Meru County", "Mombasa Central", "Kisii Teaching"]
    regions = {"Nairobi General": "Nairobi", "Kijabe Hospital": "Western", "Meru County": "Meru",
               "Mombasa Central": "Coast", "Kisii Teaching": "Kisii"}
    procedures = ["THA", "TKA", "Hip Revision", "Knee Revision", "Trauma Fixation"]
    surgeons = ["Dr. Mwangi", "Dr. Kimani", "Dr. Ochieng", "Dr. Wanjiru", "Dr. Njoroge"]
    staff_members = ["Alice", "Bob", "Charles", "Diana", "Eunice", "Francis"]
    data = []

    start_date = datetime(datetime.today().year, 1, 1)
    end_date = datetime.today()
    delta_days = (end_date - start_date).days

    for _ in range(num_records):
        date = start_date + timedelta(days=random.randint(0, delta_days))
        hospital = random.choice(hospitals)
        region = regions[hospital]
        procedure = random.choice(procedures)
        surgeon = random.choice(surgeons)
        staff = ", ".join(random.sample(staff_members, k=random.randint(1, 3)))
        notes = "Routine procedure"
        data.append((date.strftime("%Y-%m-%d"), region, hospital, procedure, surgeon, staff, notes))

    c.executemany('INSERT INTO procedures (date, region, hospital, procedure, surgeon, staff, notes) VALUES (?, ?, ?, ?, ?, ?, ?)', data)
    conn.commit()
    st.success(f"✅ Generated {num_records} random test procedures from January.")

# ---------------------------
# Load Data
# ---------------------------
df_all = pd.read_sql_query("SELECT * FROM procedures", conn)
if df_all.empty:
    generate_random_procedures(200)
    df_all = pd.read_sql_query("SELECT * FROM procedures", conn)
df_all["Date"] = pd.to_datetime(df_all["date"])

# ---------------------------
# Sidebar (High-End)
# ---------------------------
st.sidebar.header("👩‍⚕️ OrthoPulse Sidebar")

# Role Section
with st.sidebar.expander("User Role"):
    role = st.radio("Select Role", ["Admin", "Staff"])
    staff_name = st.text_input("Enter Your Name") if role == "Staff" else ""

# Filters Section
with st.sidebar.expander("Filters 🔍"):
    min_date = df_all['Date'].min()
    max_date = df_all['Date'].max()
    date_range = st.date_input("Date Range", [min_date, max_date], help="Select the date range for analysis")
    regions = ["All"] + sorted(df_all['region'].dropna().unique().tolist())
    selected_region = st.selectbox("Region", regions, help="Choose region or All")
    hospitals = ["All"] + sorted(df_all['hospital'].dropna().unique().tolist())
    selected_hospital = st.selectbox("Hospital", hospitals, help="Filter by hospital or All")
    procedures = ["All"] + sorted(df_all['procedure'].dropna().unique().tolist())
    selected_procedure = st.selectbox("Procedure", procedures, help="Filter by procedure type or All")
    surgeons = ["All"] + sorted(df_all['surgeon'].dropna().unique().tolist())
    selected_surgeon = st.selectbox("Surgeon", surgeons, help="Filter by surgeon or All")
    staff_filter = ["All"] + sorted(set(",".join(df_all['staff'].dropna()).split(", ")))
    selected_staff = st.selectbox("Staff", staff_filter, help="Filter by staff member or All")

# Quick Actions Section
with st.sidebar.expander("Quick Actions ⚡"):
    if st.button("Generate Random Test Data"):
        generate_random_procedures(100)
        st.experimental_rerun()
    if st.button("Reset Filters"):
        st.experimental_rerun()

# ---------------------------
# Data Filtering
# ---------------------------
df_filtered = df_all.copy()
if not df_filtered.empty:
    df_filtered = df_filtered[(df_filtered['Date'] >= pd.to_datetime(date_range[0])) &
                              (df_filtered['Date'] <= pd.to_datetime(date_range[1]))]
    if selected_region != "All":
        df_filtered = df_filtered[df_filtered['region'] == selected_region]
    if selected_hospital != "All":
        df_filtered = df_filtered[df_filtered['hospital'] == selected_hospital]
    if selected_procedure != "All":
        df_filtered = df_filtered[df_filtered['procedure'] == selected_procedure]
    if selected_surgeon != "All":
        df_filtered = df_filtered[df_filtered['surgeon'] == selected_surgeon]
    if role == "Staff" and staff_name:
        df_filtered = df_filtered[df_filtered['staff'].str.contains(staff_name, case=False, na=False)]
    elif selected_staff != "All":
        df_filtered = df_filtered[df_filtered['staff'].str.contains(selected_staff, case=False, na=False)]

# ---------------------------
# Tabs
# ---------------------------
tabs = st.tabs(["Metrics","Trends","Leaderboards","Reports","Add Procedure"])

# ---------------------------
# Metrics Tab
# ---------------------------
with tabs[0]:
    st.markdown("### 📊 Key Metrics")
    if df_filtered.empty:
        st.info("No data available.")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🟢 Total Cases", len(df_filtered))
        col2.metric("🔵 Total Surgeons", df_filtered["surgeon"].nunique())
        col3.metric("🟡 Total Staff", df_filtered["staff"].str.split(",").explode().str.strip().nunique())
        col4.metric("🏥 Top Hospital", df_filtered['hospital'].value_counts().idxmax())
        col5.metric("⚕️ Top Procedure", df_filtered['procedure'].value_counts().idxmax())

# ---------------------------
# Trends Tab
# ---------------------------
with tabs[1]:
    st.markdown("### 📈 Procedure Trends (Last 30 Days)")
    if not df_filtered.empty:
        last_30_days = datetime.today() - timedelta(days=30)
        df_trend = df_filtered[df_filtered['Date'] >= last_30_days]
        df_trend = df_trend.groupby([pd.Grouper(key="Date", freq="D")]).size().reset_index(name="Procedures")
        fig_line = px.line(df_trend, x="Date", y="Procedures", markers=True, color_discrete_sequence=["#1E90FF"])
        st.plotly_chart(fig_line, use_container_width=True)

        if len(df_trend) >= 2:
            df_trend['day_num'] = np.arange(len(df_trend))
            X = df_trend[['day_num']]
            y = df_trend['Procedures']
            model = LinearRegression().fit(X, y)
            future_days = np.arange(len(df_trend), len(df_trend)+7).reshape(-1,1)
            forecast = model.predict(future_days)
            future_dates = [df_trend['Date'].max() + timedelta(days=i+1) for i in range(7)]
            df_forecast = pd.DataFrame({'Date': future_dates, 'Procedures': forecast})
            fig_line.add_scatter(x=df_forecast['Date'], y=df_forecast['Procedures'], mode='lines+markers', name='Forecast', line=dict(dash='dash', color='red'))
            st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------
# Leaderboards Tab
# ---------------------------
with tabs[2]:
    st.markdown("### 🏆 Leaderboards")
    if not df_filtered.empty:
        # Surgeons
        lb_surgeons = df_filtered['surgeon'].value_counts().reset_index()
        lb_surgeons.columns = ['Surgeon', 'Procedures Done']
        fig_surgeon = px.bar(lb_surgeons, x='Surgeon', y='Procedures Done', color='Procedures Done', color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_surgeon, use_container_width=True)
        st.success(f"🏅 Top Surgeon: {lb_surgeons.iloc[0]['Surgeon']}")

        # Staff
        staff_series = df_filtered['staff'].str.split(",").explode().str.strip().dropna()
        lb_staff = staff_series.value_counts().reset_index()
        lb_staff.columns = ["Staff", "Appearances"]
        fig_staff = px.bar(lb_staff, x="Staff", y="Appearances", color="Appearances", color_continuous_scale=px.colors.sequential.Plasma)
        st.plotly_chart(fig_staff, use_container_width=True)
        st.success(f"🏅 Top Staff: {lb_staff.iloc[0]['Staff']}")

        # Hospitals
        lb_hosp = df_filtered['hospital'].value_counts().reset_index()
        lb_hosp.columns = ["Hospital", "Procedures"]
        fig_hosp = px.bar(lb_hosp, x="Hospital", y="Procedures", color="Procedures", color_continuous_scale=px.colors.sequential.Magenta)
        st.plotly_chart(fig_hosp, use_container_width=True)
        st.success(f"🏅 Top Hospital: {lb_hosp.iloc[0]['Hospital']}")

# ---------------------------
# Reports Tab
# ---------------------------
with tabs[3]:
    st.markdown("### 📝 Full Report")
    if df_filtered.empty:
        st.info("No data available.")
    else:
        st.dataframe(df_filtered.sort_values("Date", ascending=False))
        csv = df_filtered.to_csv(index=False)
        st.download_button("Download CSV", csv, "OrthoPulse_Report.csv", "text/csv")

        def create_pdf(dataframe):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=(800,1000))
            c.setFont("Helvetica", 12)
            y = 950
            for i, row in dataframe.iterrows():
                text = f"{row['Date'].date()} | {row['hospital']} | {row['procedure']} | {row['surgeon']} | {row['staff']}"
                c.drawString(30, y, text)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 950
            c.save()
            buffer.seek(0)
            return buffer

        pdf_file = create_pdf(df_filtered)
        st.download_button("Download PDF", pdf_file, "OrthoPulse_Report.pdf", "application/pdf")

# ---------------------------
# Add Procedure Tab
# ---------------------------
with tabs[4]:
    st.markdown("### ➕ Add Procedure")
    with st.form("add_proc_form"):
        date = st.date_input("Procedure Date", datetime.today())
        region = st.text_input("Region")
        hospital = st.text_input("Hospital")
        procedure = st.text_input("Procedure Type")
        surgeon = st.text_input("Surgeon Name")
        staff = st.text_input("Staff involved (comma separated)")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Procedure")
        if submitted:
            c.execute('INSERT INTO procedures (date, region, hospital, procedure, surgeon, staff, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (date.strftime("%Y-%m-%d"), region, hospital, procedure, surgeon, staff, notes))
            conn.commit()
            st.success("✅ Procedure Added Successfully!")
