-- ============================================================
-- PROJECT 2: CUSTOMER SEGMENTATION ANALYSIS
-- SQL Queries — RFM scoring, cohort analysis & segment actions
-- Table: sales (same as Project 1) + rfm_segments view
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- STEP 1: Build RFM Table from raw sales
-- ────────────────────────────────────────────────────────────
CREATE TABLE rfm AS
SELECT
    customer_id,
    DATE_PART('day', '2024-01-01'::date - MAX(date))        AS recency,
    COUNT(DISTINCT order_id)                                  AS frequency,
    SUM(revenue)                                              AS monetary
FROM sales
GROUP BY customer_id;


-- ────────────────────────────────────────────────────────────
-- STEP 2: RFM Percentile Scoring (1–5 scale)
-- ────────────────────────────────────────────────────────────
CREATE VIEW rfm_scored AS
SELECT
    customer_id,
    recency,
    frequency,
    monetary,
    -- Recency: lower days = better = higher score
    NTILE(5) OVER (ORDER BY recency DESC)    AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC)   AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC)    AS m_score
FROM rfm;


-- ────────────────────────────────────────────────────────────
-- STEP 3: Composite RFM Score + Segment Labels
-- ────────────────────────────────────────────────────────────
CREATE VIEW rfm_segments AS
SELECT
    customer_id,
    recency, frequency, monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score)                            AS rfm_total,
    CASE
        WHEN (r_score + f_score + m_score) >= 12 THEN 'Champions'
        WHEN (r_score + f_score + m_score) >= 8  THEN 'Loyal Customers'
        ELSE 'At-Risk'
    END                                                      AS segment
FROM rfm_scored;


-- ────────────────────────────────────────────────────────────
-- SECTION A: SEGMENT SUMMARY
-- ────────────────────────────────────────────────────────────

-- A1. Segment KPI Overview
SELECT
    segment,
    COUNT(*)                                                 AS customers,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)      AS customer_share_pct,
    ROUND(AVG(recency), 1)                                   AS avg_recency_days,
    ROUND(AVG(frequency), 1)                                 AS avg_frequency,
    ROUND(AVG(monetary), 0)                                  AS avg_monetary,
    ROUND(SUM(monetary), 0)                                  AS total_revenue,
    ROUND(SUM(monetary) * 100.0 / SUM(SUM(monetary)) OVER (), 2) AS revenue_share_pct
FROM rfm_segments
GROUP BY segment
ORDER BY avg_monetary DESC;


-- A2. Segment RFM Score Distribution
SELECT
    segment,
    ROUND(AVG(r_score), 2)      AS avg_recency_score,
    ROUND(AVG(f_score), 2)      AS avg_frequency_score,
    ROUND(AVG(m_score), 2)      AS avg_monetary_score,
    ROUND(AVG(rfm_total), 2)    AS avg_total_score,
    MIN(rfm_total)              AS min_score,
    MAX(rfm_total)              AS max_score
FROM rfm_segments
GROUP BY segment
ORDER BY avg_total_score DESC;


-- ────────────────────────────────────────────────────────────
-- SECTION B: CHAMPIONS DEEP DIVE
-- ────────────────────────────────────────────────────────────

-- B1. Top 20 Champions by Revenue
SELECT
    r.customer_id,
    r.recency,
    r.frequency,
    ROUND(r.monetary, 0)                 AS lifetime_value,
    ROUND(r.monetary / r.frequency, 0)   AS avg_order_value
FROM rfm_segments r
WHERE r.segment = 'Champions'
ORDER BY r.monetary DESC
LIMIT 20;


-- B2. Champions purchasing behaviour by region
SELECT
    s.region,
    COUNT(DISTINCT s.customer_id)                   AS champion_customers,
    ROUND(SUM(s.revenue), 0)                         AS revenue_from_champions,
    ROUND(AVG(s.revenue), 0)                         AS avg_order_value
FROM sales s
INNER JOIN rfm_segments r ON s.customer_id = r.customer_id
WHERE r.segment = 'Champions'
GROUP BY s.region
ORDER BY revenue_from_champions DESC;


-- B3. Champions' favourite products
SELECT
    s.product,
    COUNT(DISTINCT s.customer_id)        AS champion_buyers,
    ROUND(SUM(s.revenue), 0)             AS revenue,
    ROUND(AVG(s.revenue), 0)             AS avg_order_value
FROM sales s
INNER JOIN rfm_segments r ON s.customer_id = r.customer_id
WHERE r.segment = 'Champions'
GROUP BY s.product
ORDER BY revenue DESC;


-- ────────────────────────────────────────────────────────────
-- SECTION C: AT-RISK WIN-BACK ANALYSIS
-- ────────────────────────────────────────────────────────────

-- C1. At-Risk customers sorted by lost revenue potential
SELECT
    r.customer_id,
    r.recency,
    r.frequency,
    ROUND(r.monetary, 0)                 AS lifetime_value,
    ROUND(r.monetary / r.frequency, 0)   AS avg_order_value,
    '20% win-back discount'              AS recommended_action
FROM rfm_segments r
WHERE r.segment = 'At-Risk'
ORDER BY r.monetary DESC;


-- C2. At-Risk customers' last purchase — what did they buy?
SELECT
    s.customer_id,
    s.product,
    s.category,
    s.date                              AS last_purchase_date,
    ROUND(s.revenue, 0)                 AS last_order_value
FROM sales s
INNER JOIN rfm_segments r ON s.customer_id = r.customer_id
INNER JOIN (
    SELECT customer_id, MAX(date) AS last_date
    FROM sales GROUP BY customer_id
) ld ON s.customer_id = ld.customer_id AND s.date = ld.last_date
WHERE r.segment = 'At-Risk'
ORDER BY ld.last_date ASC;


-- ────────────────────────────────────────────────────────────
-- SECTION D: COHORT ANALYSIS (Monthly)
-- ────────────────────────────────────────────────────────────

-- D1. Monthly Acquisition Cohort
WITH first_purchase AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(date))   AS cohort_month
    FROM sales
    GROUP BY customer_id
),
cohort_orders AS (
    SELECT
        fp.customer_id,
        fp.cohort_month,
        DATE_TRUNC('month', s.date)      AS order_month,
        DATE_PART('month', AGE(DATE_TRUNC('month', s.date), fp.cohort_month)) AS period_number
    FROM sales s
    JOIN first_purchase fp ON s.customer_id = fp.customer_id
)
SELECT
    TO_CHAR(cohort_month, 'YYYY-MM')    AS cohort,
    period_number,
    COUNT(DISTINCT customer_id)          AS retained_customers
FROM cohort_orders
GROUP BY cohort_month, period_number
ORDER BY cohort_month, period_number;


-- D2. Retention Rate by Cohort Month
WITH first_purchase AS (
    SELECT customer_id, DATE_TRUNC('month', MIN(date)) AS cohort_month
    FROM sales GROUP BY customer_id
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS total_customers
    FROM first_purchase GROUP BY cohort_month
),
cohort_orders AS (
    SELECT fp.customer_id, fp.cohort_month, DATE_TRUNC('month', s.date) AS order_month,
           DATE_PART('month', AGE(DATE_TRUNC('month', s.date), fp.cohort_month)) AS period_number
    FROM sales s JOIN first_purchase fp ON s.customer_id = fp.customer_id
)
SELECT
    TO_CHAR(c.cohort_month, 'YYYY-MM')   AS cohort,
    co.period_number,
    ROUND(COUNT(DISTINCT co.customer_id) * 100.0 / cs.total_customers, 2) AS retention_rate_pct
FROM cohort_orders co
JOIN first_purchase c ON co.customer_id = c.customer_id
JOIN cohort_size cs ON c.cohort_month = cs.cohort_month
GROUP BY c.cohort_month, co.period_number, cs.total_customers
ORDER BY c.cohort_month, co.period_number;


-- ────────────────────────────────────────────────────────────
-- SECTION E: CUSTOMER LIFETIME VALUE (CLV)
-- ────────────────────────────────────────────────────────────

-- E1. Historical CLV Ranking
SELECT
    customer_id,
    segment,
    recency,
    frequency,
    ROUND(monetary, 0)                                AS historical_clv,
    ROUND(monetary / frequency, 0)                    AS avg_order_value,
    ROUND(monetary / NULLIF(frequency, 0) * 12, 0)   AS projected_annual_clv,
    RANK() OVER (ORDER BY monetary DESC)              AS clv_rank
FROM rfm_segments
ORDER BY historical_clv DESC
LIMIT 25;


-- E2. Average CLV by Segment
SELECT
    segment,
    ROUND(AVG(monetary), 0)                               AS avg_clv,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monetary), 0) AS median_clv,
    ROUND(MAX(monetary), 0)                               AS max_clv,
    ROUND(MIN(monetary), 0)                               AS min_clv
FROM rfm_segments
GROUP BY segment
ORDER BY avg_clv DESC;
