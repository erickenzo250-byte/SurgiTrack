import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from io import BytesIO
from reportlab.pdfgen import canvas

# ---------------------------
# Page Config (line 6 fixed)
# ---------------------------
st.set_page_config(
    page_title="OrthoPulse Pro 🦴",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# Load Data
# ---------------------------
df_all = pd.read_sql_query("SELECT * FROM procedures", conn)
df_all["Date"] = pd.to_datetime(df_all["date"]) if not df_all.empty else pd.to_datetime([])

# ---------------------------
# Role Selection
# ---------------------------
role = st.sidebar.selectbox("Select Role", ["Admin", "Staff"])
staff_name = st.sidebar.text_input("Enter Your Name") if role == "Staff" else ""

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("Filters")
min_date = df_all['Date'].min() if not df_all.empty else datetime.today()
max_date = df_all['Date'].max() if not df_all.empty else datetime.today()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

regions = ["All"] + sorted(df_all['region'].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

hospitals = ["All"] + sorted(df_all['hospital'].dropna().unique().tolist())
selected_hospital = st.sidebar.selectbox("Hospital", hospitals)

procedures = ["All"] + sorted(df_all['procedure'].dropna().unique().tolist())
selected_procedure = st.sidebar.selectbox("Procedure Type", procedures)

surgeons = ["All"] + sorted(df_all['surgeon'].dropna().unique().tolist())
selected_surgeon = st.sidebar.selectbox("Surgeon", surgeons)

staff_filter = ["All"] + sorted(set(",".join(df_all['staff'].dropna()).split(", ")))
selected_staff = st.sidebar.selectbox("Staff", staff_filter)

# ---------------------------
# Data Filtering
# ---------------------------
df_filtered = df_all.copy()

if df_filtered.empty == False:
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

        # Forecast next 7 days using LinearRegression
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
    if df_filtered.empty:
        st.info("No data available.")
    else:
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

        # CSV download
        csv = df_filtered.to_csv(index=False)
        st.download_button("Download CSV", csv, "OrthoPulse_Report.csv", "text/csv")

        # PDF download
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
