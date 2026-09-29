# 🥐 Retail Bakery Sales & Retention Dashboard

## 📌 Project Overview
This is an end-to-end data analytics project that transforms raw retail transaction logs into a fully interactive business intelligence dashboard. Built with Python and Streamlit, this project demonstrates data cleaning, feature engineering, and data visualization techniques to track revenue, optimize operations, and monitor customer churn.

## 🚀 Key Features
*   **Sales & Revenue Tracking:** Calculates total revenue, transaction counts, and identifies bestselling items dynamically based on date filters.
*   **Customer Churn Analysis:** Simulates a loyalty customer base to calculate retail churn rates (defined as customers who haven't made a purchase in 30+ days).
*   **Foot Traffic Insights:** Analyzes hourly transaction volume to identify peak business hours and optimize staffing.
*   **Interactive Visualizations:** Uses Plotly to render dynamic charts, including daily revenue trends, top-selling items by volume, and retention breakdowns.

## 🛠️ Tech Stack
*   **Language:** Python
*   **Data Processing:** Pandas, NumPy, Jupyter Notebook
*   **Dashboard Framework:** Streamlit
*   **Data Visualization:** Plotly Express

## 📂 Dataset Details
The initial data is based on the public **Bread Basket Dataset** from Kaggle, which contains over 20,000 raw retail transactions. 
*   **Data Cleaning:** Removed voided transactions and unified timestamp formatting.
*   **Feature Engineering:** Mapped realistic retail prices in AED (United Arab Emirates Dirham) to calculate revenue metrics and simulated unique customer IDs to enable advanced churn analytics.

## ⚙️ How to Run the Project Locally

### 1. Prerequisites
Ensure you have Python installed. Install the required libraries using pip:
```bash
pip install pandas numpy streamlit plotly
