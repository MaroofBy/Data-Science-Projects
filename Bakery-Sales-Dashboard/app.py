import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration & Modern CSS
st.set_page_config(page_title="Bakery Analytics Dashboard", page_icon="🥐", layout="wide")

st.markdown("""
<style>
    /* Modern Dashboard Styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Style the metric numbers */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #D35400; /* Warm bakery orange */
    }
    /* Make tabs look like buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #F8F9FA;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFF3E0;
        color: #D35400;
        border-bottom: 3px solid #D35400;
    }
    /* Hide the default Streamlit menu for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 2. Load and Process Data (Directly from raw CSV)
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

# 3. Sidebar Configuration
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3014/3014495.png", width=60)
    st.title("Bakery Analytics")
    st.markdown("Retail Intelligence Center")
    st.divider()
    
    date_range = st.date_input(
        "📅 Select Date Range",
        value=(df['Date'].min(), df['Date'].max()),
        min_value=df['Date'].min(),
        max_value=df['Date'].max()
    )

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
else:
    filtered_df = df

# 4. Header & Top KPIs
st.title("📊 Retail Operations & Sales Dashboard")
st.markdown("Monitor revenue, track product performance, and analyze customer retention in real-time.")
st.write("") # Spacer

total_revenue = filtered_df['Total_Sales_AED'].sum()
total_transactions = filtered_df['Transaction'].nunique()
top_item = filtered_df['Item'].value_counts().idxmax() if not filtered_df.empty else "N/A"

recent_date = filtered_df['Date'].max()
cust_last_purchase = filtered_df.groupby('Customer_ID')['Date'].max().reset_index()
cust_last_purchase['Days_Since'] = (recent_date - cust_last_purchase['Date']).apply(lambda x: x.days)
cust_last_purchase['Status'] = np.where(cust_last_purchase['Days_Since'] > 30, 'Churned', 'Active')
churn_rate = (cust_last_purchase['Status'] == 'Churned').mean() * 100 if len(cust_last_purchase) > 0 else 0

# Display KPIs in a clean row
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Gross Revenue", f"AED {total_revenue:,.0f}")
with col2: st.metric("Total Orders", f"{total_transactions:,}")
with col3: st.metric("Top Bestseller", top_item)
with col4: st.metric("Churn Rate", f"{churn_rate:.1f}%", "-Target < 40%", delta_color="inverse")

st.divider()

# 5. Multi-Tab Layout for a Modern UX
tab1, tab2, tab3 = st.tabs(["📈 Sales Overview", "🥐 Product Analytics", "👥 Customer Retention"])

# Chart Styling Helper
def apply_chart_theme(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(color="#333333")
    )
    return fig

# --- TAB 1: Sales Overview ---
with tab1:
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("Daily Revenue Trend")
        daily_revenue = filtered_df.groupby('Date')['Total_Sales_AED'].sum().reset_index()
        fig_trend = px.area(daily_revenue, x='Date', y='Total_Sales_AED', line_shape='spline')
        fig_trend.update_traces(line_color='#D35400', fillcolor='rgba(211, 84, 0, 0.2)')
        st.plotly_chart(apply_chart_theme(fig_trend), use_container_width=True)
        
    with col_b:
        st.subheader("Foot Traffic by Hour")
        hourly_traffic = filtered_df.groupby('Hour')['Transaction'].nunique().reset_index()
        fig_hour = px.bar(hourly_traffic, x='Hour', y='Transaction', color='Transaction', color_continuous_scale='Oranges')
        fig_hour.update_layout(xaxis=dict(tickmode='linear', tick0=7, dtick=1), coloraxis_showscale=False)
        st.plotly_chart(apply_chart_theme(fig_hour), use_container_width=True)

# --- TAB 2: Product Analytics ---
with tab2:
    st.subheader("Top 10 Selling Items (Volume)")
    top_items = filtered_df.groupby('Item')['Quantity'].sum().nlargest(10).reset_index()
    fig_items = px.bar(top_items, x='Quantity', y='Item', orientation='h', color='Quantity', color_continuous_scale='YlOrBr')
    fig_items.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
    st.plotly_chart(apply_chart_theme(fig_items), use_container_width=True)

# --- TAB 3: Customer Retention ---
with tab3:
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.subheader("Customer Status (30-Day Window)")
        churn_counts = cust_last_purchase['Status'].value_counts().reset_index()
        churn_counts.columns = ['Status', 'Count']
        fig_churn = px.pie(churn_counts, values='Count', names='Status', hole=0.5, 
                           color='Status', color_discrete_map={'Active': '#2ECC71', 'Churned': '#E74C3C'})
        fig_churn.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(apply_chart_theme(fig_churn), use_container_width=True)
        
    with col_d:
        st.subheader("Retention Insights")
        st.info("💡 **Active Customers:** Have made at least one purchase in the last 30 days.")
        st.warning("⚠️ **Churned Customers:** Have not returned in over 30 days. Consider a targeted SMS or email campaign to re-engage this segment.")
        
        active_count = len(cust_last_purchase[cust_last_purchase['Status'] == 'Active'])
        churned_count = len(cust_last_purchase[cust_last_purchase['Status'] == 'Churned'])
        
        st.metric("Total Active Base", f"{active_count} Customers")
        st.metric("At-Risk Base", f"{churned_count} Customers")
