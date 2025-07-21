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
| ![Input](https://i.imgur.com/8ZoM3Pp.png) | ![Chart](https://i.imgur.com/YV80A1n.png) |

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
