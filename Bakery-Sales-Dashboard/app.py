import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set modern page layout
st.set_page_config(page_title="Habib Bakery Analytics", page_icon="🎂", layout="wide")

# Load and Enrich Data
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_bakery_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # INTERVIEW FLEX: The raw Kaggle data lacks customer IDs. 
    # We simulate 400 loyalty customers here to demonstrate Churn Analysis.
    np.random.seed(42)
    unique_txns = df['Transaction'].unique()
    customer_pool = [f'CUST_{str(i).zfill(3)}' for i in range(1, 401)]
    txn_to_cust = {txn: np.random.choice(customer_pool) for txn in unique_txns}
    df['Customer_ID'] = df['Transaction'].map(txn_to_cust)
    
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.title("Habib Bakery")
st.sidebar.markdown("**Hor Al Anz Branch Analytics**")
st.sidebar.divider()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Date'].min(), df['Date'].max()),
    min_value=df['Date'].min(),
    max_value=df['Date'].max()
)

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
else:
    filtered_df = df

# --- TOP KPIs ---
st.title("📊 Retail Sales & Customer Retention Dashboard")

total_revenue = filtered_df['Total_Sales_AED'].sum()
total_transactions = filtered_df['Transaction'].nunique()
top_item = filtered_df['Item'].value_counts().idxmax()

# --- CUSTOMER CHURN CALCULATION ---
# Retail standard: A customer is "Churned" if they haven't purchased in 30+ days
recent_date = filtered_df['Date'].max()
cust_last_purchase = filtered_df.groupby('Customer_ID')['Date'].max().reset_index()
cust_last_purchase['Days_Since'] = (recent_date - cust_last_purchase['Date']).dt.days
cust_last_purchase['Status'] = np.where(cust_last_purchase['Days_Since'] > 30, 'Churned', 'Active')
churn_rate = (cust_last_purchase['Status'] == 'Churned').mean() * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"AED {total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_transactions:,}")
col3.metric("Bestseller", top_item)
col4.metric("Customer Churn Rate", f"{churn_rate:.1f}%", "-Target < 40%", delta_color="inverse")

st.divider()

# --- DATA ANALYST INSIGHTS (CHARTS) ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Busiest Times of Day (Foot Traffic)")
    hourly_traffic = filtered_df.groupby('Hour')['Transaction'].nunique().reset_index()
    fig_hour = px.bar(hourly_traffic, x='Hour', y='Transaction', 
                      labels={'Transaction': 'Distinct Orders'},
                      color='Transaction', color_continuous_scale='Blues')
    fig_hour.update_layout(xaxis=dict(tickmode='linear', tick0=7, dtick=1))
    st.plotly_chart(fig_hour, use_container_width=True)

with col_right:
    st.subheader("Top 10 Selling Items (Volume)")
    top_items = filtered_df.groupby('Item')['Quantity'].sum().nlargest(10).reset_index()
    fig_items = px.bar(top_items, x='Quantity', y='Item', orientation='h',
                       color='Quantity', color_continuous_scale='Oranges')
    fig_items.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_items, use_container_width=True)

st.divider()

col_bottom1, col_bottom2 = st.columns(2)

with col_bottom1:
    st.subheader("Daily Revenue Trend")
    daily_revenue = filtered_df.groupby('Date')['Total_Sales_AED'].sum().reset_index()
    fig_trend = px.line(daily_revenue, x='Date', y='Total_Sales_AED', line_shape='spline')
    fig_trend.update_traces(line_color='#FF5722', line_width=3)
    st.plotly_chart(fig_trend, use_container_width=True)

with col_bottom2:
    st.subheader("Customer Retention Breakdown")
    churn_counts = cust_last_purchase['Status'].value_counts().reset_index()
    churn_counts.columns = ['Status', 'Count']
    fig_churn = px.pie(churn_counts, values='Count', names='Status', hole=0.4,
                       color='Status', color_discrete_map={'Active': '#43A047', 'Churned': '#E53935'})
    st.plotly_chart(fig_churn, use_container_width=True)