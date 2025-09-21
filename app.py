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
st.set_page_config(page_title="OrthoPulse Pro 🦴", page_icon="🩺", layout="wide")
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

    start_date = datetime(datetime.today().year, 1, 1)
    end_date = datetime.today()
    delta_days = (end_date - start_date).days

    data = []
    for _ in range(num_records):
        date = start_date + timedelta(days=random.randint(0, delta_days))
        hospital = random.choice(hospitals)
        region = regions[hospital]
        procedure = random.choice(procedures)
        surgeon = random.choice(surgeons)
        staff = ", ".join(random.sample(staff_members, k=random.randint(1, 3)))
        notes = "Routine procedure"
        data.append((date.strftime("%Y-%m-%d"), region, hospital, procedure, surgeon, staff, notes))

    c.executemany(
        'INSERT INTO procedures (date, region, hospital, procedure, surgeon, staff, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
        data
    )
    conn.commit()
    st.success(f"✅ Generated {num_records} random procedures from January.")

# ---------------------------
# Load Data
# ---------------------------
df_all = pd.read_sql_query("SELECT * FROM procedures", conn)
if df_all.empty:
    generate_random_procedures(200)
    df_all = pd.read_sql_query("SELECT * FROM procedures", conn)
df_all["Date"] = pd.to_datetime(df_all["date"], errors='coerce')

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.header("👩‍⚕️ Sidebar")
role = st.sidebar.radio("Select Role", ["Admin", "Staff"])
staff_name = st.sidebar.text_input("Staff Name") if role=="Staff" else ""

min_date = df_all['Date'].min()
max_date = df_all['Date'].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])
regions = ["All"] + sorted(df_all['region'].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)
hospitals = ["All"] + sorted(df_all['hospital'].dropna().unique().tolist())
selected_hospital = st.sidebar.selectbox("Hospital", hospitals)
procedures = ["All"] + sorted(df_all['procedure'].dropna().unique().tolist())
selected_procedure = st.sidebar.selectbox("Procedure", procedures)
surgeons = ["All"] + sorted(df_all['surgeon'].dropna().unique().tolist())
selected_surgeon = st.sidebar.selectbox("Surgeon", surgeons)
staff_filter = ["All"] + sorted(set(",".join(df_all['staff'].dropna()).split(", ")))
selected_staff = st.sidebar.selectbox("Staff", staff_filter)

if st.sidebar.button("Generate Random Test Data"):
    generate_random_procedures(100)
    st.experimental_rerun()
if st.sidebar.button("Reset Filters"):
    st.experimental_rerun()

# ---------------------------
# Data Filtering
# ---------------------------
df_filtered = df_all[(df_all['Date'] >= pd.to_datetime(date_range[0])) &
                     (df_all['Date'] <= pd.to_datetime(date_range[1]))]
if selected_region != "All":
    df_filtered = df_filtered[df_filtered['region'] == selected_region]
if selected_hospital != "All":
    df_filtered = df_filtered[df_filtered['hospital'] == selected_hospital]
if selected_procedure != "All":
    df_filtered = df_filtered[df_filtered['procedure'] == selected_procedure]
if selected_surgeon != "All":
    df_filtered = df_filtered[df_filtered['surgeon'] == selected_surgeon]
if role=="Staff" and staff_name:
    df_filtered = df_filtered[df_filtered['staff'].str.contains(staff_name, case=False, na=False)]
elif selected_staff != "All":
    df_filtered = df_filtered[df_filtered['staff'].str.contains(selected_staff, case=False, na=False)]

# ---------------------------
# Tabs
# ---------------------------
tabs = st.tabs(["Metrics","Last 30 Days Trend","Linear Trend","Leaderboards","Reports","Add Procedure"])

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
# Last 30 Days Trend Tab
# ---------------------------
with tabs[1]:
    st.markdown("### 📈 Last 30 Days Trend")
    if not df_filtered.empty:
        last_30_days = datetime.today() - timedelta(days=30)
        df_trend = df_filtered[df_filtered['Date'] >= last_30_days].groupby(pd.Grouper(key="Date", freq="D")).size().reset_index(name="Procedures")
        fig_line = px.line(df_trend, x="Date", y="Procedures", markers=True, color_discrete_sequence=["#1E90FF"])
        st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------
# Linear Trend Tab (Monthly, Total Surgeries)
# ---------------------------
with tabs[2]:
    st.markdown("### 📊 Linear Trend: Total Surgeries from Jan to Now")
    if not df_filtered.empty:
        df_monthly = df_filtered.groupby(pd.Grouper(key="Date", freq="M")).size().reset_index(name="Total Procedures")
        df_monthly = df_monthly.sort_values("Date")
        df_monthly['month_num'] = np.arange(len(df_monthly))
        X = df_monthly[['month_num']]
        y = df_monthly['Total Procedures']
        model = LinearRegression().fit(X, y)
        df_monthly['Trend'] = model.predict(X)

        fig_trend = px.line(df_monthly, x="Date", y="Total Procedures", markers=True, color_discrete_sequence=["#1E90FF"])
        fig_trend.add_scatter(x=df_monthly['Date'], y=df_monthly['Trend'], mode='lines',
                              name='Linear Trend', line=dict(color='red', dash='dash'))
        st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------
# Leaderboards Tab
# ---------------------------
with tabs[3]:
    st.markdown("### 🏆 Leaderboards")
    if not df_filtered.empty:
        # Surgeons
        lb_surgeons = df_filtered['surgeon'].value_counts().reset_index()
        lb_surgeons.columns = ['Surgeon', 'Procedures Done']
        fig_surgeon = px.bar(lb_surgeons, x='Surgeon', y='Procedures Done', color='Procedures Done',
                             color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_surgeon, use_container_width=True)
        st.success(f"🏅 Top Surgeon: {lb_surgeons.iloc[0]['Surgeon']}")

        # Staff
        staff_series = df_filtered['staff'].str.split(",").explode().str.strip().dropna()
        lb_staff = staff_series.value_counts().reset_index()
        lb_staff.columns = ["Staff", "Appearances"]
        fig_staff = px.bar(lb_staff, x="Staff", y="Appearances", color="Appearances",
                           color_continuous_scale=px.colors.sequential.Plasma)
        st.plotly_chart(fig_staff, use_container_width=True)
        st.success(f"🏅 Top Staff: {lb_staff.iloc[0]['Staff']}")

        # Hospitals
        lb_hospitals = df_filtered['hospital'].value_counts().reset_index()
        lb_hospitals.columns = ["Hospital", "Procedures"]
        fig_hosp = px.bar(lb_hospitals, x="Hospital", y="Procedures", color="Procedures",
                          color_continuous_scale=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig_hosp, use_container_width=True)
        st.success(f"🏅 Top Hospital: {lb_hospitals.iloc[0]['Hospital']}")

# ---------------------------
# Reports Tab
# ---------------------------
with tabs[4]:
    st.markdown("### 📄 Reports")
    if not df_filtered.empty:
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "report.csv", "text/csv")
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.drawString(100, 800, "OrthoPulse Pro Report")
        y = 780
        for i, row in df_filtered.head(50).iterrows():
            pdf.drawString(50, y, f"{row['Date'].strftime('%Y-%m-%d')} | {row['hospital']} | {row['procedure']} | {row['surgeon']} | {row['staff']}")
            y -= 15
        pdf.save()
        st.download_button("Download PDF", buffer.getvalue(), "report.pdf", "application/pdf")

# ---------------------------
# Add Procedure Tab
# ---------------------------
with tabs[5]:
    st.markdown("### ➕ Add Procedure")
    with st.form("add_proc"):
        date_input = st.date_input("Date", datetime.today())
        region_input = st.text_input("Region")
        hospital_input = st.text_input("Hospital")
        procedure_input = st.text_input("Procedure")
        surgeon_input = st.text_input("Surgeon")
        staff_input = st.text_input("Staff (comma separated)")
        notes_input = st.text_area("Notes")
        submitted = st.form_submit_button("Add Procedure")
        if submitted:
            c.execute('INSERT INTO procedures (date, region, hospital, procedure, surgeon, staff, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (date_input.strftime("%Y-%m-%d"), region_input, hospital_input, procedure_input, surgeon_input, staff_input, notes_input))
            conn.commit()
            st.success("Procedure added successfully!")
            st.experimental_rerun()
