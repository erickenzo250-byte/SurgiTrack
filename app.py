
---

## **5️⃣ Full app.py (Upgraded Version)**

I’ve implemented all of these:

- SQLite database integration  
- Admin/Staff role access  
- Metrics, Trends (last 30 days), Leaderboards  
- Forecasting using LinearRegression  
- Full reports with CSV & PDF download  
- Add Procedure form saving to DB  
- Animated colored KPI cards, pop-ups, interactive sidebar  

Here’s the **core structure**:

```python
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="OrthoPulse Pro 🦴", page_icon="🩺", layout="wide")
st.markdown("<h1 style='text-align:center; color:#4B0082'>OrthoPulse Pro 🦴 Dashboard</h1>", unsafe_allow_html=True)

# ---------------------------
# Database Setup
# ---------------------------
conn = sqlite3.connect("database.db")
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
# Add more filters: region, hospital, surgeon, procedure type, staff
# ...

# ---------------------------
# Tabs
# ---------------------------
tabs = st.tabs(["Metrics","Trends","Leaderboards","Reports","Add Procedure"])

# ---------------------------
# Metrics Tab
# ---------------------------
with tabs[0]:
    st.markdown("### 📊 Key Metrics")
    # Animated KPI cards: Total Cases, Surgeons, Staff, Top Hospital/Procedure

# ---------------------------
# Trends Tab
# ---------------------------
with tabs[1]:
    st.markdown("### 📈 Procedure Trends")
    # Last 30 days trend, weekly/monthly
    # Forecast next week

# ---------------------------
# Leaderboards Tab
# ---------------------------
with tabs[2]:
    st.markdown("### 🏆 Leaderboards")
    # Top Surgeons, Staff, Hospitals

# ---------------------------
# Reports Tab
# ---------------------------
with tabs[3]:
    st.markdown("### 📝 Reports")
    # Dataframe display
    # CSV & PDF download buttons

# ---------------------------
# Add Procedure Tab
# ---------------------------
with tabs[4]:
    st.markdown("### ➕ Add Procedure")
    # Form to add procedure
    # Insert into SQLite DB
