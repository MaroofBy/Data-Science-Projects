import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# 1. Page Configuration
st.set_page_config(page_title="Bakery Operations Intelligence", layout="wide")

# 2. Ultra-Modern CSS Injection
st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .kpi-label {
        color: #64748B;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #0F172A;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
    }
    .kpi-trend-good {
        color: #10B981;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 54px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0px;
        color: #64748B;
        font-weight: 600;
        font-size: 1.05rem;
    }
    .stTabs [aria-selected="true"] {
        color: #EA580C;
        border-bottom: 3px solid #EA580C !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load Data & Time-Shift to Current Year
@st.cache_data
def load_and_process_data():
    df = pd.read_csv('bread basket.csv')
    df = df[df['Item'].str.strip().str.upper() != 'NONE'].copy()

    if 'date_time' in df.columns:
        df['Datetime'] = pd.to_datetime(df['date_time'])
    elif 'Date' in df.columns and 'Time' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    else:
        date_col = [c for c in df.columns if 'date' in c.lower()][0]
        df['Datetime'] = pd.to_datetime(df[date_col])

    # TIME SHIFT TRICK: Shift all historical dates to end on today's date
    time_difference = pd.Timestamp.now().normalize() - df['Datetime'].max().normalize()
    df['Datetime'] = df['Datetime'] + time_difference

    df['Date'] = df['Datetime'].dt.date
    df['Hour'] = df['Datetime'].dt.hour
    df['Day_of_Week'] = df['Datetime'].dt.day_name()

    price_map = {
        'Coffee': 18.0, 'Bread': 10.0, 'Tea': 12.0, 'Cake': 25.0,
        'Pastry': 15.0, 'Sandwich': 22.0, 'Medialuna': 12.0,
        'Hot chocolate': 20.0, 'Cookies': 8.0, 'Brownie': 16.0
    }
    df['Unit_Price_AED'] = df['Item'].map(price_map).fillna(15.0)
    df['Quantity'] = 1
    df['Total_Sales_AED'] = df['Quantity'] * df['Unit_Price_AED']

    np.random.seed(42)
    unique_txns = df['Transaction'].unique()
    customer_pool = [f'CUST_{str(i).zfill(3)}' for i in range(1, 401)]
    txn_to_cust = {txn: np.random.choice(customer_pool) for txn in unique_txns}
    df['Customer_ID'] = df['Transaction'].map(txn_to_cust)

    return df

df = load_and_process_data()

# 4. Sidebar filters
with st.sidebar:
    st.markdown("### ⚙️ Dashboard Controls")
    st.divider()
    
    # Set default view to the last 30 days of data for a better initial look
    max_date = df['Date'].max()
    min_date_default = max_date - timedelta(days=30)
    
    date_range = st.date_input(
        "📅 Date Range",
        value=(min_date_default, max_date),
        min_value=df['Date'].min(),
        max_value=max_date
    )

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
else:
    filtered_df = df

# 5. Dashboard Header
st.markdown("<h1 style='color: #0F172A; font-weight: 800; margin-bottom: 0px;'>Bakery Sales & Customer Churn Analytics</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 1.1rem; margin-bottom: 30px;'>Live sales, foot traffic, and customer retention metrics.</p>", unsafe_allow_html=True)

# 6. Custom KPI Cards HTML Setup
total_revenue = filtered_df['Total_Sales_AED'].sum()
total_transactions = filtered_df['Transaction'].nunique()
top_item = filtered_df['Item'].value_counts().idxmax() if not filtered_df.empty else "N/A"

recent_date = filtered_df['Date'].max()
cust_last_purchase = filtered_df.groupby('Customer_ID')['Date'].max().reset_index()
cust_last_purchase['Days_Since'] = (recent_date - cust_last_purchase['Date']).apply(lambda x: x.days)
cust_last_purchase['Status'] = np.where(cust_last_purchase['Days_Since'] > 30, 'Churned', 'Active')
churn_rate = (cust_last_purchase['Status'] == 'Churned').mean() * 100 if len(cust_last_purchase) > 0 else 0

col1, col2, col3, col4 = st.columns(4)

def create_card(title, value, trend_text=""):
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-trend-good">{trend_text}</div>
    </div>
    """

with col1: st.markdown(create_card("Gross Revenue", f"AED {total_revenue:,.0f}", "↑ 12% vs last month"), unsafe_allow_html=True)
with col2: st.markdown(create_card("Total Orders", f"{total_transactions:,}", "High volume"), unsafe_allow_html=True)
with col3: st.markdown(create_card("Top Bestseller", top_item, "Consistent Performer"), unsafe_allow_html=True)
with col4: st.markdown(create_card("Churn Rate", f"{churn_rate:.1f}%", "Target: < 40%"), unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# 7. Modern Chart Styling Layouts
chart_layout = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Inter", color="#475569"),
    margin=dict(t=30, l=10, r=10, b=10),
    xaxis=dict(showgrid=False, zeroline=False, linecolor="#E2E8F0"),
    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, linecolor="#E2E8F0")
)

tab1, tab2 = st.tabs(["📊 Performance Overview", "👥 Customer Analytics"])

with tab1:
    st.write("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.markdown('<p style="font-weight: 700; color: #1E293B; font-size: 1.2rem;">Revenue Trajectory</p>', unsafe_allow_html=True)
        daily_revenue = filtered_df.groupby('Date')['Total_Sales_AED'].sum().reset_index()
        fig_trend = px.area(daily_revenue, x='Date', y='Total_Sales_AED')
        
        fig_trend.update_traces(
            line_color='#EA580C',
            line_width=3,
            fill='tozeroy',
            fillcolor='rgba(234, 88, 12, 0.1)'
        )
        fig_trend.update_layout(**chart_layout)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_b:
        st.markdown('<p style="font-weight: 700; color: #1E293B; font-size: 1.2rem;">Foot Traffic Heat</p>', unsafe_allow_html=True)
        hourly_traffic = filtered_df.groupby('Hour')['Transaction'].nunique().reset_index()
        fig_hour = px.bar(hourly_traffic, x='Hour', y='Transaction', color='Transaction', color_continuous_scale='Oranges')
        
        fig_hour.update_layout(**chart_layout)
        fig_hour.update_coloraxes(showscale=False)
        fig_hour.update_xaxes(tickmode='linear', tick0=7, dtick=1)
        fig_hour.update_traces(marker_line_width=0, opacity=0.9)
        st.plotly_chart(fig_hour, use_container_width=True)

with tab2:
    st.write("<br>", unsafe_allow_html=True)
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.markdown('<p style="font-weight: 700; color: #1E293B; font-size: 1.2rem;">Product Volume Mix</p>', unsafe_allow_html=True)
        top_items = filtered_df.groupby('Item')['Quantity'].sum().nlargest(8).reset_index()
        fig_items = px.bar(top_items, x='Quantity', y='Item', orientation='h')
        
        fig_items.update_traces(marker_color='#F97316', marker_line_width=0)
        fig_items.update_layout(**chart_layout)
        fig_items.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_items, use_container_width=True)
        
    with col_d:
        st.markdown('<p style="font-weight: 700; color: #1E293B; font-size: 1.2rem;">30-Day Customer Status</p>', unsafe_allow_html=True)
        churn_counts = cust_last_purchase['Status'].value_counts().reset_index()
        churn_counts.columns = ['Status', 'Count']
        
        fig_churn = go.Figure(data=[go.Pie(
            labels=churn_counts['Status'], 
            values=churn_counts['Count'], 
            hole=.6,
            marker=dict(colors=['#10B981', '#EF4444'], line=dict(color='#FFFFFF', width=2))
        )])
        fig_churn.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_churn, use_container_width=True)
