# ✈️ Airline Booking Market Demand Dashboard

A modern Streamlit web application to analyze and visualize market demand for airline bookings using real-time data from the aviationstack API.

---

## 📊 Overview

This app fetches live flight departure data based on ICAO airport codes, identifies the top destination routes, and visualizes trends using interactive bar charts.

### 🔍 Features:
- Search by **ICAO code** (e.g., `YSSY`, `KJFK`)
- Real-time data fetching with **aviationstack API**
- View top 10 arrival airports from a selected departure airport
- Interactive **Plotly** bar chart visualization
- Built with **Streamlit** for a clean, responsive UI

---

## 📸 Screenshots

| Input ICAO Code | Sample Route Insights |
|------------------|------------------------|
| !<img width="1916" height="837" alt="image" src="https://github.com/user-attachments/assets/5d1c91ef-70ea-4f39-86e1-8cbcfa167c9c" />
 | !<img width="1557" height="832" alt="image" src="https://github.com/user-attachments/assets/6f151ded-b613-4e02-a96b-37a83c502926" />
|<img width="1511" height="759" alt="image" src="https://github.com/user-attachments/assets/50efe1d1-1ae9-427f-b398-445cd2d09da5" />
|

---

## 🏗️ Tech Stack

- **Python 3.11+**
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)
- [Aviationstack API](https://aviationstack.com/)
- Pandas, Requests, Altair, Pydeck

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/airline-demand-app.git
cd airline-demand-app


### 2. Install Dependencies

```bash
pip install -r requirements.txt

### 3. Run the App

```bash
streamlit run app.py

The app will open at http://localhost:8501

