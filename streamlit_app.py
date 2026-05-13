import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Profit Intelligence Dashboard",
    layout="wide"
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data

def load_data():
    url = "https://drive.google.com/uc?id=13bBRo5yE8JIJbjiv4rvGfZdfA8A_akB5"
    df = pd.read_csv(url, encoding='latin1')
    
    # Clean columns
    df.columns = df.columns.str.strip()
    
    # Profit Margin
    df['Profit Margin (%)'] = (
    df['Benefit per order'] / df['Sales']
    ) * 100
    return df


df = load_data()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.title(" Dashboard Filters")

segment = st.sidebar.multiselect(
 "Customer Segment",
 options=df['Customer Segment'].unique(),
 default=df['Customer Segment'].unique()
)

market = st.sidebar.multiselect(
 "Market",
 options=df['Market'].unique(),
 default=df['Market'].unique()
)

category = st.sidebar.multiselect(
"Category",
options=df['Category Name'].unique(),
default=df['Category Name'].unique()
)

region = st.sidebar.multiselect(
"Order Region",
options=df['Order Region'].unique(),
default=df['Order Region'].unique()
)

# Discount slider
discount_filter = st.sidebar.slider(
"Discount Rate",
min_value=0.0,
max_value=0.5,
value=(0.0, 0.5)
)

# -------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------
filtered_df = df[
(df['Customer Segment'].isin(segment)) &
(df['Market'].isin(market)) &
(df['Category Name'].isin(category)) &
(df['Order Region'].isin(region)) &
(df['Order Item Discount Rate'].between(
discount_filter[0],
discount_filter[1]
)
)
]

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title(" Profit Intelligence Dashboard")
st.markdown("APL Logistics Supply Chain Projects")


# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
# KPI calculations
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Benefit per order'].sum()
profit_margin = (
total_profit / total_sales
) * 100 if total_sales != 0 else 0
avg_discount = filtered_df['Order Item Discount Rate'].mean() * 100

# KPI cards
col1.metric(
" Total Sales",
f"${total_sales:,.0f}"
)
col2.metric(
" Total Profit",
f"${total_profit:,.0f}"
)
col3.metric(
" Profit Margin",
f"{profit_margin:.2f}%"
)
col4.metric(
" Avg Discount",
f"{avg_discount:.2f}%"
)

st.markdown("---")
# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
" Revenue & Profit",
" Customer Analysis",
" Product Performance",
" Discount Analysis"
])
# =================================================
# TAB 1 - REVENUE & PROFIT OVERVIEW
# =================================================
with tab1:
    st.subheader("Revenue vs Profit Comparison")
    comparison_df = pd.DataFrame({
    'Metric': ['Sales', 'Profit'],
    'Value': [
    filtered_df['Sales'].sum(),
    filtered_df['Benefit per order'].sum()
    ]
    })

fig1 = px.bar(
comparison_df,
x='Metric',
y='Value',
text='Value',
title='Total Sales vs Total Profit'
)
fig1.update_traces(
texttemplate='%{text:.2s}',
textposition='outside'
)
fig1.update_layout(
height=500
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Market Level Profitability")
market_analysis = (
filtered_df
.groupby('Market', as_index=False)
.agg({
'Sales': 'sum',
'Benefit per order': 'sum'
})
)
market_analysis['Profit Margin (%)'] = (
market_analysis['Benefit per order'] /
market_analysis['Sales']
) * 100
fig2 = px.bar(
market_analysis,
x='Market',
y='Profit Margin (%)',
text='Profit Margin (%)',
title='Profit Margin by Market'
)
fig2.update_layout(height=500)
st.plotly_chart(fig2, use_container_width=True)

# =================================================
# TAB 2 - CUSTOMER ANALYSIS
# =================================================
with tab2:
    st.subheader("Customer Value Analysis")
    customer = (
    filtered_df
    .groupby('Customer Id', as_index=False)['Benefit per order']
    .sum()
    )
col_left, col_right = st.columns(2)
# Top Customers
top = customer.sort_values(
by='Benefit per order',
ascending=False
).head(10)
fig3 = px.bar(
top,
x='Benefit per order',
y='Customer Fname',
orientation='h',
text='Benefit per order',
title='Top Customers by Profit'
)
fig3.update_layout(
height=500,
yaxis={'categoryorder':'total ascending'}
)
col_left.plotly_chart(fig3, use_container_width=True)
# Bottom Customers
bottom = customer.sort_values(
by='Benefit per order',
ascending=True
).head(10)
fig4 = px.bar(
bottom,
x='Benefit per order',
y='Customer Fname',
orientation='h',
text='Benefit per order',
title='Bottom Customers by Profit'
)
fig4.update_layout(
height=500,
yaxis={'categoryorder':'total ascending'}
)

col_right.plotly_chart(fig4, use_container_width=True)
# Segment contribution
st.subheader("Customer Segment Contribution")
segment_df = (
filtered_df
.groupby('Customer Segment', as_index=False)['Benefit per order']
.sum()
)

fig5 = px.pie(
segment_df,
names='Customer Segment',
values='Benefit per order',
title='Profit Contribution by Customer Segment'
)
st.plotly_chart(fig5, use_container_width=True)
# =================================================
# TAB 3 - PRODUCT PERFORMANCE
# =================================================
with tab3:
    st.subheader("Product & Category Performance")
# Product margin analysis
product_df = (
filtered_df
.groupby('Product Name', as_index=False)
.agg({
'Sales': 'sum',
'Benefit per order': 'sum'
})
)
product_df['Profit Margin (%)'] = (
product_df['Benefit per order'] /
product_df['Sales']
) * 100

top_products = product_df.sort_values(
by='Profit Margin (%)',
ascending=False
).head(10)
fig6 = px.bar(
top_products,
x='Profit Margin (%)',
y='Product Name',
orientation='h',
text='Profit Margin (%)',
title='Top Product Margins'
)

fig6.update_layout(height=600)
st.plotly_chart(fig6, use_container_width=True)
# Category profitability
st.subheader("Category Profitability")
category_df = (
filtered_df
.groupby('Category Name', as_index=False)
.agg({
'Sales': 'sum',
'Benefit per order': 'sum'
})
)
category_df['Profit Margin (%)'] = (
category_df['Benefit per order'] /
category_df['Sales']
) * 100
fig7 = px.bar(
category_df,
x='Category Name',
y='Profit Margin (%)',
text='Profit Margin (%)',
title='Category Profitability Analysis'
)

fig7.update_layout(height=500)
st.plotly_chart(fig7, use_container_width=True)
# =================================================
# TAB 4 - DISCOUNT ANALYSIS
# =================================================
with tab4:
    st.subheader("Discount vs Profit Margin")
# Create discount buckets
discount_analysis = (
filtered_df
.groupby('Order Item Discount Rate', as_index=False)
.agg({
'Profit Margin (%)': 'mean'
})
)
# Better readable line chart instead of messy scatter
fig8 = px.line(
discount_analysis,
x='Order Item Discount Rate',
y='Profit Margin (%)',
markers=True,
title='Discount Rate vs Average Profit Margin'
)
fig8.update_layout(height=500)
st.plotly_chart(fig8, use_container_width=True)
# Discount bucket analysis
st.subheader("Discount Threshold Analysis")
filtered_df['Discount Bucket'] = pd.cut(
filtered_df['Order Item Discount Rate'],
bins=[0, 0.05, 0.10, 0.15, 0.20, 0.30],
labels=[
'0-5%',
'5-10%',
'10-15%',
'15-20%',
'20-30%'
]
)
bucket_df = (
filtered_df
.groupby('Discount Bucket', as_index=False)
.agg({
'Profit Margin (%)': 'mean'
})
)
fig9 = px.bar(
bucket_df,
x='Discount Bucket',
y='Profit Margin (%)',
text='Profit Margin (%)',
title='Profit Margin Across Discount Buckets'
)
fig9.update_layout(height=500)
st.plotly_chart(fig9, use_container_width=True)
# What-if simulation
st.subheader("What-if Discount Simulation")
simulation_discount = st.slider(
"Simulate Discount Rate",
0.0,
0.5,
0.1
)
estimated_margin = (
filtered_df['Profit Margin (%)'].mean()
- (simulation_discount * 20)
)
st.metric(
"Estimated Profit Margin",
f"{estimated_margin:.2f}%"
)
# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.caption(
"Built with Streamlit | Profit Intelligence Dashboard"
)
