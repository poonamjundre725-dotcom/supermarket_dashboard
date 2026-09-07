# 🛒 SuperMarket Sales Dashboard

An interactive sales analytics dashboard built with **Streamlit** and **Plotly**, analyzing Q1 2019 supermarket transactions across three branches.

## 🔗 Live Demo
> Deploy link will appear here after Streamlit Cloud deployment.

## 📊 Features

- **KPI Cards** — Total sales, gross income, avg sale, avg rating at a glance
- **Branch Performance** — Compare revenue across Alex, Giza, and Cairo
- **Product Line Revenue** — Pie chart + ranked tables for all 6 product lines
- **Monthly Trend** — Dual-axis line + bar chart for sales and transactions
- **Payment Method Breakdown** — Ewallet vs Cash vs Credit Card
- **Rating Distribution** — Histogram with average line
- **Customer Type × Gender** — Avg spend grouped by membership and gender
- **Sidebar Filters** — Filter by Branch, Product Line, Customer Type, Gender, Payment
- **Raw Data Table** — Searchable, with CSV download

## 🗂️ Project Structure

```
supermarket-dashboard/
├── app.py               # Main Streamlit application
├── supermarket.csv      # Dataset (1,000 transactions, Q1 2019)
├── requirements.txt     # Python dependencies
├── .gitignore
└── README.md
```

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/supermarket-dashboard.git
cd supermarket-dashboard

# 2. Create and activate a virtual environment (optional but recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## ☁️ Deploy on Streamlit Cloud

1. Push this repository to GitHub (see steps below).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo → set **Main file path** to `app.py`.
4. Click **Deploy** — your app will be live in ~1 minute.

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web app framework |
| `pandas` | Data loading and transformation |
| `plotly` | Interactive charts |

## 📁 Dataset

| Field | Description |
|-------|-------------|
| Invoice ID | Unique transaction ID |
| Branch | Alex / Giza / Cairo |
| City | Yangon / Naypyitaw / Mandalay |
| Customer type | Member / Normal |
| Gender | Male / Female |
| Product line | 6 categories |
| Unit price | Price per item |
| Quantity | Units purchased |
| Sales | Total transaction value (incl. 5% tax) |
| Payment | Ewallet / Cash / Credit card |
| Date | Jan–Mar 2019 |
| Rating | Customer satisfaction (1–10) |

## 📄 License
MIT
