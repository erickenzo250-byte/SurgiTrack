# OrthoPulse Pro 🦴

OrthoPulse Pro is a **sophisticated orthopedic procedure tracker** for hospitals and technical teams.  
It provides **metrics, trends, leaderboards, reports**, and allows **adding new procedures dynamically**.

## Features

- Real-time metrics: total cases, active surgeons, staff coverage
- Procedure trends (weekly, last 1 month)
- Leaderboards for surgeons and staff
- Reports export (CSV)
- Add new procedures
- Interactive charts with Plotly
- Optional forecast of next week procedures (requires scikit-learn)

## Requirements

- Python 3.10+
- Streamlit
- Pandas
- Plotly
- NumPy
- scikit-learn (optional, for forecasting)

## Installation

```bash
git clone https://github.com/yourusername/OrthoPulse-Pro.git
cd OrthoPulse-Pro
pip install -r requirements.txt
streamlit run app.py
