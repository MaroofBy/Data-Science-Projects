import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Bakery Analytics Dashboard", page_icon="🥐", layout="wide")

# Load and process raw Kaggle data directly
@st.cache_data
def load_and_process_data():
    df = pd.read_csv('bread basket.csv')

    # Drop voids and cancellations
    df = df[df['Item'].str.strip().str.upper() != 'NONE'].copy()

    # Parse timestamps
    if 'date_time' in df.columns:
        df['Datetime'] = pd.to_datetime(df['date_time'])
    elif 'Date' in df.columns and 'Time' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    else:
        date_col = [c for c in df.columns if 'date' in c.lower()][0]
        df['Datetime'] = pd.to_datetime(df[date_col])

    df['Date'] = df['Datetime'].dt.date
    df['Hour'] = df['Datetime'].dt.hour
    df['Day_of_Week'] = df['Datetime'].dt.day_name()

    # Pricing map in AED
    price_map = {
        'Coffee': 18.0, 'Bread': 10.0, 'Tea': 12.0, 'Cake': 25.0,
        'Pastry': 15.0, 'Sandwich': 22.0, 'Medialuna': 12.0,
        'Hot chocolate': 20.0, 'Cookies': 8.0, 'Brownie': 16.0
    }
    df['Unit_Price_AED'] = df['Item'].map(price_map).fillna(15.0)
    df['Quantity'] = 1
    df['Total_Sales_AED'] = df['Quantity'] * df['Unit_Price_AED']

    # Simulate 400 loyalty customers mapped to transactions for churn analysis
    np.random.seed(42)
    unique_txns = df['Transaction'].unique()
    customer_pool = [f'CUST_{str(i).zfill(3)}' for i in range(1, 401)]
    txn_to_cust = {txn: np.random.choice(customer_pool) for txn in unique_txns}
    df['Customer_ID'] = df['Transaction'].map(txn_to_cust)

    return df

df = load_and_process_data()

# Sidebar date filtering
st.sidebar.title("Bakery Analytics")
st.sidebar.markdown("**Retail Operations & Churn**")
st.sidebar.divider()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Date'].min(), df['Date'].max()),
    min_value=df['Date'].min(),
    max_value=df['Date'].max()
)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
else:
    filtered_df = df

# Top KPIs
st.title("📊 Retail Bakery Sales & Customer Retention Dashboard")

total_revenue = filtered_df['Total_Sales_AED'].sum()
total_transactions = filtered_df['Transaction'].nunique()
top_item = filtered_df['Item'].value_counts().idxmax() if not filtered_df.empty else "N/A"

# Churn logic (30-day non-purchase threshold)
recent_date = filtered_df['Date'].max()
cust_last_purchase = filtered_df.groupby('Customer_ID')['Date'].max().reset_index()
cust_last_purchase['Days_Since'] = (recent_date - cust_last_purchase['Date']).apply(lambda x: x.days)
cust_last_purchase['Status'] = np.where(cust_last_purchase['Days_Since'] > 30, 'Churned', 'Active')
churn_rate = (cust_last_purchase['Status'] == 'Churned').mean() * 100 if len(cust_last_purchase) > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"AED {total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_transactions:,}")
col3.metric("Bestseller", top_item)
col4.metric("Customer Churn Rate", f"{churn_rate:.1f}%", "-Target < 40%", delta_color="inverse")

st.divider()

# Charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Busiest Times of Day (Foot Traffic)")
    hourly_traffic = filtered_df.groupby('Hour')['Transaction'].nunique().reset_index()
    fig_hour = px.bar(
        hourly_traffic,
        x='Hour',
        y='Transaction',
        labels={'Transaction': 'Distinct Orders'},
        color='Transaction',
        color_continuous_scale='Blues'
    )
    fig_hour.update_layout(xaxis=dict(tickmode='linear', tick0=7, dtick=1))
    st.plotly_chart(fig_hour, use_container_width=True)

with col_right:
    st.subheader("Top 10 Selling Items (Volume)")
    top_items = filtered_df.groupby('Item')['Quantity'].sum().nlargest(10).reset_index()
    fig_items = px.bar(
        top_items,
        x='Quantity',
        y='Item',
        orientation='h',
        color='Quantity',
        color_continuous_scale='Oranges'
    )
    fig_items.update_layout(yaxis={'categoryorder': 'total ascending'})
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
    fig_churn = px.pie(
        churn_counts,
        values='Count',
        names='Status',
        hole=0.4,
        color='Status',
        color_discrete_map={'Active': '#43A047', 'Churned': '#E53935'}
    )
    st.plotly_chart(fig_churn, use_container_width=True)
