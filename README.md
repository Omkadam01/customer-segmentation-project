# Customer Segmentation Analysis

RFM-based customer segmentation using K-Means clustering on 500 customers derived from 5,000 sales transactions. Segments customers into Champions, Loyal Customers, and At-Risk groups with a full retention strategy for each.

---

## Files

| File | Description |
|------|-------------|
| `sales_data.csv` | 5,000 raw sales transactions (source data) |
| `rfm_segments.csv` | 500 customers with computed RFM values and segment labels |
| `segment_summary.csv` | Aggregated metrics per segment |
| `customer_segmentation.xlsx` | Formatted Excel report with segment tables and strategy playbook |
| `analysis.py` | Full ML pipeline — RFM scoring, StandardScaler, KMeans, PCA, 5 charts |
| `queries.sql` | SQL-based RFM scoring, cohort retention, and CLV queries |
| `dashboard.html` | Interactive segmentation dashboard — open in any browser |
| `requirements.txt` | Python dependencies |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Feature Engineering | Python, Pandas |
| Machine Learning | Scikit-learn — StandardScaler, KMeans, PCA |
| Optimal K Selection | Elbow method and Silhouette score comparison |
| Visualization | Matplotlib, Seaborn |
| SQL | PostgreSQL — NTILE, cohort analysis, CLV calculation |
| Web Dashboard | Chart.js, HTML, CSS, JavaScript |

---

## Quick Start

```bash
pip install -r requirements.txt
python analysis.py
```

Open `dashboard.html` in a browser to explore segment profiles interactively.

## Web Deployment

The dashboard is a static site and is prepared for GitHub Pages. It does not
require a backend, database, environment variables, or build command.

- Local preview: run `python -m http.server 8000`, then open
  `http://localhost:8000/`.
- Production entry point: `index.html` redirects to the existing
  `dashboard.html` interface.
- Deployment workflow: `.github/workflows/pages.yml` publishes the repository
  root whenever a commit is pushed to `main` (after GitHub Pages is configured
  to use **GitHub Actions** as its source).
- Expected URL after activation:
  `https://omkadam01.github.io/customer-segmentation-project/`

No visitor data is collected by this dashboard. Chart.js and the two web fonts
are loaded from public CDNs, so an internet connection is required for charts
and custom typography.

---

## Methodology

1. Compute Recency, Frequency, and Monetary (RFM) values per customer from raw transactions
2. Normalize features using StandardScaler
3. Select optimal k by comparing Elbow curve and Silhouette scores across k = 2 to 8
4. Fit KMeans with k = 3 (Silhouette = 0.340)
5. Label clusters by descending average monetary value
6. Visualize using PCA 2D projection and RFM heatmaps

---

## Segment Results

| Segment | Customers | Revenue Share | Avg Recency | Avg Orders | Avg Lifetime Value |
|---------|-----------|--------------|-------------|------------|--------------------|
| Champions | 167 (33.4%) | 51.7% | 40.6 days | 13.0 | Rs. 41.6L |
| Loyal Customers | 263 (52.6%) | 38.3% | 48.5 days | 8.8 | Rs. 19.6L |
| At-Risk | 70 (14.0%) | 10.0% | 207.7 days | 7.2 | Rs. 19.2L |

---

## Business Strategy

**Champions** — Launch a VIP loyalty program with early product access and personalized rewards. Track churn rate and NPS score monthly. If even 10% of this group churns, the business loses Rs. 6.95 Cr in revenue.

**Loyal Customers** — Cross-sell premium products and introduce bundle offers. Moving 20% of this group to Champion status would add an estimated Rs. 9.2 Cr in revenue.

**At-Risk** — Deploy a win-back email series with a time-limited 20% discount. Without intervention, an estimated 60% will churn within 6 months.

---

## SQL Highlights

- RFM percentile scoring using `NTILE(5)` window function
- Monthly cohort retention using `DATE_TRUNC` and `AGE`
- Customer Lifetime Value calculation — historical and projected annual
- At-Risk customers ranked by lost revenue potential

---

## Repo Name

`customer-segmentation-project`

## Description

RFM + K-Means customer segmentation — Python, Scikit-learn, SQL cohort analysis, interactive HTML dashboard.

---


