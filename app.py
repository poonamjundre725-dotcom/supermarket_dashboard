import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SuperMarket Sales Dashboard",
    page_icon="🛒",
    layout="wide",
)

# ── Currency helpers ──────────────────────────────────────────────────────────
USD_TO_INR = 83.5  # approximate conversion rate

def to_inr(usd_value: float) -> float:
    return usd_value * USD_TO_INR

def fmt_inr(value: float) -> str:
    """Format number as Indian Rupees with ₹ symbol and comma separation."""
    return f"₹{value:,.0f}"

# ── Expected columns for auto-detection ──────────────────────────────────────
REQUIRED_COLS = {
    "sales_col":    ["Sales", "sales", "Total", "total", "Revenue", "Amount"],
    "branch_col":   ["Branch", "branch", "Store", "store", "Location"],
    "product_col":  ["Product line", "Product", "Category", "product_line", "category"],
    "payment_col":  ["Payment", "payment", "Payment Method", "PaymentMethod"],
    "rating_col":   ["Rating", "rating", "Score", "score"],
    "ctype_col":    ["Customer type", "CustomerType", "customer_type", "Member Type"],
    "gender_col":   ["Gender", "gender", "Sex"],
    "date_col":     ["Date", "date", "Transaction Date"],
    "qty_col":      ["Quantity", "quantity", "Qty", "qty", "Units"],
    "income_col":   ["gross income", "Gross Income", "GrossIncome", "Income", "Profit"],
}

def detect_col(df: pd.DataFrame, candidates: list) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None

# ── Load / Upload data ────────────────────────────────────────────────────────
st.sidebar.header("📂 Data Source")
upload_mode = st.sidebar.radio("Choose data source", ["Use sample dataset", "Upload my own CSV"])

@st.cache_data
def load_default():
    df = pd.read_csv("supermarket.csv", encoding="utf-8-sig")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

if upload_mode == "Upload my own CSV":
    uploaded = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
    if uploaded is None:
        st.info("👆 Upload a CSV file from the sidebar to get started.")
        st.markdown("""
        ### 📋 Expected Columns
        Your CSV should have columns similar to:

        | Column | Examples |
        |--------|---------|
        | Branch / Store | Alex, Branch A |
        | Product line / Category | Electronics, Food |
        | Sales / Revenue / Total | 250.00 |
        | Payment | Cash, Ewallet, Credit card |
        | Rating / Score | 7.5 |
        | Customer type | Member, Normal |
        | Gender | Male, Female |
        | Date | 1/5/2019 |
        | Quantity / Qty | 3 |
        | Gross income / Profit | 12.5 |

        > ℹ️ Column names are auto-detected — exact match not required.
        """)
        st.stop()
    df = pd.read_csv(uploaded, encoding="utf-8-sig")
    try:
        date_col = detect_col(df, REQUIRED_COLS["date_col"])
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], infer_datetime_format=True, errors="coerce")
    except Exception:
        pass
else:
    df = load_default()

# ── Auto-detect column names ──────────────────────────────────────────────────
COL = {k: detect_col(df, v) for k, v in REQUIRED_COLS.items()}

# Validate at least sales column exists
if COL["sales_col"] is None:
    st.error("❌ Could not find a Sales/Revenue column. Please check your CSV headers.")
    st.write("**Detected columns:**", list(df.columns))
    st.stop()

# Convert sales to INR
sales_col = COL["sales_col"]
df["_sales_inr"] = to_inr(df[sales_col].astype(float))

if COL["income_col"]:
    df["_income_inr"] = to_inr(df[COL["income_col"]].astype(float))

# Parse month if date available
if COL["date_col"] and pd.api.types.is_datetime64_any_dtype(df[COL["date_col"]]):
    df["_month"] = df[COL["date_col"]].dt.strftime("%B")
    df["_month_num"] = df[COL["date_col"]].dt.month
    has_date = True
else:
    has_date = False

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.header("🔍 Filters")

def make_filter(label, col):
    if col and col in df.columns:
        opts = sorted(df[col].dropna().unique().tolist())
        return st.sidebar.multiselect(label, options=opts, default=opts)
    return None

f_branch  = make_filter("Branch",         COL["branch_col"])
f_product = make_filter("Product Line",   COL["product_col"])
f_ctype   = make_filter("Customer Type",  COL["ctype_col"])
f_gender  = make_filter("Gender",         COL["gender_col"])
f_payment = make_filter("Payment Method", COL["payment_col"])

# Build filter mask
mask = pd.Series([True] * len(df), index=df.index)
if f_branch  and COL["branch_col"]:  mask &= df[COL["branch_col"]].isin(f_branch)
if f_product and COL["product_col"]: mask &= df[COL["product_col"]].isin(f_product)
if f_ctype   and COL["ctype_col"]:   mask &= df[COL["ctype_col"]].isin(f_ctype)
if f_gender  and COL["gender_col"]:  mask &= df[COL["gender_col"]].isin(f_gender)
if f_payment and COL["payment_col"]: mask &= df[COL["payment_col"]].isin(f_payment)

filtered = df[mask].copy()

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🛒 SuperMarket Sales Dashboard")
if upload_mode == "Upload my own CSV":
    st.caption(f"Analysing uploaded file · {len(filtered):,} transactions · All amounts in ₹ INR")
else:
    st.caption("Q1 2019 · Alex (Yangon) · Giza (Naypyitaw) · Cairo (Mandalay) · All amounts in ₹ INR")

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ── KPI row ───────────────────────────────────────────────────────────────────
total_sales_inr  = filtered["_sales_inr"].sum()
avg_sale_inr     = filtered["_sales_inr"].mean()
total_income_inr = filtered["_income_inr"].sum() if COL["income_col"] else None
avg_rating       = filtered[COL["rating_col"]].mean() if COL["rating_col"] else None

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Transactions", f"{len(filtered):,}")
c2.metric("Total Sales", fmt_inr(total_sales_inr))
c3.metric("Gross Income",  fmt_inr(total_income_inr) if total_income_inr else "N/A")
c4.metric("Avg Sale / Txn", fmt_inr(avg_sale_inr))
c5.metric("Avg Rating", f"{avg_rating:.2f} / 10" if avg_rating else "N/A")

st.divider()

# ── Row 1: Branch | Product Line ──────────────────────────────────────────────
r1c1, r1c2 = st.columns(2)

with r1c1:
    if COL["branch_col"]:
        branch_df = (
            filtered.groupby(COL["branch_col"])["_sales_inr"]
            .sum().reset_index()
            .sort_values("_sales_inr", ascending=False)
        )
        branch_df.columns = ["Branch", "Sales (₹)"]
        fig = px.bar(
            branch_df, x="Branch", y="Sales (₹)",
            title="Total Sales by Branch (₹)",
            color="Branch",
            color_discrete_sequence=px.colors.qualitative.Set2,
            text_auto=".2s",
        )
        fig.update_layout(showlegend=False, height=340)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Branch column detected.")

with r1c2:
    if COL["product_col"]:
        prod_df = (
            filtered.groupby(COL["product_col"])["_sales_inr"]
            .sum().reset_index()
            .sort_values("_sales_inr", ascending=False)
        )
        prod_df.columns = ["Product Line", "Sales (₹)"]
        fig = px.pie(
            prod_df, values="Sales (₹)", names="Product Line",
            title="Revenue Share by Product Line (₹)",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.35,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=340, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Product Line column detected.")

# ── Row 2: Monthly Trend | Payment ────────────────────────────────────────────
r2c1, r2c2 = st.columns(2)

with r2c1:
    if has_date:
        monthly_df = (
            filtered.groupby(["_month_num", "_month"])
            .agg(Sales=("_sales_inr", "sum"), Transactions=("_sales_inr", "count"))
            .reset_index().sort_values("_month_num")
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly_df["_month"], y=monthly_df["Sales"],
            name="Sales (₹)", marker_color="#3b82d4", yaxis="y1",
        ))
        fig.add_trace(go.Scatter(
            x=monthly_df["_month"], y=monthly_df["Transactions"],
            name="Transactions", mode="lines+markers",
            marker=dict(color="#d4a028", size=8), line=dict(width=2),
            yaxis="y2",
        ))
        fig.update_layout(
            title="Monthly Sales (₹) & Transactions",
            yaxis=dict(title="Sales (₹)"),
            yaxis2=dict(title="Transactions", overlaying="y", side="right"),
            legend=dict(orientation="h", y=-0.2), height=340,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Date column detected for monthly trend.")

with r2c2:
    if COL["payment_col"]:
        pay_df = (
            filtered.groupby(COL["payment_col"])
            .agg(Transactions=("_sales_inr", "count"), Sales=("_sales_inr", "sum"))
            .reset_index()
        )
        pay_df.columns = ["Payment", "Transactions", "Sales (₹)"]
        fig = px.bar(
            pay_df, x="Payment", y=["Transactions", "Sales (₹)"],
            title="Payment Method Breakdown",
            barmode="group",
            color_discrete_sequence=["#7c5cd8", "#3b82d4"],
            text_auto=".2s",
        )
        fig.update_layout(height=340, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Payment column detected.")

# ── Row 3: Rating Dist | Customer Type × Gender ───────────────────────────────
r3c1, r3c2 = st.columns(2)

with r3c1:
    if COL["rating_col"]:
        fig = px.histogram(
            filtered, x=COL["rating_col"], nbins=20,
            title="Customer Rating Distribution",
            color_discrete_sequence=["#2da44e"],
        )
        fig.add_vline(
            x=filtered[COL["rating_col"]].mean(),
            line_dash="dash", line_color="#cf3d3d",
            annotation_text=f"Avg {filtered[COL['rating_col']].mean():.2f}",
            annotation_position="top right",
        )
        fig.update_layout(height=320, bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Rating column detected.")

with r3c2:
    if COL["ctype_col"] and COL["gender_col"]:
        cg_df = (
            filtered.groupby([COL["ctype_col"], COL["gender_col"]])["_sales_inr"]
            .mean().reset_index()
        )
        cg_df.columns = ["Customer Type", "Gender", "Avg Sale (₹)"]
        fig = px.bar(
            cg_df, x="Customer Type", y="Avg Sale (₹)", color="Gender",
            barmode="group",
            title="Avg Sale (₹) — Customer Type × Gender",
            color_discrete_sequence=["#3b82d4", "#7c5cd8"],
            text_auto=".2s",
        )
        fig.update_layout(height=320, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)
    elif COL["ctype_col"]:
        ct_df = filtered.groupby(COL["ctype_col"])["_sales_inr"].mean().reset_index()
        ct_df.columns = ["Customer Type", "Avg Sale (₹)"]
        fig = px.bar(ct_df, x="Customer Type", y="Avg Sale (₹)",
                     title="Avg Sale (₹) by Customer Type",
                     color_discrete_sequence=["#3b82d4"], text_auto=".2s")
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Customer Type / Gender column detected.")

# ── Row 4: Avg Rating by Product | Gross Income by Branch ────────────────────
r4c1, r4c2 = st.columns(2)

with r4c1:
    if COL["product_col"] and COL["rating_col"]:
        rp_df = (
            filtered.groupby(COL["product_col"])[COL["rating_col"]]
            .mean().reset_index().sort_values(COL["rating_col"], ascending=True)
        )
        rp_df.columns = ["Product Line", "Avg Rating"]
        fig = px.bar(
            rp_df, x="Avg Rating", y="Product Line", orientation="h",
            title="Avg Rating by Product Line",
            color="Avg Rating", color_continuous_scale="Blues",
            text_auto=".2f",
        )
        fig.update_layout(height=320, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

with r4c2:
    if COL["branch_col"] and COL["income_col"]:
        ib_df = (
            filtered.groupby(COL["branch_col"])["_income_inr"]
            .sum().reset_index().sort_values("_income_inr", ascending=False)
        )
        ib_df.columns = ["Branch", "Gross Income (₹)"]
        fig = px.funnel(
            ib_df, x="Gross Income (₹)", y="Branch",
            title="Gross Income (₹) by Branch",
            color_discrete_sequence=["#3b82d4"],
        )
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Summary table ─────────────────────────────────────────────────────────────
if COL["branch_col"]:
    st.subheader("📊 Branch Summary (₹)")
    summary = filtered.groupby(COL["branch_col"]).agg(
        Transactions=("_sales_inr", "count"),
        Total_Sales=("_sales_inr", "sum"),
        Avg_Sale=("_sales_inr", "mean"),
    ).reset_index()
    if COL["income_col"]:
        inc = filtered.groupby(COL["branch_col"])["_income_inr"].sum().reset_index()
        inc.columns = [COL["branch_col"], "Gross_Income"]
        summary = summary.merge(inc, on=COL["branch_col"])
    if COL["rating_col"]:
        rat = filtered.groupby(COL["branch_col"])[COL["rating_col"]].mean().reset_index()
        rat.columns = [COL["branch_col"], "Avg_Rating"]
        summary = summary.merge(rat, on=COL["branch_col"])

    summary = summary.rename(columns={COL["branch_col"]: "Branch"})
    for col in ["Total_Sales", "Avg_Sale", "Gross_Income"]:
        if col in summary.columns:
            summary[col] = summary[col].apply(fmt_inr)
    if "Avg_Rating" in summary.columns:
        summary["Avg_Rating"] = summary["Avg_Rating"].round(2)
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ── Raw data ──────────────────────────────────────────────────────────────────
with st.expander("📋 View Raw Data"):
    display_cols = [c for c in [
        COL["branch_col"], COL["product_col"], COL["ctype_col"],
        COL["gender_col"], COL["payment_col"], COL["date_col"],
        COL["qty_col"], sales_col, COL["rating_col"]
    ] if c is not None]
    st.dataframe(filtered[display_cols].reset_index(drop=True),
                 use_container_width=True, height=320)
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=filtered[display_cols].to_csv(index=False).encode("utf-8"),
        file_name="supermarket_filtered.csv",
        mime="text/csv",
    )

st.caption(f"💱 USD → INR conversion rate used: ₹{USD_TO_INR} per $1  ·  Made with ❤️ using Streamlit")
