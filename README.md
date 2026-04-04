# 👥 Project 2 — Customer Segmentation Analysis

> RFM-based customer segmentation using K-Means clustering.
> Identifies Champions, Loyal Customers, and At-Risk segments with actionable retention strategies.

---

## 🔥 Live Demo

Open `dashboard/index.html` — click segments to explore RFM profiles, charts update live.

---

## 📁 Project Structure

```
project2-customer-segmentation/
│
├── data/
│   ├── sales_data.csv          ← Source transactions (from Project 1)
│   ├── rfm_segments.csv        ← 500 customers with RFM + segment labels
│   └── segment_summary.csv     ← Aggregated metrics per segment
│
├── notebooks/
│   └── 01_rfm_kmeans.py        ← Full ML pipeline: RFM → Scaler → KMeans → Labels
│
├── sql/
│   └── segmentation_queries.sql ← RFM scoring, cohort analysis, CLV queries
│
├── models/                     ← (model artifacts if saved via joblib)
│
├── dashboard/
│   └── index.html              ← Interactive segmentation dashboard
│
├── reports/                    ← 5 auto-generated charts (run notebook)
│
├── requirements.txt
└── README.md
```

---

## 🛠 Tech Stack & Methodology

| Step | Tool | Detail |
|------|------|--------|
| Feature Engineering | Pandas | Recency, Frequency, Monetary from raw transactions |
| Scaling | Scikit-learn StandardScaler | Z-score normalisation |
| Optimal K | Silhouette score + Elbow method | k=3 selected (silhouette=0.340) |
| Clustering | Scikit-learn KMeans | n_init=10, random_state=42 |
| Dimensionality Reduction | PCA (2D) | For scatter visualisation |
| Visualisation | Matplotlib, Seaborn | 5 charts |
| SQL | PostgreSQL | RFM scoring with NTILE, cohort retention |

---

## ⚡ Quick Start

```bash
pip install -r requirements.txt
python notebooks/01_rfm_kmeans.py
open dashboard/index.html
```

---

## 📊 Segment Results

| Segment | Customers | Revenue Share | Avg Recency | Avg Frequency | Avg Monetary |
|---------|-----------|--------------|-------------|---------------|-------------|
| Champions | 167 (33.4%) | **51.7%** | 40.6 days | 13.0 orders | ₹41.6L |
| Loyal Customers | 263 (52.6%) | 38.3% | 48.5 days | 8.8 orders | ₹19.6L |
| At-Risk | 70 (14.0%) | 10.0% | 207.7 days | 7.2 orders | ₹19.2L |

---

## 💡 Business Insights & Strategy

### 🏆 Champions (167 customers → 51.7% revenue)
- These are your best customers: recent, frequent, high-spend
- **Action:** VIP loyalty program, early access to new products, personalized thank-you campaigns
- **Risk:** If even 10% churn, you lose ₹6.95 Cr in revenue
- **Metric:** Track monthly churn rate and NPS score

### 💛 Loyal Customers (263 customers → 38.3% revenue)
- Strong base, moderate recency — engaged but not maximised
- **Action:** Cross-sell premium products (Headphones to Laptop buyers), bundle offers, loyalty points
- **Opportunity:** Moving 20% of Loyal → Champions would add ₹9.2 Cr revenue
- **Metric:** Average order value growth, category expansion rate

### ⚠️ At-Risk (70 customers → 10% revenue)
- Long recency gap (208 days avg) — these customers are disengaging
- **Action:** Win-back email series, 20% time-limited discount, personalized product recommendation
- **Urgency:** Without intervention, estimated 60% will churn within 6 months
- **Metric:** Re-engagement rate, campaign open rate, days since last purchase

---

## 🗄 SQL Highlights

- **RFM Scoring** using `NTILE(5)` window function for percentile-based scoring
- **Cohort Analysis** — month-by-month retention tracking using `DATE_TRUNC` + `AGE`
- **CLV Calculation** — historical + projected annual customer lifetime value
- **Champion Behaviour** — preferred regions and products for top-tier customers
- **Win-back Targeting** — At-Risk customers sorted by lost revenue potential

---

## 📈 Charts Generated

| File | Description |
|------|-------------|
| `01_optimal_k.png` | Elbow curve + silhouette score comparison |
| `02_rfm_distributions.png` | RFM histograms per segment |
| `03_pca_scatter.png` | 2D PCA projection — cluster separation |
| `04_segment_overview.png` | Revenue share donut + customer count bar |
| `05_rfm_heatmap.png` | Segment × RFM dimension heatmap |

---

## 📌 Interview Talking Points

- "I chose K-Means after comparing 7 values of k using both elbow method and silhouette score — I didn't just guess k=3"
- "The SQL file shows I can do RFM scoring purely in SQL using NTILE window functions, without needing Python"
- "The cohort retention query uses DATE_TRUNC and self-joins — the same pattern used in production analytics at companies like Flipkart"
- "The At-Risk segment has 208-day average recency — without a win-back campaign, I estimated ₹8 Cr at risk of churning"

---

*Built by [Your Name] | Data Analyst Portfolio | 2024*
