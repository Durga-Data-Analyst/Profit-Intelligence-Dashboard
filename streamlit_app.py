import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Profit Intelligence Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("APL_Logistics.csv", encoding="latin1")

df.columns = df.columns.str.strip()

st.write("Columns:", df.columns)

df['Profit Margin (%)'] = (df['Benefit per order'] / df['Sales']) * 100


# ---------------- SIDEBAR ----------------
st.sidebar.title("🔍 Filters")

segment = st.sidebar.multiselect("Customer Segment", df['Customer Segment'].unique(), default=df['Customer Segment'].unique())
market = st.sidebar.multiselect("Market", df['Market'].unique(), default=df['Market'].unique())
category = st.sidebar.multiselect("Category", df['Category Name'].unique(), default=df['Category Name'].unique())

discount_filter = st.sidebar.slider("Discount Rate", 0.0, 0.5, (0.0, 0.5))

# Apply filters
filtered_df = df[
    (df['Customer Segment'].isin(segment)) &
    (df['Market'].isin(market)) &
    (df['Category Name'].isin(category)) &
    (df['Order Item Discount Rate'].between(discount_filter[0], discount_filter[1]))
]

# ---------------- HEADER ----------------
st.title("📊 Profit Intelligence Dashboard")
st.markdown("Analyze profitability, customer value, and discount impact in one place")

# ---------------- KPI SECTION ----------------
col1, col2, col3 = st.columns(3)

total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Order Profit Per Order'].sum()
margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

col1.metric("💰 Revenue", f"${total_sales:,.0f}")
col2.metric("📈 Profit", f"${total_profit:,.0f}")
col3.metric("📊 Margin %", f"{margin:.2f}%")

st.markdown("---")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview",
    "👥 Customers",
    "📦 Products",
    "💸 Discount"
])

# ================= TAB 1 =================
with tab1:
    st.subheader("Revenue vs Profit Trend")

    if 'order date (DateOrders)' in filtered_df.columns:
        filtered_df['Order Date'] = pd.to_datetime(filtered_df['order date (DateOrders)'])
        filtered_df['Month'] = filtered_df['Order Date'].dt.to_period('M').astype(str)

        trend = filtered_df.groupby('Month')[['Sales', 'Order Profit Per Order']].sum().reset_index()

        fig = px.line(trend, x='Month', y=['Sales', 'Order Profit Per Order'], title="Trend Over Time")
        st.plotly_chart(fig, use_container_width=True)

# ================= TAB 2 =================
with tab2:
    st.subheader("Customer Value Analysis")

    customer = filtered_df.groupby('Customer Id')['Order Profit Per Order'].sum().reset_index()

    col1, col2 = st.columns(2)

    top = customer.nlargest(10, 'Order Profit Per Order')
    fig1 = px.bar(top, x='Customer Id', y='Order Profit Per Order', title="Top Customers")
    col1.plotly_chart(fig1, use_container_width=True)

    bottom = customer.nsmallest(10, 'Order Profit Per Order')
    fig2 = px.bar(bottom, x='Customer Id', y='Order Profit Per Order', title="Bottom Customers")
    col2.plotly_chart(fig2, use_container_width=True)

    segment_contribution = filtered_df.groupby('Customer Segment')['Order Profit Per Order'].sum().reset_index()
    fig3 = px.pie(segment_contribution, names='Customer Segment', values='Order Profit Per Order', title="Segment Contribution")
    st.plotly_chart(fig3, use_container_width=True)

# ================= TAB 3 =================
with tab3:
    st.subheader("Product & Category Performance")

    product = filtered_df.groupby('Product Name')['Profit Margin (%)'].mean().reset_index()
    product = product.sort_values(by='Profit Margin (%)', ascending=False).head(10)

    fig4 = px.bar(product, x='Product Name', y='Profit Margin (%)', title="Top Product Margins")
    st.plotly_chart(fig4, use_container_width=True)

    category = filtered_df.groupby('Category Name')['Profit Margin (%)'].mean().reset_index()
    fig5 = px.bar(category, x='Category Name', y='Profit Margin (%)', title="Category Profitability")
    st.plotly_chart(fig5, use_container_width=True)

# ================= TAB 4 =================
with tab4:
    st.subheader("Discount Impact Analysis")

    fig6 = px.scatter(
        filtered_df,
        x='Order Item Discount Rate',
        y='Profit Margin (%)',
        title="Discount vs Profit Margin"
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("What-if Scenario")

    discount = st.slider("Simulate Discount Rate", 0.0, 0.5, 0.1)
    estimated_margin = filtered_df['Profit Margin (%)'].mean() - (discount * 20)

    st.metric("Estimated Margin After Discount", f"{estimated_margin:.2f}%")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with Streamlit | Profit Intelligence Project")
