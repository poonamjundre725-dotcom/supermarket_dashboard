import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SuperMarket Sales Dashboard",
    page_icon="🛒",
    layout="wide",
)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("supermarket.csv", encoding="utf-8-sig")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.strftime("%B")
    df["Month_num"] = df["Date"].dt.month
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("🔍 Filters")

branches = st.sidebar.multiselect(
    "Branch", options=sorted(df["Branch"].unique()), default=sorted(df["Branch"].unique())
)
product_lines = st.sidebar.multiselect(
    "Product Line", options=sorted(df["Product line"].unique()), default=sorted(df["Product line"].unique())
)
customer_types = st.sidebar.multiselect(
    "Customer Type", options=sorted(df["Customer type"].unique()), default=sorted(df["Customer type"].unique())
)
genders = st.sidebar.multiselect(
    "Gender", options=sorted(df["Gender"].unique()), default=sorted(df["Gender"].unique())
)
payments = st.sidebar.multiselect(
    "Payment Method", options=sorted(df["Payment"].unique()), default=sorted(df["Payment"].unique())
)

# Apply filters
mask = (
    df["Branch"].isin(branches)
    & df["Product line"].isin(product_lines)
    & df["Customer type"].isin(customer_types)
    & df["Gender"].isin(genders)
    & df["Payment"].isin(payments)
)
filtered = df[mask]

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🛒 SuperMarket Sales Dashboard")
st.caption("Q1 2019 · Alex (Yangon) · Giza (Naypyitaw) · Cairo (Mandalay)")

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ── KPI row ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Transactions", f"{len(filtered):,}")
col2.metric("Total Sales", f"${filtered['Sales'].sum():,.0f}")
col3.metric("Gross Income", f"${filtered['gross income'].sum():,.0f}")
col4.metric("Avg Sale / Txn", f"${filtered['Sales'].mean():,.2f}")
col5.metric("Avg Rating", f"{filtered['Rating'].mean():.2f} / 10")

st.divider()

# ── Row 1: Branch sales  |  Product line ─────────────────────────────────────
r1c1, r1c2 = st.columns(2)

with r1c1:
    branch_df = (
        filtered.groupby("Branch")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )
    fig = px.bar(
        branch_df, x="Branch", y="Sales",
        title="Total Sales by Branch",
        color="Branch",
        color_discrete_sequence=px.colors.qualitative.Set2,
        text_auto=".2s",
    )
    fig.update_layout(showlegend=False, height=340)
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    prod_df = (
        filtered.groupby("Product line")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )
    fig = px.pie(
        prod_df, values="Sales", names="Product line",
        title="Revenue Share by Product Line",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.35,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=340, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Monthly trend  |  Payment method ──────────────────────────────────
r2c1, r2c2 = st.columns(2)

with r2c1:
    monthly_df = (
        filtered.groupby(["Month_num", "Month"])
        .agg(Sales=("Sales", "sum"), Transactions=("Sales", "count"))
        .reset_index()
        .sort_values("Month_num")
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_df["Month"], y=monthly_df["Sales"],
        name="Sales ($)", marker_color="#3b82d4", yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=monthly_df["Month"], y=monthly_df["Transactions"],
        name="Transactions", mode="lines+markers",
        marker=dict(color="#d4a028", size=8), line=dict(width=2),
        yaxis="y2",
    ))
    fig.update_layout(
        title="Monthly Sales & Transactions",
        yaxis=dict(title="Sales ($)"),
        yaxis2=dict(title="Transactions", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.2),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)

with r2c2:
    pay_df = (
        filtered.groupby("Payment")
        .agg(Transactions=("Sales", "count"), Sales=("Sales", "sum"))
        .reset_index()
    )
    fig = px.bar(
        pay_df, x="Payment", y=["Transactions", "Sales"],
        title="Payment Method Breakdown",
        barmode="group",
        color_discrete_sequence=["#7c5cd8", "#3b82d4"],
        text_auto=".2s",
    )
    fig.update_layout(height=340, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Rating distribution  |  Customer type vs gender ───────────────────
r3c1, r3c2 = st.columns(2)

with r3c1:
    fig = px.histogram(
        filtered, x="Rating", nbins=20,
        title="Customer Rating Distribution",
        color_discrete_sequence=["#2da44e"],
    )
    fig.add_vline(
        x=filtered["Rating"].mean(), line_dash="dash", line_color="#cf3d3d",
        annotation_text=f"Avg {filtered['Rating'].mean():.2f}",
        annotation_position="top right",
    )
    fig.update_layout(height=320, bargap=0.05)
    st.plotly_chart(fig, use_container_width=True)

with r3c2:
    cg_df = (
        filtered.groupby(["Customer type", "Gender"])["Sales"]
        .agg(["sum", "mean", "count"])
        .reset_index()
        .rename(columns={"sum": "Total Sales", "mean": "Avg Sale", "count": "Transactions"})
    )
    fig = px.bar(
        cg_df, x="Customer type", y="Avg Sale", color="Gender",
        barmode="group",
        title="Avg Sale — Customer Type × Gender",
        color_discrete_sequence=["#3b82d4", "#7c5cd8"],
        text_auto=".2f",
    )
    fig.update_layout(height=320, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 4: Avg rating by product line  |  Gross income by branch ─────────────
r4c1, r4c2 = st.columns(2)

with r4c1:
    rating_prod = (
        filtered.groupby("Product line")["Rating"]
        .mean()
        .reset_index()
        .sort_values("Rating", ascending=True)
    )
    fig = px.bar(
        rating_prod, x="Rating", y="Product line",
        orientation="h",
        title="Avg Rating by Product Line",
        color="Rating",
        color_continuous_scale="Blues",
        text_auto=".2f",
    )
    fig.update_layout(height=320, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with r4c2:
    income_branch = (
        filtered.groupby("Branch")["gross income"]
        .sum()
        .reset_index()
        .sort_values("gross income", ascending=False)
    )
    fig = px.funnel(
        income_branch, x="gross income", y="Branch",
        title="Gross Income by Branch",
        color_discrete_sequence=["#3b82d4"],
    )
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Raw data table (expandable) ───────────────────────────────────────────────
with st.expander("📋 View Raw Data"):
    st.dataframe(
        filtered[[
            "Invoice ID", "Branch", "City", "Customer type", "Gender",
            "Product line", "Unit price", "Quantity", "Sales",
            "Payment", "Date", "Rating",
        ]].reset_index(drop=True),
        use_container_width=True,
        height=350,
    )
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="supermarket_filtered.csv",
        mime="text/csv",
    )

st.caption("Made with ❤️ using Streamlit · Data: SuperMarket Q1 2019")
